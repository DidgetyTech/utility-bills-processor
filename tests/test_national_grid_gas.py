"""The GasBill extracts, validates, and outputs the data correctly."""

from datetime import date
from pathlib import Path
from unittest import TestCase, main

from utility_bills_processor.national_grid_gas import GasBill

DATA_ROOT = Path(__file__).parents[1].joinpath("tests_data")
BILL_PATH = DATA_ROOT.joinpath("gas.pdf")


class GasBillTest(TestCase):
    """The GasBill extracts, validates, and outputs the data correctly."""

    def test_extract_fields(self) -> None:
        """It extracts all the fields correctly from a real (redacted) PDF."""
        bill = GasBill.extract_fields(BILL_PATH)
        self.assertIsInstance(bill, GasBill)
        self.assertEqual(bill.current_date, date(2024, 4, 19))
        self.assertEqual(bill.current_meter_reading, 1805)
        self.assertEqual(bill.current_method, "ACTUAL")
        self.assertEqual(bill.days_since_last_reading, 31)
        self.assertEqual(bill.delivery_distribution_adjustment_rate, 0.45740)
        self.assertEqual(bill.delivery_first_tier_rate_usd, 0.9537)
        self.assertEqual(bill.delivery_min_rate_usd, 0.4)
        self.assertEqual(bill.delivery_total_usd, 75.90)
        self.assertEqual(bill.paperless_bill_credit_usd, -0.38)
        self.assertEqual(bill.previous_date, date(2024, 3, 19))
        self.assertEqual(bill.previous_meter_reading, 1761)
        self.assertEqual(bill.previous_method, "ACTUAL")
        self.assertEqual(bill.supply_rate, 0.81220)
        self.assertEqual(bill.supply_total_usd, 36.55)
        self.assertEqual(bill.thermal_factor, 1.0303)
        self.assertEqual(bill.total_therms, 45)
        self.assertEqual(bill.total_usd, 112.07)

    def test_validate(self) -> None:
        """It validates all the fields correctly from a real (redacted) PDF."""
        bill = GasBill.extract_fields(BILL_PATH)
        # doesn't raise an exception
        bill.validate()

    def test_validate_inaccurate_total(self) -> None:
        """It finds an issue when the total doesn't match the line values."""
        bill = GasBill.extract_fields(BILL_PATH)
        bill.total_usd = -100
        with self.assertRaises(ValueError):
            bill.validate()

    def test_to_header(self) -> None:
        """It validates the header is in the correct order and correct set."""
        self.assertEqual(
            GasBill.to_header(),
            (
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
            ),
        )

    def test_to_row(self) -> None:
        """It validates that the row has the correct values in the correct order."""
        bill = GasBill.extract_fields(BILL_PATH)
        self.assertEqual(
            bill.to_row(),
            (
                bill.current_date.isoformat(),
                bill.days_since_last_reading,
                bill.current_meter_reading,
                bill.previous_meter_reading,
                bill.thermal_factor,
                bill.total_therms,
                bill.delivery_min_rate_usd,
                bill.delivery_first_tier_rate_usd,
                bill.delivery_distribution_adjustment_rate,
                bill.delivery_total_usd,
                bill.supply_rate,
                bill.supply_total_usd,
                bill.paperless_bill_credit_usd,
                bill.total_usd,
            ),
        )


if __name__ == "__main__":
    main()
