import requests
from bs4 import BeautifulSoup
from helpers.constants import Constants
import logging

from managers.bal.data_manager import DataManager
from managers.bal.price_action_data_manager import PriceActionDataManager
from models.schemas.responses import ScrapeMCResponse


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
        stocks = pa_data_manager.get_stocks_with_missing_symbol()
        for stock in pa_data_manager.get_stocks_with_missing_symbol():
            try:
                symbol = self.get_symbol(stock.details_url)
                if symbol is not None or symbol != "":
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
            response = self.session.get(stock_details_url, headers=Constants.USER_AGENT)
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
        except Exception as e:
            print(f"Couldn't get sector details. Error: {e}")
            return None
