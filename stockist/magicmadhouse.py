import logging

import urllib.parse
from bs4 import BeautifulSoup

from stockist.stockist import Stock, Stockist

log = logging.getLogger(__name__)


class Magicmadhouse(Stockist):
    def __init__(self, messengers):
        super().__init__(messengers=messengers)

        self.params = {
            "Filters": urllib.parse.unquote(
                "products:Booster%20Box,Booster%20Pack,Elite%20Trainer%20Box,Mini%20Album;language:English"
            ),
            "Page": 1,
        }

    base_url = "https://magicmadhouse.co.uk/pokemon/pokemon-sealed-product"
    name = "Magicmadhouse"

    def get_pokemon(self):
        all_found = []

        for page in range(1, 30):
            self.params["Page"] = page
            log.info(f"Scraping page {page} of {self.name}")

            response = self.scrape(url=self.base_url, payload=self.params)
            soup = BeautifulSoup(response.content, "html.parser")
            cards = soup.find_all("div", class_="kuProdWrap")

            if len(cards) == 0:
                log.info("Requests library failed, attempting with selenium")
                response = self.scrape_with_selenium(
                    url=self.base_url, payload=self.params
                )
                soup = BeautifulSoup(response, "html.parser")
                cards = soup.find_all("div", class_="kuProdWrap")

            if len(cards) == 0:
                break

            for card in cards:
                name = card.find_all(
                    "div",
                    attrs={"class": lambda e: e.startswith("kuName") if e else False},
                )
                stock = card.find_all(
                    "div",
                    attrs={
                        "class": lambda e: e.startswith("kuAddtocart") if e else False
                    },
                )
                price = card.find_all(
                    "div",
                    attrs={
                        "class": lambda e: e.startswith("kuSalePrice") if e else False
                    },
                )
                img = card.find_all(
                    "img",
                    attrs={
                        "class": lambda e: e.startswith("kuProdImg") if e else False
                    },
                )
                url = card.find_all(
                    "a",
                    attrs={
                        "class": lambda e: (
                            e.startswith("klevuProductClick") if e else False
                        )
                    },
                )

                if name and price and img and url:
                    name = name[0]
                    price = price[0]
                    img = img[0]
                    url = url[0]
                else:
                    continue

                found = {
                    "Colour": 0x0000FF,
                    "Title": name.text.strip(),
                    "Image": f"{img['src'][:img.find("c=")].strip()}",
                    "URL": f"{url['href'].strip()}",
                    "Price": price.text.strip(),
                    "Stock": "",
                    "Website": self.name,
                }

                if len(stock) > 0:
                    found["Colour"] = 0x00FF00
                    found["Stock"] = Stock.IN_STOCK.value

                else:
                    found["Colour"] = 0xFF0000
                    found["Stock"] = Stock.OUT_OF_STOCK.value
                all_found.append(found)

        return all_found
