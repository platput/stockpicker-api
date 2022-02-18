from datetime import datetime, date
from enum import Enum

from pydantic import BaseModel, Field

# Schema for money control data
from typing import List
from decimal import Decimal

from sqlalchemy_utils.types import uuid


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


class PriceActionTimePeriod(Enum):
    NINE_TO_TEN = 1
    TEN_TO_ELEVEN = 2
    ELEVEN_TO_TWELVE = 3
    TWELVE_TO_ONE = 4
    ONE_TO_TWO = 5
    TWO_TO_THREE = 6
    THREE_TO_FOUR = 7


class StockPrice(BaseModel):
    stock_start_price: Decimal
    stock_end_price: Decimal


class PriceActions(BaseModel):
    price_action_id: uuid
    price_action_date: date
    price_action_time_period: PriceActionTimePeriod
    stock_price: StockPrice


class ShortListedStocks(BaseModel):
    stock_id: uuid
    stock_name: str
    price_actions: List[PriceActions]
