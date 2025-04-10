import logging

from bs4 import BeautifulSoup

from stockist.stockist import Stock, Stockist

log = logging.getLogger(__name__)


class Hillscards(Stockist):
    def __init__(self, messengers):
        super().__init__(messengers=messengers)

        self.params = {
            "base_url": "trading-card-games-c78%2Fsealed-products-c92%2Fpokemon-trading-card-game-m2",
            "page_type": "productlistings",
            "page_variant": "show",
            "parent_category_id[]": "92",
            "manufacturer_id[]": "2",
            "all_upcoming_flag[]": "78",
            "keywords": "",
            "show": "48",
            "sort": "7",
            "tags_id[]": ["368", "376", "379", "382"],
            "child_categories[]": "92|97|98|99|100|101|102",
            "transport": "html",
        }

    base_url = "https://www.hillscards.co.uk/ajax/getProductListings"
    name = "Hillscards"

    def get_pokemon(self):
        all_found = []

        for page in range(1, 6):
            self.params["page"] = page
            log.info(f"Scraping page {page} of {self.name}")

            response = self.scrape(url=self.base_url, payload=self.params)
            soup = BeautifulSoup(response.content, "html.parser")
            cards = soup.find_all("li", class_="col l-col-8 m-col-third s-col-16")

            if len(cards) == 0 and page < 3:
                log.info("Requests library failed, attempting with selenium")
                response = self.scrape_with_selenium(
                    url=self.base_url, payload=self.params
                )
                soup = BeautifulSoup(response, "html.parser")
                cards = soup.find_all("li", class_="col l-col-8 m-col-third s-col-16")

            if len(cards) == 0:
                break

            for card in cards:
                name = card.find_all(
                    "div",
                    attrs={
                        "class": lambda e: (
                            e.startswith("product__details__title") if e else False
                        )
                    },
                )
                url = name[0].find("a")
                name = url.text.replace("Pokemon Trading Card Game", "").strip()

                stock = card.find_all(
                    "a",
                    attrs={
                        "class": lambda e: (
                            e.startswith("product__options__view") if e else False
                        )
                    },
                )

                stock = stock[0].find("span").text.strip()

                price = card.find_all(
                    "span",
                    attrs={"class": lambda e: e.startswith("GBP") if e else False},
                )

                price = price[0]

                img = card.find_all(
                    "div",
                    attrs={
                        "class": lambda e: (
                            e.startswith("product__image") if e else False
                        )
                    },
                )
                img = img[0].find("img")

                if name and stock and price and img and url:
                    name = name
                    stock = stock
                    price = price
                    img = img
                    url = url
                else:
                    continue

                found = {
                    "Colour": 0x0000FF,
                    "Title": name,
                    "Image": f"https://www.hillscards.co.uk{img['data-src'].strip()}",
                    "URL": f"https://www.hillscards.co.uk{url['href'].strip()}",
                    "Price": price.text.strip(),
                    "Stock": "",
                    "Website": self.name,
                }

                if stock.strip() == "Buy":
                    found["Colour"] = 0x00FF00
                    found["Stock"] = Stock.IN_STOCK.value
                else:
                    found["Colour"] = 0xFF0000
                    found["Stock"] = Stock.OUT_OF_STOCK.value
                all_found.append(found)

        return all_found
