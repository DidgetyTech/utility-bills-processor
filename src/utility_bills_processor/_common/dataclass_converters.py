"""Classes to help with value and type conversions for @dataclass fields."""

from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


class ConversionDescriptor(Generic[T]):
    """A Dataclass-style converter to adapt the value to another value and/or type."""

    def __init__(self, _default: T, converter: Callable[[Any], T]):
        """Use like a Dataclass field.

        Args:
            _default: the default value if one is not explicitly set
            converter: a function to convert the value to another value and/or type
        """
        self._default: T = _default
        self._converter = converter

    def __set_name__(self, owner: Any, name: str) -> None:
        """Invoked by Dataclass."""
        self._name = "_" + name

    def __get__(self, obj: Any, type: type) -> T:
        """Invoked by Dataclass."""
        if obj is None:
            return self._default
        value: T = getattr(obj, self._name)
        return value

    def __set__(self, obj: Any, value: Any) -> None:
        """Invoked by Dataclass."""
        converted_value: T = self._converter(value)
        setattr(obj, self._name, converted_value)
