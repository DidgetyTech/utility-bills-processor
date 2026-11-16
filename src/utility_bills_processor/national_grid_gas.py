"""Represents and validates a National Grid Gas bill PDF."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import ClassVar, override

from ._common.bill import Bill
from ._common.dataclass_converters import ConversionDescriptor


def _spaced_int(value: str | int) -> int:
    if isinstance(value, str) and " " in value:
        value = value.replace(" ", "")
    return int(value)


def _spaced_float(value: str | float) -> float:
    if isinstance(value, str) and " " in value:
        value = value.replace(" ", "")
    return float(value)


def _spaced_optional_int(value: str | int | None) -> int | None:
    return _spaced_int(value) if value is not None else None


def _spaced_optional_float(value: str | float | None) -> float | None:
    return _spaced_float(value) if value is not None else None


@dataclass
class GasBill(Bill):
    """A Data Object representation of a Gas Bill."""

    current_method: str
    previous_method: str
    days_since_last_reading: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=_spaced_int
    )
    current_date: ConversionDescriptor = ConversionDescriptor(
        _default=date(1970, 1, 1),
        converter=lambda x: (
            datetime.strptime(x, "%b %d, %Y")
            if "," in x
            else datetime.strptime(x, "%b %d %Y")
        ).date(),
    )
    current_meter_reading: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=_spaced_int
    )
    previous_date: ConversionDescriptor = ConversionDescriptor(
        _default=date(1970, 1, 1),
        converter=lambda x: (
            datetime.strptime(x, "%b %d, %Y")
            if "," in x
            else datetime.strptime(x, "%b %d %Y")
        ).date(),
    )
    previous_meter_reading: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=_spaced_int
    )
    measured_therms: ConversionDescriptor = ConversionDescriptor(
        _default=None, converter=_spaced_optional_int
    )
    peak_therms: ConversionDescriptor = ConversionDescriptor(
        _default=0.0, converter=_spaced_optional_float
    )
    offpeak_therms: ConversionDescriptor = ConversionDescriptor(
        _default=0.0, converter=_spaced_optional_float
    )
    thermal_factor: ConversionDescriptor = ConversionDescriptor(
        _default=0.0, converter=_spaced_float
    )
    total_therms: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=_spaced_int
    )
    delivery_min_charge_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0.4, converter=_spaced_optional_float
    )
    delivery_peak_rate_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0.0, converter=_spaced_optional_float
    )
    delivery_offpeak_rate_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0.0, converter=_spaced_optional_float
    )
    delivery_distribution_adjustment_ee_rate_usd: ConversionDescriptor = (
        ConversionDescriptor(_default=0, converter=_spaced_optional_float)
    )
    delivery_distribution_adjustment_other_rate_usd: ConversionDescriptor = (
        ConversionDescriptor(_default=0, converter=_spaced_optional_float)
    )
    delivery_distribution_adjustment_rate_usd: ConversionDescriptor = (
        ConversionDescriptor(_default=0, converter=_spaced_optional_float)
    )
    delivery_total_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=_spaced_float
    )
    supply_peak_rate_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0.0, converter=_spaced_optional_float
    )
    supply_offpeak_rate_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0.0, converter=_spaced_optional_float
    )
    supply_total_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=_spaced_float
    )
    paperless_bill_credit_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=_spaced_float
    )
    total_usd: ConversionDescriptor = ConversionDescriptor(
        _default=0, converter=_spaced_float
    )

    _patterns: ClassVar[tuple[str, ...]] = (
        (
            r".*BILLING PERIOD"
            r".*(?P<previous_date>[a-zA-Z]{3} [0-9]{2}, 20\d{2})"
            r" to (?P<current_date>[a-zA-Z]{3} [0-9]{2}, 20\d{2})"
            r".*\$\s+(?P<total_usd>[.0-9]+)"
            r".*DETAIL OF CURRENT CHARGES"
            r".*Delivery Services"
            r".*Service\s+Period.*No.\s+of\s+days.*Current\s+Reading.*Previous\s+Reading.*Measured"
            r"\s+CCF.*Therm\s+Factor.*Therms\s+Used"
            r".*\w{3}\s+\d{2}\s+-\s+\w{3}\s+\d{2}"
            r" +(?P<days_since_last_reading>\d{2})"
            r" +(?P<current_meter_reading>\d+) +(?P<current_method>\w+)"
            r" +(?P<previous_meter_reading>\d+) +(?P<previous_method>\w+)"
            r" +(?P<measured_therms>\d+)"
            r" +(?P<thermal_factor>[.0-9]+)"
            r" +(?P<total_therms>\d+)"
            r".*RATE +R\-3B Residential Heating"
            r".*Minimum Charge\s+(?P<delivery_min_charge_usd>[.0-9]+)"
            r"(.*Delivery Peak\s+(?P<delivery_peak_rate_usd>[.0-9]+)\s*"
            r"x\s*(?P<peak_therms>[.0-9]+)\stherms)?"
            r"(.*Delivery Off.Peak\s+(?P<delivery_offpeak_rate_usd>[.0-9]+)\s*"
            r"x\s*(?P<offpeak_therms>[.0-9]+)\stherms)?"
            r".*(Distribution Adjustment\s+(?P<delivery_distribution_adjustment_rate_usd>[.0-9]+)"
            r"\s*x\s*[.0-9]+\stherms"
            r"|Dist Adj - Energy Efficiency\s+"
            r"(?P<delivery_distribution_adjustment_ee_rate_usd>[.0-9]+)\s*x\s*[.0-9]+\stherms"
            r".*Distribution Adj - Other\s+"
            r"(?P<delivery_distribution_adjustment_other_rate_usd>[.0-9]+)\s*x\s*[.0-9]+\stherms)"
            r".*Total Delivery Services[ $]+(?P<delivery_total_usd>[.0-9]+)"
            r".*Supply Services"
            r".*SUPPLIER *National Grid"
            r"(.*Gas Supply Peak\s+(?P<supply_peak_rate_usd>[.0-9]+)\s*x\s*[.0-9]+ therms)?"
            r"(.*Gas Supply Off.Peak\s+(?P<supply_offpeak_rate_usd>[.0-9]+)\s*x\s*[.0-9]+ therms)?"
            r".*Total Supply Services[ $]+(?P<supply_total_usd>[.0-9]+)"
            r".*Other Charges/Adjustments"
            r".*Paperless Billing Credit\s+(?P<paperless_bill_credit_usd>[\-.0-9]+)"
            r".*Total Other Charges/Adjustments"
            r".*"
        ),
    )

    _header: ClassVar[tuple[str, ...]] = (
        "current_date",
        "days_since_last_reading",
        "current_meter_reading",
        "previous_meter_reading",
        "thermal_factor",
        "total_therms_used",
        "peak_therms_used",
        "offpeak_therms_used",
        "delivery_min_charge_usd",
        "delivery_peak_rate_usd",
        "delivery_offpeak_rate_usd",
        "delivery_distribution_adjustment_rate_usd",
        "delivery_total_usd",
        "supply_peak_rate_usd",
        "supply_offpeak_rate_usd",
        "supply_total_usd",
        "paperless_bill_credit_usd",
        "total_usd",
    )

    def __post_init__(self) -> None:
        """Dataclass post-init to account for fields that may not be present in all bills."""
        if not self.delivery_distribution_adjustment_rate_usd:
            self.delivery_distribution_adjustment_rate_usd = (
                self.delivery_distribution_adjustment_ee_rate_usd
                + self.delivery_distribution_adjustment_other_rate_usd
            )

    @property
    @override
    def date(self) -> date:  # noqa: D102
        d: date = self.current_date
        return d

    @override
    def validate(self) -> None:  # noqa: D102
        # TODO validation with fields that are inconsistent between bill layouts
        calculated = self.current_date - self.previous_date
        if calculated != timedelta(days=self.days_since_last_reading):
            raise ValueError(
                f"Dates don't match: {self.current_date=}"
                f" {self.previous_date=} => {calculated=}"
                f" {self.days_since_last_reading=}"
            )

        calculated = round(
            (self.current_meter_reading - self.previous_meter_reading)
            * self.thermal_factor,
            0,
        )
        if calculated != self.total_therms:
            raise ValueError(
                "Readings and therms don't match:"
                f" {self.current_meter_reading=}"
                f" {self.previous_meter_reading=}"
                f" {self.thermal_factor=}"
                f" => {calculated=} != {self.total_therms=}"
            )

        calculated = round(self.peak_therms + self.offpeak_therms, 2)
        if calculated != self.total_therms:
            raise ValueError(
                "Peak and Off Peak therms don't match Total Therms:"
                f" {self.peak_therms=}"
                f" {self.offpeak_therms=}"
                f" => {calculated=}"
                f" {self.total_therms=}"
            )

        calculated = round(
            self.delivery_min_charge_usd
            + self.peak_therms * self.delivery_peak_rate_usd
            + self.offpeak_therms * self.delivery_offpeak_rate_usd
            + self.total_therms * self.delivery_distribution_adjustment_rate_usd,
            2,
        )
        if calculated != self.delivery_total_usd:
            raise ValueError(
                "Delivery rates and therms don't match total:"
                f" {self.total_therms=}"
                f" {self.peak_therms=}"
                f" {self.offpeak_therms=}"
                f" {self.delivery_peak_rate_usd=}"
                f" {self.delivery_offpeak_rate_usd=}"
                f" {self.delivery_distribution_adjustment_rate_usd=}"
                f" => {calculated=}"
                f" != {self.delivery_total_usd=}"
            )

        calculated = round(
            self.peak_therms * self.supply_peak_rate_usd
            + self.offpeak_therms * self.supply_offpeak_rate_usd,
            2,
        )
        if calculated != self.supply_total_usd:
            raise ValueError(
                "Supply rates and therms don't match total:"
                f" {self.peak_therms=}"
                f" {self.offpeak_therms=}"
                f" {self.supply_peak_rate_usd=}"
                f" {self.supply_offpeak_rate_usd=}"
                f" => {calculated=}"
                f" != {self.supply_total_usd}"
            )

        calculated = round(
            self.delivery_total_usd
            + self.supply_total_usd
            + self.paperless_bill_credit_usd,
            2,
        )
        if calculated != self.total_usd:
            raise ValueError(
                f"Totals don't match: {self.delivery_total_usd=}"
                + f" {self.supply_total_usd=}"
                + f" {self.paperless_bill_credit_usd=}"
                + f" => {calculated=} != {self.total_usd=}"
            )

    @override
    def to_row(self) -> tuple[str | int | float, ...]:  # noqa: D102
        return (
            self.current_date.isoformat(),
            self.days_since_last_reading,
            self.current_meter_reading,
            self.previous_meter_reading,
            self.thermal_factor,
            self.total_therms,
            self.peak_therms,
            self.offpeak_therms,
            self.delivery_min_charge_usd,
            self.delivery_peak_rate_usd,
            self.delivery_offpeak_rate_usd,
            self.delivery_distribution_adjustment_rate_usd,
            self.delivery_total_usd,
            self.supply_peak_rate_usd,
            self.supply_offpeak_rate_usd,
            self.supply_total_usd,
            self.paperless_bill_credit_usd,
            self.total_usd,
        )
