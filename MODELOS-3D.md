# Os modelos 3D — o que existe e como entra na obra

Medido em 09/09/2026. **Para refazer esta conta:** `python fontes/modelos_em_pontos.py` reconverte tudo e imprime triangulo por triangulo; os pesos abaixo saem do `fontes/nuvens.js` que ele gera.

Os arquivos vivem em `Downloads/Visões filmes/Modelos 3D/`, e alguns soltos um nivel acima. **Quem esta acima so entra se estiver citado pelo nome** na lista `extras` do conversor — foi assim que os treze cogumelos passaram a obra inteira sem existir.

## Na obra

| modelo | tri | peças | no `nuvens.js` | como entra | onde |
|---|---:|---:|---:|---|---|
| `rocks-icon` | 5856 | 21 | 169 KB | nuvem + malha (8) | as onze pedras do chao, as montanhas do horizonte e o fundo do mar |
| `crisalida_borboleta88_diaethria` | 39594 | 1 | 77 KB | nuvem + malha (1) | o casulo |
| `cogumelo` | 138 | 1 | 61 KB | nuvem + malha (2) | os treze cogumelos, e a casca de luz que eles derramam |
| `jellyfish-icon` | 5408 | 17 | 58 KB | nuvem + malha (8) | o fundo do mar, e os seres que flutuam entre os planetas |
| `animated_butterfly` | 2144 | 5 | 52 KB | nuvem + malha (5) | a borboleta |
| `coral-icon` | 5888 | 50 | 51 KB | nuvem + malha (8) | o fundo do mar, e os seres que flutuam entre os planetas |
| `ser_alienigena_rigged` | 39680 | 1 | 49 KB | nuvem | o ser camuflado no ceu |
| `grass-icon` | 4288 | 21 | 30 KB | nuvem | a grama |
| `autumn-leaves-icon` | 101501 | — | 28 KB | nuvem | folhas do chao — atras de OBJETOS_NO_CHAO, hoje desligado |
| `autumn-leaves-icon-22705` | 4800 | 3 | 28 KB | nuvem | folhas do chao — atras de OBJETOS_NO_CHAO, hoje desligado |
| `seaweed-icon` | 10056 | 70 | 25 KB | nuvem | o fundo do mar |
| `seaweed-icon-13702` | 3360 | 9 | 25 KB | nuvem | o fundo do mar |
| `seaweed-icon-17190` | 7752 | 42 | 25 KB | nuvem | o fundo do mar |
| `scallop-icon` | 1500 | 3 | 21 KB | nuvem | a concha |
| `soya-icon` | 2640 | 10 | 18 KB | nuvem | soja do chao — atras de OBJETOS_NO_CHAO, hoje desligado |
| `clover-icon` | 9792 | 5 | 18 KB | nuvem | trevo do chao — atras de OBJETOS_NO_CHAO, hoje desligado |

## Baixados e nunca usados

Somam **183 KB dentro do `nuvens.js`** — peso que o Quest baixa e decodifica a cada abertura sem nada aparecer na tela.

| modelo | tri | no `nuvens.js` | o que é |
|---|---:|---:|---|
| `hand-icon` | 1344 | 37 KB | mao; as maos em RM sao as da pessoa, vistas pelas cameras. |
| `tree-icon` | 5064 | 35 KB | outra arvore; a arvore-mae hoje e procedural, sem modelo. |
| `crisalida_borboleta88_rigged` | 39594 | 23 KB | a mesma crisalida com esqueleto; a obra usa a lisa. |
| `seashells-icon` | 3409 | 23 KB | conchas; a obra usa a scallop-icon. |
| `mao_cosmica_teia` | 38070 | 23 KB | **a mao gigante que puxa, aos 8:25.** Esta no roteiro e nunca foi ligada. |
| `berry-pick` | 19250 | 21 KB | frutos; nunca entraram no roteiro. |
| `star` | 23651 | 21 KB | estrela; as estrelas da obra sao pontos gerados por codigo. |
| `ser_alienigena` | 39801 | não embarcado | o mesmo ser sem esqueleto; a obra usa a rigged. |
| `ser_alienigena_apose` | 39680 | não embarcado | o mesmo ser em outra pose; a obra usa a rigged. |

## O que isto revelou

**Os cogumelos nunca existiram.** O `cogumelo.glb` mora um nivel acima da
colecao e nao estava na lista `extras`. O efeito era mudo do inicio ao fim:
o `COMO_MALHA` pedia a malha, o conversor nunca via o arquivo, o `nuvens.js`
saia sem ela, o `decodificarMalha` devolvia nulo, o `plantarMalha` devolvia
zero, o `montarCogumelos` desistia sem reclamar e o desenho nao acontecia.
Treze cogumelos que o interruptor dizia ligados e que a documentacao
descrevia em tres paragrafos. Corrigido em 09/09 — e confirmado pelo numero:
86 112 indices por quadro que antes nao existiam.

**A mao cosmica esta no roteiro e fora da obra.** Aos 8:25 "a mao gigante
vem, e puxa". O modelo esta baixado, embarcado no `nuvens.js`, e nunca foi
ligado.

**Ha tres versoes do ser alienigena e duas da crisalida.** A obra usa uma de
cada; as outras continuam sendo baixadas pelo aparelho.

## Licencas

`CREDITOS.md` tem a lista, e ela nao mudou com esta contagem: dois
resolvidos — a **borboleta** (CC BY 4.0, Artistic_side no Sketchfab, credito
obrigatorio) e o **cogumelo** (CC0, Quaternius via poly.pizza) — e o resto e
pendencia declarada. Agora que os cogumelos aparecem de fato, o credito CC0
deixou de ser teorico.
