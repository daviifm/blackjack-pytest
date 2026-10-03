import pytest
import random
from blackjack import Card, Deck, Hand


def hand(*ranks):
    return Hand([Card(rank, "♠") for rank in ranks])


@pytest.mark.parametrize(
    "rank, value",
    [("2", 2), ("7", 7), ("10", 10), ("J", 10), ("Q", 10), ("K", 10), ("A", 11)],
)
def test_valor_da_carta(rank, value):
    assert Card(rank, "♠").value == value


def test_mao_soma_valores_das_cartas():
    assert hand("7", "9").score == 16


def test_adicionar_carta_atualiza_pontuacao():
    h = hand("2")
    h.add(Card("3", "♥"))
    assert h.score == 5


def test_as_conta_1_para_evitar_estouro():
    assert hand("A", "K", "5").score == 16


def test_dois_ases_valem_12():
    assert hand("A", "A").score == 12


def test_mao_estourada():
    assert hand("K", "Q", "5").is_bust
    assert not hand("K", "Q").is_bust


def test_blackjack_natural_so_com_duas_cartas():
    assert hand("A", "K").is_blackjack
    assert not hand("7", "7", "7").is_blackjack

# Daqui em diante, começa o segundo teste

def test_carta_como_texto():
    assert str(Card("Q", "♥")) == "Q♥"


def test_baralho_padrao_tem_52_cartas_unicas():
    deck = Deck()
    assert len(deck) == 52
    assert len({str(c) for c in deck.cards}) == 52


def test_comprar_remove_carta_do_topo():
    deck = Deck(cards=[Card("A", "♠"), Card("2", "♠")])
    assert str(deck.draw()) == "A♠"
    assert len(deck) == 1


def test_comprar_de_baralho_vazio_levanta_erro():
    with pytest.raises(IndexError):
        Deck(cards=[]).draw()


def test_embaralhar_com_seed_e_reprodutivel():
    a, b = Deck(rng=random.Random(42)), Deck(rng=random.Random(42))
    a.shuffle()
    b.shuffle()
    assert [str(c) for c in a.cards] == [str(c) for c in b.cards]
    assert [str(c) for c in a.cards] != [str(c) for c in Deck().cards]