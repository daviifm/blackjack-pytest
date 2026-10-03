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
INITIAL_CARDS = 2
DEALER_STANDS_ON = 17
HIDDEN_CARD = "??"
HIDDEN_CARD_INDEX = 1  # a segunda carta da mesa fica oculta
PLAYER = "player"
DEALER = "dealer"


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

    @property
    def strength(self):
        """Chave de comparação: estourar perde de tudo; blackjack desempata 21."""
        if self.is_bust:
            return (-1, False)
        return (self.score, self.is_blackjack)


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
    """Uma rodada de blackjack: um jogador contra a mesa."""

    def __init__(self, deck=None):
        if deck is None:
            deck = Deck()
            deck.shuffle()
        self.deck = deck
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self._player_stood = False

    # --- ações do jogador ---
    def deal(self):
        for _ in range(INITIAL_CARDS):
            self.player_hand.add(self.deck.draw())
            self.dealer_hand.add(self.deck.draw())

    def hit(self):
        self._require_player_turn()
        self.player_hand.add(self.deck.draw())

    def stand(self):
        self._require_player_turn()
        self._player_stood = True
        self._dealer_play()

    # --- estado da rodada ---
    @property
    def is_over(self):
        return self._player_stood or self.player_hand.is_bust

    def winner(self):
        """PLAYER, DEALER ou None em caso de empate."""
        if not self.is_over:
            raise ValueError("a rodada ainda não terminou")
        player_strength = self.player_hand.strength
        dealer_strength = self.dealer_hand.strength
        if player_strength == dealer_strength:
            return None
        return PLAYER if player_strength > dealer_strength else DEALER

    # --- visibilidade ---
    def table_view(self):
        """A mesa vista pelo jogador: a segunda carta da mesa fica oculta até o fim."""
        dealer_cards = [str(card) for card in self.dealer_hand.cards]
        if not self.is_over and len(dealer_cards) > HIDDEN_CARD_INDEX:
            dealer_cards[HIDDEN_CARD_INDEX] = HIDDEN_CARD
        return {
            PLAYER: [str(card) for card in self.player_hand.cards],
            DEALER: dealer_cards,
        }

    # --- internos ---
    def _dealer_play(self):
        while self.dealer_hand.score < DEALER_STANDS_ON:
            self.dealer_hand.add(self.deck.draw())

    def _require_player_turn(self):
        if self.is_over:
            raise ValueError("a rodada já terminou")