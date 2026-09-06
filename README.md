# Raízes Cósmicas v2

**v2** para não confundir com o `floresta-psicodelica-ar`, que também se
chama Raízes Cósmicas: são a mesma obra, construídas em dois lugares.

Obra em **realidade mista** para Meta Quest 3, em WebXR. Abre no navegador do
headset — não precisa instalar nada.

Visões Filmes · FIL 2026

**No ar:** <https://visoes-filmes.github.io/raizes-cosmicas-v2/>
É esse o endereço que se digita no navegador do Quest 3.

---

## O que já roda

O `index.html` é a cena de realidade mista da primeira parte: a pintura
projetada como cúpula em volta, a nuvem cósmica marmorizada, as raízes
procedurais e a poeira. Um arquivo só, autossuficiente, com as imagens e o
som embutidos — abre offline, com um clique.

Depois da primeira abertura ele fica **guardado no aparelho** por um service
worker: abre sem rede, e não trava no meio porque o wi-fi oscilou. Numa feira
isso não é conforto, é o que decide se a obra funciona.

Publicado em GitHub Pages, é também o endereço que se abre **dentro do
Quest 3**: lá o botão *Entrar em RM* troca o cinza pela sua sala de verdade,
vista pelas câmeras.

### A partitura

A obra corre num relógio de dez minutos, e cada momento acontece
**independente de a pessoa interagir**: há uma janela para ela agir, e
passada a janela a narrativa segue. Quem interage conduz, quem não interage
é conduzido — e ninguém trava a fila.

A barra na parte de baixo é o andaime de ateliê: cada faixa é um momento,
com a largura da duração real e a cor do cenário a que pertence. As marcas
laranja são as três **janelas de interação**. Clicar em qualquer ponto salta
para lá — sem isso não haveria como trabalhar num cenário que só acontece
aos 6:30.

Ela some com o resto pela tecla **H**.

### Os astros

O Sol e os quatro planetas do cenário 2. Uma esfera só de geometria,
desenhada cinco vezes com centro, raio e pele diferentes — não há
*instancing* no WebGL 1 sem extensão, e nem faz falta: cinco chamadas de
desenho não custam nada perto do que a nuvem já faz por pixel.

A pele sai das texturas recortadas da pintura. Não há material inventado
aqui: é a Odara envolvendo uma esfera.

A coreografia é a do roteiro, e é uma sequência de estados, não uma órbita
contínua: os planetas surgem em volta do Sol, **descem** e vêm girar em
volta da pessoa, e depois **se dispersam pelo céu com espaço entre si** —
porque amontoados ela não consegue lidar com nenhum. O planeta que aceita
entrada é o único que não se afasta: **a distância é o convite**.

Eles são desenhados **antes da nuvem** e escrevem profundidade. Na ordem
inversa, um planeta apagaria a nuvem que passasse na frente dele — a nuvem
não escreve profundidade, então quem vem depois vence. E só escrevem
profundidade quando já estão praticamente opacos: enquanto nascem, esconder
o que está atrás por trás de uma coisa que mal se vê seria pior.

### A água

O cenário 3. Uma lâmina na altura da cintura, e a pessoa dentro dela.

Em realidade mista este é o efeito mais forte que a obra tem — e não por
causa da água: é porque **metade da imagem passa a ser a pessoa**. As pernas
dela continuam ali, vistas pelas câmeras, agora sob uma superfície que as
ondula. Não há efeito gráfico que compita com o próprio corpo.

Por isso a lâmina é **translúcida**. Opaca, ela esconderia as pernas e o
feito se perderia.

O reflexo é reflexo de verdade: o raio que vem do olho bate na lâmina e
sobe, então basta espelhar a componente vertical da direção e ler o céu ali
— e é por isso que ele acompanha a cabeça. O Fresnel faz o resto: olhando
quase a pino a água é transparente, de raspão vira espelho. É o que faz uma
superfície parecer molhada em vez de pintada.

### As camadas de papel

O cenário 4. Formas recortadas, uma atrás da outra, flutuando no cosmos.

O que faz isto funcionar não é o desenho, é a **paralaxe**: cada camada
está a uma distância diferente, então mover a cabeça as desloca umas em
relação às outras e o espaço aparece sozinho. É a coisa mais barata que se
pode fazer num headset — planos e uma textura — e uma das que mais
convence, porque a profundidade não está desenhada, está acontecendo.

O recorte não vem da imagem: é feito no shader, por uma borda rasgada
gerada na hora. Assim cada camada tem silhueta própria, e nenhuma repete a
da outra — que é o que denunciaria que são a mesma imagem várias vezes.

Elas são desenhadas **do fundo para a frente**, e isso é obrigatório: não
escrevem profundidade (escrever cortaria a franja de quem vem atrás), então
a ordem de desenho *é* a ordem de profundidade.

### Mipmap

As texturas carregadas geram mipmap e usam filtro trilinear. Sem isso, uma
imagem de 2048×1024 vista de raspão faz a placa buscar texels distantes a
cada pixel — o cache nunca acerta, e o céu ainda **cintila**, porque cada
pixel pega um texel sorteado em vez da média da região que ele cobre.

Custa um terço a mais de memória. Em troca, o custo por pixel deixa de
depender do ângulo e o serrilhado do céu some. Só funciona porque as duas
medidas são potência de dois.

### Os céus

Os três céus estão embutidos, e o shader **mistura dois** durante a passagem
entre cenários. Trocar de imagem de um quadro para o outro seria o único
corte duro da obra; misturando, a passagem tem a mesma natureza de tudo o
mais aqui, que é metamorfose.

No cenário 4 o céu do primeiro é lido **de cabeça para baixo** — a floresta
de onde se partiu reaparece sob os pés. Custa uma multiplicação, não uma
imagem nova.

### O som

**Desligado por padrão enquanto se constrói**, porque a trilha entrando a
cada recarga atrapalha quem está trabalhando. Antes do FIL isto volta a ser
`true` em `somLigado` — é a única coisa que muda.

---

Controles pela tecla **H** ou pelo botão no canto. O número no canto inferior
direito são os quadros por segundo — fica laranja abaixo de 30, que é o aviso
de que a máquina não está dando conta.

---

## A obra

Quatro cenários em dez minutos, numa área caminhável de 3 × 3 m:

1. **A floresta cósmica** — a sala real, o céu já estrelado; as estrelas caem
   e de onde tocam nasce a floresta. Numa árvore, o casulo.
2. **O sistema solar** — as estrelas acendem uma a uma até o Sol; os planetas
   descem e vêm orbitar a pessoa.
3. **O planeta rosa** — aquático, água na cintura, a deusa vermelha na margem.
4. **O mundo de papel** — camadas recortadas flutuando no cosmos, e embaixo a
   primeira floresta invertida.

Nenhuma passagem tem corte: tudo é metamorfose, como na animação que deu
origem a isto.

---

## Os arquivos

```
index.html              a cena de realidade mista, pronta para o headset
assets/ceus/            as panorâmicas 360°, todas 2048×1024
assets/texturas/        texturas que repetem sem emenda nos dois eixos
assets/audio/           a trilha, já cortada para fechar em laço
fontes/                 os programas que geram tudo o que está em assets/
sw.js                   guarda a obra no aparelho, para abrir sem rede
manifest.webmanifest    permite instalar no headset como aplicativo
```

**Os céus já são consumidos pelo `index.html`** (vão embutidos nele). As texturas ainda não: Ele é a primeira
parte da obra e já traz as suas imagens embutidas. O que está em `assets/`
é material tratado esperando os cenários 2, 3 e 4, que ainda não existem.

**Por que 2048×1024.** O WebGL 1 só aceita repetir uma textura — que é o que
faz a esfera fechar a volta — se as duas medidas forem potência de dois. Fora
disso a textura sai preta, sem erro nenhum no console.

---

## As panorâmicas

Nenhuma delas sai costurada da ferramenta que a gerou. Uma imagem 2:1 tem a
borda esquerda e a direita se encostando quando envolve a esfera, e os polos
convergindo num ponto — e as duas coisas denunciam a emenda se não forem
tratadas.

O tratamento está em `fontes/nivelar.py`, e é de duas partes:

**Nivelamento das bordas.** Em vez de espelhar — o que criaria uma simetria de
borboleta bem no meio do campo de visão — as duas bordas escorregam de tom até
se encontrarem no meio do caminho, ao longo de 260 px. A textura fica
intocada; só a diferença de tom some.

**Convergência dos polos.** O borrão horizontal cresce com `1/sen(θ)`: zero no
equador, a linha inteira no polo. É o mesmo fator pelo qual a projeção
equirretangular estica a imagem ali, então o borrão desfaz exatamente o que a
esfera vai fazer.

O `fontes/analise_panorama.py` mede o resultado. Números destas:

| céu | costura | polos |
|---|---|---|
| floresta | 47,92 → 0,10 | 4,42 e 67,19 → 0,00 e 0,04 |
| cósmico | 18,15 → 0,08 | 37,08 e 23,45 → 0,02 |
| rosa | 32,58 → 0,11 | → 0,01 |

A costura é medida contra a diferença média entre colunas vizinhas normais:
uma razão perto de 1 significa que a emenda não se distingue do resto da
imagem.

---

## As texturas

Não são geradas nem redesenhadas: são **recorte da pintura real**, tratado
para emendar sozinho nos dois eixos (`fontes/texturas_odara.py`).

A região de cada recorte é escolhida automaticamente — procuro o trecho mais
uniforme e ao mesmo tempo mais detalhado do quadro. Detalhe garante que há
pintura ali; uniformidade garante que a estatística não muda de um canto ao
outro, que é o que faz o azulejo não denunciar onde ele começa.

As cinco tiradas dos quadros da Odara emendam de 40–66 para **0,00** nos
dois eixos.

A `tex-raiz` é a exceção, e de propósito: ela repete **só ao longo do galho**,
que é o único eixo em que uma casca precisa emendar. Na horizontal ela não
fecha, e não precisa.

---

## A trilha

O arquivo original tinha 2,5 s de entrada e um desvanecimento de 5 s no fim.
Em laço, isso seria um buraco de silêncio a cada volta, marcando o compasso da
repetição — a coisa mais denunciável numa instalação.

As duas pontas mortas foram removidas e o fim atravessa o começo num
cruzamento de 5 s, então o arquivo fecha em si mesmo e `loop` basta. Ficaram
71 s, com o nível dos 2 s iniciais e dos 2 s finais praticamente iguais.

Nenhum navegador deixa som começar sozinho, só depois de um gesto da pessoa —
por isso a trilha espera o primeiro toque, clique ou tecla. No Quest, o
próprio clique em *Entrar em RM* já serve.

---

## Refazer os assets

```bash
python fontes/nivelar.py entrada.png saida.png 260 70
python fontes/analise_panorama.py saida.png offset.png
python fontes/texturas_odara.py

python fontes/montar_mr.py   assets/texturas/tex-raiz.png   assets/ceus/ceu-floresta-2048.png   index.html   assets/audio/trilha-loop.mp3
```

Os caminhos são relativos a onde o comando é dado, não a onde o script mora.

O `montar_mr.py` embute as imagens e o som no HTML e recusa a compilação se
achar uma crase solta fora de um shader — uma crase perdida num comentário de
GLSL fecha o *template literal* do JavaScript no meio e quebra o arquivo
inteiro, com o erro aparecendo longe dali. Já aconteceu duas vezes.
