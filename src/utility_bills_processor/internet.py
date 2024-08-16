"""Extracts a TSV line (with header line) from my Internet Bill PDF."""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, override

from ._common.bill import Bill
from ._common.dataclass_converters import ConversionDescriptor

__EXAMPLE = """

"""


@dataclass
class InternetBill(Bill):
    """A Data Object representation of a Internet Bill."""

    due_date: ConversionDescriptor = ConversionDescriptor(
        _default=datetime(1970, 1, 1),
        converter=lambda x: datetime.strptime(x, "%m/%d/%Y").date(),
    )
    service_charge: ConversionDescriptor = ConversionDescriptor(
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
    _header: ClassVar[tuple[str, ...]] = ()

    @override
    def validate(self) -> None:
        pass

    @override
    def to_row(self) -> tuple[str | int | float, ...]:
        return ()
