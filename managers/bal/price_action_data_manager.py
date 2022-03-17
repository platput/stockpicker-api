import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from helpers.constants import Constants
from models.db.schema import PriceAction, StockName, Sector
import uuid


class PriceActionDataManager:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def add_price_actions_to_db(self, data):
        """
        Adds price actions to db
        :param data:
        :return:
        """
        for price_action in data:
            stock_name = price_action.get(Constants.STOCK_NAME)
            stock_url = price_action.get(Constants.STOCK_DETAILS_URL)
            price_date = price_action.get(Constants.DATE).date().strftime('%Y-%m-%d')
            stock_from_db = self.get_stock_from_db(stock_name, stock_url)
            if self.check_if_price_action_exists(stock_from_db.id, price_date):
                continue
            price_action_obj = PriceAction()
            price_action_obj.id = uuid.uuid4()
            price_action_obj.stock_id = stock_from_db.id
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

    def add_and_get_new_stock_to_db(self, stock_name, stock_url):
        """
        Adds a new stock to db with just the name and the url and returns the stock object
        :param stock_name:
        :param stock_url:
        :return:
        """
        stock_obj = StockName(id=uuid.uuid4(), stock_name=stock_name, details_url=stock_url)
        self.db_connection.add(stock_obj)
        self.db_connection.commit()
        return stock_obj

    def get_stock_from_db(self, stock_name, stock_url):
        """
        Get stock from db
        If it doesn't have the details url this will add it and return the stock
        Otherwise, this will just return the stock without doing anything else
        If the stock doesn't exist altogether, this adds new stock to db and returns it
        :param stock_name:
        :param stock_url:
        :return:
        """
        try:
            stmt = select(StockName).where(StockName.stock_name == stock_name)
            if result := self.db_connection.execute(stmt).scalar():
                if result.details_url is None:
                    # Add details url to db
                    result.details_url = stock_url
                    self.db_connection.add(result)
                    self.db_connection.commit()
                return result
            else:
                return self.add_and_get_new_stock_to_db(stock_name, stock_url)
        except Exception as e:
            logging.getLogger().error(e)

    def check_if_price_action_exists(self, stock_id, date):
        """
        Checks if price action exists for a stock on a particular date
        and returns a boolean value; true if it exists, false otherwise
        :param stock_id:
        :param date:
        :return:
        """
        try:
            stmt = select(PriceAction).where(PriceAction.stock_id == stock_id, PriceAction.price_date == date)
            if self.db_connection.execute(stmt).scalar() is not None:
                return True
            else:
                return False
        except Exception as e:
            logging.getLogger().error(e)

    def get_stocks_with_missing_sector_details(self):
        """
        Gets the stocks with missing sector details
        :return:
        """
        try:
            stmt = select(StockName).where(StockName.sector_id == None, StockName.details_url != None)
            return self.db_connection.execute(stmt).scalars()
        except Exception as e:
            logging.getLogger().error(e)

    def get_stocks_with_missing_symbol(self):
        """
        Gets the stocks with missing symbol
        :return:
        """
        try:
            stmt = select(StockName).where(StockName.symbol == None)
            return self.db_connection.execute(stmt).scalars()
        except Exception as e:
            logging.getLogger().error(e)

    def add_sector_details_to_db(self, stock_id, sector_name, sector_url):
        """
        Adds the sector details to db and update the stock with the sector id
        :param stock_id:
        :param sector_name:
        :param sector_url:
        :return:
        """
        try:
            sector_stmt = select(Sector).where(Sector.sector_name == sector_name)
            if sector := self.db_connection.execute(sector_stmt).scalar():
                logging.getLogger().info(f"Sector {sector_name} already exists in db, not adding again.")
            else:
                sector = Sector(id=uuid.uuid4(), sector_name=sector_name, sector_url=sector_url)
                self.db_connection.add(sector)
                self.db_connection.commit()
            stmt = select(StockName).where(StockName.id == stock_id)
            stock_obj = self.db_connection.execute(stmt).scalar()
            stock_obj.sector_id = sector.id
            self.db_connection.add(stock_obj)
            self.db_connection.commit()
        except Exception as e:
            logging.getLogger().error(e)
            self.db_connection.rollback()

    def add_symbol_to_db(self, stock_id, symbol):
        """
        Adds the sector details to db and update the stock with the sector id
        :param stock_id:
        :param symbol:
        :return:
        """
        try:
            stmt = select(StockName).where(StockName.id == stock_id)
            stock_obj = self.db_connection.execute(stmt).scalar()
            stock_obj.symbol = symbol
            self.db_connection.add(stock_obj)
            self.db_connection.commit()
        except Exception as e:
            logging.getLogger().error(e)
            self.db_connection.rollback()
