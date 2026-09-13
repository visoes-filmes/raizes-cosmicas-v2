# -*- coding: utf-8 -*-
"""O teatro de papel do cenario 4: as camadas de ondas cortadas do quadro.

    python fontes/teatro_de_papel.py

Entra o quadro de 186 s da animacao da Odara ampliado 2x no Magnific
(assets/texturas/papel-teatro-2x.jpg, 2560 x 1424) e os CORTES
(assets/texturas/papel-teatro-cortes.json): uma linha por camada, y por
coluna, tirada das marcacoes que a direcao de arte desenhou sobre o quadro
em 13/09 -- "essas marcacoes coloridas e onde voce tem que cortar, e sao as
camadas" (e "nao e para cortar do jeito que desenhei, e so para entender":
por isso a linha e suavizada, e o que decide a beira de verdade e o preto do
proprio quadro, que vira transparencia).

Saem:
  assets/texturas/papel-teatro-cor.jpg      a cor, faixas empilhadas (atlas)
  assets/texturas/papel-teatro-mascara.png  o alfa de cada faixa (cinza)
  e a tabela CAMADAS_TEATRO impressa, para colar em fontes/mr.template.html

Cada camada e uma faixa do quadro: da linha de corte dela para baixo, ate a
linha da camada da frente (mais uma margem que esmaece). Dentro da faixa, o
que e preto de verdade -- os portais com estrelas -- vira buraco. Nas
laterais a faixa acaba na abertura da caixa: as paredes marmorizadas ficam
de fora.
"""
import io, json, os
import numpy as np
from PIL import Image, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(RAIZ, "assets", "texturas")
QUADRO = os.path.join(TEX, "papel-teatro-2x.jpg")
CORTES = os.path.join(TEX, "papel-teatro-cortes.json")

ORDEM = ["vermelho", "turquesa", "roxo", "azul", "amarelo"]   # do fundo para a frente
CHAO = "branco"                                               # a beira de baixo de todas
ABERTURA = (540, 2030)        # a abertura da caixa, em x (2x): fora dela e parede
FOLGA_BAIXO = 10              # quanto a faixa continua abaixo da linha da frente
ESMAECE = 12                  # e em quantos pixels ela some ali
# (era 80 + 70: a faixa de tras carregava uma copia do alto da faixa da
#  frente, e essa copia aparecia pelos portais e nas beiradas -- "essas
#  falhas assim nao podem existir", 13/09. Agora cada pedaco da pintura
#  existe numa camada so; o que a paralaxe abre entre elas e ar.)


def suave(y, k):
    return np.convolve(np.pad(y, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")


def main():
    im = Image.open(QUADRO).convert("RGB")
    W, H = im.size
    cortes = json.load(open(CORTES, encoding="utf-8"))

    # cada linha vira y por coluna inteira, suavizada; fora do trecho
    # desenhado a camada nao existe (nan)
    linhas = {}
    for nome, pts in cortes.items():
        pts = sorted(pts)
        xs = np.array([p[0] for p in pts], float)
        ys = np.array([p[1] for p in pts], float)
        y = np.full(W, np.nan)
        x0, x1 = int(xs.min()), int(xs.max())
        cols = np.arange(x0, x1 + 1)
        y[x0:x1 + 1] = suave(np.interp(cols, xs, ys), 41)
        linhas[nome] = y

    # o chao vale em toda a largura: fora do trecho, a media
    chao = linhas[CHAO].copy()
    chao[np.isnan(chao)] = np.nanmean(chao)
    chao = suave(chao, 151)          # o chao e reto: a covinha do traco e o reflexo da luz, nao papel

    lum = np.asarray(im.convert("L").filter(ImageFilter.GaussianBlur(2))).astype(float) / 255.0
    yy = np.arange(H)[:, None].astype(float)
    xx = np.arange(W)[None, :].astype(float)

    faixas, tabela = [], []
    for k, nome in enumerate(ORDEM):
        topo = linhas[nome]
        existe = ~np.isnan(topo)
        # a beira de baixo: a primeira linha da frente que existe nesta coluna; senao o chao
        fundo = chao.copy()
        coberta = np.zeros(W, bool)          # ha camada na frente nesta coluna?
        for j in range(k + 1, len(ORDEM)):
            f = linhas[ORDEM[j]]
            tem = ~np.isnan(f)
            fundo[tem] = np.minimum(fundo[tem], f[tem])
            coberta |= tem
        t = np.where(existe, topo, H)[None, :]
        b = fundo[None, :]
        # alfa: 1 abaixo do corte (3 px de macio). Abaixo da beira da frente a
        # faixa continua um pouco e esmaece -- e o que a paralaxe revela --,
        # mas no chao do teatro ela acaba: o piso nao e papel
        folga = np.where(coberta, FOLGA_BAIXO, 10.0)[None, :]
        esmaece = np.where(coberta, ESMAECE, 60.0)[None, :]
        a = np.clip((yy - t + 1.5) / 3.0, 0, 1)
        a *= 1.0 - np.clip((yy - (b + folga - esmaece)) / esmaece, 0, 1)
        # so onde a camada existe, com 24 px de macio nas pontas do trecho
        xe = np.nonzero(existe)[0]
        if len(xe):
            x0, x1 = xe.min(), xe.max()
            a *= np.clip((xx - x0) / 24.0, 0, 1) * np.clip((x1 - xx) / 24.0, 0, 1)
        # a abertura da caixa: as paredes ficam de fora, e o teatro se
        # desfaz devagar nas laterais -- sem isso ele acaba numa reta
        # vertical e le como imagem colada no cenario (13/09)
        a *= np.clip((xx - ABERTURA[0]) / 160.0, 0, 1) * np.clip((ABERTURA[1] - xx) / 160.0, 0, 1)
        # os portais: o preto de verdade vira buraco (as estrelas ja foram
        # borradas, entao nao sobram pontos soltos)
        a *= np.clip((lum - 0.05) / 0.09, 0, 1)
        # a faixa do atlas: onde ha alfa
        linhas_com = np.nonzero(a.max(axis=1) > 0.01)[0]
        y0, y1 = int(linhas_com.min()), int(linhas_com.max()) + 1
        faixas.append((nome, y0, y1, a[y0:y1]))
        print(f"  {nome:9} linhas {y0}-{y1}  ({y1 - y0} px)")

    altura = sum(y1 - y0 for _, y0, y1, _ in faixas)
    cor = Image.new("RGB", (W, altura))
    masc = Image.new("L", (W, altura))
    v = 0
    for nome, y0, y1, a in faixas:
        h = y1 - y0
        cor.paste(im.crop((0, y0, W, y1)), (0, v))
        masc.paste(Image.fromarray((a * 255).astype(np.uint8), "L"), (0, v))
        tabela.append({"nome": nome, "v0": v / altura, "v1": (v + h) / altura,
                       "topo": y0, "altura": h})
        v += h
    cor.save(os.path.join(TEX, "papel-teatro-cor.jpg"), quality=95)
    masc.save(os.path.join(TEX, "papel-teatro-mascara.png"), optimize=True)
    print(f"atlas {W} x {altura}")
    print("\n// CAMADAS_TEATRO -- gerado por fontes/teatro_de_papel.py; topo e altura em pixels do quadro 2x (2560 x 1424)")
    for c in tabela:
        print(f"  {{ nome:'{c['nome']}', v0:{c['v0']:.4f}, v1:{c['v1']:.4f}, topo:{c['topo']}, altura:{c['altura']} }},")


if __name__ == "__main__":
    main()
