"""Extracts a TSV line (with header line) from a National Grid Gas bill PDF."""
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Generic, List, Optional, TypeVar, Union

from pypdf import PdfReader

T = TypeVar("T")


__EXAMPLE = """
   CURRENT BILL ITEMIZED      SUMMARY OF CHARGES
In 29 days you used 2 therms: Total Current Charges    $13.59
Amount Due Last Bill     15.26
Aug 18 2023 reading ACTUAL       1481 Your Total Payments Since
Jul 20 2023 reading ACTUAL        ____     1479   Last Bill. Thank You!    -15.26     ______
CCF Used for METER# 007030517        2
DirectPay Amount    $13.59
Thermal Factor     _______    x1.0289
Total therms used         2 GAS USE HISTORY
     Days  Therms      Days  Therms
Your Cost is determined as follows: Aug 23  29 Act    2   Jan 23  30 Act   65
Jul 23  30 Act    3   Dec 22  34 Act   63
Minimum Charge      $11.60 Jun 23  32 Act    3   Nov 22  28 Act   11
$.4000 per day for 29 days May 23  29 Act   11   Oct 22  32 Act    4
First 2.0 therms @ $.4784        .96 Apr 23  31 Act   25   Sep 22  30 Act    3
Distribution Adjustment: Mar 23  32 Act   62   Aug 22  28 Act    5
2 therms x 0.47960 per therm        ______      .96 Feb 23  28 Act   62   Jul 22  34 Act    7
GAS DELIVERY CHARGE    $13.52
GAS SUPPLY CHARGE
@ $.22730 /therm        .45
Paperless Bill Credit         -.38     ______
TOTAL CURRENT CHARGES    $13.59
"""  # noqa: E501

__PATTERN = (
    r".*In (?P<days_since_last_reading>\d+) days"
    r".*(?P<current_date>[a-zA-Z]{3} [0-9]{2} 20\d{2}) reading"
    r" (?P<current_method>[^\s]*)             (?P<current_meter_reading>\d+)"
    r".*(?P<previous_date>[a-zA-Z]{3} [0-9]{2} 20\d{2}) reading"
    r" (?P<previous_method>[^\s]*)"
    r"                ____         (?P<previous_meter_reading>\d+)"
    r".*Thermal Factor.*x(?P<thermal_factor>[\.0-9]+)"
    r".*Total therms used.*(?P<total_therms>\d+)"
    r".*\$(?P<delivery_min_rate_usd>[\.0-9]+) per day for (?P=days_since_last_reading)"
    r" days"
    r".*First [\.0-9]+ therms @ \$(?P<delivery_first_tier_rate_usd>[\.0-9]+)"
    r".*Distribution Adjustment"
    r".*(?P=total_therms) therms x (?P<delivery_distribution_adjustment_rate>[\.0-9]+)"
    r" per therm"
    r".*GAS DELIVERY CHARGE.*\$(?P<delivery_total_usd>[\.0-9]+)"
    r".*GAS SUPPLY CHARGE"
    r".*@ \$(?P<supply_rate>[\.0-9]+) /therm"
    r".*Paperless Bill Credit.*(?P<paperless_bill_credit_usd>-[\.0-9]+)"
    r".*TOTAL CURRENT CHARGES.*\$(?P<total_usd>[\.0-9]+)"
    r".*"
)


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


@dataclass
class GasBill:
    """A Data Object representation of a Gas Bill."""

    current_method: str
    previous_method: str
    days_since_last_reading: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=int
    )
    current_date: ConversionDescriptor = ConversionDescriptor(
        _default=datetime(1970, 1, 1),
        converter=lambda x: datetime.strptime(x, "%b %d %Y").date(),
    )
    current_meter_reading: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=int
    )
    previous_date: ConversionDescriptor = ConversionDescriptor(
        _default=datetime(1970, 1, 1),
        converter=lambda x: datetime.strptime(x, "%b %d %Y").date(),
    )
    previous_meter_reading: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=int
    )
    thermal_factor: ConversionDescriptor = ConversionDescriptor(
        _default=0.0, converter=float
    )
    total_therms: ConversionDescriptor = ConversionDescriptor(_default=0, converter=int)
    delivery_min_rate_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    delivery_first_tier_rate_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    delivery_distribution_adjustment_rate: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    delivery_total_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    supply_rate: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    supply_total_usd: float = field(init=False)
    paperless_bill_credit_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    total_usd: ConversionDescriptor = ConversionDescriptor(_default=0, converter=float)

    def __post_init__(self):
        """Dataclass method invoked after __init__() to compute derived properties."""
        self.supply_total_usd = round(self.total_therms * self.supply_rate, 2)

    def validate(self):
        """
        Validate the current properties for consistency.

        This helps to catch extraction errors or change in PDF format.

        Will throw a ValueError if a violation is found.
        """
        calculated = self.current_date - self.previous_date
        if calculated != timedelta(days=self.days_since_last_reading):
            raise ValueError(
                f"Dates don't match: current_date={self.current_date}"
                + f" previous_date={self.previous_date} => calculated={calculated}"
                + f" days_since_last_reading={self.days_since_last_reading}"
            )

        calculated = round(
            (self.current_meter_reading - self.previous_meter_reading)
            * self.thermal_factor,
            0,
        )
        if calculated != self.total_therms:
            raise ValueError(
                "Readings and therms don't match:"
                + f" current_meter_reading={self.current_meter_reading}"
                + f" previous_meter_reading={self.previous_meter_reading}"
                + f" thermal_factor={self.thermal_factor}"
                + f" => calculated={calculated} != total_therms={self.total_therms}"
            )

        calculated = round(
            self.days_since_last_reading * self.delivery_min_rate_usd
            + self.total_therms
            * (
                self.delivery_first_tier_rate_usd
                + self.delivery_distribution_adjustment_rate
            ),
            2,
        )
        if calculated != self.delivery_total_usd:
            raise ValueError(
                "Delivery rates and therms don't match total:"
                + f" total_therms={self.total_therms}"
                + f" delivery_min_rate_usd={self.delivery_min_rate_usd}"
                + f" delivery_first_tier_rate_usd={self.delivery_first_tier_rate_usd}"
                + " delivery_distribution_adjustment_rate="
                + f"{self.delivery_distribution_adjustment_rate}"
                + f" => calculated={calculated}"
                + f" != delivery_total_usd={self.delivery_total_usd}"
            )

        calculated = round(
            self.delivery_total_usd
            + self.supply_total_usd
            + self.paperless_bill_credit_usd,
            2,
        )
        if calculated != self.total_usd:
            raise ValueError(
                f"Totals don't match: delivery_total_usd={self.delivery_total_usd}"
                + f" supply_total_usd={self.supply_total_usd}"
                + f" paperless_bill_credit_usd={self.paperless_bill_credit_usd}"
                + f" => calculated={calculated} != total_usd={self.total_usd}"
            )

    def to_header(self) -> List[str]:
        """Return the names of the row values in the same order as ``to_row()``."""
        return [
            "current_date",
            "days_since_last_reading",
            "current_meter_reading",
            "previous_meter_reading",
            "thermal_factor",
            "total_therms_used",
            "delivery_min_rate_usd",
            "delivery_first_tier_rate_usd",
            "delivery_distribution_adjustment_rate",
            "delivery_total_usd",
            "supply_rate",
            "supply_total_usd",
            "paperless_bill_credit_usd",
            "total_usd",
        ]

    def to_row(self) -> List[Union[str, int, float]]:
        """
        Return a row-based representation of the GasBill.

        The values match ``to_header()``.
        """
        return [
            self.current_date.isoformat(),
            self.days_since_last_reading,
            self.current_meter_reading,
            self.previous_meter_reading,
            self.thermal_factor,
            self.total_therms,
            self.delivery_min_rate_usd,
            self.delivery_first_tier_rate_usd,
            self.delivery_distribution_adjustment_rate,
            self.delivery_total_usd,
            self.supply_rate,
            self.supply_total_usd,
            self.paperless_bill_credit_usd,
            self.total_usd,
        ]


def extract_gas_fields(file: Path, password: Optional[str]) -> GasBill:
    """
    Extract a GasBill from the given PDF file.

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
    match = re.search(__PATTERN, text, flags=re.DOTALL)
    if match is None:
        raise RuntimeError(f"Cannot parse bill\n{text}")
    return GasBill(**match.groupdict())


if __name__ == "__main__":
    import sys

    bill = extract_gas_fields(
        Path(sys.argv[1]),
        sys.argv[2] if len(sys.argv) >= 3 else None,
    )
    bill.validate()
    print(", ".join(map(str, bill.to_header())))
    print(", ".join(map(str, bill.to_row())))
