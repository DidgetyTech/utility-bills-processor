from datetime import date
from pathlib import Path
from unittest import TestCase, main

from utility_bills_processor.internet import InternetBill

DATA_ROOT = Path(__file__).parents[1].joinpath("tests_data")


class InternetBillTest(TestCase):
    """The WaterBill extracts, validates, and outputs the data correctly."""

    def test_extract_fields(self) -> None:
        """It extracts all the fields correctly from a real (redacted) PDF."""
        bill = InternetBill.extract_fields(DATA_ROOT.joinpath("fios-internet.pdf"))
        assert isinstance(bill, InternetBill)

    def test_validate(self) -> None:
        """It validates all the fields correctly from a real (redacted) PDF."""
        bill = InternetBill.extract_fields(DATA_ROOT.joinpath("fios-internet.pdf"))
        # doesn't raise an exception
        bill.validate()

    def test_validate_inaccurate_total(self) -> None:
        """It finds an issue when the total doesn't match the line values."""
        bill = InternetBill.extract_fields(DATA_ROOT.joinpath("fios-internet.pdf"))
        bill.total = -100
        with self.assertRaises(ValueError):
            bill.validate()

    def test_to_header(self) -> None:
        """It validates the header is in the correct order and correct set."""
        self.assertEqual(
            InternetBill.to_header(),
            (
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
            ),
        )

    def test_to_row(self) -> None:
        """It validates that the row has the correct values in the correct order."""
        bill = InternetBill.extract_fields(DATA_ROOT.joinpath("fios-internet.pdf"))
        self.assertEqual(
            bill.to_row(),
            (
                bill.read_date,
                bill.current_meter_reading,
                bill.usage_type,
                bill.usage,
                bill.water_charge,
                bill.sewer_charge,
                bill.past_due,
                bill.interest,
                bill.adjustments,
                bill.total,
            ),
        )


if __name__ == "__main__":
    main()
