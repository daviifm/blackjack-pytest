from dataclasses import dataclass

RANK_VALUES = {**{str(n): n for n in range(2, 11)}, "J": 10, "Q": 10, "K": 10, "A": 11}
BLACKJACK = 21
ACE_ADJUSTMENT = 10  # um ás passa de 11 para 1, para separar os ases (ou aces?  ou azes?) em soft e hard


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def value(self):
        return RANK_VALUES[self.rank]

    @property
    def is_ace(self):
        return self.rank == "A"


class Hand:
    def __init__(self, cards=None):
        self.cards = list(cards or [])

    def add(self, card):
        self.cards.append(card)

    @property
    def score(self):
        total = sum(card.value for card in self.cards)
        soft_aces = sum(card.is_ace for card in self.cards)
        while total > BLACKJACK and soft_aces:
            total -= ACE_ADJUSTMENT
            soft_aces -= 1
        return total

    @property
    def is_bust(self):
        return self.score > BLACKJACK

    @property
    def is_blackjack(self):
        return len(self.cards) == 2 and self.score == BLACKJACK