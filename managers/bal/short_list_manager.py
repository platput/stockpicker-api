import logging
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from zoneinfo import ZoneInfo

from sqlalchemy import select

from models.db.schema import PriceAction, StockName, ShortlistedStock
from models.schemas.responses import ShortListResponse, ShortListedStock, ShortListedStocksResponse, PriceActions as PriceActionsORM


class ShortListManager:
    """
    ShortListManager class
    Use this to both create the shortlists and fetch the shortlists
    """

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def fetch_latest_short_list(self):
        """
        Fetch the latest shortlist from the database
        :return:
        """
        try:
            stmt = select(ShortlistedStock).limit(1).order_by(ShortlistedStock.conditions_met_on.desc())
            short_listed_stock = self.db_connection.execute(stmt).scalar()
            if short_listed_stock:
                latest_date = short_listed_stock.conditions_met_on
                latest_short_list_stmt = select(ShortlistedStock, StockName).where(
                    ShortlistedStock.conditions_met_on == latest_date,
                    StockName.id == ShortlistedStock.stock_id
                )
                short_listed_stocks_resp = []
                for short_list, stock in self.db_connection.execute(latest_short_list_stmt):
                    price_actions = []
                    price_action_ids = short_list.price_action_ids
                    for price_action_id in price_action_ids:
                        price_action = self.db_connection.execute(select(PriceAction).where(
                            PriceAction.id == price_action_id
                        )).scalar()
                        price_actions.append(PriceActionsORM.from_orm(price_action))
                    short_listed_stock_resp = ShortListedStock(
                        stock_name=stock.stock_name,
                        price_actions=price_actions
                    )
                    short_listed_stocks_resp.append(short_listed_stock_resp)
                return ShortListedStocksResponse(
                    success=True,
                    message="Shortlisted stocks fetched successfully",
                    shortlisted_stocks=short_listed_stocks_resp
                )
            else:
                return ShortListedStocksResponse(
                    success=False,
                    message="Failed to get the latest shortlist.",
                    shortlisted_stocks=[]
                )
        except Exception as e:
            logging.error(f'Error while fetching the short list for the day: {str(datetime.now())} Error: {type(e)}')
            return ShortListedStocksResponse(
                success=False,
                message="Failed to get the latest shortlist.",
                shortlisted_stocks=[]
            )

    def create_short_list(self):
        """
        Creates the shortlist for the current day
        :return:
        """
        # datetime.now(ZoneInfo('Asia/Kolkata'))
        current_date = datetime.now(ZoneInfo('Asia/Kolkata')).date()
        # day_minus_two = current_date - timedelta(days=2)
        # day_minus_three = current_date - timedelta(days=3)
        # Get the list of stock names and their price actions for day_minus_one
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
                        short_list_stock = ShortlistedStock(
                            id=uuid.uuid4(),
                            stock_id=price_action_one.stock_id,
                            price_action_ids=[str(price_action_one.id), str(price_action_two.id),
                                              str(price_action_three.id)],
                            conditions_met_on=price_action_one.price_date,
                        )
                        self.db_connection.add(short_list_stock)
            self.db_connection.commit()
            logging.info('Short list created for the day: {}'.format(current_date))
            return ShortListResponse(
                success=True,
                message=f"Successfully created the shortlist for the day: {str(current_date + timedelta(days=1))}. "
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