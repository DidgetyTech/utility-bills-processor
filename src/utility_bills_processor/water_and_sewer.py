"""Extracts a TSV line (with header line) from my Water/Sewer Bill PDF."""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, override

from ._common.bill import Bill
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


@dataclass
class WaterBill(Bill):
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

    _patterns: ClassVar[tuple[str, ...]] = (
        (
            r".*Meter Number Read Date Reading Usage Type Usage Description Charge.*"
            r"?(?P<read_date>\d\d/\d\d/\d\d\d\d)"
            r"? +(?P<current_meter_reading>\d+)"
            r"? +(?P<usage_type>[^ ]+)"
            r"? +(?P<usage>\d+)"
        ),
        r"WATER +\$(?P<water_charge>\d+.\d{2})",
        r"SEWER +\$(?P<sewer_charge>\d+.\d{2})",
        r"Past Due +\$(?P<past_due>\d+.\d{2})",
        r"Interest +\$(?P<interest>\d+.\d{2})",
        r"Adjustments +\$(?P<adjustments>\d+.\d{2})",
        r"Total Due +\$(?P<total>\d+.\d{2})",
    )
    _header: ClassVar[tuple[str, ...]] = (
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
    )

    @override
    def validate(self) -> None:  # noqa: D102
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
                + f" {self.water_charge=}"
                + f" {self.sewer_charge=}"
                + f" {self.past_due=}"
                + f" {self.adjustments=}"
                + f" {self.interest=}"
                + f" => {calculated=} != {self.total=}"
            )
        # TODO extract rate to check usage against charges

    @override
    def to_row(self) -> tuple[str | int | float, ...]:  # noqa: D102
        return (
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
        )
