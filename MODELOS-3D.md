# Os modelos 3D — o que existe e como entra na obra

Gerado por `python fontes/listar_modelos.py`, que tambem escreve as folhas de contato em `_fotos/modelagem-*.png`. **Refaca depois de mexer no conversor** — os pesos saem do `fontes/nuvens.js`.

Os arquivos vivem em `Downloads/Visões filmes/Modelos 3D/`, e alguns soltos um nivel acima. **Quem esta acima so entra se estiver citado pelo nome** na lista `extras` do conversor — foi assim que os treze cogumelos passaram a obra inteira sem existir.

## Na obra

| modelo | tri | peças | no `nuvens.js` | como entra | onde |
|---|---:|---:|---:|---|---|
| `mao_cosmica_teia` | 38070 | 1 | 512 KB | nuvem + malha (1) | — |
| `star` | 23651 | 1 | 316 KB | nuvem + malha (1) | — |
| `crisalida_borboleta88_diaethria` | 39594 | 1 | 288 KB | nuvem + malha (1) | o casulo |
| `berry-pick` | 19250 | 38 | 216 KB | nuvem + malha (38) | — |
| `rocks-icon` | 5856 | 21 | 169 KB | nuvem + malha (8) | as onze pedras do chao, as montanhas do horizonte, o fundo do mar |
| `coral-icon` | 5888 | 50 | 108 KB | nuvem + malha (47) | o fundo do mar, e os seres que flutuam entre os planetas |
| `tree-icon` | 5064 | 1 | 79 KB | nuvem + malha (1) | — |
| `seaweed-icon` | 10056 | 70 | 71 KB | nuvem + malha (22) | o fundo do mar |
| `seaweed-icon-17190` | 7752 | 42 | 70 KB | nuvem + malha (16) | o fundo do mar |
| `seashells-icon` | 3409 | 6 | 69 KB | nuvem + malha (6) | — |
| `seaweed-icon-13702` | 3360 | 9 | 68 KB | nuvem + malha (8) | o fundo do mar |
| `cogumelo` | 138 | 1 | 61 KB | nuvem + malha (2) | os treze cogumelos, e a casca de luz que eles derramam |
| `jellyfish-icon` | 5408 | 17 | 58 KB | nuvem + malha (8) | o fundo do mar, e os seres que flutuam entre os planetas |
| `animated_butterfly` | 2144 | 5 | 52 KB | nuvem + malha (5) | a borboleta |
| `ser_alienigena_rigged` | 39680 | 1 | 49 KB | nuvem | o ser camuflado no ceu |
| `grass-icon` | 4288 | 21 | 30 KB | nuvem | a grama |
| `autumn-leaves-icon` | 101501 | — | 28 KB | nuvem | folhas — atras de OBJETOS_NO_CHAO, hoje desligado |
| `autumn-leaves-icon-22705` | 4800 | 3 | 28 KB | nuvem | folhas — atras de OBJETOS_NO_CHAO, hoje desligado |
| `scallop-icon` | 1500 | 3 | 21 KB | nuvem | a concha |
| `soya-icon` | 2640 | 10 | 18 KB | nuvem | soja — atras de OBJETOS_NO_CHAO, hoje desligado |
| `clover-icon` | 9792 | 5 | 18 KB | nuvem | trevo — atras de OBJETOS_NO_CHAO, hoje desligado |

## Baixados e nunca usados

Somam **60 KB dentro do `nuvens.js`** — peso que o Quest baixa e decodifica a cada abertura sem nada aparecer na tela.

| modelo | tri | no `nuvens.js` | o que é |
|---|---:|---:|---|
| `hand-icon` | 1344 | 37 KB | mao; em RM as maos sao as da pessoa, vistas pelas cameras. |
| `crisalida_borboleta88_rigged` | 39594 | 23 KB | a mesma crisalida com esqueleto; a obra usa a lisa. |
| `ser_alienigena` | 39801 | não embarcado | o mesmo ser sem esqueleto; a obra usa a rigged. |
| `ser_alienigena_apose` | 39680 | não embarcado | o mesmo ser em outra pose; a obra usa a rigged. |

## O que a folha de contato mostrou, e a conta nao mostrava

**Os treze cogumelos nunca existiram.** O `cogumelo.glb` mora um nivel acima
da colecao e nao estava na lista `extras`. O efeito era mudo do inicio ao
fim: o `COMO_MALHA` pedia a malha, o conversor nunca via o arquivo, o
`decodificarMalha` devolvia nulo, o `montarCogumelos` desistia sem reclamar
e o desenho nao acontecia. Corrigido em 09/09.

**O coral chegava como oito varetas soltas.** O modelo tem cinquenta pecas
— cada ramo e uma — e o conversor guardava as oito maiores. No numero, oito
malhas de duzentos triangulos pareciam certas. Hoje ele tem teto proprio
(`PECAS_POR`).

**E vinha com o pedestal junto.** Estes modelos trazem um disco de terra
embaixo, para o icone pousar numa pagina de catalogo. A nuvem ja o
descartava; a malha nao. Largo e baixo e pedestal, estreito e alto e ramo —
so a altura nao separa, porque o disco sobe ate 24% e um ramo comeca em
0,2%. O que separa e a pegada vista de cima: os ramos ocupam menos de 10%
da area do modelo, o pedestal ocupa 31% e 40%.

**A mao cosmica esta no roteiro e fora da obra.** Aos 8:25 "a mao gigante
vem, e puxa". O modelo esta baixado, embarcado, e nunca foi ligado.

## Quando um modelo parece anguloso

Primeiro, desconfie do desenho: **sombrear por face mostra faceta em tudo**.
As folhas aqui sombreiam por vertice, que e como o WebGL faz.

O que sobrar depois disso e do modelo, e tem conserto no conversor — sao
tres botoes, por modelo:

- `DIVISOES` divide cada triangulo em quatro. Sozinho nao arredonda nada
  (os pontos novos caem sobre as faces velhas), mas muda o que a suavizacao
  seguinte consegue fazer;
- `SUAVE` puxa cada vertice para a media dos vizinhos. Em malha grossa isso
  deforma o corpo inteiro e o objeto vira ovo; em malha fina so alisa a
  quina;
- `POLIR` sao passadas de media SEM dividir de novo. Nao custa triangulo.

O cogumelo e a prova: 138 triangulos, com o chapeu num octogono visivel.
Duas divisoes e tres polimentos o levam a 2 208 com o contorno fechado.

## Licencas

`CREDITOS.md` tem a lista. Dois resolvidos — a **borboleta** (CC BY 4.0,
Artistic_side no Sketchfab, credito obrigatorio) e o **cogumelo** (CC0,
Quaternius via poly.pizza). O resto e pendencia declarada.
