import logging  # noqa: D100
import re
from abc import abstractmethod
from pathlib import Path
from typing import ClassVar

from .readers import read_pdf


class Bill:
    """The relevant fields of a PDF bill."""

    _patterns: ClassVar[tuple[str, ...]] = ("NOT SET ON SUBCLASS",)
    _header: ClassVar[tuple[str, ...]] = ("NOT SET ON SUBCLASS",)

    @abstractmethod
    def validate(self) -> None:
        """
        Validate the fields.

        Raises ValueError if the validation fails.
        """
        pass

    @abstractmethod
    def to_row(self) -> tuple[str | int | float, ...]:
        """
        Produce a TSV/CSV style row of all the fields.

        Order of the fields must match `to_header()`.
        """
        pass

    @classmethod
    def to_header(cls) -> tuple[str, ...]:
        """
        Produce a TSV/CSV style row of header names.

        Order of the header names must match `to_row()`.
        """
        return cls._header

    @classmethod
    def extract_fields(cls, file: Path, password: str | None = None) -> "Bill":
        """
        Extract a GasBill from the given PDF file.

        :param file: a pointer to a valid PDF file, may be encrypted
        :param password: the password to unlock an encrypted PDF file
        :return: a GasBill instance
        """
        text = read_pdf(file, password)

        values = {}
        for pattern in cls._patterns:
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
