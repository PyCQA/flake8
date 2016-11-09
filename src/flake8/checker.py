"""Checker Manager and Checker classes."""
import errno
import logging
import os
import sys
import tokenize

try:
    import multiprocessing
except ImportError:
    multiprocessing = None

try:
    import Queue as queue
except ImportError:
    import queue

from flake8 import defaults
from flake8 import exceptions
from flake8 import processor
from flake8 import utils

LOG = logging.getLogger(__name__)

SERIAL_RETRY_ERRNOS = set([
    # ENOSPC: Added by sigmavirus24
    # > On some operating systems (OSX), multiprocessing may cause an
    # > ENOSPC error while trying to trying to create a Semaphore.
    # > In those cases, we should replace the customized Queue Report
    # > class with pep8's StandardReport class to ensure users don't run
    # > into this problem.
    # > (See also: https://gitlab.com/pycqa/flake8/issues/74)
    errno.ENOSPC,
    # NOTE(sigmavirus24): When adding to this list, include the reasoning
    # on the lines before the error code and always append your error
    # code. Further, please always add a trailing `,` to reduce the visual
    # noise in diffs.
])


class Manager(object):
    """Manage the parallelism and checker instances for each plugin and file.

    This class will be responsible for the following:

    - Determining the parallelism of Flake8, e.g.:

      * Do we use :mod:`multiprocessing` or is it unavailable?

      * Do we automatically decide on the number of jobs to use or did the
        user provide that?

    - Falling back to a serial way of processing files if we run into an
      OSError related to :mod:`multiprocessing`

    - Organizing the results of each checker so we can group the output
      together and make our output deterministic.
    """

    def __init__(self, style_guide, arguments, checker_plugins, junit_xml_report):
        """Initialize our Manager instance.

        :param style_guide:
            The instantiated style guide for this instance of Flake8.
        :type style_guide:
            flake8.style_guide.StyleGuide
        :param list arguments:
            The extra arguments parsed from the CLI (if any)
        :param checker_plugins:
            The plugins representing checks parsed from entry-points.
        :type checker_plugins:
            flake8.plugins.manager.Checkers
        :param str junit_xml_report:
            Filename to write a JUnit XML report to
        """
        self.arguments = arguments
        self.style_guide = style_guide
        self.options = style_guide.options
        self.checks = checker_plugins
        self.junit_xml_report = junit_xml_report
        self.jobs = self._job_count()
        self.process_queue = None
        self.results_queue = None
        self.statistics_queue = None
        self.using_multiprocessing = self.jobs > 1
        self.processes = []
        self.checkers = []
        self.statistics = {
            'files': 0,
            'logical lines': 0,
            'physical lines': 0,
            'tokens': 0,
        }

        if self.using_multiprocessing:
            try:
                self.process_queue = multiprocessing.Queue()
                self.results_queue = multiprocessing.Queue()
                self.statistics_queue = multiprocessing.Queue()
            except OSError as oserr:
                if oserr.errno not in SERIAL_RETRY_ERRNOS:
                    raise
                self.using_multiprocessing = False

    @staticmethod
    def _cleanup_queue(q):
        while not q.empty():
            q.get_nowait()

    def _force_cleanup(self):
        if self.using_multiprocessing:
            for proc in self.processes:
                proc.join(0.2)
            self._cleanup_queue(self.process_queue)
            self._cleanup_queue(self.results_queue)
            self._cleanup_queue(self.statistics_queue)

    def _process_statistics(self):
        all_statistics = self.statistics
        if self.using_multiprocessing:
            total_number_of_checkers = len(self.checkers)
            statistics_gathered = 0
            while statistics_gathered < total_number_of_checkers:
                try:
                    statistics = self.statistics_queue.get(block=False)
                    statistics_gathered += 1
                except queue.Empty:
                    break

                for statistic in defaults.STATISTIC_NAMES:
                    all_statistics[statistic] += statistics[statistic]
        else:
            statistics_generator = (checker.statistics
                                    for checker in self.checkers)
            for statistics in statistics_generator:
                for statistic in defaults.STATISTIC_NAMES:
                    all_statistics[statistic] += statistics[statistic]
        all_statistics['files'] += len(self.checkers)

    def _job_count(self):
        # type: () -> int
        # First we walk through all of our error cases:
        # - multiprocessing library is not present
        # - we're running on windows in which case we know we have significant
        #   implemenation issues
        # - the user provided stdin and that's not something we can handle
        #   well
        # - we're processing a diff, which again does not work well with
        #   multiprocessing and which really shouldn't require multiprocessing
        # - the user provided some awful input
        if not multiprocessing:
            LOG.warning('The multiprocessing module is not available. '
                        'Ignoring --jobs arguments.')
            return 0

        if (utils.is_windows() and
                not utils.can_run_multiprocessing_on_windows()):
            LOG.warning('The --jobs option is not available on Windows due to'
                        ' a bug (https://bugs.python.org/issue27649) in '
                        'Python 2.7.11+ and 3.3+. We have detected that you '
                        'are running an unsupported version of Python on '
                        'Windows. Ignoring --jobs arguments.')
            return 0

        if utils.is_using_stdin(self.arguments):
            LOG.warning('The --jobs option is not compatible with supplying '
                        'input using - . Ignoring --jobs arguments.')
            return 0

        if self.options.diff:
            LOG.warning('The --diff option was specified with --jobs but '
                        'they are not compatible. Ignoring --jobs arguments.')
            return 0

        jobs = self.options.jobs
        if jobs != 'auto' and not jobs.isdigit():
            LOG.warning('"%s" is not a valid parameter to --jobs. Must be one '
                        'of "auto" or a numerical value, e.g., 4.', jobs)
            return 0

        # If the value is "auto", we want to let the multiprocessing library
        # decide the number based on the number of CPUs. However, if that
        # function is not implemented for this particular value of Python we
        # default to 1
        if jobs == 'auto':
            try:
                return multiprocessing.cpu_count()
            except NotImplementedError:
                return 0

        # Otherwise, we know jobs should be an integer and we can just convert
        # it to an integer
        return int(jobs)

    def _results(self):
        seen_done = 0
        LOG.info('Retrieving results')
        while True:
            result = self.results_queue.get()
            if result == 'DONE':
                seen_done += 1
                if seen_done >= self.jobs:
                    break
                continue

            yield result

    def _handle_results(self, filename, results):
        style_guide = self.style_guide
        reported_results_count = 0
        for (error_code, line_number, column, text, physical_line) in results:
            reported_results_count += style_guide.handle_error(
                code=error_code,
                filename=filename,
                line_number=line_number,
                column_number=column,
                text=text,
                physical_line=physical_line,
            )
        return reported_results_count

    def is_path_excluded(self, path):
        # type: (str) -> bool
        """Check if a path is excluded.

        :param str path:
            Path to check against the exclude patterns.
        :returns:
            True if there are exclude patterns and the path matches,
            otherwise False.
        :rtype:
            bool
        """
        if path == '-':
            if self.options.stdin_display_name == 'stdin':
                return False
            path = self.options.stdin_display_name

        exclude = self.options.exclude
        if not exclude:
            return False
        basename = os.path.basename(path)
        if utils.fnmatch(basename, exclude):
            LOG.debug('"%s" has been excluded', basename)
            return True

        absolute_path = os.path.abspath(path)
        match = utils.fnmatch(absolute_path, exclude)
        LOG.debug('"%s" has %sbeen excluded', absolute_path,
                  '' if match else 'not ')
        return match

    def make_checkers(self, paths=None):
        # type: (List[str]) -> NoneType
        """Create checkers for each file."""
        if paths is None:
            paths = self.arguments

        if not paths:
            paths = ['.']

        filename_patterns = self.options.filename

        # NOTE(sigmavirus24): Yes this is a little unsightly, but it's our
        # best solution right now.
        def should_create_file_checker(filename):
            """Determine if we should create a file checker."""
            matches_filename_patterns = utils.fnmatch(
                filename, filename_patterns
            )
            is_stdin = filename == '-'
            file_exists = os.path.exists(filename)
            return (file_exists and matches_filename_patterns) or is_stdin

        checks = self.checks.to_dictionary()
        self.checkers = [
            FileChecker(filename, checks, self.options)
            for argument in paths
            for filename in utils.filenames_from(argument,
                                                 self.is_path_excluded)
            if should_create_file_checker(filename)
        ]
        LOG.info('Checking %d files', len(self.checkers))

    def report(self):
        # type: () -> (int, int)
        """Report all of the errors found in the managed file checkers.

        This iterates over each of the checkers and reports the errors sorted
        by line number.

        :returns:
            A tuple of the total results found and the results reported.
        :rtype:
            tuple(int, int)
        """
        results_reported = results_found = 0
        all_results = {}
        for checker in self.checkers:
            if checker.filename not in all_results:
                all_results[checker.filename] = {'checker': checker}
            results = sorted(checker.results, key=lambda tup: (tup[1], tup[2]))
            all_results[checker.filename]['errors'] = results
            results_reported += self._handle_results(checker.display_name,
                                                     results)
            results_found += len(results)

        # Output JUnit XML
        self.report_junit_xml(all_results)

        return (results_found, results_reported)

    def report_junit_xml(self, all_results):
        """
        Report all results to a JUnit XML file

        :param dict all_results: A dictionary containing all results
        """
        # If no junit_xml_report file was provided, just skip this
        if not self.junit_xml_report:
            return

        testcase_success_template = '<testcase classname="{classname}" file="{filename}" line="{line_number}" ' \
                                    'name="{name}" time="{time_elapsed}"/>'
        testcase_failure_template = '<testcase classname="{classname}" file="{filename}" line="{line_number}" ' \
                                    'name="{name}" time="{time_elapsed}"><failure message="{short_message}">' \
                                    '{long_message}</failure></testcase>'
        testsuite_template = '<testsuite errors="{num_errors}" failures="{num_failures}" name="flake8" ' \
                             'skips="{num_skips}" tests="{num_tests}" time="{time_elapsed}">' \
                             '\n{testcase_nodes}\n</testsuite>'

        testcase_nodes = []
        num_failures = 0
        num_files = len(all_results)
        for filename in sorted(all_results.keys()):
            errors = all_results[filename]['errors']
            if errors:
                num_failures += 1
                for error_code, line_number, column, text, physical_line in errors:
                    testcase_nodes.append(testcase_failure_template.format(**{
                        'classname': '',  # n.a.
                        'filename': filename,
                        'line_number': line_number,
                        'name': '%s: %s' % (filename, error_code),
                        'time_elapsed': '0.1',  # Not yet measured?
                        'short_message': text,
                        'long_message': 'lineno: %d, column: %d, code: %s, error: %s\n>>%s' % (
                            line_number, column, error_code, text, physical_line)
                    }))
            else:
                testcase_nodes.append(testcase_success_template.format(**{
                    'classname': '',  # n.a.
                    'filename': filename,
                    'line_number': 1,
                    'name': filename,
                    'time_elapsed': '0.1',  # Not yet measured?
                }))

        ouput = testsuite_template.format(**{
            'num_errors': 0,
            'num_failures': num_failures,
            'num_skips': 0,
            'num_tests': num_files,
            'time_elapsed': 1,
            'testcase_nodes': '\n'.join(testcase_nodes)
        })

        with open(self.junit_xml_report, 'w') as junit_xml_file:
            junit_xml_file.write(ouput)

    def run_parallel(self):
        """Run the checkers in parallel."""
        LOG.info('Starting %d process workers', self.jobs)
        for i in range(self.jobs):
            proc = multiprocessing.Process(
                target=_run_checks_from_queue,
                args=(self.process_queue, self.results_queue,
                      self.statistics_queue)
            )
            proc.daemon = True
            proc.start()
            self.processes.append(proc)

        final_results = {}
        for (filename, results) in self._results():
            final_results[filename] = results

        for checker in self.checkers:
            filename = checker.display_name
            checker.results = sorted(final_results.get(filename, []),
                                     key=lambda tup: (tup[2], tup[2]))

    def run_serial(self):
        """Run the checkers in serial."""
        for checker in self.checkers:
            checker.run_checks(self.results_queue, self.statistics_queue)

    def run(self):
        """Run all the checkers.

        This will intelligently decide whether to run the checks in parallel
        or whether to run them in serial.

        If running the checks in parallel causes a problem (e.g.,
        https://gitlab.com/pycqa/flake8/issues/74) this also implements
        fallback to serial processing.
        """
        try:
            if self.using_multiprocessing:
                self.run_parallel()
            else:
                self.run_serial()
        except OSError as oserr:
            if oserr.errno not in SERIAL_RETRY_ERRNOS:
                LOG.exception(oserr)
                raise
            LOG.warning('Running in serial after OS exception, %r', oserr)
            self.run_serial()
        except KeyboardInterrupt:
            LOG.warning('Flake8 was interrupted by the user')
            raise exceptions.EarlyQuit('Early quit while running checks')
        finally:
            self._force_cleanup()

    def start(self, paths=None):
        """Start checking files.

        :param list paths:
            Path names to check. This is passed directly to
            :meth:`~Manager.make_checkers`.
        """
        LOG.info('Making checkers')
        self.make_checkers(paths)
        if not self.using_multiprocessing:
            return

        LOG.info('Populating process queue')
        for checker in self.checkers:
            self.process_queue.put(checker)

        for i in range(self.jobs):
            self.process_queue.put('DONE')

    def stop(self):
        """Stop checking files."""
        self._process_statistics()
        for proc in self.processes:
            LOG.info('Joining %s to the main process', proc.name)
            proc.join()


class FileChecker(object):
    """Manage running checks for a file and aggregate the results."""

    def __init__(self, filename, checks, options):
        """Initialize our file checker.

        :param str filename:
            Name of the file to check.
        :param checks:
            The plugins registered to check the file.
        :type checks:
            dict
        :param options:
            Parsed option values from config and command-line.
        :type options:
            optparse.Values
        """
        self.options = options
        self.filename = filename
        self.checks = checks
        self.results = []
        self.processor = self._make_processor()
        self.display_name = self.processor.filename
        self.statistics = {
            'tokens': 0,
            'logical lines': 0,
            'physical lines': len(self.processor.lines),
        }

    def _make_processor(self):
        try:
            return processor.FileProcessor(self.filename, self.options)
        except IOError:
            # If we can not read the file due to an IOError (e.g., the file
            # does not exist or we do not have the permissions to open it)
            # then we need to format that exception for the user.
            # NOTE(sigmavirus24): Historically, pep8 has always reported this
            # as an E902. We probably *want* a better error code for this
            # going forward.
            (exc_type, exception) = sys.exc_info()[:2]
            message = '{0}: {1}'.format(exc_type.__name__, exception)
            self.report('E902', 0, 0, message)
            return None

    def report(self, error_code, line_number, column, text, line=None):
        # type: (str, int, int, str) -> str
        """Report an error by storing it in the results list."""
        if error_code is None:
            error_code, text = text.split(' ', 1)

        physical_line = line
        # If we're recovering from a problem in _make_processor, we will not
        # have this attribute.
        if not physical_line and getattr(self, 'processor', None):
            physical_line = self.processor.line_for(line_number)

        error = (error_code, line_number, column, text, physical_line)
        self.results.append(error)
        return error_code

    def run_check(self, plugin, **arguments):
        """Run the check in a single plugin."""
        LOG.debug('Running %r with %r', plugin, arguments)
        try:
            self.processor.keyword_arguments_for(
                plugin['parameters'],
                arguments,
            )
        except AttributeError as ae:
            LOG.error('Plugin requested unknown parameters.')
            raise exceptions.PluginRequestedUnknownParameters(
                plugin=plugin,
                exception=ae,
            )
        return plugin['plugin'](**arguments)

    @staticmethod
    def _extract_syntax_information(exception):
        token = ()
        if len(exception.args) > 1:
            token = exception.args[1]
            if len(token) > 2:
                row, column = token[1:3]
        else:
            row, column = (1, 0)

        if column > 0 and token and isinstance(exception, SyntaxError):
            # NOTE(sigmavirus24): SyntaxErrors report 1-indexed column
            # numbers. We need to decrement the column number by 1 at
            # least.
            offset = 1
            physical_line = token[-1]
            if len(physical_line) == column and physical_line[-1] == '\n':
                # NOTE(sigmavirus24): By default, we increment the column
                # value so that it's always 1-indexed. The SyntaxError that
                # we are trying to handle here will end up being 2 past
                # the end of the line. This happens because the
                # SyntaxError is technically the character after the
                # new-line. For example, if the code is ``foo(\n`` then
                # ``\n`` will be 4, the empty string will be 5 but most
                # tools want to report the at column 4, i.e., the opening
                # parenthesis. Semantically, having a column number of 6 is
                # correct but not useful for tooling (e.g., editors that
                # constantly run Flake8 for users).
                # See also: https://gitlab.com/pycqa/flake8/issues/237
                offset += 1
            column -= offset
        return row, column

    def run_ast_checks(self):
        """Run all checks expecting an abstract syntax tree."""
        try:
            ast = self.processor.build_ast()
        except (ValueError, SyntaxError, TypeError):
            (exc_type, exception) = sys.exc_info()[:2]
            row, column = self._extract_syntax_information(exception)
            self.report('E999', row, column, '%s: %s' %
                        (exc_type.__name__, exception.args[0]))
            return

        for plugin in self.checks['ast_plugins']:
            checker = self.run_check(plugin, tree=ast)
            # If the plugin uses a class, call the run method of it, otherwise
            # the call should return something iterable itself
            try:
                runner = checker.run()
            except AttributeError:
                runner = checker
            for (line_number, offset, text, check) in runner:
                self.report(
                    error_code=None,
                    line_number=line_number,
                    column=offset,
                    text=text,
                )

    def run_logical_checks(self):
        """Run all checks expecting a logical line."""
        comments, logical_line, mapping = self.processor.build_logical_line()
        if not mapping:
            return
        self.processor.update_state(mapping)

        LOG.debug('Logical line: "%s"', logical_line.rstrip())

        for plugin in self.checks['logical_line_plugins']:
            self.processor.update_checker_state_for(plugin)
            results = self.run_check(plugin, logical_line=logical_line) or ()
            for offset, text in results:
                offset = find_offset(offset, mapping)
                line_number, column_offset = offset
                self.report(
                    error_code=None,
                    line_number=line_number,
                    column=column_offset,
                    text=text,
                )

        self.processor.next_logical_line()

    def run_physical_checks(self, physical_line, override_error_line=None):
        """Run all checks for a given physical line."""
        for plugin in self.checks['physical_line_plugins']:
            self.processor.update_checker_state_for(plugin)
            result = self.run_check(plugin, physical_line=physical_line)
            if result is not None:
                column_offset, text = result
                error_code = self.report(
                    error_code=None,
                    line_number=self.processor.line_number,
                    column=column_offset,
                    text=text,
                    line=(override_error_line or physical_line),
                )

                self.processor.check_physical_error(error_code, physical_line)

    def process_tokens(self):
        """Process tokens and trigger checks.

        This can raise a :class:`flake8.exceptions.InvalidSyntax` exception.
        Instead of using this directly, you should use
        :meth:`flake8.checker.FileChecker.run_checks`.
        """
        parens = 0
        statistics = self.statistics
        file_processor = self.processor
        for token in file_processor.generate_tokens():
            statistics['tokens'] += 1
            self.check_physical_eol(token)
            token_type, text = token[0:2]
            processor.log_token(LOG, token)
            if token_type == tokenize.OP:
                parens = processor.count_parentheses(parens, text)
            elif parens == 0:
                if processor.token_is_newline(token):
                    self.handle_newline(token_type)
                elif (processor.token_is_comment(token) and
                        len(file_processor.tokens) == 1):
                    self.handle_comment(token, text)

        if file_processor.tokens:
            # If any tokens are left over, process them
            self.run_physical_checks(file_processor.lines[-1])
            self.run_logical_checks()

    def run_checks(self, results_queue, statistics_queue):
        """Run checks against the file."""
        if self.processor.should_ignore_file():
            return

        try:
            self.process_tokens()
        except exceptions.InvalidSyntax as exc:
            self.report(exc.error_code, exc.line_number, exc.column_number,
                        exc.error_message)

        self.run_ast_checks()

        if results_queue is not None:
            results_queue.put((self.filename, self.results))

        logical_lines = self.processor.statistics['logical lines']
        self.statistics['logical lines'] = logical_lines
        if statistics_queue is not None:
            statistics_queue.put(self.statistics)

    def handle_comment(self, token, token_text):
        """Handle the logic when encountering a comment token."""
        # The comment also ends a physical line
        token = list(token)
        token[1] = token_text.rstrip('\r\n')
        token[3] = (token[2][0], token[2][1] + len(token[1]))
        self.processor.tokens = [tuple(token)]
        self.run_logical_checks()

    def handle_newline(self, token_type):
        """Handle the logic when encountering a newline token."""
        if token_type == tokenize.NEWLINE:
            self.run_logical_checks()
            self.processor.reset_blank_before()
        elif len(self.processor.tokens) == 1:
            # The physical line contains only this token.
            self.processor.visited_new_blank_line()
            self.processor.delete_first_token()
        else:
            self.run_logical_checks()

    def check_physical_eol(self, token):
        """Run physical checks if and only if it is at the end of the line."""
        if processor.is_eol_token(token):
            # Obviously, a newline token ends a single physical line.
            self.run_physical_checks(token[4])
        elif processor.is_multiline_string(token):
            # Less obviously, a string that contains newlines is a
            # multiline string, either triple-quoted or with internal
            # newlines backslash-escaped. Check every physical line in the
            # string *except* for the last one: its newline is outside of
            # the multiline string, so we consider it a regular physical
            # line, and will check it like any other physical line.
            #
            # Subtleties:
            # - have to wind self.line_number back because initially it
            #   points to the last line of the string, and we want
            #   check_physical() to give accurate feedback
            line_no = token[2][0]
            with self.processor.inside_multiline(line_number=line_no):
                for line in self.processor.split_line(token):
                    self.run_physical_checks(line + '\n',
                                             override_error_line=token[4])


def _run_checks_from_queue(process_queue, results_queue, statistics_queue):
    LOG.info('Running checks in parallel')
    try:
        for checker in iter(process_queue.get, 'DONE'):
            LOG.info('Checking "%s"', checker.filename)
            checker.run_checks(results_queue, statistics_queue)
    except exceptions.PluginRequestedUnknownParameters as exc:
        print(str(exc))
    except Exception as exc:
        LOG.error('Unhandled exception occurred')
        raise
    finally:
        results_queue.put('DONE')


def find_offset(offset, mapping):
    """Find the offset tuple for a single offset."""
    if isinstance(offset, tuple):
        return offset

    for token_offset, position in mapping:
        if offset <= token_offset:
            break
    return (position[0], position[1] + offset - token_offset)
