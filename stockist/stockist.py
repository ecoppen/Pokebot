import logging
import time
import urllib.error
from enum import Enum
from typing import Any, Union

import chromedriver_autoinstaller
from seleniumbase import SB

from stockist.useragents import UserAgent
from stockist.utils import send_public_request

log = logging.getLogger(__name__)

user_agents = UserAgent()
user_agent_list = user_agents.get_user_agents()


class Stock(Enum):
    DELISTED = "Delisted"
    IN_STOCK = "In stock"
    OUT_OF_STOCK = "Out of Stock"
    PRICE_CHANGE = "Price change"


class Stockist:
    def __init__(self, messengers) -> None:
        self.params: dict[str, Any] = {}
        self.messengers = messengers

    base_url: Union[str, None] = None
    name: Union[str, None] = None

    def scrape(self, url, payload):
        return send_public_request(url=url, payload=payload)

    def scrape_with_selenium(self, url, payload):
        try:
            chromedriver_autoinstaller.install()
        except urllib.error.URLError as e:
            log.error(f"Error with chromedriver auto-installation - {e}")
            return ""

        with SB(uc=True) as sb:
            try:
                sb.uc_open_with_reconnect(url, reconnect_time=4)
            except Exception as e:
                log.error(f"Selenium exception: {e}")
                return ""
            time.sleep(5)
            html = sb.get_page_source()
        return html

    def get_pokemon(self):
        pass
