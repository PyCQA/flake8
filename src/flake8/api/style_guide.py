"""Module containing shims around Flake8 2.0 behaviour."""
import os.path

from flake8.formatting import base as formatter


class LegacyStyleGuide(object):
    """Public facing object that mimic's Flake8 2.0's StyleGuide."""

    def __init__(self, application):
        self._application = application
        self._file_checker_manager = application.file_checker_manager

    @property
    def options(self):
        """The parsed options.

        An instance of :class:`optparse.Values` containing parsed options.
        """
        return self._application.options

    @property
    def paths(self):
        """The extra arguments passed as paths."""
        return self._application.paths

    def check_files(self, paths=None):
        raise NotImplementedError('This should be easy')

    def excluded(self, filename, parent=None):
        return (self._file_checker_manager.is_path_excluded(filename) or
                (parent and
                    self._file_checker_manager.is_path_excluded(
                        os.path.join(parent, filename))))

    def init_report(self, reporter=None):
        if (reporter is not None and
                isinstance(reporter, formatter.BaseFormatter)):
            self._application.formatter = reporter
            self._application.guide = None
            # NOTE(sigmavirus24): This isn't the intended use of
            # Application#make_guide but it works pretty well.
            # Stop cringing... I know it's gross.
            self._application.make_guide()

    def input_file(self, filename, lines=None, expected=None, line_offset=0):
        raise NotImplementedError('This should be a pain')
