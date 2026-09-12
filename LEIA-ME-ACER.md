# Raízes Cósmicas v2 — tudo o que é preciso para continuar em outra máquina

Escrito em 06/09/2026 para a mudança para a Acer.
Este arquivo é o mapa completo: o que é, o que instalar, o que cada arquivo
faz, como reconstruir, como publicar, e onde estão as armadilhas.

---

## 1. O que é isto

Uma obra de **realidade mista para Meta Quest 3**, feita em **WebXR**, que
abre no navegador do headset sem instalar nada. Dez minutos, quatro
cenários, área caminhável de 3 × 3 m numa sala escura. Para o FIL 2026.

Deriva da animação **Odara — Cosmos**, feita para o Coletivo MUANES: os
céus, as texturas e as figuras foram todos recortados dos quadros dela.

**Endereços no ar:**

| | |
|---|---|
| A obra (é este que se digita no Quest) | https://visoes-filmes.github.io/raizes-cosmicas-v2/ |
| O roteiro de sala | https://visoes-filmes.github.io/raizes-cosmicas-v2/roteiro.html |
| O repositório | https://github.com/visoes-filmes/raizes-cosmicas-v2 |

O repositório pertence à organização **visoes-filmes** no GitHub. Crisia é
owner; a conta pessoal do Plinio não foi tocada.

> O nome `visoesfilmes` sem hífen já pertence a outra conta no GitHub. Por
> isso a organização é `visoes-filmes`.

---

## 2. Como levar a pasta para a Acer

**O jeito certo é clonar**, porque aí dá para continuar publicando de lá:

```bash
git clone https://github.com/visoes-filmes/raizes-cosmicas-v2.git
```

Vai pedir login do GitHub na primeira vez que empurrar alguma coisa. Use a
conta **Crisia-poria**, que já é owner da organização.

**Se só quiser os arquivos, sem git:** na página do repositório, botão verde
`Code` → `Download ZIP`. Serve para ver e editar, mas **não** para publicar.

A pasta inteira tem **25 MB**.

---

## 3. O que instalar na Acer

| o quê | para quê | como conferir |
|---|---|---|
| **Git** | clonar e publicar | `git --version` |
| **Python 3** | reconstruir a cena | `python --version` |
| **Pillow** | é a biblioteca que mexe nas imagens | `pip install Pillow` |
| **Um navegador com WebGL** | ver a cena no computador | Chrome ou Edge |

Só isso. **Não** precisa de Node, npm, nem servidor local: a cena é um
arquivo HTML único que abre com duplo clique.

> **numpy não é necessário** para reconstruir. Quatro scripts em `fontes/`
> usam numpy — `nivelar.py`, `analise_panorama.py`, `figuras_odara.py` e
> `texturas_odara.py` — mas todos já fizeram o trabalho deles: os céus, as
> figuras e as texturas prontas estão em `assets/`. Só precisará de numpy se
> for **refazer um desses do zero**.

---

## 4. A pasta, arquivo por arquivo

```
raizes-cosmicas-v2/
├── index.html                 7,2 MB  A OBRA. Um arquivo só, com tudo dentro.
├── roteiro.html                72 KB  O roteiro de sala, com as abas.
├── LEIA-ME-ACER.md                    Este arquivo.
├── README.md                          Resumo do projeto.
├── sw.js                              Guarda a obra no aparelho (offline).
├── manifest.webmanifest               Faz o Quest tratar como aplicativo.
├── .nojekyll                          Impede o GitHub de processar a pasta.
├── icone-192.png / icone-512.png      Ícones do aplicativo.
│
├── assets/                    AS IMAGENS E O SOM DE ORIGEM
│   ├── ceus/
│   │   ├── ceu-floresta-2048.png      Cenário 1. Da pintura da Odara.
│   │   ├── ceu-cosmico-2048.png       Cenário 2 e 4.
│   │   └── ceu-rosa-2048.png          Cenário 3.
│   ├── figuras/
│   │   ├── fig-galactico.png          O recorte antigo do ser galáctico — não é mais usado.
│   │   ├── fig-galactica-inteira.jpg  A deusa galáctica, o quadro inteiro como a direção de arte
│   │   │                              mandou (11/09), 1364 × 767. Guardado; a obra usa o abaixo.
│   │   ├── fig-galactica-ceu.jpg      O mesmo quadro EXPANDIDO no Magnific (pelo site, 11/09, duas
│   │   │                              vezes) a 2536 × 1586: nebulosa continuada em volta e céu sobre
│   │   │                              a cabeça. Guardado; a obra usa o abaixo.
│   │   ├── fig-galactica-ampliada.jpg A que a obra usa (12/09): o expandido AMPLIADO 2× no Magnific
│   │   │                              (criativo, sutil, arte e ilustração), 5072 × 3168, embutido a
│   │   │                              3072 × 1921. Antes era embutido a 2048 — a 118° de largura no
│   │   │                              céu dava 17 px por grau, abaixo do que o Quest mostra; agora
│   │   │                              26. Sem alfa; o alfa nasce no shader, da beirada e do preto.
│   │   ├── fig-deusa-vermelha.png     O recorte antigo da deusa vermelha (chave_23) — não é mais usado.
│   │   ├── fig-vermelha-91.jpg        A deusa vermelha, o quadro inteiro aos 91 s da animação da Odara
│   │   │                              (o MESMO momento do recorte antigo), 1280 × 714. fig-vermelha-quadro.jpg
│   │   │                              é a mesma imagem com o nome de antes.
│   │   ├── fig-vermelha-sem-chao.png  O mesmo quadro sem o chão: abaixo da linha do piso entrou céu
│   │   │                              escuro costurado de retalhos do próprio quadro, e a neblina e a
│   │   │                              barra do vestido dissolvem numa faixa irregular (12/09).
│   │   ├── fig-vermelha-cosmos.jpg    A que a obra usa: o sem-chão EXPANDIDO no Magnific (pelo site) a
│   │   │                              2048 × 1280, o facho de luz que ele inventou no alto removido, e
│   │   │                              ampliado 2× (criativo, sutil, arte e ilustração): 4096 × 2560.
│   │   ├── fig-deusa-integra.png      O recorte antigo da deusa que integra tudo (t_072) — não é mais usado.
│   │   ├── fig-integra-quadro.jpg     O quadro inteiro aos 152 s da animação; fig-integra-recorte.jpg é
│   │   │                              ele sem as margens de papel (1150 × 696).
│   │   ├── fig-integra-ceu.jpg        A que a obra usa: o recorte expandido no Magnific a 2048 × 1280
│   │   │                              com fundo escuro, e ampliado 2×: 4096 × 2560.
│   │   └── fig-borboleta.png          A borboleta 88 (t_005).
│   ├── texturas/
│   │   ├── tex-raiz.png               A casca das raízes e do tronco.
│   │   ├── tex-marmore.png            Mármore, ladrilha sem emenda.
│   │   ├── tex-agua.png               Água, ladrilha sem emenda.
│   │   ├── tex-papel.png              O papel recortado do cenário 4.
│   │   ├── tex-galaxia.png            Sobrando, não está ligada.
│   │   ├── tex-ornamento.png          Sobrando, não está ligada.
│   │   └── tex-planeta.png            Sobrando, não está ligada.
│   ├── peles/                 AS SEIS DO MIDJOURNEY, uma por corpo
│   │   ├── pele-sol.jpg               Coral saindo de um ponto.
│   │   ├── pele-rosa.jpg              A nebulosa rosa.
│   │   ├── pele-asteroide.jpg         Mármore violeta e coral.
│   │   ├── pele-verde.jpg             Samambaia magenta e ciano.
│   │   ├── pele-agua.jpg              Azul profundo com o olho.
│   │   └── pele-fogo.jpg              Veias de lava.
│   └── audio/
│       └── trilha-loop.mp3            71 s, fecha em si mesma.
│
└── fontes/                    O CÓDIGO E AS FERRAMENTAS
    ├── mr.template.html      144 KB  O CÓDIGO DE VERDADE. É aqui que se edita.
    ├── montar_mr.py                  Embute as imagens e gera o index.html.
    ├── verificar.py                  Procura erros ANTES de montar.
    ├── peles_planetas.py             Fez as seis peles a partir das do MJ.
    ├── figuras_odara.py              Recortou as quatro figuras.
    ├── texturas_odara.py             Fez as texturas que ladrilham.
    ├── nivelar.py                    Costurou a emenda e os polos do céu.
    ├── analise_panorama.py           Mede emenda e polos de um equirretangular.
    ├── gerar_visualizador.py         Visualizador 360 avulso, com a imagem dentro.
    ├── planetas/mj1..mj6.jpg         As seis do Midjourney, originais.
    └── (outros patch_*.py)           Histórico das mudanças, um por assunto.
```

### A regra que não pode ser esquecida

> **Nunca edite o `index.html` direto.**
> Ele é **gerado**. Toda edição vai em `fontes/mr.template.html`, e depois
> se roda o montador. Editar o index.html funciona até a próxima montagem,
> que apaga tudo.

---

## 5. Como ver

**No computador:** duplo clique no `index.html`. Abre no navegador, aparece
o portão, botão **Iniciar na tela**.

**No Quest 3:** abra o navegador do headset e digite

```
visoes-filmes.github.io/raizes-cosmicas-v2/
```

Aparece o portão. Espere as **17 imagens** carregarem (o botão fica cinza até
lá) e toque em **Iniciar em RM**. O headset pede permissão uma vez.

> Depois da primeira abertura com internet, a obra fica **guardada no
> aparelho** e abre offline. Numa feira isso não é conforto: é o que decide
> se ela funciona quando o wi-fi oscilar.
>
> **Se abrir e parecer a versão antiga**, puxe a página para baixo para
> recarregar, ou feche e abra a aba. O navegador guarda a versão anterior
> com bastante teimosia.

---

## 6. Como reconstruir depois de editar

Da pasta do projeto, **sem argumento nenhum**:

```bash
python fontes/verificar.py
python fontes/montar_mr.py
```

O primeiro procura erros; o segundo gera o `index.html`. Se o verificador
apontar alguma coisa, **conserte antes** — ele só reclama do que já quebrou
esta obra alguma vez.

Os caminhos resolvem a partir da pasta do projeto, então funciona de
qualquer diretório e em qualquer máquina.

---

## 7. Como publicar

**A versão do cache se troca sozinha.** O `montar_mr.py` gira o `VERSAO` do
`sw.js` a cada montagem (data + letra: `2026-09-06`, `…06b`, `…06c`).

O service worker serve **cache primeiro, rede como reserva**, e o nome do
cache *é* o número da versão: um nome novo cria um cache novo, baixa tudo
dentro dele e só então apaga o antigo — nunca há um momento em que metade da
obra é de uma versão e metade de outra. **Sem trocá-lo, o headset continua
servindo o cache antigo** e a obra nova não chega lá.

> Era feito à mão, e à mão significa esquecer: já se perdeu uma tarde
> olhando um defeito que estava corrigido havia meia hora. Por isso passou a
> ser o montador quem troca — ele não pode esquecer.

Depois:

```bash
git add -A
git commit -m "o que mudou"
git push
```

Um ou dois minutos depois o endereço está no ar. Não há build, não há
Actions — o GitHub Pages serve a pasta como ela está.

> Já tentamos usar GitHub Actions para isso e **falhou**: o token padrão do
> repositório é só de leitura. Foi removido de propósito. HTML estático não
> precisa de build.

---

## 8. Como a cena funciona por dentro

### As medidas da sala

```js
const LARG = 4.00, PROF = 4.70, ALTURA = 3.00, OLHO = 1.60;
```

Metros. A **área caminhável** é 3 × 3; a sala é um pouco maior para o céu
ter onde se apoiar. `OLHO` é a altura dos olhos no computador (no headset
quem manda é o rastreamento).

### A partitura: os dez minutos

Cada momento tem hora de começar e **acontece independente de a pessoa
interagir**. Quem interage conduz; quem não interage é conduzido; e ninguém
trava a fila.

| tempo | cenário | o que acontece |
|---|---|---|
| 0:00 | 1 | a sala real; o céu estrelado já está lá |
| 0:20 | 1 | as estrelas começam a cair |
| 1:00 | 1 | o nascimento: grama, cogumelo, a árvore |
| 1:50 | 1 | **janela** — os cogumelos, o casulo |
| 2:50 | 1 | a borboleta sobe e o mundo se desintegra |
| 3:00 | 2 | as estrelas acendem, da mais distante até o Sol |
| 3:40 | 2 | os planetas descem e orbitam a pessoa |
| 3:46 | 2 | a deusa vermelha entra, à esquerda do Sol, perto da galáctica |
| 4:10 | 2 | eles se dispersam pelo céu e esperam |
| 4:40 | 2 | os buracos negros aparecem |
| 5:00 | 2 | o balé dos planetas não escolhidos |
| 5:30 | 2 | **janela** — pegar e dimensionar um planeta |
| 6:20 | 2 | entrar no planeta |
| 6:30 | 3 | o planeta rosa; a água sobe até a cintura |
| 7:30 | 3 | **janela** — os seres, as pedras, a concha |
| 8:25 | 3 | a mão gigante vem, e puxa |
| 8:45 | 4 | o mundo de papel sobe, de baixo para cima |
| 9:20 | 4 | a deusa que integra tudo |
| 9:45 | 4 | tudo se desmancha; sobra o quarto real |

No código: `const MOMENTOS`, `DURACAO = 600`, `TRAVESSIA = 6`.

**A travessia de 6 segundos é o que conecta os cenários.** Nenhum parâmetro
salta: todos correm para o destino por `1 − e^(−1.8·dt)`, e os dois céus se
misturam. É por isso que não há corte em lugar nenhum da obra.

### Os quatro cenários

```js
const CENAS = {
  1: { ceu:3, tinta:0.85, neblina:0.20, ... ini:0.22, fim:0.72, inverter:0 },
  2: { ceu:2, tinta:0.0,  neblina:0.18, ... ini:0.12, fim:0.58, inverter:0 },
  3: { ceu:2, tinta:0.92, neblina:0.16, ... ini:0.30, fim:0.86, inverter:0 },
  4: { ceu:1, tinta:0.82, neblina:0.11, ... ini:0.10, fim:0.55, inverter:1 },
};
```

- `ceu` — qual dos quatro céus (0 floresta da Odara, 1 cósmico, 2 rosa,
  3 mata — os filamentos do Midjourney, só no cenário 1)
- `tinta` — quanto do que se vê é pintura e quanto é noite. **O cenário dos
  planetas está em zero desde 11/09**: sem pintura, só a noite da cúpula e
  as oitenta e quatro estrelas, como na abertura — e a neblina (a nuvem
  cósmica do começo) indo e vindo num ciclo de 48 s (`nuvemVaiEVem`). Ele
  declara o céu rosa porque a travessia para o 3 mistura os dois céus
  enquanto a tinta sobe, e com o cósmico declarado a pintura cósmica
  aparecia por três segundos no meio da passagem.
- `ini` / `fim` — **o degradê vertical**, em fração do quarto de volta:
  0 no horizonte, 1 no zênite. Já foi fração do pé-direito, quando o céu
  era uma caixa. O céu é
  cheio no teto e some ao descer. No cenário 3 ele só começa a 0,84 m,
  porque a água tapa o resto.
- `inverter` — o cenário 4 lê o céu **de cabeça para baixo**. É o que faz a
  floresta do primeiro cenário reaparecer sob os pés no último, sem custar
  uma imagem nova.

**O que há no cenário dos planetas** (inventário de 11/09, medido por
chamada de desenho aos 5:00): a cúpula da noite, 84 estrelas, o Sol com
três cascas de corona, quatro planetas com halo (rosa, água, fogo, verde),
sete asteroides, o buraco negro no chão (**deitado** desde 12/09 — era um
disco virado para a câmera, uma placa de pé no chão; agora é um disco no
plano do piso, `deitado` em `VS_BOLHA`, e de longe é a elipse rasa de um
poço), a deusa galáctica inteira ao
fundo (e desde 12/09 a deusa vermelha ao lado dela), os seres aquáticos (7 águas-vivas, 4 corais, 2 estrelas-do-mar —
pedidos: "você esqueceu os seres aquáticos estranhos"), a neblina indo e
vindo e 2 600 grãos de poeira. **Saíram em 11/09** a mão cósmica, a árvore
de ícone, as conchas e o galho de frutos em neon ("estavam baixados e nunca
tinham aparecido") e, na rodada seguinte, os seres aquáticos
(`SERES_NO_ESPACO = false` — "nele é apenas os planetas"). O ser do céu
(`alien-0`) é desde 11/09 o modelo `ser_alienigena_androgino_rigged.glb`,
com **60 m** a 46 m de distância (era 26 m a 35); continua camuflado e só
existe onde há pintura no céu — no cenário dos planetas ele some.

**As figuras recortadas** (`FIGURAS`, `FS_FIGU`): desde 11/09 o shader não
corta mais nada além da beirada — havia um corte em 0,17 no alfa, um pé
dissolvido e uma moldura circular que tiravam da deusa vermelha 44% do
arquivo. A galáctica é a pintura expandida, **150 × 94 m a 45 m de
distância** (118° × 92°): é o céu do lado direito de quem entra, do azimute
−23° ao +95° — "parte do céu", pedido de 11/09. O Sol pousa a −38°, fora do
corpo dela. Não há mais rasgo na beirada (comia o cabelo e as raízes): só o
preto de verdade vira noite, gradualmente (luminância 0,012–0,09). E há
**dois tempos** na mesma pintura (`FS_FIGU`, `inteira`): o fundo é lido com
um balanço lento (ciclo de ~1 min, 0,005 do quadro) e o corpo dela, dentro
de uma elipse macia, só respira (0,5% em 25 s) — a ilusão de que ela se
move noutro tempo, pedida em 11/09 como teste. E a pintura sai da pintura:
**160 partículas** azuis-brancas (`bPontosDeusa`, pelo `progPo` com `fixo`)
entre 6 e 35 m no cone dela, e **14 fios de luz** (`progFio`, `LINE_STRIP`
em cinco passadas de 2 cm) que nascem no plano dela e vêm até 9–16 m da
pessoa, com um pulso correndo da pintura para fora a cada ~14 s — pedidos
em 11/09 "para integrar mais"; os fios são **ramificados** (14 troncos, 2–4
ramos cada, às vezes um raminho) e azuis como os veios da pintura. Só
enquanto ela está no céu (3:26–6:16). **Luas** (11/09): água 2, fogo 1,
verde 3 — esferas pequenas com a pele do asteroide, em órbitas inclinadas
(`PLANETAS[i].luas`, `ondeLua`); o rosa fica sem, porque é o que se pega. E
o rosa é **gasoso** (`gas: 1` → uniforme `gas` em `FS_ASTRO`): a borda cede
sobre metade do disco, o corpo a 82%, e um segundo halo a 2,3 raios.

**As outras duas deusas passaram pelo mesmo método em 12/09** — "aproveite,
faça a mesma técnica": o quadro inteiro, tirado da animação da Odara
(`_fotos/animacao.mp4`, cópia local; os quadros-chave antigos não estão
mais nesta máquina) **no mesmo momento dos recortes antigos** — a vermelha
aos 91 s, a integra aos 152 s —, expandido no Magnific pelo site (a API de
expansão ignora a proporção), ampliado 2×, e desenhado pelo mesmo ramo
`inteira` do `FS_FIGU`: só o preto vira noite, a beirada esmaece, dois
tempos, partículas e fios na cor de cada quadro (`ENFEITES`).

**A vermelha mudou de cenário.** No planeta rosa ela ficava "bem poluída, e
o fundo preto não dá certo" — o preto do quadro dela não casa com o céu
pintado. Está no **cosmos**, "do lado da deusa azul, mas nem tão do lado:
próxima": azimute −78°, 84 × 52 m a 40 m (93° × 66°), o centro a 18° de
altura, de 3:46 a 6:16, sem reflexo. A galáctica começa em −23°, o Sol pousa
em −38°, no vão entre as duas. **Antes de expandir, o chão saiu** ("ela está
no planeta água... remova esse chão"): a primeira tentativa foi escurecer o
piso na imagem já expandida, e sobrava um retângulo preto; a segunda foi o
retoque do Magnific por máscara, que inventava um horizonte; o que ficou foi
costurar céu escuro de retalhos do próprio quadro no lugar do piso, com uma
dissolução irregular coluna a coluna (`fig-vermelha-sem-chao.png`), e só
então expandir. O facho de luz que a expansão inventou sobre a cabeça foi
subtraído (passa-alta na faixa de cima). Os fios dela são cinco troncos de
ouro num cone pela metade (`abre: 0.55`, 80 partículas): o que sai dela são
os fios das mãos, não uma tempestade. E os fios de todas ficaram curvas de
verdade: todo ramo tem 40 pontos e o tremor fino tem 3 ciclos — com 13
pontos e 5 ciclos era zigue-zague de relâmpago.

**A integra** continua no cenário 4 (9:16–9:54), 80 × 50 m a 40 m, sobre o
céu cósmico invertido; a composição ali está densa e ainda não foi julgada
pela direção de arte.

### Os corpos e as peles

| corpo | pele | por que essa |
|---|---|---|
| o Sol | `pele-sol` | os raios saem de um ponto: é literalmente um sol |
| planeta rosa | `pele-rosa` | a nebulosa rosa |
| planeta água | `pele-agua` | azul profundo, e o olho lembra um oceano |
| planeta fogo | `pele-fogo` | as veias de lava |
| planeta verde | `pele-verde` | a samambaia tem o verde e o ciano |
| asteroides | `pele-asteroide` | o mármore tira o cinza deles |

**A cor de cada planeta agora é quase branca, de propósito.** O shader
multiplica a textura pela cor. Como cada pele já chega colorida, um
tingimento forte apagaria justamente o que se foi buscar.

### As unidades de textura

Confundir uma delas troca a imagem de um objeto pela de outro, e não dá erro
nenhum:

| unidade | o que fica lá |
|---|---|
| 0 | céu A (o de saída da travessia) |
| 2 | textura das raízes |
| 3 | o atlas de tinta assado a cada quadro |
| 4 | céu B (o de chegada) |
| 5 | as peles (planetas, asteroides, água) |
| 6 | o papel |
| 7 | a figura sendo desenhada |

### Os catorze programas de shader

`progRaiz` (raízes e árvore) · `progSolida` (a floresta como superfície:
troncos, pedras, terra, grama, crisálida, cogumelos) · `progSala` (a cúpula)
· `progMata` (as nuvens de pontos e as estrelas) · `progFig` (a nuvem
marmorizada) · `progPo` (a poeira) · `progBorbo` (a borboleta) · `progAssa`
(assa o atlas de tinta) · `progAstro` (sol, planetas, asteroides) ·
`progPapel` (as sete camadas) · `progAgua` (a lâmina) · `progFigu` (as
figuras recortadas) · `progBolha` (buracos negros e seres do mar) ·
`progTexto` (a frase, o título e o botão, pintados num quadro fora da tela).

> Eram dez quando isto foi escrito. `progSolida` nasceu quando a floresta
> deixou de ser nuvem e virou superfície; `progBorbo` quando a borboleta
> deixou de ser recorte plano.

### O toque e o som (11/09)

As duas mãos rastreadas (`MAOS`, lidas em `lerMaos`) são conferidas a cada
quadro contra a lista de `alvosAgora()`. **Uma vez por encostar**: a mão
lembra em que alvo está (`ultimoAlvo`) e só dispara de novo depois de sair
dele — antes o `fazer()` rodava setenta e duas vezes por segundo.

O que responde, e como:

| alvo | luz | som |
|---|---|---|
| a árvore-mãe (tronco e sapopemas) | um anel ciano que parte de onde a mão encostou e atravessa o que estiver no caminho, a 3,2 m/s, sumindo em 1,4 s (`pulsarEm` → uniforme `toque`) | sino grave |
| os treze cogumelos | o mesmo anel; **neles a onda multiplica**, porque somar ciano em coisa que já é luz não se vê | sino, uma nota por cogumelo |
| a borboleta, na volta que ela dá | **glitter**: 48 grãos saem dela e caem por 2,2 s (`soltarGlitter`, andam na CPU, usam `progPo` com `fixo = 1`) | o som estranho: triângulo subindo uma oitava e meia com vibrato largo, mais sete pings agudos |
| o casulo, a concha, o rizomar | o anel | sino |
| o planeta rosa | **uma onda de luz que atravessa o disco** a partir do ponto tocado, em ~1 s (o mesmo `toque`, agora também no `FS_ASTRO` — até 12/09 o anel só existia no shader das superfícies, e o toque no planeta era só o sino) | sino |

**Pegar e dimensionar o planeta rosa** (12/09, `rosaNaMao`, `seguirRosa`) —
a janela das 5:30 existe de verdade agora:

- **pegar**: pinçar (`selectstart` — nas mãos nuas o Quest lê o pinçar do
  indicador com o polegar; no controle, o gatilho) com a mão a menos de um
  palmo do rosa. Ele vai com a mão, sem saltar: o desvio entre a mão e o
  centro no instante da pegada é guardado e mantido. Segue com atraso de
  ~70 ms, que é o que lixa o tremor do rastreio.
- **dimensionar**: com o rosa numa mão, pinçar com a outra perto dele. A
  distância entre as mãos vira a régua (nunca menor que 15 cm ao começar):
  afastar cresce, juntar encolhe, **da metade a 2,5×** (raio de 12 a 59 cm).
  O tamanho escolhido fica — o toque, o pulso e os halos acompanham
  (`raioDoRosa()`).
- **soltar**: ele volta à órbita devagar (constante de tempo 2 s, ~6 s até
  chegar). Um planeta largado no chão ou atirado longe nunca se perde, e
  voltar devagar é soltar, não mola.
- **na cara ele se dissolve**: entre um e dois raios do olho a presença cai
  a zero. Medido na bancada, de dentro da casca de luz via-se a parede de
  trás dela, facetada e chapada. É gás; atravessa-se, e volta ao afastar.
- aos 6:18 a mão larga (o planeta se apaga), e o reinício (`rizomar`) zera
  posição e tamanho. Relatos: `PEGOU-O-ROSA`, `SOLTOU-O-ROSA`.

Só o rosa, como antes: é o único ao alcance. A entrada no planeta (6:20)
continua pelo relógio, para todo mundo. **Nada disto foi tocado no Quest
ainda** — o pinçar de mão nua e o que decide se o palmo de folga (10 cm)
basta, e só o aparelho responde.

E **a asa soa**: um sopro de ruído filtrado por batida, só a menos de cinco
metros, caindo com o quadrado da distância.

**Nenhum agudo alto** (pedido de 11/09): os sinos vão de 131 a 262 Hz, o
som estranho sobe de 110 a 330 Hz, o sopro da asa fica entre 240 e 540 Hz, e
um passa-baixas em 1,4 kHz depois do mestre abafa qualquer coisa acima. Medido
na bancada: mãe a −35 dBFS com centroide em 138 Hz; som estranho a −40 dBFS,
165 Hz; sopro da asa a −58 dBFS, 675 Hz — o mais fraco de todos, de propósito.

**Todo som é sintetizado** (Web Audio, `acordarGestos`), por três motivos:
não há licença a resolver, não há byte a mais nos onze megabytes, e é o que
a obra é — tudo aqui é feito na hora. Ganho mestre **0,35**, e cada som
nasce abaixo da trilha (0,16). O contexto nasce no mesmo gesto humano que
acorda a trilha (`acordarSom`): sem gesto o navegador não deixa som existir.
Se um dia se quiser som gravado, cada função vira um `createBufferSource`
com o arquivo e o resto não muda.

**A floresta está fora do alcance** — as onze árvores moram no anel de 2,9
a 5,0 m, por decisão anterior da direção de arte, e um braço a partir da
beira da área caminhável chega a uns 2,2. Por isso a lista é o que está
perto, e não "as árvores".

Na bancada, sem headset: `raizes.mao(x, y, z)` põe a mão 0 num ponto;
`raizes.mao()` tira.

---

## 9. As armadilhas deste projeto

Todas já aconteceram aqui. **Nenhuma dá erro visível** — ou a página morre
inteira, ou a coisa simplesmente não aparece, e o console fica em silêncio.
O `verificar.py` procura as sete primeiras.

1. **Crase perdida num comentário de shader.** Os shaders moram dentro de
   *template literal* do JavaScript, delimitado por crase. Uma crase num
   comentário fecha a string no meio e quebra o arquivo inteiro, com o erro
   aparecendo longe dali. **Aconteceu cinco vezes.**
2. **Nome declarado duas vezes.** Mata a página antes de qualquer coisa rodar.
3. **Constante usada antes de existir.** O console diz só *"Cannot access
   before initialization"*.
4. **Constante de shader não declarada.** O GLSL não herda nada entre
   shaders: cada um é um programa fechado.
5. **Precisão de uniforme diferente entre os dois estágios.** No shader de
   vértice `float` é `highp` por padrão. Não batendo, **o programa não
   linka — e não linkar não aparece como erro:** o desenho simplesmente não
   acontece.
6. **Atributo vazando entre programas.** Ligar um atributo vale para
   sempre, não para o desenho. Existe `soltarAtributos()` — chame depois de
   todo `useProgram`.
7. **`${` dentro de shader.** O JavaScript tenta interpolar.

E as que o verificador **não** pega, porque são de comportamento:

8. **Alocar memória a cada quadro.** O coletor de lixo junta e recolhe tudo
   de uma vez, e a parada aparece como engasgo periódico — o travamento
   mais difícil de diagnosticar, porque não tem relação com o que está na
   tela. Use o `mvpBuf` que já existe.
9. **Contar tempo em quadros.** `relogio += 1/60` supõe 60 fps. Use sempre
   `passo()`, que devolve o tempo real com teto de 0,1 s.
10. **Mipmap em imagem com alfa.** Borra a cor para dentro do transparente e
    deixa halo escuro em volta da figura. As figuras carregam sem mipmap de
    propósito.
11. **Repetição vertical em céu.** O eixo vertical é a latitude, e os
    extremos dela não são vizinhos: um é o zênite e o outro é o nadir.
    Céus usam `CLAMP_TO_EDGE` no vertical; as peles que ladrilham repetem
    nos dois.

### E a maior de todas, achada no teste de 06/09

12. **O alfa é elevado ao quadrado no headset se a mistura for a comum.**
    `blendFunc(SRC_ALPHA, ONE_MINUS_SRC_ALPHA)` trata os quatro canais
    igual, então no alfa faz `srcA × srcA` — e o quadro do headset começa
    com **alfa zero**, que é o alfa que deixa a câmera aparecer.
    Uma cúpula a 30% compunha a 9%. Uma nuvem a 15% compunha a 2%. **Tudo o
    que não fosse quase opaco sumia.** Foi por isso que o primeiro teste no
    Quest não mostrou nada.

    Use sempre as duas funções que existem: **`sobrepor()`** e
    **`somarLuz()`**. Nunca `gl.blendFunc` cru.

    > **A lição, que vale para tudo daqui em diante:** o passthrough é um
    > ambiente diferente, não uma janela para o mesmo. Ali o alfa deixa de
    > ser um detalhe e passa a ser o canal que decide se a obra existe.
    > **Nada visto no computador prova coisa alguma sobre o headset.**

---

## 10. O orçamento de quadros

O número no canto mostra **`68 / 72`**: o que se está fazendo, contra o alvo.

**72 é o alvo, e é pedido explicitamente ao aparelho.** O Quest sabe rodar a
72, 90 e 120, e sem pedir nada o navegador escolhe. Se escolher 90, a obra
passa a ter 11 ms por quadro em vez de 13,9 — 25% a mais de trabalho para
uma peça que não ganha nada com isso.

**Cair de quadros aqui não faz mal a ninguém.** O compositor do headset
guarda o último quadro desenhado e o reposiciona para onde a cabeça está no
instante de mostrar — chama-se *timewarp*, é sempre ligado. Então o mundo
não escorrega junto com a cabeça: o que fica ruim é a animação.

O medidor fica laranja **abaixo de metade do alvo**, que é onde o timewarp
deixa de disfarçar e o que se move ganha rastro visível.

> **O que dá enjoo em RV é mover a câmera sem a pessoa ter se movido.**
> Esta obra não faz isso em lugar nenhum: quem anda é a pessoa, com as
> próprias pernas. A maior causa de mal-estar está fora do projeto por
> construção.
>
> Sobra um risco real, e não é de quadros: **se o rastreamento perder a
> sala**, o mundo desliza sozinho. Por isso a luz do estande decide mais do
> que qualquer otimização de código.

**Se faltar quadro, a ordem de corte é esta:**

1. `ANISO_ALVO` de 4 para 0 — é um número só, e a obra continua inteira
2. menos camadas na nuvem
3. reduzir a resolução de desenho quando os quadros caem

---

## 11. O que falta

### O teste de rastreamento: o que se concluiu errado, e o que é verdade

**Em 06/09 o teste de mão falhou, e concluímos que era a escuridão da sala.
Estava errado.** Medido no aparelho em 06/09, à noite, na mesma luz:

```
RM-ABRIU espaco=local-floor
features = viewer, plane-detection, webxr, hit-test,
           anchors, local, local-floor, hand-tracking
MAO-0 apareceu tipo=mao-nua
MAO-1 apareceu tipo=mao-nua
```

As duas mãos, rastreadas, na luz que temos. **O rastreamento sempre
funcionou.**

O que havia era que **a obra nunca pediu `hand-tracking`**. Quando os
recursos opcionais foram a zero para destravar a sessão, ele foi junto — e
sem pedir, o WebXR não entrega mão nenhuma, com ou sem luz. Uma linha de
código produziu uma conclusão sobre iluminação que quase redesenhou o
projeto.

> A lição não é sobre WebXR: é que **um teste negativo só vale se o que se
> testa estiver ligado**. Antes de concluir sobre o mundo, confira se o
> aparelho foi de fato solicitado.

**A luz continua importando**, mas por outro motivo: ela é cenografia da
obra, e o `fontes/luz-segue-cena.mjs` já a faz seguir o cenário e subir nas
três janelas de interação. Isso agora é escolha estética, não muleta
técnica.

### A lâmpada da sala (12/09)

A lâmpada do estande é uma Tuya RGBW (`LDV SMART+ CLA60`), falada pelo
estúdio do v1 (`Downloads/claude/raizes-display`, `node estudio.mjs`, porta
8600 — subir com `QUEST=<serial do cabo>` para ele não procurar o headset
pela Wi-Fi). A ponte `fontes/luz-segue-cena.mjs` lê o cenário da obra pelo
DevTools do Quest (`adb forward tcp:9222 localabstract:chrome_devtools_remote`)
e pinta a lâmpada. O `window.raizes.onde()` passou a existir **também na
obra publicada** (só ele: leitura), porque no estande a obra mora no
aparelho e vem do endereço publicado.

**O defeito que a desligava do cenário:** a lâmpada tem dois modos, e o
brilho (`dps 22`) só vale no branco. Subir o brilho na janela a trocava para
BRANCO, e ela ficava branca até o cenário seguinte. Agora tudo vai pela cor:
o escuro e o claro são o *valor* da mesma cor, e ela nunca sai do modo de cor.

**As cores, medidas** (histograma de matiz dos pixels com cor e luz, em três
olhares por cenário na bancada) e o que a lâmpada faz — **saturação cheia
sempre** ("tem que ter cor", olhando a lâmpada em 12/09: a 40% e com a
saturação afrouxada na janela, a cor não se lia):

| cenário | medido | lâmpada | escuro (V 60%) | janela das mãos (V 100%) |
|---|---|---|---|---|
| 1 floresta | azul 220–240° (52–77%) | **verde-turquesa** 170° — "falta um verde turquesa"; é a floresta, e a régua já a chamava de verde-azulado | `#009980` | `#00ffd5` |
| 2 cosmos | azul 200–220° (a galáctica), vermelho e magenta atrás | **violeta** 262° — a assinatura da régua | `#380099` | `#5d00ff` |
| 3 planeta rosa | magenta 320–340° (45–62%) | **rosa-claro** 350°, saturação 50% — "mais avermelhado" e "mais suave, para o branco" (12/09); é a única sem saturação cheia | `#994d59` | `#ff8095` |
| 4 papel | azul-violeta 210–260° (o céu cósmico invertido) | **azul** 230° — o medido; o âmbar de vela "não combina" | `#001999` | `#002aff` |

Na espera do fim (depois dos 10:00) a sala volta ao azul da floresta, pronta
para a próxima pessoa. As janelas de mão (1:50–2:50, 5:30–6:20, 7:30–8:25)
sobem a luz a 100% na mesma cor, para a câmera achar as mãos — **se luz
colorida saturada basta para o rastreio, só o Quest diz**; se não bastar, o
que cede é o valor do escuro, não a cor.

### Conferido no aparelho, pelo cabo (12/09)

Pelo DevTools do Quest (`adb forward tcp:9222 localabstract:chrome_devtools_remote`),
com a obra servida por `estande.py` e o navegador do headset na frente
(`am broadcast -a com.oculus.vrpowermanager.prox_close` finge o capacete na
cabeça; `automation_disable` desfaz):

- OculusBrowser 150 / Chrome 150, Adreno 740, `MAX_TEXTURE_SIZE` 8192 (as
  deusas a 3072 cabem), `navigator.xr` presente, `immersive-ar` suportado;
  o contexto não se perde e `gl.getError()` fica em zero nos quatro cenários.
- **Nenhuma exceção de JavaScript** ao carregar e ao correr os quatro
  cenários. Os únicos erros de console são os 404 dos `/_relato/…`, que
  são o bilhete pela janela: o servidor lê a URL e responde 404 de
  propósito.
- Os quatro cenários desenham na GPU do aparelho (`_fotos/quest-c*.jpg`,
  capturas pelo `Page.captureScreenshot`): floresta, cosmos com as duas
  deusas e o rosa ao alcance, planeta rosa, papel com a integra.
- **Quadros por segundo NA TELA PLANA do navegador** (1280 × 670, um olho
  só): floresta **50**, cosmos 72 (o teto), planeta rosa 69, papel 65. Em
  RM são dois olhos a mais resolução — é esperado cair bem abaixo disto, e
  a floresta é a mais pesada (1,6 milhão de pontos da mata como nuvem, mais
  a mata sólida). **A medida em RM ainda não foi feita**: precisa de alguém
  com o capacete na cabeça para entrar na sessão.

O que continua sem conferência dentro da RM: o toque, o pegar e dimensionar
do rosa, as deusas vistas em estéreo, o buraco no chão, a luz da sala com as
mãos.

### Decidido, mas não construído

- **As interações que faltam.** Pegar um planeta, tocar a mão gigante.
  Tocar o casulo, a mãe, os cogumelos e a borboleta já respondem (seção 8,
  "O toque e o som") — **nada disso foi visto dentro do Quest ainda**.
- **Um sinal de que uma coisa pode ser tocada.** Uma respiração, um brilho.
- **As borboletas circundando**, depois de tocar o casulo.
- **As deusas em vídeo**, em bumerangue. **Um por cenário, nunca dois ao
  mesmo tempo** — os cenários não se sobrepõem, então o decodificador do
  Quest nunca vê dois. E **nenhum vídeo começa sozinho: só ao toque.**
- **A mão gigante.** Não existe quadro dela na Odara. Precisa de imagem.
- **O céu marmorizado e estrelado do planeta rosa**, no Midjourney. Quando
  sair, vale mapear só no hemisfério de cima: no cenário 3 a água tapa
  **39%** da imagem, que nunca é lida.

### Em aberto, e é decisão de vocês

- Onde as partículas caem: só no polígono do chão, ou por todo o volume?
- Os asteroides são cinzas? (agora estão com o mármore violeta)
- O prazo do FIL. Tudo se dimensiona a partir dele.

---

## 12. Onde continuar

Este projeto tem dois chats: **um de código e outro de conteúdo.** Este é o
de código. Levando este arquivo para um chat novo, ele tem o suficiente para
continuar sem perguntar nada.

Se algo não bater com o que está aqui, **o código manda** — e este arquivo
precisa ser corrigido.
