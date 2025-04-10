import logging

from bs4 import BeautifulSoup

from stockist.stockist import Stock, Stockist

log = logging.getLogger(__name__)


class Chaoscards(Stockist):
    def __init__(self, messengers):
        super().__init__(messengers=messengers)

        self.params = None

    base_url = "https://www.chaoscards.co.uk/brand/pokemon/sort/release-date-newest-first/show/64-products/oos/yes/cat/booster-boxes-pokemon,booster-packs-pokemon,collection-boxes-pokemon,elite-trainer-boxes-pokemon/page/"
    name = "Chaoscards"

    def get_pokemon(self):
        all_found = []

        for page in range(1, 2):

            url = f"{self.base_url}{page}"

            response = self.scrape(url=url, payload=self.params)
            soup = BeautifulSoup(response.content, "html.parser")
            cards = soup.find_all("div", class_="prod-el__wrapper")

            if len(cards) == 0:
                log.info("Requests library failed, attempting with selenium")
                response = self.scrape_with_selenium(url=url, payload=self.params)
                soup = BeautifulSoup(response, "html.parser")
                cards = soup.find_all("div", class_="prod-el__wrapper")

            if len(cards) == 0:
                break

            for card in cards:
                name = card.find_all(
                    "h6",
                    attrs={
                        "class": lambda e: (
                            e.startswith("prod-el__title") if e else False
                        )
                    },
                )
                stock = card.find_all(
                    "p",
                    attrs={
                        "class": lambda e: (
                            e.startswith("prod-el__availability") if e else False
                        )
                    },
                )
                price = card.find_all(
                    "span",
                    attrs={
                        "class": lambda e: (
                            e.startswith("prod-el__pricing-price") if e else False
                        )
                    },
                )
                img = card.find_all(
                    "img",
                    attrs={
                        "class": lambda e: (
                            e.startswith("prod-el__image") if e else False
                        )
                    },
                )
                url = card.find_all(
                    "a",
                    attrs={
                        "class": lambda e: e.startswith("prod-el__link") if e else False
                    },
                )

                if name and stock and price and img and url:
                    name = name[0]
                    stock = stock[0]
                    price = price[0]
                    img = img[0]["src"].strip()
                    img = img[: img.find("v=")]
                    url = url[0]
                else:
                    continue

                found = {
                    "Colour": 0x0000FF,
                    "Title": name.text.strip(),
                    "Image": f"{img}",
                    "URL": f"https://www.chaoscards.co.uk/{url['href'].strip()}",
                    "Price": price.text.strip(),
                    "Stock": "",
                    "Website": self.name,
                }

                if (
                    stock.text.strip() == "Out of stock"
                    or stock.text.strip() == "Coming soon"
                ):
                    found["Colour"] = 0xFF0000
                    found["Stock"] = Stock.OUT_OF_STOCK.value
                else:
                    found["Colour"] = 0x00FF00
                    found["Stock"] = Stock.IN_STOCK.value
                all_found.append(found)

        return all_found
