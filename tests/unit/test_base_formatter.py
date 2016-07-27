"""Tests for the BaseFormatter object."""
import optparse

import mock
import pytest

from flake8 import style_guide
from flake8.formatting import base


def options(**kwargs):
    """Create an optparse.Values instance."""
    kwargs.setdefault('output_file', None)
    return optparse.Values(kwargs)


@pytest.mark.parametrize('filename', [None, 'out.txt'])
def test_start(filename):
    """Verify we open a new file in the start method."""
    mock_open = mock.mock_open()
    formatter = base.BaseFormatter(options(output_file=filename))
    with mock.patch('flake8.formatting.base.open', mock_open):
        formatter.start()

    if filename is None:
        assert mock_open.called is False
    else:
        mock_open.assert_called_once_with(filename, 'w')


def test_stop():
    """Verify we close open file objects."""
    filemock = mock.Mock()
    formatter = base.BaseFormatter(options())
    formatter.output_fd = filemock
    formatter.stop()

    filemock.close.assert_called_once_with()
    assert formatter.output_fd is None


def test_format_needs_to_be_implemented():
    """Ensure BaseFormatter#format raises a NotImplementedError."""
    formatter = base.BaseFormatter(options())
    with pytest.raises(NotImplementedError):
        formatter.format('foo')


def test_show_source_returns_nothing_when_not_showing_source():
    """Ensure we return nothing when users want nothing."""
    formatter = base.BaseFormatter(options(show_source=False))
    assert formatter.show_source(
        style_guide.Error('A000', 'file.py', 1, 1, 'error text', 'line')
    ) is ''


def test_show_source_returns_nothing_when_there_is_source():
    """Ensure we return nothing when there is no line."""
    formatter = base.BaseFormatter(options(show_source=True))
    assert formatter.show_source(
        style_guide.Error('A000', 'file.py', 1, 1, 'error text', None)
    ) is ''


@pytest.mark.parametrize('line, column', [
    ('x=1\n', 2),
    ('    x=(1\n       +2)\n', 5),
    # TODO(sigmavirus24): Add more examples
])
def test_show_source_updates_physical_line_appropriately(line, column):
    """Ensure the error column is appropriately indicated."""
    formatter = base.BaseFormatter(options(show_source=True))
    error = style_guide.Error('A000', 'file.py', 1, column, 'error', line)
    output = formatter.show_source(error)
    _, pointer = output.rsplit('\n', 1)
    assert pointer.count(' ') == (column - 1)


def test_write_uses_an_output_file():
    """Verify that we use the output file when it's present."""
    line = 'Something to write'
    source = 'source'
    filemock = mock.Mock()

    formatter = base.BaseFormatter(options())
    formatter.output_fd = filemock
    formatter.write(line, source)

    assert filemock.write.called is True
    assert filemock.write.call_count == 2
    assert filemock.write.mock_calls == [
        mock.call(line + formatter.newline),
        mock.call(source + formatter.newline),
    ]


@mock.patch('flake8.formatting.base.print')
def test_write_uses_print(print_function):
    """Verify that we use the print function without an output file."""
    line = 'Something to write'
    source = 'source'

    formatter = base.BaseFormatter(options())
    formatter.write(line, source)

    assert print_function.called is True
    assert print_function.call_count == 2
    assert print_function.mock_calls == [
        mock.call(line),
        mock.call(source),
    ]


class AfterInitFormatter(base.BaseFormatter):
    """Subclass for testing after_init."""

    def after_init(self):
        """Define method to verify operation."""
        self.post_initialized = True


def test_after_init_is_always_called():
    """Verify after_init is called."""
    formatter = AfterInitFormatter(options())
    assert getattr(formatter, 'post_initialized') is True


class FormatFormatter(base.BaseFormatter):
    """Subclass for testing format."""

    def format(self, error):
        """Define method to verify operation."""
        return repr(error)


def test_handle_formats_the_error():
    """Verify that a formatter will call format from handle."""
    formatter = FormatFormatter(options(show_source=False))
    filemock = formatter.output_fd = mock.Mock()
    error = style_guide.Error(
        code='A001',
        filename='example.py',
        line_number=1,
        column_number=1,
        text='Fake error',
        physical_line='a = 1',
    )

    formatter.handle(error)

    filemock.write.assert_called_once_with(repr(error) + '\n')
