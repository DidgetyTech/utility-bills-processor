"""Contains the base Bill class for all utility bills."""

import logging
import re
from abc import abstractmethod
from pathlib import Path
from typing import ClassVar, Iterable, TypeVar

from .readers import PdfReader, read_pdf

B = TypeVar("B", bound="Bill")


class Bill:
    """The validated relevant fields of a PDF bill."""

    _patterns: ClassVar[tuple[str, ...]] = ("NOT SET ON SUBCLASS",)
    _header: ClassVar[tuple[str, ...]] = ("NOT SET ON SUBCLASS",)

    @abstractmethod
    def validate(self) -> None:
        """Validate the fields.

        Raises:
            ValueError: if any data integrity issues are found
        """
        pass

    @abstractmethod
    def to_row(self) -> tuple[str | int | float, ...]:
        """Produce a TSV/CSV style row of all the fields.

        Order of the fields must match `to_header()`.

        Returns:
            a tuple of field values in the order of `to_header()`.
        """
        pass

    @classmethod
    def pick_patterns(cls, text: str, reader: PdfReader) -> Iterable[str]:
        """Pick which set of patterns to use.

        Useful to override when the format of the bill has changed enough that the same regex can't
        be used.

        Args:
            text: the text of the PDF
            reader: the reader with other parsing information

        Returns:
            an iterable of pattern strings
        """
        return cls._patterns

    @classmethod
    def to_header(cls) -> tuple[str, ...]:
        """Produce a TSV/CSV style row of header names.

        Returns:
            a tuple of field values in the order of `to_row()`.
        """
        return cls._header

    @classmethod
    def extract_fields(cls: type[B], file: Path, password: str | None = None) -> B:
        """Extract a Bill from the given PDF file.

        Args:
            file: a pointer to a valid PDF file, may be encrypted
            password: the password to unlock an encrypted PDF file

        Returns:
            a Bill instance
        """
        text, reader = read_pdf(file, password)
        patterns = cls.pick_patterns(text, reader)

        values = {}
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.DOTALL)
            if match is None:
                raise RuntimeError(
                    f"Cannot parse bill with pattern: '{pattern}'. Found text:\n{text}"
                )
            values.update(match.groupdict())

        # on the root logger
        logging.debug(f"Parsed text\n{text}")
        logging.debug(f"Extracted fields:\n{values}")
        if len(values) == 0:
            raise RuntimeError(f"Cannot parse bill. Found text:\n{text}")
        return cls(**values)
