import logging
from typing import Union

from stockist.chaoscards import Chaoscards
from stockist.chiefcards import Chiefcards
from stockist.hillscards import Hillscards
from stockist.magicmadhouse import Magicmadhouse

log = logging.getLogger(__name__)


class StockistManager:
    def __init__(self, messengers) -> None:
        self.all_stockists: list[
            Union[
                Chiefcards,
                Chaoscards,
                Hillscards,
                Magicmadhouse,
            ]
        ] = []
        self.messengers = messengers
        self.relationships: dict[str, list[str]] = {}

        for messenger in messengers.all_messengers:
            for stockist in messenger.stockists:
                if stockist not in self.relationships:
                    self.relationships[stockist] = []
                if messenger.name not in self.relationships[stockist]:
                    self.relationships[stockist].append(messenger.name)

        for stockist in self.relationships:
            messengers = self.relationships[stockist]
            if stockist == "chiefcards.co.uk":
                chiefcards = Chiefcards(messengers=messengers)
                self.all_stockists.append(chiefcards)
                log.info(f"Now tracking {stockist}")
            elif stockist == "chaoscards.co.uk":
                chaoscards = Chaoscards(messengers=messengers)
                self.all_stockists.append(chaoscards)
                log.info(f"Now tracking {stockist}")
            elif stockist == "hillscards.co.uk":
                hillscards = Hillscards(messengers=messengers)
                self.all_stockists.append(hillscards)
                log.info(f"Now tracking {stockist}")
            elif stockist == "magicmadhouse.co.uk":
                magicmadhouse = Magicmadhouse(messengers=messengers)
                self.all_stockists.append(magicmadhouse)
                log.info(f"Now tracking {stockist}")

        stockist_check = self.check_for_one_stockist()
        if stockist_check:
            stockists = ", ".join([stockist.name for stockist in self.all_stockists])
            log.info(f"Now scraping {len(self.all_stockists)} site(s): {stockists}")

    def check_for_one_stockist(self):
        if len(self.all_stockists) < 1:
            log.error("No stockists were set to be scraped")
            return False
        return True
