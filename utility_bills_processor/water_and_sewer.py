"""Extracts a TSV line (with header line) from my Water/Sewer Bill PDF."""
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader

from ._common.dataclass_converters import ConversionDescriptor

__EXAMPLE = """
Usage History  \n
Meter Number Read Date Reading Usage Type Usage Description Charge \n
45872997 11/25/2023        743 Actual          1 WATER          $2.70 \n
 10/25/2023        742 Actual          1 SEWER          $7.33 \n
 09/25/2023        741 Actual          3     \n
 08/25/2023        738 Actual          2     \n
 07/25/2023        736 Actual          3    \n
 06/25/2023        733 Actual          2    Charge Summary  \n
Total Current Charges         $10.03 \n
Past Due          $0.00 \n
Interest          $0.00 \n
Adjustments          $0.00 \n
Total Due         $10.03 \n
Total Current Charges         $10.03 \n
Past Due          $0.00 \n
Interest          $0.00 \n
Adjustments          $0.00 \n
Pay This Amount  \n
"""

__PATTERNS = [
    (
        r".*Meter Number Read Date Reading Usage Type Usage Description Charge.*"
        r"?(?P<read_date>\d\d/\d\d/\d\d\d\d)"
        r"? +(?P<current_meter_reading>\d+)"
        r"? +(?P<usage_type>[^ ]+)"
        r"? +(?P<usage>\d+)"
    ),
    (r"WATER +\$(?P<water_charge>\d+.\d{2})"),
    (r"SEWER +\$(?P<sewer_charge>\d+.\d{2})"),
    (r"Past Due +\$(?P<past_due>\d+.\d{2})"),
    (r"Interest +\$(?P<interest>\d+.\d{2})"),
    (r"Adjustments +\$(?P<adjustments>\d+.\d{2})"),
    (r"Total Due +\$(?P<total>\d+.\d{2})"),
]


@dataclass
class WaterBill:
    """A Data Object representation of a Water Bill."""

    usage_type: str
    read_date: ConversionDescriptor = ConversionDescriptor(
        _default=datetime(1970, 1, 1),
        converter=lambda x: datetime.strptime(x, "%m/%d/%Y").date(),
    )
    current_meter_reading: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=int
    )
    usage: ConversionDescriptor = ConversionDescriptor(_default=0, converter=int)
    water_charge: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    sewer_charge: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    past_due: ConversionDescriptor = ConversionDescriptor(_default=0, converter=float)
    interest: ConversionDescriptor = ConversionDescriptor(_default=0, converter=float)
    adjustments: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    total: ConversionDescriptor = ConversionDescriptor(_default=0, converter=float)

    def validate(self) -> None:
        """
        Validate the current properties for consistency.

        This helps to catch extraction errors or change in PDF format.

        Will throw a ValueError if a violation is found.
        """
        calculated = round(
            self.water_charge
            + self.sewer_charge
            + self.past_due
            + self.interest
            + self.adjustments,
            2,
        )
        if self.total != calculated:
            raise ValueError(
                "Changes don't sum to the total due."
                + f" water_charge={self.water_charge}"
                + f" sewer_charge={self.sewer_charge}"
                + f" past_due={self.past_due}"
                + f" adjustments={self.adjustments}"
                + f" interest={self.interest}"
                + f" => calculated={calculated} != total={self.total}"
            )
        # TODO extract rate to check usage against charges

    def to_header(self) -> List[str]:
        """Return the names of the row values in the same order as ``to_row()``."""
        return [
            "read_date",
            "reading",
            "usage_type",
            "usage",
            "water_charge_usd",
            "sewer_charge_usd",
            "past_due_usd",
            "adjustments_usd",
            "interest_usd",
            "total_usd",
        ]

    def to_row(self) -> List[str]:
        """
        Return a row-based representation of the WaterBill.

        The values match ``to_header()``.
        """
        return [
            self.read_date,
            self.current_meter_reading,
            self.usage_type,
            self.usage,
            self.water_charge,
            self.sewer_charge,
            self.past_due,
            self.interest,
            self.adjustments,
            self.total,
        ]


def extract_fields(file: Path, password: Optional[str]) -> WaterBill:
    """
    Extract a WaterBill from the given PDF file.

    :param file: a pointer to a valid PDF file, may be encrypted
    :param password: the password to unlock an encrypted PDF file
    :return: a GasBill instance
    """
    reader = PdfReader(str(file))

    if reader.is_encrypted:
        if password is None:
            raise RuntimeError("Cannot read an encrypted document without a password")
        reader.decrypt(password)

    text = "\n\n".join((page.extract_text() for page in reader.pages))
    values = {}
    for pattern in __PATTERNS:
        match = re.search(pattern, text, flags=re.DOTALL)
        if match is None:
            raise RuntimeError(
                f"Cannot parse bill with pattern: '{pattern}'. Found text:\n{text}"
            )
        values.update(match.groupdict())
    return WaterBill(**values)


def main():
    """Start processing the provided gas bill PDF."""
    import sys

    arg_len = len(sys.argv)
    if arg_len < 2:
        print(f"Usage: {sys.argv[0]} BILL_FILE [PASSWORD]")
        sys.exit(1)

    bill = extract_fields(
        Path(sys.argv[1]),
        sys.argv[2] if arg_len >= 3 else None,
    )
    bill.validate()
    print(", ".join(map(str, bill.to_header())))
    print(", ".join(map(str, bill.to_row())))


if __name__ == "__main__":
    main()
