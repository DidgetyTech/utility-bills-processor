"""Classes to help with value and type conversions for @dataclass fields."""
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


class ConversionDescriptor(Generic[T]):
    """A Dataclass-style converter to adapt the value to another value and/or type."""

    def __init__(self, _default: T, converter: Callable[[Any], T]):
        """
        Use like a Dataclass field.

        :param _default: the default value if one is not explicitly set
        :param converter: a function to convert the value to another value and/or type
        """
        self._default = _default
        self._converter = converter

    def __set_name__(self, owner, name):
        """Invoke by Dataclass."""
        self._name = "_" + name

    def __get__(self, obj, type):
        """Invoke by Dataclass."""
        if obj is None:
            return self._default

        return getattr(obj, self._name)

    def __set__(self, obj, value):
        """Invoke by Dataclass."""
        setattr(obj, self._name, self._converter(value))
