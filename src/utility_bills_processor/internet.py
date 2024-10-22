"""Extracts a TSV line (with header line) from my Internet Bill PDF."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import ClassVar, override

from ._common.bill import Bill
from ._common.dataclass_converters import ConversionDescriptor

__EXAMPLE = """
Bill Date :    October 9, 2024
Page 3 of 4Details of Payments
   Payments
Previous Balance 59.99
Payment Received - Thank You -59.99 9/30
Balance Forward $.00Payment activity since last bill date.
Details of Charges
   Services & Equipment
Services
300 Mbps 3.0 59.99 10/10 - 11/9 R
Total Due $59.99Equipment and additional services to
personalize your Fios service.
"""


@dataclass
class InternetBill(Bill):
    """A Data Object representation of an Internet Bill."""

    bill_date: ConversionDescriptor = ConversionDescriptor(
        _default=date(1970, 1, 1),
        converter=lambda x: datetime.strptime(x, "%B %d, %Y").date(),
    )
    service_charge_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=float
    )
    speed: ConversionDescriptor = ConversionDescriptor(_default=0, converter=int)
    speed_unit: str = ""
    one_time_charges_usd = 0.0
    taxes_usd = 0.0
    fees_usd = 0.0
    late_fees_usd = 0.0
    total_usd: ConversionDescriptor = ConversionDescriptor(_default=0, converter=float)

    _patterns: ClassVar[tuple[str, ...]] = (
        (
            r"Bill Date : *(?P<bill_date>\w+ \d{1,2}, \d{4}).*"
            "Details of Charges.*"
            "Services & Equipment.*"
            "Services\n"
            r"(?P<speed>\d+) (?P<speed_unit>[MG]bps) 3.0 "
            r"(?P<service_charge_usd>[0-9.]+) \d{1,2}/\d{1,2} - \d{1,2}/\d{1,2}.*"
            r"Total Due \$(?P<total_usd>[0-9.]+).*"
        ),
    )
    _header: ClassVar[tuple[str, ...]] = (
        "bill_date",
        "speed",
        "service_charge_usd",
        "one_time_charges_usd",
        "taxes_usd",
        "fees_usd",
        "late_fees_usd",
        "total_usd",
    )

    @property
    @override
    def date(self) -> date:  # noqa: D102
        d: date = self.bill_date
        return d

    @override
    def validate(self) -> None:  # noqa: D102
        calculated = (
            self.service_charge_usd
            + self.one_time_charges_usd
            + self.taxes_usd
            + self.fees_usd
            + self.late_fees_usd
        )
        if calculated != self.total_usd:
            raise ValueError(
                f"Totals don't match: {self.service_charge_usd=}"
                + f" + {self.one_time_charges_usd=}"
                + f" + {self.taxes_usd=}"
                + f" + {self.fees_usd=}"
                + f" + {self.late_fees_usd=}"
                + f" => {calculated=} != {self.total_usd=}"
            )

    @override
    def to_row(self) -> tuple[str | int | float, ...]:  # noqa: D102
        return (
            self.bill_date,
            f"{self.speed} {self.speed_unit}",
            self.service_charge_usd,
            self.one_time_charges_usd,
            self.taxes_usd,
            self.fees_usd,
            self.late_fees_usd,
            self.total_usd,
        )
