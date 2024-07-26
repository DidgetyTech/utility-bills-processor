from datetime import date
from pathlib import Path
from unittest import TestCase, main

from utility_bills_processor.water_and_sewer import WaterBill

DATA_ROOT = Path(__file__).parents[1].joinpath("tests_data")
MUNICIPAL_BILL_PATH = DATA_ROOT.joinpath("municipal-water-sewer.pdf")


class WaterBillTest(TestCase):
    def test_extract_fields(self) -> None:
        bill: WaterBill = WaterBill.extract_fields(MUNICIPAL_BILL_PATH)  # type: ignore[assignment]
        assert isinstance(bill, WaterBill)
        self.assertEqual(bill.adjustments, 0.0)
        self.assertEqual(bill.current_meter_reading, 743)
        self.assertEqual(bill.interest, 0.0)
        self.assertEqual(bill.past_due, 0.0)
        self.assertEqual(bill.read_date, date(2023, 11, 25))
        self.assertEqual(bill.sewer_charge, 7.33)
        self.assertEqual(bill.total, 10.03)
        self.assertEqual(bill.usage, 1)
        self.assertEqual(bill.usage_type, "Actual")
        self.assertEqual(bill.water_charge, 2.70)

    def test_validate(self) -> None:
        bill = WaterBill.extract_fields(MUNICIPAL_BILL_PATH)
        # doesn't raise an exception
        bill.validate()

    def test_validate_inaccurate_total(self) -> None:
        bill: WaterBill = WaterBill.extract_fields(MUNICIPAL_BILL_PATH)  # type: ignore[assignment]
        bill.total = -100
        with self.assertRaises(ValueError):
            bill.validate()

    def test_to_header(self) -> None:
        self.assertEqual(
            WaterBill.to_header(),
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
        bill: WaterBill = WaterBill.extract_fields(MUNICIPAL_BILL_PATH)  # type: ignore[assignment]
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
