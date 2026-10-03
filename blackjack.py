class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    @property
    def value(self):
        if self.rank == "A":
            return 11
        if self.rank in ("J", "Q", "K"):
            return 10
        return int(self.rank)


class Hand:
    def __init__(self, cards=None):
        self.cards = list(cards or [])

    def add(self, card):
        self.cards.append(card)

    @property
    def score(self):
        total = sum(c.value for c in self.cards)
        aces = sum(1 for c in self.cards if c.rank == "A")
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    @property
    def is_bust(self):
        return self.score > 21

    @property
    def is_blackjack(self):
        return len(self.cards) == 2 and self.score == 21