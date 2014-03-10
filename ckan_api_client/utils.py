from collections import namedtuple, Mapping, Sequence, MutableSequence


class IDPair(namedtuple('IDPair', ['source_id', 'ckan_id'])):
    """
    A pair (named tuple) mapping a "source" id with the one used
    internally in Ckan.

    This is mostly used associated with :py:class:`IDMap`.

    Keys: ``source_id``, ``ckan_id``
    """
    __slots__ = ()


class SuppressExceptionIf(object):
    """
    Context manager used to suppress exceptions if they match
    a given condition.

    Usage example::

        is_404 = lambda x: isinstance(x, HTTPError) and x.status_code == 404
        with SuppressExceptionIf(is_404):
            client.request(...)
    """

    def __init__(self, cond):
        self.cond = cond

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None:
            return
        if callable(self.cond):
            # If the callable returns True, exception
            # will be suppressed
            return self.cond(exc_value)
        return self.cond


class IDMap(object):
    """
    Two-way hashmap to map source ids to ckan ids
    and the other way back.
    """

    def __init__(self):
        self._source_to_ckan = {}
        self._ckan_to_source = {}

    def to_ckan(self, source_id):
        """Convert a source id to ckan id"""
        return self._source_to_ckan[source_id]

    def to_source(self, ckan_id):
        """Convert a ckan id to source id"""
        return self._ckan_to_source[ckan_id]

    def add(self, pair):
        """
        Add a new id pair

        :param IDPair pair:
            the id pair to be added
        :raises ValueError:
            if one of the two ids is found in a mismatching pair
        """
        ## Check both directions first..
        if pair.source_id in self._source_to_ckan:
            if self._source_to_ckan[pair.source_id] != pair.ckan_id:
                raise ValueError("Mismatching information")

        if pair.ckan_id in self._ckan_to_source:
            if self._ckan_to_source[pair.ckan_id] != pair.source_id:
                raise ValueError("Mismatching information")

        self._source_to_ckan[pair.source_id] = pair.ckan_id
        self._ckan_to_source[pair.ckan_id] = pair.source_id

    def remove(self, pair):
        """
        Remove an id pair.

        :param IDPair pair:
            the id pair to be removed
        :raises ValueError:
            if one of the two ids is found in a mismatching pair
        """
        ## Check both directions first..
        if pair.source_id in self._source_to_ckan:
            if self._source_to_ckan[pair.source_id] != pair.ckan_id:
                raise ValueError("Mismatching information")

        if pair.ckan_id in self._ckan_to_source:
            if self._ckan_to_source[pair.ckan_id] != pair.source_id:
                raise ValueError("Mismatching information")

        del self._source_to_ckan[pair.source_id]
        del self._ckan_to_source[pair.ckan_id]


##------------------------------------------------------------
## Frozen objects, mainly used while running tests,
## to make sure certain objects are left untouched.
##------------------------------------------------------------

class FrozenDict(Mapping):
    """
    Frozen dictionary.
    Acts as a read-only dictionary, preventing changes
    and returning frozen objects when asked for values.
    """

    def __init__(self, data):
        self.__wrapped = data

    def __getitem__(self, name):
        return freeze(self.__wrapped[name])

    def __iter__(self):
        return iter(self.__wrapped)

    def __len__(self):
        return len(self.__wrapped)


class FrozenSequence(Sequence):
    """
    Base class for the FrozenList/FrozenTuple classes.
    Acts as a read-only sequence type, returning frozen
    versions of mutable objects.
    """

    def __init__(self, data):
        self.__wrapped = data

    def __getitem__(self, name):
        return freeze(self.__wrapped[name])

    def __len__(self):
        return len(self.__wrapped)


class FrozenList(FrozenSequence):
    """Immutable list-like."""
    pass


class FrozenTuple(FrozenSequence):
    """Immutable tuple-like."""
    pass


def freeze(obj):
    """
    Returns the "frozen" version of a mutable type.

    :raises TypeError:
        if a frozen version for that object doesn't exist
    """
    if obj is None:
        return None
    if isinstance(obj, (basestring, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return FrozenDict(obj)
    if isinstance(obj, list):
        return FrozenList(obj)
    if isinstance(obj, tuple):
        return FrozenTuple(obj)
    raise TypeError("I don't know how to freeze this!")


class WrappedList(MutableSequence):
    def __init__(self, iterable=None):
        self._list = []
        if iterable is not None:
            self._list.extend(iterable)

    def __getitem__(self, name):
        return self._list[name]

    def __setitem__(self, name, value):
        self._list[name] = value

    def __delitem__(self, name):
        del self._list[name]

    def __len__(self):
        return len(self._list)

    def insert(self, pos, item):
        self._list.insert(pos, item)

    def __contains__(self, item):
        return item in self._list
