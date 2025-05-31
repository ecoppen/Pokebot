import logging

from bs4 import BeautifulSoup

from stockist.stockist import Stock, Stockist

log = logging.getLogger(__name__)


class Ultracards(Stockist):
    def __init__(self, messengers):
        super().__init__(messengers=messengers)

        self.params = None

    base_url = "https://www.ultracards.co.uk/search?q=pokemon&type=products&collections=Pokemon:+Booster+Boxes,Pokemon:+Elite+Trainer+Box&page="
    name = "Ultracards"

    def get_pokemon(self):
        all_found = []

        for page in range(1, 6):

            url = f"{self.base_url}{page}"

            response = self.scrape(url=url, payload=self.params)
            soup = BeautifulSoup(response.content, "html.parser")
            cards = soup.find_all("li", attrs={"data-hook": "grid-layout-item"})

            if len(cards) == 0:
                log.info("Requests library failed, attempting with selenium")
                response = self.scrape_with_selenium(url=url, payload=self.params)
                soup = BeautifulSoup(response, "html.parser")
                cards = soup.find_all("li", attrs={"data-hook": "grid-layout-item"})

            if len(cards) == 0:
                break

            for card in cards:
                name = card.find_all(
                    "a",
                    attrs={"data-hook": "item-title"},
                )
                stock = card.find_all(
                    "button",
                    attrs={
                        "data-hook": "add-to-cart-button"
                    },
                )
                price = card.find_all(
                    "span",
                    attrs={
                        "data-hook": "item-price",
                    },
                )
                img = card.find_all(
                    "img",
                )
                url = card.find_all(
                    "a",
                    attrs={"data-hook": "item-title"},
                )

                if name and stock and price and img and url:
                    name = name[0]
                    stock = stock[0]
                    price = price[0]
                    img = img[0]["src"].strip()
                    url = url[0]
                else:
                    continue

                found = {
                    "Colour": 0x0000FF,
                    "Title": name.text.strip(),
                    "Image": f"{img}",
                    "URL": f"{url['href'].strip()}",
                    "Price": price.text.strip(),
                    "Stock": "",
                    "Website": self.name,
                }

                if stock.text.strip() == "Out of Stock":
                    found["Colour"] = 0xFF0000
                    found["Stock"] = Stock.OUT_OF_STOCK.value
                else:
                    found["Colour"] = 0x00FF00
                    found["Stock"] = Stock.IN_STOCK.value
                all_found.append(found)

        return all_found
