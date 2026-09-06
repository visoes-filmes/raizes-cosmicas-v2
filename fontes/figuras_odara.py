# -*- coding: utf-8 -*-
"""
Recorta as figuras da Odara em PNG com alfa.

Nao ha mascara feita a mao: as figuras sao CLARAS sobre fundo escuro, entao
a propria luminancia da o recorte. E o que sobra na borda — o halo claro que
um recorte por luminancia sempre deixa — nao e defeito aqui: e a ORLA CLARA
que a Crisia pediu, e e o que faz a figura se destacar contra o ceu em vez
de sumir nele.

Depois do recorte, corto na caixa do que sobrou: sem isso a figura viria
nadando num quadro cheio de transparencia, e o plano que a carrega teria
que ser grande a toa.
"""
import io
import os
import numpy as np
from PIL import Image

SRC = r"C:\Users\crisi\Desktop\Odara - Cosmos - frames\01_frames_chave"
AQUI = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(AQUI, 'figuras')
os.makedirs(DEST, exist_ok=True)

# A CAIXA VEM A MAO, e nao por preguica de automatizar: estes quadros nao
# sao "figura sobre preto", sao pinturas inteiras com uma figura dentro. O
# fundo tambem e claro e denso, entao nenhum criterio de luminancia ou de
# vizinhanca separa uma coisa da outra. Dizer onde a figura esta e a unica
# informacao que a imagem nao carrega sozinha.
#
# quadro, nome, caixa (x0,y0,x1,y1 em fracao), corte0, corte1, ganho
ALVOS = [
    ('chave_05', 'galactico',      (0.30, 0.04, 0.70, 1.00), 0.17, 0.47, 1.06),
    ('chave_23', 'deusa-vermelha', (0.17, 0.08, 0.63, 1.00), 0.14, 0.42, 1.10),
    ('t_072',    'deusa-integra',  (0.27, 0.00, 0.73, 0.98), 0.16, 0.46, 1.04),
    # A borboleta e o unico caso em que o PRETO e desenho, nao fundo: as
    # asas dela sao escuras com anel branco. Corte alto apagaria a asa.
    # Por isso o corte dela e baixo, e a caixa mais justa para compensar
    # o fundo que entra junto.
    ('t_005',    'borboleta',      (0.31, 0.10, 0.71, 0.72), 0.05, 0.22, 1.14),
]

LADO = 512

for quadro, nome, caixa, c0, c1, ganho in ALVOS:
    im = Image.open(os.path.join(SRC, quadro + '.jpg')).convert('RGB')
    W, H = im.size
    im = im.crop((int(caixa[0]*W), int(caixa[1]*H),
                  int(caixa[2]*W), int(caixa[3]*H)))
    a = np.asarray(im).astype(np.float64) / 255.0

    lum = a[:, :, 0]*0.299 + a[:, :, 1]*0.587 + a[:, :, 2]*0.114

    # alfa por luminancia, com transicao macia: corte duro daria a serra
    # que a Crisia nao quer ver em lugar nenhum
    al = np.clip((lum - c0) / max(c1 - c0, 1e-6), 0.0, 1.0)
    al = al * al * (3.0 - 2.0 * al)

    # DENSIDADE. Um respingo e claro e SOZINHO; uma figura e clara e
    # cercada de claro. Borrando o alfa e multiplicando de volta, o que
    # nao tem vizinhanca desaparece — e sao as estrelas espalhadas que
    # mantinham a caixa aberta no quadro inteiro, deixando a figura
    # pequena dentro da textura e cercada de sujeira.
    from PIL import ImageFilter
    vizinhanca = np.asarray(
        Image.fromarray((al * 255).astype(np.uint8))
             .filter(ImageFilter.GaussianBlur(14))
    ).astype(np.float64) / 255.0
    densa = np.clip((vizinhanca - 0.10) / 0.22, 0.0, 1.0)
    densa = densa * densa * (3.0 - 2.0 * densa)
    al = al * densa

    # caixa do que sobrou, com folga
    ys, xs = np.where(al > 0.10)
    if len(xs) == 0:
        print(f'  {nome}: nada acima do corte — pulei')
        continue
    x0, x1 = max(0, xs.min() - 12), min(a.shape[1], xs.max() + 12)
    y0, y1 = max(0, ys.min() - 12), min(a.shape[0], ys.max() + 12)

    rgb = np.clip(a[y0:y1, x0:x1] * ganho, 0, 1)
    aa = al[y0:y1, x0:x1]

    # ORLA CLARA: onde o alfa esta a meio caminho, a cor puxa para o claro.
    # E o contorno luminoso que a animacao tem em tudo, e o que separa a
    # figura do fundo sem precisar de sombra.
    borda = (aa * (1.0 - aa) * 4.0) ** 1.5
    rgb = np.clip(rgb + borda[:, :, None] * 0.30, 0, 1)

    h, w = aa.shape
    lado = max(h, w)
    quad_rgb = np.zeros((lado, lado, 3))
    quad_a = np.zeros((lado, lado))
    oy, ox = (lado - h) // 2, (lado - w) // 2
    quad_rgb[oy:oy+h, ox:ox+w] = rgb
    quad_a[oy:oy+h, ox:ox+w] = aa

    saida = np.dstack([quad_rgb, quad_a])
    img = Image.fromarray((saida * 255).astype(np.uint8), 'RGBA')
    img = img.resize((LADO, LADO), Image.LANCZOS)
    alvo = os.path.join(DEST, 'fig-' + nome + '.png')
    img.save(alvo)
    cobertura = float((quad_a > 0.5).mean()) * 100
    print(f'  {nome:16} de {quadro:9} — recorte {w}x{h}, '
          f'{cobertura:.0f}% do quadro tem figura')
