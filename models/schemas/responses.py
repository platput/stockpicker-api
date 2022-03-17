from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel
from uuid import UUID

# Schema for money control data
from typing import List
from decimal import Decimal


class MCDataDetails(BaseModel):
    time_period: str
    starting_price: str
    ending_price: str


class MCData(BaseModel):
    stock_name: str
    stock_details: List[MCDataDetails]
    date: datetime


# Response model for /scrape/mc endpoint
class ScrapeMCResponse(BaseModel):
    success: bool
    message: str


# Response model for /shortlist/get endpoint
class ShortListResponse(BaseModel):
    success: bool
    message: str


class StockPrice(BaseModel):
    stock_start_price: Decimal
    stock_end_price: Decimal


class PriceActions(BaseModel):
    id: UUID
    stock_id: UUID
    price_date: date
    hour_1_start: Decimal
    hour_1_end: Decimal
    hour_2_start: Decimal
    hour_2_end: Decimal
    hour_3_start: Decimal
    hour_3_end: Decimal
    hour_4_start: Decimal
    hour_4_end: Decimal
    hour_5_start: Decimal
    hour_5_end: Decimal
    hour_6_start: Decimal
    hour_6_end: Decimal
    hour_7_start: Decimal
    hour_7_end: Decimal
    created_at: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ShortListedStock(BaseModel):
    stock_name: str
    symbol: str
    stock_url: Optional[str]
    stock_sector_name: Optional[str]
    stock_sector_url: Optional[str]
    is_intraday_allowed: Optional[bool]
    price_actions: List[PriceActions]


class ShortListedStocksResponse(BaseModel):
    success: bool
    message: str
    shortlisted_stocks: List[ShortListedStock]
