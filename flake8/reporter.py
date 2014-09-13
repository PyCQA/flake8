# -*- coding: utf-8 -*-
# Adapted from a contribution of Johan Dahlin

import collections
import sys
try:
    import multiprocessing
except ImportError:     # Python 2.5
    multiprocessing = None

import pep8

__all__ = ['multiprocessing', 'BaseQReport', 'QueueReport']


class BaseQReport(pep8.BaseReport):
    """Base Queue Report."""
    _loaded = False   # Windows support

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
            # collect queues
            for i in range(self.n_jobs):
                self.task_queue.put('DONE')
                self.update_state(self.result_queue.get())
        except KeyboardInterrupt:
            pass
        finally:
            # cleanup queues to unlock threads
            while not self.result_queue.empty():
                self.result_queue.get_nowait()
            while not self.task_queue.empty():
                self.task_queue.get_nowait()

            super(BaseQReport, self).stop()

    def process_main(self):
        if not self._loaded:
            # Windows needs to parse again the configuration
            from flake8.main import get_style_guide, DEFAULT_CONFIG
            get_style_guide(parse_argv=True, config_file=DEFAULT_CONFIG)
        try:
            for filename in iter(self.task_queue.get, 'DONE'):
                self.input_file(filename)
        except KeyboardInterrupt:
            pass
        finally:
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


class QueueReport(pep8.StandardReport, BaseQReport):
    """Standard Queue Report."""
