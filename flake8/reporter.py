# -*- coding: utf-8 -*-
# Adapted from a contribution of Johan Dahlin

import collections
import errno
import re
import sys
try:
    import multiprocessing
except ImportError:     # Python 2.5
    multiprocessing = None

import pycodestyle as pep8

__all__ = ['multiprocessing', 'BaseQReport', 'QueueReport']


class BaseQReport(pep8.BaseReport):
    """Base Queue Report."""
    _loaded = False   # Windows support

    # Reasoning for ignored error numbers is in-line below
    ignored_errors = set([
        # EPIPE: Added by sigmavirus24
        # > If output during processing is piped to something that may close
        # > its own stdin before we've finished printing results, we need to
        # > catch a Broken pipe error and continue on.
        # > (See also: https://gitlab.com/pycqa/flake8/issues/69)
        errno.EPIPE,
        # NOTE(sigmavirus24): When adding to this list, include the reasoning
        # on the lines before the error code and always append your error
        # code. Further, please always add a trailing `,` to reduce the visual
        # noise in diffs.
    ])

    def __init__(self, options):
        assert options.jobs > 0
        super(BaseQReport, self).__init__(options)
        self.counters = collections.defaultdict(int)
        self.n_jobs = options.jobs

        # init queues
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        if sys.platform == 'win32':
            # Work around http://bugs.python.org/issue10845
            sys.modules['__main__'].__file__ = __file__

    def _cleanup_queue(self, queue):
        while not queue.empty():
            queue.get_nowait()

    def _put_done(self):
        # collect queues
        for i in range(self.n_jobs):
            self.task_queue.put('DONE')
            self.update_state(self.result_queue.get())

    def _process_main(self):
        if not self._loaded:
            # Windows needs to parse again the configuration
            from flake8.main import get_style_guide
            get_style_guide(parse_argv=True)
        for filename in iter(self.task_queue.get, 'DONE'):
            self.input_file(filename)

    def start(self):
        super(BaseQReport, self).start()
        self.__class__._loaded = True
        # spawn processes
        for i in range(self.n_jobs):
            p = multiprocessing.Process(target=self.process_main)
            p.daemon = True
            p.start()

    def stop(self):
        try:
            self._put_done()
        except KeyboardInterrupt:
            pass
        finally:
            # cleanup queues to unlock threads
            self._cleanup_queue(self.result_queue)
            self._cleanup_queue(self.task_queue)
            super(BaseQReport, self).stop()

    def process_main(self):
        try:
            self._process_main()
        except KeyboardInterrupt:
            pass
        except IOError as ioerr:
            # If we happen across an IOError that we aren't certain can/should
            # be ignored, we should re-raise the exception.
            if ioerr.errno not in self.ignored_errors:
                raise
        finally:
            # ensure all output is flushed before main process continues
            sys.stdout.flush()
            sys.stderr.flush()
            self.result_queue.put(self.get_state())

    def get_state(self):
        return {'total_errors': self.total_errors,
                'counters': self.counters,
                'messages': self.messages}

    def update_state(self, state):
        self.total_errors += state['total_errors']
        for key, value in state['counters'].items():
            self.counters[key] += value
        self.messages.update(state['messages'])


class FileQReport(BaseQReport):
    """File Queue Report."""
    print_filename = True


class QueueReport(pep8.StandardReport, BaseQReport):
    """Standard Queue Report."""

    def get_file_results(self):
        """Print the result and return the overall count for this file."""
        self._deferred_print.sort()

        for line_number, offset, code, text, doc in self._deferred_print:
            print(self._fmt % {
                'path': self.filename,
                'row': self.line_offset + line_number, 'col': offset + 1,
                'code': code, 'text': text,
            })
            # stdout is block buffered when not stdout.isatty().
            # line can be broken where buffer boundary since other processes
            # write to same file.
            # flush() after print() to avoid buffer boundary.
            # Typical buffer size is 8192. line written safely when
            # len(line) < 8192.
            sys.stdout.flush()
            if self._show_source:
                if line_number > len(self.lines):
                    line = ''
                else:
                    line = self.lines[line_number - 1]
                print(line.rstrip())
                sys.stdout.flush()
                print(re.sub(r'\S', ' ', line[:offset]) + '^')
                sys.stdout.flush()
            if self._show_pep8 and doc:
                print('    ' + doc.strip())
                sys.stdout.flush()
        return self.file_errors
