"""Functions to parse files."""

from pathlib import Path

from pypdf import PdfReader


def read_pdf(file: Path, password: str | None) -> str:
    """Read PDF file that could be encrypted.

    Returns:
        the contents of the PDF file as text

    Raises:
        RuntimeError: if the file is encrypted but no password was provided
    """
    reader = PdfReader(str(file))

    if reader.is_encrypted:
        if password is None:
            raise RuntimeError("Cannot read an encrypted document without a password")
        reader.decrypt(password)
    text = "\n\n".join((page.extract_text() for page in reader.pages))
    return text
