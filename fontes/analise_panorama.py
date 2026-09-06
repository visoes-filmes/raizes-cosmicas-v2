# -*- coding: utf-8 -*-
"""
Diagnostico de panorama equirretangular.
Mede: (1) descontinuidade da costura horizontal, (2) convergencia dos polos.
Gera a versao deslocada (offset) pronta pra correcao no Photoshop.
"""
import sys
import numpy as np
from PIL import Image

src = sys.argv[1]
out_offset = sys.argv[2]

im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float64)
H, W, _ = a.shape
print(f"Dimensoes: {W}x{H}  (proporcao {W/H:.3f} : 1)")
print()

# ---------------------------------------------------------------
# 1) DESCONTINUIDADE DA COSTURA
# Comparo a diferenca entre a ultima e a primeira coluna (que se
# encostam numa esfera) com a diferenca media entre colunas vizinhas
# normais. Se a costura for muito maior que a media, ela aparece.
# ---------------------------------------------------------------
diffs = np.abs(a[:, 1:, :] - a[:, :-1, :]).mean(axis=(0, 2))  # por par de colunas
baseline = float(np.median(diffs))
seam = float(np.abs(a[:, 0, :] - a[:, -1, :]).mean())

print("== COSTURA HORIZONTAL (esquerda encontra direita) ==")
print(f"  diferenca media entre colunas vizinhas normais : {baseline:6.2f}")
print(f"  diferenca na costura (col 0 vs col {W-1})        : {seam:6.2f}")
print(f"  razao costura/normal                           : {seam/baseline:6.2f}x")
if seam / baseline > 3:
    print("  -> COSTURA VISIVEL. Precisa correcao.")
elif seam / baseline > 1.5:
    print("  -> Costura leve, perceptivel em area clara.")
else:
    print("  -> Costura aceitavel.")
print()

# Onde a costura mais dói: por faixa de altura
print("  Onde a costura mais aparece (por faixa vertical):")
bands = 6
for i in range(bands):
    y0, y1 = i * H // bands, (i + 1) * H // bands
    d = float(np.abs(a[y0:y1, 0, :] - a[y0:y1, -1, :]).mean())
    lum = float(a[y0:y1, [0, -1], :].mean())
    tag = "CRITICO" if d > baseline * 4 else ("atencao" if d > baseline * 2 else "ok")
    print(f"    y {y0:4d}-{y1:4d} | dif {d:6.2f} | brilho {lum:6.2f} | {tag}")
print()

# ---------------------------------------------------------------
# 2) CONVERGENCIA DOS POLOS
# Numa esfera, a linha do topo inteira vira UM unico ponto (zenite),
# e a de baixo idem (nadir). Se essas linhas tiverem cores variadas,
# o polo vira um redemoinho borrado quando a pessoa olha pra cima.
# ---------------------------------------------------------------
print("== POLOS (topo = zenite, base = nadir) ==")
for nome, row in (("topo ", a[0]), ("base ", a[-1])):
    desvio = float(row.std(axis=0).mean())
    media = float(row.mean())
    tag = "OK, converge" if desvio < 12 else ("aceitavel" if desvio < 30 else "VAI BORRAR")
    print(f"  {nome}: variacao de cor {desvio:6.2f} | brilho medio {media:6.2f} | {tag}")
print()

# ---------------------------------------------------------------
# 3) MAPA DE BRILHO POR COLUNA
# Serve pra saber onde estao as areas escuras (onde emenda some).
# ---------------------------------------------------------------
col_lum = a.mean(axis=(0, 2))
print("== BRILHO POR REGIAO HORIZONTAL (12 fatias) ==")
slices = 12
for i in range(slices):
    x0, x1 = i * W // slices, (i + 1) * W // slices
    m = float(col_lum[x0:x1].mean())
    bar = "#" * int(m / 4)
    print(f"  x {x0:4d}-{x1:4d} | {m:6.2f} {bar}")
print()

# ---------------------------------------------------------------
# 4) GERA A VERSAO DESLOCADA
# Deslocar meia largura leva a costura pro centro da tela, onde da
# pra ver e corrigir. Depois de corrigida, desloca de volta e as
# bordas ficam perfeitas.
# ---------------------------------------------------------------
half = W // 2
rolled = np.roll(a, half, axis=1).astype(np.uint8)
Image.fromarray(rolled).save(out_offset)
print(f"Gerado (costura no centro, x={half}): {out_offset}")
