"""The WaterBill extracts, validates, and outputs the data correctly."""

from datetime import date
from pathlib import Path
from unittest import TestCase, main

from utility_bills_processor.internet import InternetBill

DATA_ROOT = Path(__file__).parents[1].joinpath("tests_data")
BILL_PATH = DATA_ROOT / "fios-internet.pdf"


class InternetBillTest(TestCase):
    """The WaterBill extracts, validates, and outputs the data correctly."""

    def test_extract_fields(self) -> None:
        """It extracts all the fields correctly from a real (redacted) PDF."""
        bill = InternetBill.extract_fields(BILL_PATH)
        assert isinstance(bill, InternetBill)
        assert bill.bill_date == date(2024, 10, 9)
        assert bill.fees_usd == 0.0
        assert bill.late_fees_usd == 0.0
        assert bill.one_time_charges_usd == 0.0
        assert bill.service_charge_usd == 59.99
        assert bill.speed == 300
        assert bill.speed_unit == "Mbps"
        assert bill.taxes_usd == 0.0
        assert bill.total_usd == 59.99

    def test_validate(self) -> None:
        """It validates all the fields correctly from a real (redacted) PDF."""
        bill = InternetBill.extract_fields(BILL_PATH)
        # doesn't raise an exception
        bill.validate()

    def test_validate_inaccurate_total(self) -> None:
        """It finds an issue when the total doesn't match the line values."""
        bill = InternetBill.extract_fields(BILL_PATH)
        bill.total_usd = -100
        with self.assertRaises(ValueError):
            bill.validate()

    def test_to_header(self) -> None:
        """It validates the header is in the correct order and correct set."""
        self.assertEqual(
            InternetBill.to_header(),
            (
                "bill_date",
                "speed",
                "service_charge_usd",
                "one_time_charges_usd",
                "taxes_usd",
                "fees_usd",
                "late_fees_usd",
                "total_usd",
            ),
        )

    def test_to_row(self) -> None:
        """It validates that the row has the correct values in the correct order."""
        bill = InternetBill.extract_fields(BILL_PATH)
        self.assertEqual(
            bill.to_row(),
            (
                bill.bill_date,
                f"{bill.speed} {bill.speed_unit}",
                bill.service_charge_usd,
                bill.one_time_charges_usd,
                bill.taxes_usd,
                bill.fees_usd,
                bill.late_fees_usd,
                bill.total_usd,
            ),
        )


if __name__ == "__main__":
    main()
