import logging

from bs4 import BeautifulSoup

from stockist.stockist import Stock, Stockist

log = logging.getLogger(__name__)


class Pokedecks(Stockist):
    def __init__(self, messengers):
        super().__init__(messengers=messengers)

        self.params = None

    base_url = "https://pokedecks.uk/collections/pokemon-tcg"
    name = "Pokedecks"

    def get_pokemon(self):
        all_found = []

        for page in range(1, 2):
            self.params["page"] = page
            log.info(f"Scraping page {page} of {self.name}")

            response = self.scrape(url=self.base_url)
            soup = BeautifulSoup(response.content, "html.parser")
            cards = soup.find_all("li", class_="grid__item")

            if len(cards) == 0 and page < 3:
                log.info("Requests library failed, attempting with selenium")
                response = self.scrape_with_selenium(
                    url=self.base_url, payload=self.params
                )
                soup = BeautifulSoup(response, "html.parser")
                cards = soup.find_all("li", class_="grid__item")

            if len(cards) == 0:
                break

            for card in cards:
                name = card.find_all(
                    "a",
                    attrs={
                        "class": lambda e: (
                            e.startswith("full-unstyled-link") if e else False
                        )
                    },
                )

                name = name[0].text.strip()

                url = card.find_all(
                    "a",
                    attrs={
                        "class": lambda e: (
                            e.startswith("full-unstyled-link") if e else False
                        )
                    },
                )

                stock = card.find_all(
                    "span",
                    attrs={"class": lambda e: e.startswith("badge") if e else False},
                )

                price = card.find_all(
                    "span",
                    attrs={
                        "class": lambda e: (
                            e.startswith("price-item price-item--sale") if e else False
                        )
                    },
                )

                img = card.find_all(
                    "img",
                    attrs={
                        "class": lambda e: e.startswith("motion-reduce") if e else False
                    },
                )

                if name and price and img and url:
                    name = name
                    price = price[0]
                    img = img[0]
                    url = url[0]
                else:
                    continue

                found = {
                    "Colour": 0x00FF00,
                    "Title": name,
                    "Image": f"https:{img['src'][:img['src'].find("?")].strip()}",
                    "URL": f"https://pokedecks.uk{url['href'][:url['href'].find("?")].strip()}",
                    "Price": price.text.strip(),
                    "Stock": Stock.IN_STOCK.value,
                    "Website": self.name,
                }

                if len(stock) > 0:
                    if "OUT OF STOCK" in stock[0].text:
                        found["Colour"] = 0xFF0000
                        found["Stock"] = Stock.OUT_OF_STOCK.value

                all_found.append(found)

        return all_found
