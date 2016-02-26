"""Checker Manager and Checker classes."""
import io
import logging
import os
import sys
import tokenize

try:
    import multiprocessing
except ImportError:
    multiprocessing = None

from flake8 import utils

LOG = logging.getLogger(__name__)


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

    def __init__(self, options, arguments, checker_plugins):
        """Initialize our Manager instance.

        :param options:
            The options parsed from config files and CLI.
        :type options:
            optparse.Values
        :param list arguments:
            The extra arguments parsed from the CLI (if any)
        :param checker_plugins:
            The plugins representing checks parsed from entry-points.
        :type checker_plugins:
            flake8.plugins.manager.Checkers
        """
        self.arguments = arguments
        self.options = options
        self.checks = checker_plugins
        self.jobs = self._job_count()
        self.process_queue = None
        self.using_multiprocessing = False
        self.processes = []
        self.checkers = []

        if self.jobs is not None and self.jobs > 1:
            self.using_multiprocessing = True
            self.process_queue = multiprocessing.Queue()

    def _job_count(self):
        # type: () -> Union[int, NoneType]
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
            return None

        if utils.is_windows():
            LOG.warning('The --jobs option is not available on Windows. '
                        'Ignoring --jobs arguments.')
            return None

        if utils.is_using_stdin(self.arguments):
            LOG.warning('The --jobs option is not compatible with supplying '
                        'input using - . Ignoring --jobs arguments.')
            return None

        if self.options.diff:
            LOG.warning('The --diff option was specified with --jobs but '
                        'they are not compatible. Ignoring --jobs arguments.')
            return None

        jobs = self.options.jobs
        if jobs != 'auto' and not jobs.isdigit():
            LOG.warning('"%s" is not a valid parameter to --jobs. Must be one '
                        'of "auto" or a numerical value, e.g., 4.', jobs)
            return None

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

    def start(self):
        """Start checking files."""
        pass
        # for i in range(self.jobs or 0):
        #     proc = multiprocessing.Process(target=self.process_files)
        #     proc.daemon = True
        #     proc.start()
        #     self.processes.append(proc)

    def make_checkers(self, paths=None):
        # type: (List[str]) -> NoneType
        """Create checkers for each file."""
        if paths is None:
            paths = self.arguments
        filename_patterns = self.options.filename
        self.checkers = [
            FileChecker(filename, self.checks)
            for argument in paths
            for filename in utils.filenames_from(argument,
                                                 self.is_path_excluded)
            if utils.fnmatch(filename, filename_patterns)
        ]

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
        exclude = self.options.exclude
        if not exclude:
            return False
        basename = os.path.basename(path)
        if utils.fnmatch(basename, exclude):
            LOG.info('"%s" has been excluded', basename)
            return True

        absolute_path = os.path.abspath(path)
        match = utils.fnmatch(absolute_path, exclude)
        LOG.info('"%s" has %sbeen excluded', absolute_path,
                 '' if match else 'not ')
        return match


class FileChecker(object):
    """Manage running checks for a file and aggregate the results."""

    def __init__(self, filename, checks):
        # type: (str, flake8.plugins.manager.Checkers) -> NoneType
        """Initialize our file checker.

        :param str filename:
            Name of the file to check.
        :param checks:
            The plugins registered to check the file.
        :type checks:
            flake8.plugins.manager.Checkers
        """
        self.filename = filename
        self.checks = checks
        self.results = []
        self.processor = FileProcessor(filename)

    def report(self, error_code, line_number, column, text):
        # type: (str, int, int, str) -> NoneType
        """Report an error by storing it in the results list."""
        error = (error_code, self.filename, line_number, column, text)
        self.results.append(error)

    def run_check(self, plugin):
        """Run the check in a single plugin."""
        arguments = {}
        for parameter in plugin.parameters:
            arguments[parameter] = self.attributes[parameter]
        return plugin.execute(**arguments)

    def run_checks(self):
        """Run checks against the file."""
        self.run_ast_checks()
        self.run_physical_checks()
        self.run_logical_checks()

    def run_ast_checks(self):
        """Run checks that require an abstract syntax tree."""
        pass

    def run_physical_checks(self):
        """Run checks that require the physical line."""
        pass

    def run_logical_checks(self):
        """Run checks that require the logical line from a file."""
        pass


class FileProcessor(object):
    """Processes a file and holdes state.

    This processes a file by generating tokens, logical and physical lines,
    and AST trees. This also provides a way of passing state about the file
    to checks expecting that state. Any public attribute on this object can
    be requested by a plugin. The known public attributes are:

    - multiline
    - max_line_length
    - tokens
    - indent_level
    - indect_char
    - noqa
    - verbose
    - line_number
    - total_lines
    - previous_logical
    - logical_line
    - previous_indent_level
    - blank_before
    - blank_lines
    """

    def __init__(self, filename):
        """Initialice our file processor.

        :param str filename:
            Name of the file to process
        """
        self.filename = filename
        self.lines = self.read_lines()
        self.strip_utf_bom()

    def read_lines(self):
        # type: () -> List[str]
        """Read the lines for this file checker."""
        if self.filename is None or self.filename == '-':
            self.filename = 'stdin'
            return self.read_lines_from_stdin()
        return self.read_lines_from_filename()

    def _readlines_py2(self):
        # type: () -> List[str]
        with open(self.filename, 'rU') as fd:
            return fd.readlines()

    def _readlines_py3(self):
        # type: () -> List[str]
        try:
            with open(self.filename, 'rb') as fd:
                (coding, lines) = tokenize.detect_encoding(fd.readline)
                textfd = io.TextIOWrapper(fd, coding, line_buffering=True)
                return ([l.decode(coding) for l in lines] +
                        textfd.readlines())
        except (LookupError, SyntaxError, UnicodeError):
            # If we can't detect the codec with tokenize.detect_encoding, or
            # the detected encoding is incorrect, just fallback to latin-1.
            with open(self.filename, encoding='latin-1') as fd:
                return fd.readlines()

    def read_lines_from_filename(self):
        # type: () -> List[str]
        """Read the lines for a file."""
        if (2, 6) <= sys.version_info < (3, 0):
            readlines = self._readlines_py2
        elif (3, 0) <= sys.version_info < (4, 0):
            readlines = self._readlines_py3

        try:
            return readlines()
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
            return []

    def read_lines_from_stdin(self):
        # type: () -> List[str]
        """Read the lines from standard in."""
        return utils.stdin_get_value().splitlines(True)

    def strip_utf_bom(self):
        # type: () -> NoneType
        """Strip the UTF bom from the lines of the file."""
        if not self.lines:
            # If we have nothing to analyze quit early
            return

        first_byte = ord(self.lines[0][0])
        if first_byte not in (0xEF, 0xFEFF):
            return

        # If the first byte of the file is a UTF-8 BOM, strip it
        if first_byte == 0xFEFF:
            self.lines[0] = self.lines[0][1:]
        elif self.lines[0][:3] == '\xEF\xBB\xBF':
            self.lines[0] = self.lines[0][3:]
