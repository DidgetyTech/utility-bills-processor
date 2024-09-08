"""The GasBill extracts, validates, and outputs the data correctly."""

from datetime import date
from pathlib import Path

import pytest

from utility_bills_processor.national_grid_gas import GasBill

DATA_ROOT = Path(__file__).parents[1].joinpath("tests_data")
OLD_BILL_PATH = DATA_ROOT.joinpath("gas-old.pdf")
BILL_PATH = DATA_ROOT.joinpath("gas.pdf")


def test_extract_fields_old_bill() -> None:
    """It extracts all the fields correctly from a real (redacted) PDF, in the old style."""
    bill = GasBill.extract_fields(OLD_BILL_PATH)
    assert isinstance(bill, GasBill)
    assert bill.current_date == date(2024, 4, 19)
    assert bill.current_meter_reading == 1805
    assert bill.current_method == "ACTUAL"
    assert bill.days_since_last_reading == 31
    assert bill.delivery_distribution_adjustment_rate_usd == 0.45740
    assert bill.delivery_first_tier_rate_usd == 0.9537
    assert bill.delivery_min_rate_usd == 0.4
    assert bill.delivery_total_usd == 75.90
    assert bill.paperless_bill_credit_usd == -0.38
    assert bill.previous_date, date(2024, 3, 19)
    assert bill.previous_meter_reading == 1761
    assert bill.previous_method == "ACTUAL"
    assert bill.supply_rate_usd == 0.81220
    assert bill.supply_total_usd == 36.55
    assert bill.thermal_factor == 1.0303
    assert bill.total_therms == 45
    assert bill.total_usd == 112.07


def test_extract_fields() -> None:
    """It extracts all the fields correctly from a real (redacted) PDF, in the current style."""
    bill = GasBill.extract_fields(BILL_PATH)
    assert isinstance(bill, GasBill)
    assert bill.current_date == date(2024, 7, 20)
    assert bill.current_meter_reading == 1829
    assert bill.current_method == "Actual"
    assert bill.days_since_last_reading == 32
    assert bill.delivery_distribution_adjustment_rate_usd == 0.4858
    # TODO delivery off-peak rate
    assert bill.delivery_first_tier_rate_usd == 0.4991
    # FIXME assert bill.delivery_min_rate_usd == -111111
    assert bill.delivery_total_usd == 17.72
    assert bill.paperless_bill_credit_usd == -0.38
    assert bill.previous_date, date(2024, 6, 20)
    assert bill.previous_meter_reading == 1824
    assert bill.previous_method == "Actual"
    assert bill.supply_rate_usd == 0.3813
    assert bill.supply_total_usd == 1.91
    assert bill.thermal_factor == 1.02923
    assert bill.total_therms == 5
    assert bill.total_usd == 19.25


def test_date_set() -> None:
    """It validates that the date property is the same as the current_date."""
    bill = GasBill.extract_fields(BILL_PATH)
    assert bill.date is bill.current_date


def test_validate() -> None:
    """It validates all the fields correctly from a real (redacted) PDF."""
    bill = GasBill.extract_fields(OLD_BILL_PATH)
    # doesn't raise an exception
    bill.validate()


def test_validate_inaccurate_total() -> None:
    """It finds an issue when the total doesn't match the line values."""
    bill = GasBill.extract_fields(OLD_BILL_PATH)
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
        "delivery_min_rate_usd",
        "delivery_first_tier_rate_usd",
        "delivery_distribution_adjustment_rate_usd",
        "delivery_total_usd",
        "supply_rate_usd",
        "supply_total_usd",
        "paperless_bill_credit_usd",
        "total_usd",
    )


def test_to_row() -> None:
    """It validates that the row has the correct values in the correct order."""
    bill = GasBill.extract_fields(OLD_BILL_PATH)
    assert bill.to_row() == (
        bill.current_date.isoformat(),
        bill.days_since_last_reading,
        bill.current_meter_reading,
        bill.previous_meter_reading,
        bill.thermal_factor,
        bill.total_therms,
        bill.delivery_min_rate_usd,
        bill.delivery_first_tier_rate_usd,
        bill.delivery_distribution_adjustment_rate_usd,
        bill.delivery_total_usd,
        bill.supply_rate_usd,
        bill.supply_total_usd,
        bill.paperless_bill_credit_usd,
        bill.total_usd,
    )
