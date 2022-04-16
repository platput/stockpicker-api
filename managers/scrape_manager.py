import json
from datetime import timedelta

import requests
from bs4 import BeautifulSoup

from helpers.constants import Constants
import logging
import pandas as pd

from managers.bal.data_manager import DataManager
from managers.bal.price_action_data_manager import PriceActionDataManager
from managers.dal.redis_manager import RedisManager
from models.schemas.responses import ScrapeMCResponse, SectorialIndex, SectorialIndicesResponse


class ScrapeManager:
    session = requests.Session()

    def __init__(self, urls_to_scrape):
        self.urls_to_scrape = urls_to_scrape
        self.scraped_data = {}

    def fetch_scraped_data(self, db_session):
        for time_period, link in self.urls_to_scrape.items():
            count = 0
            while count < 3:
                try:
                    self.scrape_url(time_period, link)
                    break
                except ConnectionError as ce:
                    count += 1
                    if count == 3:
                        logging.error(f"Couldn't connect to {link}. Error: {ce}\n")
                        raise ce
        formatted_data = DataManager.format_scrapped_mc_data(self.scraped_data)
        # Update the database with the scraped data
        pa_data_manager = PriceActionDataManager(db_session)
        pa_data_manager.add_price_actions_to_db(formatted_data)
        # Add the missing sector details to the database
        # This is being done here because this has to be fetched after going to each individual stock's page
        # So considering we are going through all the price action hours pages, it's better to do it once
        # after the price action pages are done scraping. The sector details might be already available for
        # any give stock in the database.
        for stock in pa_data_manager.get_stocks_with_missing_sector_details():
            sector_details = self.get_sector_details(stock.details_url)
            if sector_details.get(Constants.SECTOR_NAME) is None or sector_details.get(Constants.SECTOR_URL) is None:
                continue
            pa_data_manager.add_sector_details_to_db(
                stock.id,
                sector_details.get(Constants.SECTOR_NAME),
                sector_details.get(Constants.SECTOR_URL)
            )
        # # Adding the missing symbols to the stocks table
        # for stock in pa_data_manager.get_stocks_with_missing_symbol():
        #     symbol = self.get_symbol(stock.details_url)
        #     if symbol is not None or symbol != "":
        #         pa_data_manager.add_symbol_to_db(
        #             stock.id,
        #             symbol,
        #         )
        return ScrapeMCResponse(success=True, message="Successfully scraped data")

    def scrape_url(self, time_period, link):
        response = self.session.get(link, headers=Constants.USER_AGENT)
        if response.status_code == 200:
            soup_content = BeautifulSoup(response.content, Constants.HTML_PARSER)
            stocks_table = soup_content.find('div', attrs={'class': 'bsr_table'})
            for row in stocks_table.find_all('tr'):
                columns = row.find_all('td')
                if columns:
                    stock_name = columns[0].find('span', attrs={'class': 'gld13 disin'}).a.text
                    stock_name = stock_name.replace(' ', '-').strip().lower()
                    starting_price = columns[1].text
                    ending_price = columns[2].text
                    price_action = {
                        Constants.TIME_PERIOD: time_period,
                        Constants.STARTING_PRICE: starting_price,
                        Constants.ENDING_PRICE: ending_price,
                    }
                    if self.scraped_data.get(stock_name):
                        self.scraped_data[stock_name][Constants.PRICE_ACTION].append(price_action)
                    else:
                        stock_details_url = columns[0].find('span', attrs={'class': 'gld13 disin'}).a.get('href')
                        self.scraped_data[stock_name] = {
                            Constants.PRICE_ACTION: [price_action],
                            Constants.STOCK_DETAILS_URL: stock_details_url
                        }

    def get_sector_details(self, stock_details_url):
        try:
            response = self.session.get(stock_details_url, headers=Constants.USER_AGENT)
            if response.status_code == 200:
                soup_content = BeautifulSoup(response.content, Constants.HTML_PARSER)
                stocks_name = soup_content.find('div', attrs={'id': 'stockName'})
                sector_name = stocks_name.find('span').strong.a.text
                sector_url = stocks_name.find('span').strong.a.get('href')
                return {
                    Constants.SECTOR_NAME: sector_name.strip(),
                    Constants.SECTOR_URL: sector_url,
                }
            else:
                logging.getLogger().warning(
                    f"Couldn't get sector details for {stock_details_url}. Error: {response.status_code}"
                )
                return {
                    Constants.SECTOR_NAME: None,
                    Constants.SECTOR_URL: None,
                }
        except Exception as e:
            logging.getLogger().warning(f"Couldn't get sector details for {stock_details_url}. Error: {e}")
            return {
                Constants.SECTOR_NAME: None,
                Constants.SECTOR_URL: None,
            }

    def fetch_symbols_and_update(self, db_session):
        # Get all the stocks with empty symbols
        pa_data_manager = PriceActionDataManager(db_session)
        for stock in pa_data_manager.get_stocks_with_missing_symbol():
            try:
                symbol = self.get_symbol(stock.details_url)
                pa_data_manager.add_symbol_to_db(
                    stock.id,
                    symbol,
                )
            except Exception as e:
                logging.getLogger().error(f"Error while fetching symbol for {stock.stock_name}: {e}")
        return ScrapeMCResponse(success=True, message="Successfully scraped data")

    def get_symbol(self, stock_details_url):
        try:
            if stock_details_url is None:
                return None
            response = self.session.get(stock_details_url.replace("http://", "https://"), headers=Constants.USER_AGENT, timeout=5)
            if response.status_code == 200:
                soup_content = BeautifulSoup(response.content, Constants.HTML_PARSER)
                symbol_section = soup_content.find('div', attrs={'id': 'company_info'})
                details_section = symbol_section.findAll('li')
                for column in details_section:
                    if column.h3 is not None:
                        if column.h3.text == 'Details':
                            rows = column.findAll('li')
                            for row in rows:
                                if row.span is not None:
                                    if 'NSE' in row.span.text:
                                        if row.p is not None and row.p.text is not None:
                                            if row.p.text.strip() != "":
                                                return row.p.text
                return None
            elif response.status_code == 404:
                return None
            else:
                return 0
        except Exception as e:
            logging.getLogger().error(f"Couldn't get stock symbol. Error: {e}")
            return 0

    @staticmethod
    def get_intraday_allowed_stocks():
        allowed_mis_stocks = pd.read_csv(
            Constants.GOOGLE_DOC_CSV_EXPORT_READY_URL.format(doc_id=Constants.DOC_ID, sheet_id=Constants.SHEET_ID),
        )
        return [item for item in allowed_mis_stocks["Stocks allowed for MIS"]]

    def fetch_sectorial_indices(self, sector_details_list):
        # Checks if the data exists in redis
        # If it exists, reads it and returns it
        # If not, it needs to be scrapped
        # Gets the sectorial indices from money control
        # Create the list of objects with all the details
        # add the data to redis
        try:
            redis_manager = RedisManager()
            conn = redis_manager.client
            value = conn.get(Constants.SECTORIAL_INDICES_KEY)
            if value is not None:
                unique_indices = json.loads(value.decode('utf-8'))
            else:
                sectorial_indices = []
                for sector in sector_details_list:
                    response = self.session.get(sector.sector_details_url, headers=Constants.USER_AGENT)
                    if response.status_code == 200:
                        soup_content = BeautifulSoup(response.content, Constants.HTML_PARSER)
                        if ticker := soup_content.find('div', attrs={'class': 'secdrop_bg clearfix indian_indices_element'}):
                            if inside_ticker := ticker.find('div', attrs={'class': 'customDdl lstpg ML10 FL'}):
                                if index_price_details := inside_ticker.find('span', attrs={'class': 'selectedText'}):
                                    index_price_text = index_price_details.text.strip()
                                    market_movement_up = inside_ticker.find('span', attrs={'class': 'mk_txt up'})
                                    market_movement_down = inside_ticker.find('span', attrs={'class': 'mk_txt down'})
                                    market_movement_no_change = inside_ticker.find('span', attrs={'class': 'mk_txt'})
                                    if market_movement_up is not None:
                                        positive_movement_flag = True
                                        market_movement = market_movement_up.text.strip()
                                    elif market_movement_down is not None:
                                        positive_movement_flag = False
                                        market_movement = market_movement_down.text.strip()
                                    else:
                                        positive_movement_flag = False
                                        market_movement = market_movement_no_change.text.strip()
                                    index_price_and_name = index_price_text.split(market_movement)[0].strip()
                                    index_price = index_price_and_name.split(" ")[-1]
                                    index_name = index_price_and_name.split(index_price)[0].strip()
                                    sectorial_index = {
                                        "sector_name": sector.sector_name,
                                        "sector_url": sector.sector_details_url,
                                        "positive_movement": positive_movement_flag,
                                        "market_movement": market_movement,
                                        "index_name": index_name,
                                        "index_value": index_price,
                                    }
                                    sectorial_indices.append(sectorial_index)
                unique_indices = {}
                for sectorial_index in sectorial_indices:
                    market_movement = sectorial_index.get("market_movement")
                    positive_movement = sectorial_index.get("positive_movement")
                    index_name = sectorial_index.get("index_name")
                    index_value = sectorial_index.get("index_value")
                    sector_name = sectorial_index.get("sector_name")
                    sector_url = sectorial_index.get("sector_url")
                    if index_name not in unique_indices:
                        unique_indices[sectorial_index.get("index_name")] = {
                            "positive_movement": positive_movement,
                            "market_movement": market_movement,
                            "index_name": index_name,
                            "index_value": index_value,
                            "sectors": [{
                                "sector_name": sector_name,
                                "sector_url": sector_url,
                            }]
                        }
                    else:
                        unique_indices[sectorial_index.get("index_name")]["sectors"].append({
                            "sector_name": sector_name,
                            "sector_url": sector_url,
                        })
                conn.setex(
                    Constants.SECTORIAL_INDICES_KEY,
                    timedelta(hours=1),
                    value=json.dumps(unique_indices)
                )
        except Exception as e:
            logging.getLogger().error(f"Error while fetching sectorial indices: {e}")
            raise
        return SectorialIndicesResponse(
            success=True,
            message="Sectorial indices fetched successfully",
            sectorial_indices=[SectorialIndex(**sectorial_index) for _, sectorial_index in unique_indices.items()]
        )
