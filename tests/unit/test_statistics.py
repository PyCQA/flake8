"""Tests for the statistics module in Flake8."""
import pytest

from flake8 import statistics as stats
from flake8.violation import Violation

DEFAULT_ERROR_CODE = "E100"
DEFAULT_FILENAME = "file.py"
DEFAULT_TEXT = "Default text"


def make_error(**kwargs):
    """Create errors with a bunch of default values."""
    kwargs.setdefault("code", DEFAULT_ERROR_CODE)
    kwargs.setdefault("filename", DEFAULT_FILENAME)
    kwargs.setdefault("line_number", 1)
    kwargs.setdefault("column_number", 1)
    kwargs.setdefault("text", DEFAULT_TEXT)
    return Violation(**kwargs, physical_line=None)


def test_key_creation():
    """Verify how we create Keys from Errors."""
    key = stats.Key.create_from(make_error())
    assert key == (DEFAULT_FILENAME, DEFAULT_ERROR_CODE)
    assert key.filename == DEFAULT_FILENAME
    assert key.code == DEFAULT_ERROR_CODE


@pytest.mark.parametrize(
    "code, filename, args, expected_result",
    [
        # Error prefix matches
        ("E123", "file000.py", ("E", None), True),
        ("E123", "file000.py", ("E1", None), True),
        ("E123", "file000.py", ("E12", None), True),
        ("E123", "file000.py", ("E123", None), True),
        # Error prefix and filename match
        ("E123", "file000.py", ("E", "file000.py"), True),
        ("E123", "file000.py", ("E1", "file000.py"), True),
        ("E123", "file000.py", ("E12", "file000.py"), True),
        ("E123", "file000.py", ("E123", "file000.py"), True),
        # Error prefix does not match
        ("E123", "file000.py", ("W", None), False),
        # Error prefix matches but filename does not
        ("E123", "file000.py", ("E", "file001.py"), False),
        # Error prefix does not match but filename does
        ("E123", "file000.py", ("W", "file000.py"), False),
        # Neither error prefix match nor filename
        ("E123", "file000.py", ("W", "file001.py"), False),
    ],
)
def test_key_matching(code, filename, args, expected_result):
    """Verify Key#matches behaves as we expect with fthe above input."""
    key = stats.Key.create_from(make_error(code=code, filename=filename))
    assert key.matches(*args) is expected_result


def test_statistic_creation():
    """Verify how we create Statistic objects from Errors."""
    stat = stats.Statistic.create_from(make_error())
    assert stat.error_code == DEFAULT_ERROR_CODE
    assert stat.message == DEFAULT_TEXT
    assert stat.filename == DEFAULT_FILENAME
    assert stat.count == 0


def test_statistic_increment():
    """Verify we update the count."""
    stat = stats.Statistic.create_from(make_error())
    assert stat.count == 0
    stat.increment()
    assert stat.count == 1


def test_recording_statistics():
    """Verify that we appropriately create a new Statistic and store it."""
    aggregator = stats.Statistics()
    assert list(aggregator.statistics_for("E")) == []
    aggregator.record(make_error())
    storage = aggregator._store
    for key, value in storage.items():
        assert isinstance(key, stats.Key)
        assert isinstance(value, stats.Statistic)

    assert storage[stats.Key(DEFAULT_FILENAME, DEFAULT_ERROR_CODE)].count == 1


def test_statistics_for_single_record():
    """Show we can retrieve the only statistic recorded."""
    aggregator = stats.Statistics()
    assert list(aggregator.statistics_for("E")) == []
    aggregator.record(make_error())
    statistics = list(aggregator.statistics_for("E"))
    assert len(statistics) == 1
    assert isinstance(statistics[0], stats.Statistic)


def test_statistics_for_filters_by_filename():
    """Show we can retrieve the only statistic recorded."""
    aggregator = stats.Statistics()
    assert list(aggregator.statistics_for("E")) == []
    aggregator.record(make_error())
    aggregator.record(make_error(filename="example.py"))

    statistics = list(aggregator.statistics_for("E", DEFAULT_FILENAME))
    assert len(statistics) == 1
    assert isinstance(statistics[0], stats.Statistic)


def test_statistic_for_retrieves_more_than_one_value():
    """Show this works for more than a couple statistic values."""
    aggregator = stats.Statistics()
    for i in range(50):
        aggregator.record(make_error(code=f"E1{i:02d}"))
        aggregator.record(make_error(code=f"W2{i:02d}"))

    statistics = list(aggregator.statistics_for("E"))
    assert len(statistics) == 50

    statistics = list(aggregator.statistics_for("W22"))
    assert len(statistics) == 10
