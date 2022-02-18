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
                    stock_details = {
                        Constants.TIME_PERIOD: time_period,
                        Constants.STARTING_PRICE: starting_price,
                        Constants.ENDING_PRICE: ending_price,
                    }
                    if self.scraped_data.get(stock_name):
                        self.scraped_data[stock_name].append(stock_details)
                    else:
                        self.scraped_data[stock_name] = [stock_details]




