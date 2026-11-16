"""The GasBill extracts, validates, and outputs the data correctly."""

from datetime import date
from pathlib import Path

import pytest

from utility_bills_processor.national_grid_gas import GasBill

DATA_ROOT = Path(__file__).parents[1].joinpath("tests_data")
BILL_PATH = DATA_ROOT.joinpath("gas.pdf")


def test_extract_fields() -> None:
    """It extracts all the fields correctly from a real (redacted) PDF, in the current style."""
    bill = GasBill.extract_fields(BILL_PATH)
    assert isinstance(bill, GasBill)
    assert bill.current_date == date(2025, 4, 22)
    assert bill.current_meter_reading == 2264
    assert bill.current_method == "Actual"
    assert bill.days_since_last_reading == 33
    assert bill.delivery_distribution_adjustment_rate_usd == 0.31157128
    assert bill.delivery_min_charge_usd == 13.20
    assert bill.delivery_offpeak_rate_usd == 0.0
    assert bill.delivery_peak_rate_usd == 0.98
    assert bill.delivery_total_usd == 84.23
    assert bill.offpeak_therms == 0.0
    assert bill.paperless_bill_credit_usd == -0.38
    assert bill.peak_therms == 55
    assert bill.previous_date, date(2025, 3, 20)
    assert bill.previous_meter_reading == 2211
    assert bill.previous_method == "Actual"
    assert bill.supply_offpeak_rate_usd == 0.0
    assert bill.supply_peak_rate_usd == 0.8467
    assert bill.supply_total_usd == 46.57
    assert bill.thermal_factor == 1.03042
    assert bill.total_therms == 55
    assert bill.total_usd == 130.42


def test_date_set() -> None:
    """It validates that the date property is the same as the current_date."""
    bill = GasBill.extract_fields(BILL_PATH)
    assert bill.date is bill.current_date


def test_validate() -> None:
    """It validates all the fields correctly from a real (redacted) PDF."""
    bill = GasBill.extract_fields(BILL_PATH)
    # current bills has off-by-one-cent error in the delivery. mundge it to test calcs.
    bill.delivery_min_charge_usd -= 0.01
    # doesn't raise an exception
    bill.validate()


def test_validate_inaccurate_total() -> None:
    """It finds an issue when the total doesn't match the line values."""
    bill = GasBill.extract_fields(BILL_PATH)
    bill.total_usd = -100
    with pytest.raises(ValueError):
        bill.validate()


def test_to_header() -> None:
    """It validates the header is in the correct order and correct set."""
    assert GasBill.to_header() == (
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


def test_to_row() -> None:
    """It validates that the row has the correct values in the correct order."""
    bill = GasBill.extract_fields(BILL_PATH)
    assert bill.to_row() == (
        bill.current_date.isoformat(),
        bill.days_since_last_reading,
        bill.current_meter_reading,
        bill.previous_meter_reading,
        bill.thermal_factor,
        bill.total_therms,
        bill.peak_therms,
        bill.offpeak_therms,
        bill.delivery_min_charge_usd,
        bill.delivery_peak_rate_usd,
        bill.delivery_offpeak_rate_usd,
        bill.delivery_distribution_adjustment_rate_usd,
        bill.delivery_total_usd,
        bill.supply_peak_rate_usd,
        bill.supply_offpeak_rate_usd,
        bill.supply_total_usd,
        bill.paperless_bill_credit_usd,
        bill.total_usd,
    )
