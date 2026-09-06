# -*- coding: utf-8 -*-
"""As seis do Midjourney viram peles de esfera.

A pele de um planeta e lida como equirretangular: o eixo horizontal da a
volta no equador, o vertical vai de polo a polo. Duas consequencias:

  1. A EMENDA HORIZONTAL PRECISA FECHAR. Se a coluna da direita nao
     continua a da esquerda, sai uma costura vertical no planeta — e ela
     nao passa despercebida, porque o planeta gira e a costura passa pela
     frente uma vez por volta.

  2. O VERTICAL NAO PRECISA. Os polos convergem para um ponto, e o que
     sobra la e sempre uma media. Por isso nao mexo neles.

Fecho a emenda por SOBREPOSICAO: uma faixa da borda esquerda entra por
cima da direita com uma rampa suave, e o pedaco consumido sai do fim. O
que sobra e uma imagem menor cuja ultima coluna e a vizinha da primeira no
original — continua, sem espelho e sem borrao.
"""
import os
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(AQUI, 'planetas')
SAIDA = os.path.join(AQUI, 'peles')
os.makedirs(SAIDA, exist_ok=True)

LARG, ALT = 1024, 512          # potencia de dois nos dois lados: o mipmap exige

# imagem -> destino, e o porque da escolha
ALVOS = [
    ('mj1.jpg', 'pele-sol',        'coral saindo de um ponto: e um sol'),
    ('mj2.jpg', 'pele-rosa',       'a nebulosa rosa, no planeta rosa'),
    ('mj3.jpg', 'pele-asteroide',  'marmore violeta e coral, para tirar o cinza'),
    ('mj4.jpg', 'pele-verde',      'a samambaia magenta e ciano tem o verde'),
    ('mj5.jpg', 'pele-agua',       'azul profundo com o olho no meio'),
    ('mj6.jpg', 'pele-fogo',       'as veias de lava'),
]


def suave(t):
    """Rampa com derivada zero nas pontas — sem quina, sem listra."""
    return t * t * (3.0 - 2.0 * t)


def fechar_horizontal(im, fracao=0.18):
    """Sobrepoe a borda esquerda na direita e devolve a imagem menor."""
    W, H = im.size
    b = max(8, int(W * fracao))
    esq = im.crop((0, 0, b, H))
    dir_ = im.crop((W - b, 0, W, H))

    # mascara: 0 na esquerda da faixa (fica a direita original),
    #          255 na direita da faixa (fica a esquerda original)
    masc = Image.new('L', (b, H))
    linha = [int(255 * suave(x / (b - 1.0))) for x in range(b)]
    masc.putdata(linha * H)

    fundido = Image.composite(esq, dir_, masc)
    out = im.copy()
    out.paste(fundido, (W - b, 0))
    # o pedaco que a esquerda ocupou agora esta repetido: tira do inicio
    return out.crop((b, 0, W, H))


def medir_emenda(im):
    """Diferenca media entre a primeira e a ultima coluna, 0 a 255."""
    W, H = im.size
    a = list(im.crop((0, 0, 1, H)).convert('RGB').getdata())
    z = list(im.crop((W - 1, 0, W, H)).convert('RGB').getdata())
    return sum(abs(p[c] - q[c]) for p, q in zip(a, z) for c in range(3)) / (H * 3.0)


for arq, nome, motivo in ALVOS:
    im = Image.open(os.path.join(ORIG, arq)).convert('RGB')
    antes = medir_emenda(im)
    im = fechar_horizontal(im)
    im = im.resize((LARG, ALT), Image.LANCZOS)
    depois = medir_emenda(im)
    caminho = os.path.join(SAIDA, nome + '.jpg')
    im.save(caminho, quality=90, optimize=True)
    kb = os.path.getsize(caminho) // 1024
    print('%-16s %4d KB   emenda %5.2f -> %4.2f   %s'
          % (nome, kb, antes, depois, motivo))
