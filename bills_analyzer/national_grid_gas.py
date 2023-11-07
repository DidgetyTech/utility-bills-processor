from pypdf import PdfReader
from pathlib import Path
from typing import Optional, Callable, Any
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta


EXAMPLE="""
   CURRENT BILL ITEMIZED      SUMMARY OF CHARGES
In 29 days you used 2 therms: Total Current Charges    $13.59
Amount Due Last Bill     15.26
Aug 18 2023 reading ACTUAL       1481 Your Total Payments Since
Jul 20 2023 reading ACTUAL        ____     1479   Last Bill. Thank You!    -15.26     ______
CCF Used for METER# 007030517        2
DirectPay Amount    $13.59
Thermal Factor     _______    x1.0289
Total therms used         2 GAS USE HISTORY
     Days  Therms      Days  Therms
Your Cost is determined as follows: Aug 23  29 Act    2   Jan 23  30 Act   65
Jul 23  30 Act    3   Dec 22  34 Act   63
Minimum Charge      $11.60 Jun 23  32 Act    3   Nov 22  28 Act   11
$.4000 per day for 29 days May 23  29 Act   11   Oct 22  32 Act    4
First 2.0 therms @ $.4784        .96 Apr 23  31 Act   25   Sep 22  30 Act    3
Distribution Adjustment: Mar 23  32 Act   62   Aug 22  28 Act    5
2 therms x 0.47960 per therm        ______      .96 Feb 23  28 Act   62   Jul 22  34 Act    7
GAS DELIVERY CHARGE    $13.52
GAS SUPPLY CHARGE
@ $.22730 /therm        .45
Paperless Bill Credit         -.38     ______
TOTAL CURRENT CHARGES    $13.59
"""

PATTERN = (
  r".*In (?P<days>\d+) days"
  r".*(?P<cur_date>[a-zA-Z]{3} [0-9]{2} 20\d{2}) reading (?P<cur_method>[^\s]*)             (?P<cur_reading>\d+)"
  r".*(?P<prev_date>[a-zA-Z]{3} [0-9]{2} 20\d{2}) reading (?P<prev_method>[^\s]*)                ____         (?P<prev_reading>\d+)"
  r".*Thermal Factor.*x(?P<thermal_factor>[\.0-9]+)"
  r".*Total therms used.*(?P<total_therms>\d+)"
  r".*\$(?P<delivery_min_rate_usd>[\.0-9]+) per day for (?P=days) days"
  r".*First [\.0-9]+ therms @ \$(?P<delivery_first_tier_rate_usd>[\.0-9]+)"
  r".*Distribution Adjustment"
  r".*(?P=total_therms) therms x (?P<delivery_distribution_adjustment_rate>[\.0-9]+) per therm"
  r".*GAS DELIVERY CHARGE.*\$(?P<delivery_total_usd>[\.0-9]+)"
  r".*GAS SUPPLY CHARGE"
  r".*@ \$(?P<supply_rate>[\.0-9]+) /therm"
  r".*Paperless Bill Credit.*(?P<paperless_bill_credit_usd>-[\.0-9]+)"
  r".*TOTAL CURRENT CHARGES.*\$(?P<total_usd>[\.0-9]+)"
  r".*"
)

class ConversionDescriptor:
  def __init__(self, *, converter: Callable[[Any], Any]):
    self._converter = converter

  def __set_name__(self, owner, name):
    self._name = "_" + name

  def __get__(self, obj, type):
    if obj is None:
      return self._default

    return getattr(obj, self._name)

  def __set__(self, obj, value):
    setattr(obj, self._name, self._converter(value))


@dataclass
class GasBill:
  days: ConversionDescriptor = ConversionDescriptor(converter=int)
  cur_date: ConversionDescriptor = ConversionDescriptor(converter=lambda x: datetime.strptime(x, "%b %d %Y").date())
  cur_method: str
  cur_reading: ConversionDescriptor = ConversionDescriptor(converter=int)
  prev_date: ConversionDescriptor = ConversionDescriptor(converter=lambda x: datetime.strptime(x, "%b %d %Y").date())
  prev_method: str
  prev_reading: ConversionDescriptor = ConversionDescriptor(converter=int)
  thermal_factor: ConversionDescriptor = ConversionDescriptor(converter=float)
  total_therms: ConversionDescriptor = ConversionDescriptor(converter=int)
  delivery_min_rate_usd: ConversionDescriptor = ConversionDescriptor(converter=float)
  delivery_first_tier_rate_usd: ConversionDescriptor = ConversionDescriptor(converter=float)
  delivery_distribution_adjustment_rate: ConversionDescriptor = ConversionDescriptor(converter=float)
  delivery_total_usd: ConversionDescriptor = ConversionDescriptor(converter=float)
  supply_rate: ConversionDescriptor = ConversionDescriptor(converter=float)
  supply_total_usd: float = field(init=False)
  paperless_bill_credit_usd: ConversionDescriptor = ConversionDescriptor(converter=float)
  total_usd: ConversionDescriptor = ConversionDescriptor(converter=float)

  def __post_init__(self):
    self.supply_total_usd = round(self.total_therms * self.supply_rate, 2)

  def validate(self):
    calculated = self.cur_date - self.prev_date
    if calculated != timedelta(days=self.days):
      raise ValueError(f"Dates don't match: cur_date={self.cur_date} prev_date={self.prev_date} => calculated={calculated} days={self.days}")
    
    calculated = round((self.cur_reading - self.prev_reading) * self.thermal_factor, 0)
    if calculated != self.total_therms:
      raise ValueError(f"Readings and therms don't match: cur_reading={self.cur_reading} prev_reading={self.prev_reading} thermal_factor={self.thermal_factor} => calculated={calculated} != total_therms={self.total_therms}")
    
    calculated = round(self.days * self.delivery_min_rate_usd + self.total_therms * (self.delivery_first_tier_rate_usd + self.delivery_distribution_adjustment_rate), 2)
    if calculated != self.delivery_total_usd:
      raise ValueError(f"Delivery rates and therms don't match total: total_therms={self.total_therms} delivery_min_rate_usd={self.delivery_min_rate_usd} delivery_first_tier_rate_usd={self.delivery_first_tier_rate_usd} delivery_distribution_adjustment_rate={self.delivery_distribution_adjustment_rate} => calculated={calculated} != delivery_total_usd={self.delivery_total_usd}")
    
    calculated = round(self.delivery_total_usd + self.supply_total_usd + self.paperless_bill_credit_usd, 2)
    if calculated != self.total_usd:
      raise ValueError(f"Totals don't match: delivery_total_usd={self.delivery_total_usd} supply_total_usd={self.supply_total_usd} paperless_bill_credit_usd={self.paperless_bill_credit_usd} => calculated={calculated} != total_usd={self.total_usd}")


  def to_row(self):
    return [
      self.cur_date.isoformat(),
      self.days,
      self.cur_reading,
      self.prev_reading,
      self.thermal_factor,
      self.total_therms,
      self.delivery_min_rate_usd,
      self.delivery_first_tier_rate_usd,
      self.delivery_distribution_adjustment_rate,
      self.delivery_total_usd,
      self.supply_rate,
      self.supply_total_usd,
      self.paperless_bill_credit_usd,
      self.total_usd,
    ]


def extract_gas_fields(file: Path, password: Optional[str]):
  reader = PdfReader(str(file))

  if reader.is_encrypted:
    if password is None:
      raise RuntimeError("Cannot read an encrypted document without a password")
    reader.decrypt(password)

  text = "\n\n".join((page.extract_text() for page in reader.pages))
  match = re.search(PATTERN, text, flags=re.DOTALL)
  if match is None:
    raise RuntimeError(f"Cannot parse bill\n{text}")
  return GasBill(**match.groupdict())


if __name__ == "__main__":
  import sys
  bill = extract_gas_fields(
    Path(sys.argv[1]),
    sys.argv[2] if len(sys.argv) >= 3 else None,
  )
  bill.validate()
  print(", ".join(map(str, bill.to_row())))
