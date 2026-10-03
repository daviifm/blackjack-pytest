## Blackjack com TDD

Jogo de blackjack (jogador vs. mesa) em Python, feito com TDD. Cada ciclo teve três commits: red (testes falhando), green (código mínimo) e refactor (limpeza).

### Ciclo 1: Cartas e mão

- `Card`: valor da carta (figuras valem 10, ás vale 11).
- `Hand`: pontuação, ás valendo 1 para evitar estouro, `is_bust` e `is_blackjack`.

### Ciclo 2: Baralho

- `Deck`: 52 cartas únicas, `shuffle` (com seed opcional), `draw` e erro ao comprar de baralho vazio.
- `Card.__str__` para exibir cartas como `Q♥`.

### Ciclo 3: Jogo

- `Game`: distribuição inicial, `hit`, `stand`, fim de rodada e `winner`.
- Mesa joga sozinha pela regra do 17.
- `table_view`: a segunda carta da mesa fica oculta (`??`) até o fim da rodada.
- Vencedor: `"player"`, `"dealer"` ou `None` (empate). Estourar perde e blackjack natural vence um 21 de 3 ou mais cartas.

Possíveis TDDs futuros: Um blackjack natural na distribuição não encerra a rodada automaticamente (o jogador ainda precisa dar stand()), e o jogador pode dar hit() mesmo com 21. Os dois casos poderiam adicionar mais ciclos de TDD.


