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

> **numpy não é necessário** para reconstruir. Alguns scripts antigos em
> `fontes/` (`costurar_esfera.py`, `nivelar.py`) usam numpy, mas eles já
> fizeram o trabalho deles: os céus prontos estão em `assets/ceus/`. Só
> precisará de numpy se for **refazer um céu do zero**.

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
│   │   ├── fig-galactico.png          O ser galáctico (quadro chave_05).
│   │   ├── fig-deusa-vermelha.png     A deusa vermelha (chave_23).
│   │   ├── fig-deusa-integra.png      A deusa que integra tudo (t_072).
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
| 4:10 | 2 | eles se dispersam pelo céu e esperam |
| 4:40 | 2 | os buracos negros aparecem |
| 5:00 | 2 | o balé dos planetas não escolhidos |
| 5:30 | 2 | **janela** — pegar e dimensionar um planeta |
| 6:20 | 2 | entrar no planeta |
| 6:30 | 3 | o planeta rosa; a água sobe até a cintura |
| 7:05 | 3 | a deusa vermelha na margem, com reflexo |
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
  1: { ceu:0, tinta:0.85, nuvem:0.55, ... ini:0.10, fim:0.80, inverter:0 },
  2: { ceu:1, tinta:0.96, nuvem:0.18, ... ini:0.00, fim:0.30, inverter:0 },
  3: { ceu:2, tinta:0.92, nuvem:0.42, ... ini:0.28, fim:0.95, inverter:0 },
  4: { ceu:1, tinta:0.82, nuvem:0.30, ... ini:0.02, fim:0.50, inverter:1 },
};
```

- `ceu` — qual dos três céus (0 floresta, 1 cósmico, 2 rosa)
- `tinta` — quanto o céu aparece no total
- `ini` / `fim` — **o degradê vertical**, em fração do pé-direito. O céu é
  cheio no teto e some ao descer. No cenário 3 ele só começa a 0,84 m,
  porque a água tapa o resto.
- `inverter` — o cenário 4 lê o céu **de cabeça para baixo**. É o que faz a
  floresta do primeiro cenário reaparecer sob os pés no último, sem custar
  uma imagem nova.

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

### Os dez programas de shader

`progRaiz` (raízes e árvore) · `progSala` (a cúpula) · `progFig` (a nuvem
marmorizada) · `progPo` (a poeira) · `progAssa` (assa o atlas de tinta) ·
`progAstro` (sol, planetas, asteroides) · `progPapel` (as sete camadas) ·
`progAgua` (a lâmina) · `progFigu` (as figuras recortadas) · `progBolha`
(buracos negros e seres do mar).

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

### Bloqueado por um teste que ninguém fez ainda

**O rastreamento de mão no escuro.** O Quest se localiza por visão, e a mão
nua é a primeira coisa a falhar com pouca luz. **Toda a interação depende
dela.**

> **O teste mais barato do projeto:** montar 3 × 3 na luz que vocês
> pretendem, pôr o capacete e mexer as mãos por dois minutos. Vinte
> minutos, sem programação. Derruba ou confirma metade do que está escrito
> aqui.

### Decidido, mas não construído

- **As interações.** Tocar o casulo, pegar um planeta, tocar a mão gigante.
  Dependem do teste acima.
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
