from pydantic import BaseModel
from datetime import datetime
from typing import List


class RateBase(BaseModel):
    rate: float


class RateCreate(RateBase):
    pass


class PayBase(BaseModel):
    method: str
    native_amount: float


class SaleCreate(BaseModel):
    total_usd: float
    payments: List[PayBase]


class DailyReport(BaseModel):
    total_sale_usd: float
    sale_count: int
    total_zelle: float
    total_usd: float
    total_binance_pay: float
    total_bs: float
    total_bs_efectivo: float
    total_mobile_payment_bs: float
    total_point_of_sale_bs: float


class History(BaseModel):
    date: datetime
    first_sale_date: datetime
    last_sale_date: datetime
    total_sales: int
    total_amount: float
    last_rate_used: float
