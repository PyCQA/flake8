"""Statistic collection logic for Flake8."""
import collections


class Statistics(object):
    """Manager of aggregated statistics for a run of Flake8."""

    def __init__(self):
        """Initialize the underlying dictionary for our statistics."""
        self._store = {}

    def record(self, error):
        """Add the fact that the error was seen in the file.

        :param error:
            The Error instance containing the information about the violation.
        :type error:
            flake8.style_guide.Error
        """
        key = Key.create_from(error)
        if key in self._store:
            statistic = self._store[key]
        else:
            statistic = Statistic.create_from(error)
        self._store[key] = statistic.increment()

    def statistics_for(self, prefix, filename=None):
        """Generate statistics for the prefix and filename.

        If you have a :class:`Statistics` object that has recorded errors,
        you can generate the statistics for a prefix (e.g., ``E``, ``E1``,
        ``W50``, ``W503``) with the optional filter of a filename as well.

        .. code-block:: python

            >>> stats = Statistics()
            >>> stats.statistics_for('E12',
                                     filename='src/flake8/statistics.py')
            <generator ...>
            >>> stats.statistics_for('W')
            <generator ...>

        :param str prefix:
            The error class or specific error code to find statistics for.
        :param str filename:
            (Optional) The filename to further filter results by.
        :returns:
            Generator of instances of :class:`Statistic`
        """
        matching_errors = sorted(key for key in self._store.keys()
                                 if key.matches(prefix, filename))
        for error_code in matching_errors:
            yield self._store[error_code]


class Key(collections.namedtuple('Key', ['filename', 'code'])):
    __slots__ = ()

    @classmethod
    def create_from(cls, error):
        return cls(
            filename=error.filename,
            code=error.code,
        )

    def matches(self, prefix, filename):
        return (self.code.startswith(prefix) and
                (filename is None or
                    self.filename == filename))


_Statistic = collections.namedtuple('Statistic', [
    'error_code',
    'filename',
    'message',
    'count',
])


class Statistic(_Statistic):
    __slots__ = ()

    @classmethod
    def create_from(cls, error):
        return cls(
            error_code=error.code,
            filename=error.filename,
            message=error.message,
            count=0,
        )

    def increment(self):
        return Statistic(
            error_code=self.error_code,
            filename=self.filename,
            message=self.message,
            count=self.count + 1,
        )


del _Statistic
