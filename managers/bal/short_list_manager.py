import logging
import threading
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from zoneinfo import ZoneInfo
from sqlalchemy.sql import text

from sqlalchemy import select

from fastapi.responses import StreamingResponse
from managers.bal.excel_manager import ExcelManager
from managers.scrape_manager import ScrapeManager
from models.db.schema import PriceAction, StockName, ShortlistedStock, Sector
from models.schemas.responses import ShortListResponse, ShortListedStock, ShortListedStocksResponse, \
    PriceActions as PriceActionsORM


class ShortListManager:
    """
    ShortListManager class
    Use this to both create the shortlists and fetch the shortlists
    """

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def download_short_list(self, offset=0):
        """
        Create the Excel sheet on the fly and download the shortlist
        :param offset:
        :return:
        """
        shortlists = self.get_short_list(offset)
        excel_manager = ExcelManager()
        shortlist_excel = excel_manager.create_excel_file_for_shortlist(shortlists)
        headers = {
            'Content-Disposition': 'attachment; filename="shortlist.xlsx"'
        }
        return StreamingResponse(iter([shortlist_excel.getvalue()]), headers=headers)

    def get_short_list(self, offset=0):
        stmt = select(
            ShortlistedStock.conditions_met_on
        ).distinct().limit(1).offset(offset).order_by(ShortlistedStock.conditions_met_on.desc())
        short_listed_stock = self.db_connection.execute(stmt).scalar()
        if short_listed_stock:
            latest_date = short_listed_stock
            # latest_short_list_stmt = select(ShortlistedStock, StockName, Sector).where(
            #     ShortlistedStock.conditions_met_on == latest_date,
            #     StockName.id == ShortlistedStock.stock_id,
            #     ).join(Sector, Sector.id == StockName.sector_id, isouter=True)
            latest_short_list_stmt = text("""
            SELECT 
                shortlisted_stocks.price_action_ids, 
                shortlisted_stocks.is_intraday_allowed, 
                sectors.sector_name, 
                sectors.sector_url, 
                stock_names.symbol, 
                stock_names.stock_name, 
                stock_names.details_url, 
                counter.stock_name_repetitions,
                shortlisted_stocks.volume
            FROM shortlisted_stocks 
            JOIN stock_names ON shortlisted_stocks.stock_id = stock_names.id 
            LEFT OUTER JOIN sectors ON stock_names.sector_id  = sectors.id 
            JOIN( 
                SELECT stock_names.id as stock_id, count(stock_name) as stock_name_repetitions 
                FROM (shortlisted_stocks 
                JOIN stock_names on shortlisted_stocks.stock_id = stock_names.id) 
                WHERE shortlisted_stocks.conditions_met_on > NOW() - INTERVAL '1 MONTH' GROUP BY 1) 
                counter ON counter.stock_id = shortlisted_stocks.stock_id 
                WHERE conditions_met_on=:latest_date;
            """)
            short_listed_stocks_resp = []
            for short_list_details in self.db_connection.execute(
                    latest_short_list_stmt,
                    {"latest_date": latest_date}
            ).all():
                price_action_ids = short_list_details[0]
                is_intraday_allowed = short_list_details[1]
                volume = short_list_details[8]
                sector_name = short_list_details[2] if short_list_details[2] else None
                sector_url = short_list_details[3] if short_list_details[3] else None
                symbol = short_list_details[4] if short_list_details[4] else ""
                stock_name = short_list_details[5]
                details_url = short_list_details[6]
                stock_name_repetitions = short_list_details[7]
                price_actions = []
                for price_action_id in price_action_ids:
                    price_action = self.db_connection.execute(select(PriceAction).where(
                        PriceAction.id == price_action_id
                    )).scalar()
                    price_actions.append(PriceActionsORM.from_orm(price_action))
                short_listed_stock_resp = ShortListedStock(
                    stock_name=stock_name,
                    symbol=symbol,
                    is_intraday_allowed=is_intraday_allowed,
                    stock_url=details_url,
                    stock_sector_name=sector_name,
                    stock_sector_url=sector_url,
                    price_actions=price_actions,
                    stock_name_repetitions=stock_name_repetitions,
                    volume=volume
                )
                short_listed_stocks_resp.append(short_listed_stock_resp)
            return short_listed_stocks_resp
        else:
            return []

    def fetch_short_list(self, offset=0):
        """
        Fetch the latest shortlist from the database
        :return:
        """
        try:
            shortlists = self.get_short_list(offset)
            if shortlists:
                return ShortListedStocksResponse(
                    success=True,
                    message="Shortlisted stocks fetched successfully",
                    shortlisted_stocks=shortlists
                )
            else:
                return ShortListedStocksResponse(
                    success=False,
                    message="Failed to get the shortlist.",
                    shortlisted_stocks=[]
                )

        except Exception as e:
            logging.error(f'Error while fetching the short list for the day: {str(datetime.now())} Error: {type(e)}')
            return ShortListedStocksResponse(
                success=False,
                message="Failed to get the shortlist.",
                shortlisted_stocks=[]
            )

    def create_short_list(self):
        """
        Creates the shortlist for the current day
        :return:
        """
        # Get the list of allowed intraday stocks
        allowed_intraday_stocks = ScrapeManager.get_intraday_allowed_stocks()
        # datetime.now(ZoneInfo('Asia/Kolkata'))
        current_date = datetime.now(ZoneInfo('Asia/Kolkata')).date()
        # day_minus_two = current_date - timedelta(days=2)
        # day_minus_three = current_date - timedelta(days=3)
        # Get the list of stock names and their price actions for day_minus_one
        conditions_met_on = None
        try:
            stock_names_day_one, day_one = self.__get_stocks_for_the_day(current_date)
            next_date = day_one - timedelta(days=1)
            stock_names_day_two, day_two = self.__get_stocks_for_the_day(next_date)
            next_date = day_two - timedelta(days=1)
            stock_names_day_three, day_three = self.__get_stocks_for_the_day(next_date)
            stocks_present_in_last_three_days = stock_names_day_one. \
                intersection(stock_names_day_two). \
                intersection(stock_names_day_three)
            short_listed_stocks = []
            for stock in stocks_present_in_last_three_days:
                # Get the price actions for three days
                stmt_one = select(PriceAction).where(
                    StockName.stock_name == stock,
                    PriceAction.price_date == day_one,
                    PriceAction.stock_id == StockName.id,
                )
                stmt_two = select(PriceAction).where(
                    StockName.stock_name == stock,
                    PriceAction.price_date == day_two,
                    PriceAction.stock_id == StockName.id,
                )
                stmt_three = select(PriceAction).where(
                    StockName.stock_name == stock,
                    PriceAction.price_date == day_three,
                    PriceAction.stock_id == StockName.id,
                )
                price_action_one = self.db_connection.execute(stmt_one).scalar()
                price_action_two = self.db_connection.execute(stmt_two).scalar()
                price_action_three = self.db_connection.execute(stmt_three).scalar()
                if price_action_one and price_action_two and price_action_three:
                    # Remove the hours which didn't see any price gain,
                    # this means, in the db row, it will have the value of zero
                    price_action_list_day_one = self.__get_sorted_price_action_list_with_only_gains(price_action_one)
                    price_action_list_day_two = self.__get_sorted_price_action_list_with_only_gains(price_action_two)
                    price_action_list_day_three = self.__get_sorted_price_action_list_with_only_gains(
                        price_action_three)
                    # Compare the price actions for the last three days
                    # Conditions
                    # 1. If the start price for the day_three is less than or equal to the end price for the day_three
                    # 2. If the end price for the day_three is less than or equal to the start price for the day_two
                    # 3. If the start price for the day_two is less than or equal to the end price for the day_two
                    # 4. If the end price for the day_two is less than or equal to the start price for the day_one
                    # 5. If the start price for the day_one is less than or equal to the end price for the day_one
                    if price_action_list_day_one[-1].get("end") >= price_action_list_day_one[0].get("start") >= \
                            price_action_list_day_two[-1].get("end") >= price_action_list_day_two[0].get("start") >= \
                            price_action_list_day_three[-1].get("end") >= price_action_list_day_three[0].get("start"):
                        short_listed_stocks.append(stock)
                        # Save shortlisted stocks into db
                        is_allowed_for_intraday_trading = self.__check_if_intraday_is_allowed(
                            price_action_one.stock_id,
                            allowed_intraday_stocks
                        )
                        short_list_stock = ShortlistedStock(
                            id=uuid.uuid4(),
                            stock_id=price_action_one.stock_id,
                            is_intraday_allowed=is_allowed_for_intraday_trading,
                            price_action_ids=[str(price_action_one.id), str(price_action_two.id),
                                              str(price_action_three.id)],
                            conditions_met_on=price_action_one.price_date,
                        )
                        conditions_met_on = price_action_one.price_date
                        self.db_connection.add(short_list_stock)
            self.db_connection.commit()
            logging.info('Short list created for the day: {}'.format(current_date))
            if conditions_met_on:
                volumes_thread = threading.Thread(
                    target=self.__get_volumes_for_shortlisted_stocks,
                    args=(conditions_met_on,)
                )
                volumes_thread.start()
            return ShortListResponse(
                success=True,
                message=f"Successfully created the shortlist with the data up to: {str(current_date)}."
                        f"Shortlisted {len(short_listed_stocks)} stocks",
            )
        except IntegrityError as e:
            logging.getLogger().error(e)
            if "UniqueViolation" in str(e):
                return ShortListResponse(
                    success=False,
                    message=f"Short list already exists for the day, skipping the creation."
                )
            else:
                return ShortListResponse(success=False, message=f"Failed to create shortlist. {e}")
        except Exception as e:
            logging.error(f'Error while creating short list for the day: {current_date} Error: {type(e)}')
            return ShortListResponse(success=False, message="Failed to create shortlist.")

    def __get_stocks_for_the_day(self, current_date) -> (set, datetime):
        """
        Get the list of stock names and their price actions for the current date
        :param current_date:
        :return:
        """
        stock_names_day = set()
        # This while loop should break if it iterates over for more than 10 times
        # If the stockmarket has remained closed for 10 days that means, world war 3 has begun ;-)
        iteration_count = 0
        while True:
            iteration_count += 1
            if iteration_count > 10:
                logging.getLogger().error("The stock market has remained closed for 10 days.")
                break
            stmt_one = select(StockName, PriceAction).where(
                StockName.id == PriceAction.stock_id,
                PriceAction.price_date == current_date.strftime('%Y-%m-%d')
            )
            for stock in self.db_connection.execute(stmt_one).scalars():
                stock_names_day.add(stock.stock_name)
            if len(stock_names_day) > 0:
                break
            else:
                current_date = current_date - timedelta(days=1)
        return stock_names_day, current_date

    @staticmethod
    def __get_sorted_price_action_list_with_only_gains(price_action) -> list:
        """
        Remove the hours which didn't see any price gain,
        :param price_action:
        :return:
        """
        price_actions = []
        if price_action.hour_1_start > 0:
            price_actions.append({"start": price_action.hour_1_start, "end": price_action.hour_1_end})
        if price_action.hour_2_start > 0:
            price_actions.append({"start": price_action.hour_2_start, "end": price_action.hour_2_end})
        if price_action.hour_3_start > 0:
            price_actions.append({"start": price_action.hour_3_start, "end": price_action.hour_3_end})
        if price_action.hour_4_start > 0:
            price_actions.append({"start": price_action.hour_4_start, "end": price_action.hour_4_end})
        if price_action.hour_5_start > 0:
            price_actions.append({"start": price_action.hour_5_start, "end": price_action.hour_5_end})
        if price_action.hour_6_start > 0:
            price_actions.append({"start": price_action.hour_6_start, "end": price_action.hour_6_end})
        if price_action.hour_7_start > 0:
            price_actions.append({"start": price_action.hour_7_start, "end": price_action.hour_7_end})
        return price_actions

    def __check_if_intraday_is_allowed(self, stock_id, allowed_intraday_stocks) -> bool:
        """
        Check if the stock is allowed for intraday trading
        :param stock_id:
        :param allowed_intraday_stocks:
        :return:
        """
        # First get the stock symbol from db
        # If it doesn't exist, then it is not allowed
        # If it exists but doesn't appear in the allowed list, then it is not allowed
        stmt = select(StockName).where(StockName.id == stock_id)
        if stock := self.db_connection.execute(stmt).scalar():
            if stock_symbol := stock.symbol:
                if stock_symbol in allowed_intraday_stocks:
                    return True
        return False

    def __get_volumes_for_shortlisted_stocks(self, conditions_met_on):
        """
        Retrieves the volumes of each shortlisted stock and saves it in the db
        :param conditions_met_on:
        :return:
        """
        try:
            scrape_manager = ScrapeManager(urls_to_scrape=None)
            short_list_stmt = text("""
            SELECT 
                shortlisted_stocks.id, 
                stock_names.details_url
            FROM shortlisted_stocks 
            JOIN stock_names ON shortlisted_stocks.stock_id = stock_names.id 
            WHERE shortlisted_stocks.conditions_met_on=:conditions_met_on;
            """)
            shortlisted_stocks = self.db_connection.execute(
                short_list_stmt,
                {"conditions_met_on": conditions_met_on}
            ).all()
            for short_list_details in shortlisted_stocks:
                shortlist_id = short_list_details[0]
                if stock_url := short_list_details[1]:
                    if "http://" in stock_url:
                        stock_url = stock_url.replace("http://", "https://")
                    volume = scrape_manager.get_volume_from_stock_details_url(stock_url)
                    short_list_stock_stmt = select(ShortlistedStock).where(ShortlistedStock.id == shortlist_id)
                    short_list_stock = self.db_connection.execute(short_list_stock_stmt).scalar()
                    short_list_stock.volume = volume
                    self.db_connection.add(short_list_stock)
            self.db_connection.commit()
        except Exception as e:
            logging.getLogger().error(f"Fetching volume failed with error: {e}")
