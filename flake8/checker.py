"""Checker Manager and Checker classes."""
import contextlib
import io
import logging
import os
import sys
import tokenize

try:
    import multiprocessing
except ImportError:
    multiprocessing = None

from flake8 import defaults
from flake8 import exceptions
from flake8 import utils

LOG = logging.getLogger(__name__)

SKIP_TOKENS = frozenset([tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                         tokenize.DEDENT])


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

    def __init__(self, style_guide, arguments, checker_plugins):
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
        """
        self.arguments = arguments
        self.style_guide = style_guide
        self.options = style_guide.options
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
            FileChecker(filename, self.checks, self.style_guide)
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

    def __init__(self, filename, checks, style_guide):
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
        self.style_guide = style_guide
        self.results = []
        self.processor = self._make_processor()

    def _make_processor(self):
        try:
            return FileProcessor(self.filename, self.style_guide.options)
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

    def report(self, error_code, line_number, column, text):
        # type: (str, int, int, str) -> str
        """Report an error by storing it in the results list."""
        if error_code is None:
            error_code, text = text.split(' ', 1)
        error = (error_code, self.filename, line_number, column, text)
        self.results.append(error)
        return error_code

    def run_check(self, plugin, **arguments):
        """Run the check in a single plugin."""
        self.processor.keyword_arguments_for(plugin.parameters, arguments)
        return plugin.execute(**arguments)

    def run_logical_checks(self):
        """Run all checks expecting a logical line."""
        comments, logical_line, mapping = self.processor.build_logical_line()
        if not mapping:
            return
        self.processor.update_state(mapping)

        LOG.debug('Logical line: "%s"', logical_line.rstrip())

        for plugin in self.checks.logical_line_plugins:
            result = self.run_check(plugin, logical_line=logical_line)
            if result is not None:
                column_offset, text = result
                self.report(
                    error_code=None,
                    line_number=self.processor.line_number,
                    column=column_offset,
                    text=text,
                )

    def run_physical_checks(self, physical_line):
        """Run all checks for a given physical line."""
        for plugin in self.checks.physical_line_plugins:
            result = self.run_check(plugin, physical_line=physical_line)
            if result is not None:
                column_offset, text = result
                error_code = self.report(
                    error_code=None,
                    line_number=self.processor.line_number,
                    column=column_offset,
                    text=text,
                )

                self.processor.check_physical_error(error_code, physical_line)

    def _log_token(self, token):
        if token[2][0] == token[3][0]:
            pos = '[%s:%s]' % (token[2][1] or '', token[3][1])
        else:
            pos = 'l.%s' % token[3][0]
        LOG.debug('l.%s\t%s\t%s\t%r' %
                  (token[2][0], pos, tokenize.tok_name[token[0]],
                      token[1]))

    def process_tokens(self):
        """Process tokens and trigger checks.

        This can raise a :class:`flake8.exceptions.InvalidSyntax` exception.
        Instead of using this directly, you should use
        :meth:`flake8.checker.FileChecker.run_checks`.
        """
        parens = 0
        processor = self.processor
        for token in processor.generate_tokens():
            self.check_physical_eol(token)
            token_type, text = token[0:2]
            self._log_token(token)
            if token_type == tokenize.OP:
                parens = utils.count_parentheses(parens, text)
            elif parens == 0:
                if utils.token_is_newline(token):
                    self.handle_newline(token_type)
                elif (utils.token_is_comment(token) and
                        len(processor.tokens) == 1):
                    self.handle_comment(token, text)

        if processor.tokens:
            # If any tokens are left over, process them
            self.run_physical_checks(processor.lines[-1])
            self.run_logical_checks()

    def run_checks(self):
        """Run checks against the file."""
        try:
            self.process_tokens()
        except exceptions.InvalidSyntax as exc:
            self.report(exc.error_code, exc.line_number, exc.column_number,
                        exc.error_message)

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
            self.check_logical()
            self.processor.reset_blank_before()
        elif len(self.processor.tokens) == 1:
            # The physical line contains only this token.
            self.processor.visited_new_blank_line()
            self.processor.delete_first_token()
        else:
            self.run_logical_checks()

    def check_physical_eol(self, token):
        """Run physical checks if and only if it is at the end of the line."""
        if utils.is_eol_token(token):
            # Obviously, a newline token ends a single physical line.
            self.run_physical_checks(token[4])
        elif utils.is_multiline_string(token):
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
                    self.run_physical_checks(line + '\n')


class FileProcessor(object):
    """Processes a file and holdes state.

    This processes a file by generating tokens, logical and physical lines,
    and AST trees. This also provides a way of passing state about the file
    to checks expecting that state. Any public attribute on this object can
    be requested by a plugin. The known public attributes are:

    - blank_before
    - blank_lines
    - indect_char
    - indent_level
    - line_number
    - logical_line
    - max_line_length
    - multiline
    - noqa
    - previous_indent_level
    - previous_logical
    - tokens
    - total_lines
    - verbose
    """

    def __init__(self, filename, options):
        """Initialice our file processor.

        :param str filename:
            Name of the file to process
        """
        self.filename = filename
        self.lines = self.read_lines()
        self.strip_utf_bom()
        self.options = options

        # Defaults for public attributes
        #: Number of preceding blank lines
        self.blank_before = 0
        #: Number of blank lines
        self.blank_lines = 0
        #: Character used for indentation
        self.indent_char = None
        #: Current level of indentation
        self.indent_level = 0
        #: Line number in the file
        self.line_number = 0
        #: Current logical line
        self.logical_line = ''
        #: Maximum line length as configured by the user
        self.max_line_length = options.max_line_length
        #: Whether the current physical line is multiline
        self.multiline = False
        #: Whether or not we're observing NoQA
        self.noqa = False
        #: Previous level of indentation
        self.previous_indent_level = 0
        #: Previous logical line
        self.previous_logical = ''
        #: Current set of tokens
        self.tokens = []
        #: Total number of lines in the file
        self.total_lines = len(self.lines)
        #: Verbosity level of Flake8
        self.verbosity = options.verbosity

    @contextlib.contextmanager
    def inside_multiline(self, line_number):
        """Context-manager to toggle the multiline attribute."""
        self.line_number = line_number
        self.multiline = True
        yield
        self.multiline = False

    def reset_blank_before(self):
        """Reset the blank_before attribute to zero."""
        self.blank_before = 0

    def delete_first_token(self):
        """Delete the first token in the list of tokens."""
        del self.tokens[0]

    def visited_new_blank_line(self):
        """Note that we visited a new blank line."""
        self.blank_lines += 1

    def build_logical_line_tokens(self):
        """Build the mapping, comments, and logical line lists."""
        logical = []
        comments = []
        length = 0
        previous_row = previous_column = mapping = None
        for token_type, text, start, end, line in self.tokens:
            if token_type in SKIP_TOKENS:
                continue
            if not mapping:
                mapping = [(0, start)]
            if token_type == tokenize.COMMENT:
                comments.append(text)
                continue
            if token_type == tokenize.STRING:
                text = utils.mutate_string(text)
            if previous_row:
                (start_row, start_column) = start
                if previous_row != start_row:
                    row_index = previous_row - 1
                    column_index = previous_column - 1
                    previous_text = self.lines[row_index][column_index]
                    if (previous_text == ',' or
                            (previous_text not in '{[(' and
                             text not in '}])')):
                        text = ' ' + text
                    elif previous_column != start_column:
                        text = line[previous_column:start_column] + text
            logical.append(text)
            length += len(text)
            mapping.append((length, end))
            (previous_row, previous_column) = end
        return comments, logical, mapping

    def build_logical_line(self):
        """Build a logical line from the current tokens list."""
        comments, logical, mapping_list = self.build_logical_line_tokens()
        return ''.join(comments), ''.join(logical), mapping_list

    def split_line(self, token):
        """Split a physical line's line based on new-lines.

        This also auto-increments the line number for the caller.
        """
        for line in token[1].split('\n')[:-1]:
            yield line
            self.line_number += 1

    def keyword_arguments_for(self, parameters, arguments=None):
        """Generate the keyword arguments for a list of parameters."""
        if arguments is None:
            arguments = {}
        for param in parameters:
            if param not in arguments:
                arguments[param] = getattr(self, param)
        return arguments

    def check_physical_error(self, error_code, line):
        """Update attributes based on error code and line."""
        if error_code == 'E101':
            self.indent_char = line[0]

    def generate_tokens(self):
        """Tokenize the file and yield the tokens.

        :raises flake8.exceptions.InvalidSyntax:
            If a :class:`tokenize.TokenError` is raised while generating
            tokens.
        """
        try:
            for token in tokenize.generate_tokens(self.next_line):
                if token[2][0] > self.total_lines:
                    break
                self.tokens.append(token)
                yield token
        # NOTE(sigmavirus24): pycodestyle was catching both a SyntaxError
        # and a tokenize.TokenError. In looking a the source on Python 2 and
        # Python 3, the SyntaxError should never arise from generate_tokens.
        # If we were using tokenize.tokenize, we would have to catch that. Of
        # course, I'm going to be unsurprised to be proven wrong at a later
        # date.
        except tokenize.TokenError as exc:
            raise exceptions.InvalidSyntax(exc.message, exception=exc)

    def next_line(self):
        """Get the next line from the list."""
        if self.line_number >= self.total_lines:
            return ''
        line = self.lines[self.line_number]
        self.line_number += 1
        if self.indent_char is None and line[:1] in defaults.WHITESPACE:
            self.indent_char = line[0]
        return line

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
        return readlines()

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
