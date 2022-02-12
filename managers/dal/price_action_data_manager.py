import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils.types.pg_composite import psycopg2

from helpers.constants import Constants
from models.db.schema import PriceAction, StockName
import uuid


class PriceActionDataManager:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def add_price_actions_to_db(self, data):
        for price_action in data:
            stock_name = price_action.get(Constants.STOCK_NAME)
            price_date = price_action.get(Constants.DATE).date().strftime('%Y-%m-%d')
            if self.check_if_price_action_exists(self.get_stock_from_db(stock_name).id, price_date):
                continue
            price_action_obj = PriceAction()
            price_action_obj.id = uuid.uuid4()
            price_action_obj.stock_id = self.get_stock_from_db(stock_name).id
            price_action_obj.price_date = price_date
            stock_details = price_action.get(Constants.STOCK_DETAILS)
            for stock in stock_details:
                time_period = stock.get(Constants.TIME_PERIOD)
                match time_period:
                    case Constants.NINE_TO_TEN:
                        price_action_obj.hour_1_start = stock.get(Constants.STARTING_PRICE).replace(",", "")
                        price_action_obj.hour_1_end = stock.get(Constants.ENDING_PRICE).replace(",", "")
                    case Constants.TEN_TO_ELEVEN:
                        price_action_obj.hour_2_start = stock.get(Constants.STARTING_PRICE).replace(",", "")
                        price_action_obj.hour_2_end = stock.get(Constants.ENDING_PRICE).replace(",", "")
                    case Constants.ELEVEN_TO_TWELVE:
                        price_action_obj.hour_3_start = stock.get(Constants.STARTING_PRICE).replace(",", "")
                        price_action_obj.hour_3_end = stock.get(Constants.ENDING_PRICE).replace(",", "")
                    case Constants.TWELVE_TO_THIRTEEN:
                        price_action_obj.hour_4_start = stock.get(Constants.STARTING_PRICE).replace(",", "")
                        price_action_obj.hour_4_end = stock.get(Constants.ENDING_PRICE).replace(",", "")
                    case Constants.THIRTEEN_TO_FOURTEEN:
                        price_action_obj.hour_5_start = stock.get(Constants.STARTING_PRICE).replace(",", "")
                        price_action_obj.hour_5_end = stock.get(Constants.ENDING_PRICE).replace(",", "")
                    case Constants.FOURTEEN_TO_FIFTEEN:
                        price_action_obj.hour_6_start = stock.get(Constants.STARTING_PRICE).replace(",", "")
                        price_action_obj.hour_6_end = stock.get(Constants.ENDING_PRICE).replace(",", "")
                    case Constants.FIFTEEN_TO_SIXTEEN:
                        price_action_obj.hour_7_start = stock.get(Constants.STARTING_PRICE).replace(",", "")
                        price_action_obj.hour_7_end = stock.get(Constants.ENDING_PRICE).replace(",", "")
            price_action_obj.created_at = datetime.now(ZoneInfo('Asia/Kolkata'))
            try:
                self.db_connection.add(price_action_obj)
                self.db_connection.commit()
            except IntegrityError as e:
                logging.getLogger().error(e)

    def add_and_get_new_stock_to_db(self, stock_name):
        stock_obj = StockName(id=uuid.uuid4(), stock_name=stock_name)
        self.db_connection.add(stock_obj)
        self.db_connection.commit()
        return stock_obj

    def get_stock_from_db(self, stock_name):
        try:
            stmt = select(StockName).where(StockName.stock_name == stock_name)
            if result := self.db_connection.execute(stmt).scalar():
                return result
            else:
                return self.add_and_get_new_stock_to_db(stock_name)
        except Exception as e:
            logging.getLogger().error(e)

    def check_if_price_action_exists(self, stock_id, date):
        try:
            stmt = select(PriceAction).where(PriceAction.stock_id == stock_id, PriceAction.price_date == date)
            if self.db_connection.execute(stmt).scalar() is not None:
                return True
            else:
                return False
        except Exception as e:
            logging.getLogger().error(e)

