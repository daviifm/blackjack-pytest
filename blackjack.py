import random
from collections import deque
from dataclasses import dataclass

RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
SUITS = ("♠", "♥", "♦", "♣")
RANK_VALUES = {
    **{str(n): n for n in range(2, 11)},
    "J": 10, "Q": 10, "K": 10, "A": 11,
}
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

    def __str__(self):
        return f"{self.rank}{self.suit}"


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


class Deck:
    def __init__(self, cards=None, rng=None):
        if cards is None:
            cards = (Card(rank, suit) for suit in SUITS for rank in RANKS)
        self.cards = deque(cards)
        self._rng = rng or random.Random()

    def shuffle(self):
        shuffled = list(self.cards)
        self._rng.shuffle(shuffled)
        self.cards = deque(shuffled)

    def draw(self):
        if not self.cards:
            raise IndexError("baralho vazio")
        return self.cards.popleft()

    def __len__(self):
        return len(self.cards)

class Game:
    def __init__(self, deck=None):
        if deck is None:
            deck = Deck()
            deck.shuffle()
        self.deck = deck
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self._player_stood = False

    def deal(self):
        for _ in range(2):
            self.player_hand.add(self.deck.draw())
            self.dealer_hand.add(self.deck.draw())

    def hit(self):
        self._require_player_turn()
        self.player_hand.add(self.deck.draw())

    def stand(self):
        self._require_player_turn()
        self._player_stood = True
        while self.dealer_hand.score < 17:
            self.dealer_hand.add(self.deck.draw())

    @property
    def is_over(self):
        return self._player_stood or self.player_hand.is_bust

    def winner(self):
        if not self.is_over:
            raise ValueError("a rodada ainda não terminou")
        player, dealer = self.player_hand, self.dealer_hand
        if player.is_bust:
            return "dealer"
        if dealer.is_bust:
            return "player"
        if player.score > dealer.score:
            return "player"
        if dealer.score > player.score:
            return "dealer"
        if player.is_blackjack and not dealer.is_blackjack:
            return "player"
        if dealer.is_blackjack and not player.is_blackjack:
            return "dealer"
        return None

    def table_view(self):
        dealer_cards = [str(card) for card in self.dealer_hand.cards]
        if not self.is_over and len(dealer_cards) > 1:
            dealer_cards[1] = "??"
        return {
            "player": [str(card) for card in self.player_hand.cards],
            "dealer": dealer_cards,
        }

    def _require_player_turn(self):
        if self.is_over:
            raise ValueError("a rodada já terminou")