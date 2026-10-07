import pytest
import random
from blackjack import Card, Deck, Game, Hand


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

def make_cards(*codes):
    return [Card(code[:-1], code[-1]) for code in codes]


def new_game(*codes):
    """Baralho empilhado: distribui jogador, mesa, jogador, mesa e depois as compras."""
    game = Game(deck=Deck(cards=make_cards(*codes)))
    game.deal()
    return game


def cards_of(hand):
    return [str(c) for c in hand.cards]


def test_distribuir_da_duas_cartas_para_jogador_e_mesa():
    game = new_game("K♠", "10♣", "5♥", "8♦")
    assert cards_of(game.player_hand) == ["K♠", "5♥"]
    assert cards_of(game.dealer_hand) == ["10♣", "8♦"]


def test_hit_adiciona_carta_ao_jogador():
    game = new_game("K♠", "10♣", "5♥", "8♦", "2♣")
    game.hit()
    assert game.player_hand.score == 17


def test_nao_pode_comprar_depois_de_parar():
    game = new_game("K♠", "10♣", "5♥", "8♦", "2♣")
    game.stand()
    with pytest.raises(ValueError):
        game.hit()


def test_rodada_so_termina_quando_jogador_para():
    game = new_game("K♠", "10♣", "5♥", "8♦")
    assert not game.is_over
    game.stand()
    assert game.is_over


def test_jogador_estoura_termina_rodada_e_mesa_nao_joga():
    game = new_game("K♠", "5♣", "6♥", "6♦", "Q♣")
    game.hit()  # 26
    assert game.is_over
    assert game.winner() == "dealer"
    assert len(game.dealer_hand.cards) == 2


def test_mesa_compra_ate_chegar_a_17():
    game = new_game("K♠", "5♣", "9♥", "6♦", "4♠", "3♥")  # mesa: 11 -> 15 -> 18
    game.stand()
    assert game.dealer_hand.score == 18
    assert len(game.dealer_hand.cards) == 4
    assert game.winner() == "player"  # 19 x 18


def test_mesa_para_em_17_e_vence_maior_pontuacao():
    game = new_game("K♠", "10♣", "5♥", "7♦", "2♠")  # 15 x 17
    game.stand()
    assert len(game.deck) == 1  # a mesa não comprou
    assert game.winner() == "dealer"


def test_mesa_para_em_17_soft():
    game = new_game("K♠", "A♣", "9♥", "6♦", "5♠")  # mesa: A+6 = 17
    game.stand()
    assert len(game.dealer_hand.cards) == 2
    assert len(game.deck) == 1


def test_mesa_estoura_jogador_vence():
    game = new_game("K♠", "10♣", "5♥", "6♦", "Q♣")  # mesa: 16 + Q = 26
    game.stand()
    assert game.dealer_hand.is_bust
    assert game.winner() == "player"


def test_maior_pontuacao_do_jogador_vence():
    game = new_game("K♠", "10♣", "9♥", "8♦")  # 19 x 18
    game.stand()
    assert game.winner() == "player"


def test_empate_retorna_none():
    game = new_game("K♠", "K♣", "9♥", "9♦")  # 19 x 19
    game.stand()
    assert game.winner() is None


def test_natural_vence_21_de_tres_cartas():
    assert hand("A", "K").strength > hand("7", "7", "7").strength


def test_natural_do_jogador_encerra_rodada_na_distribuicao():
    game = new_game("A♠", "7♣", "K♥", "8♦")  # jogador: A+K = 21 (natural)
    assert game.is_over
    assert game.winner() == "player"
    assert game.table_view()["dealer"] == ["7♣", "8♦"]  # mesa revelada


def test_natural_da_mesa_encerra_rodada_na_distribuicao():
    game = new_game("9♠", "A♣", "7♥", "K♦")  # mesa: A+K = 21 (natural)
    assert game.is_over
    assert game.winner() == "dealer"


def test_naturais_dos_dois_lados_empatam():
    game = new_game("A♠", "A♣", "K♥", "K♦")
    assert game.is_over
    assert game.winner() is None


def test_nao_pode_agir_depois_de_natural():
    game = new_game("A♠", "7♣", "K♥", "8♦", "2♣")
    with pytest.raises(ValueError):
        game.hit()
    with pytest.raises(ValueError):
        game.stand()