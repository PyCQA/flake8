"""Default formatting class for Flake8."""
from flake8.formatting import base


class Default(base.BaseFormatter):
    """Default formatter for Flake8.

    This also handles backwards compatibility for people specifying a custom
    format string.
    """

    error_format = '%(path)s:%(row)d:%(col)d: %(code)s %(text)s'

    def after_init(self):
        """Check for a custom format string."""
        if self.options.format.lower() != 'default':
            self.error_format = self.options.format

    def format(self, error):
        """Format and write error out.

        If an output filename is specified, write formatted errors to that
        file. Otherwise, print the formatted error to standard out.
        """
        return self.error_format % {
            "code": error.code,
            "text": error.text,
            "path": error.filename,
            "row": error.line_number,
            "col": error.column_number,
        }
