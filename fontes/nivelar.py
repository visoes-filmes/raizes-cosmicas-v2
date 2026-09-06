# -*- coding: utf-8 -*-
"""
Costura de panorama por NIVELAMENTO (a mesma familia de tecnica que o
Photoshop usa pra juntar fotos numa panoramica).

Em vez de espelhar (que cria simetria de borboleta), eu deslizo a COR das
duas bordas ate elas se encontrarem no meio do caminho, deixando a textura
original intacta. Some so a diferenca de tom, nao o desenho.
"""
import sys
import numpy as np
from PIL import Image


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def nivelar_bordas(a, largura):
    """Puxa as duas bordas pro tom medio entre elas, com peso que some ao
    entrar na imagem. Preserva 100% da textura: so corrige o tom."""
    H, W, C = a.shape
    out = a.copy()

    esquerda = a[:, 0, :]      # (H, C)
    direita = a[:, -1, :]
    meio = (esquerda + direita) / 2.0

    corr_esq = meio - esquerda     # o quanto a borda esquerda precisa mudar
    corr_dir = meio - direita

    for i in range(largura):
        peso = smoothstep(1.0 - i / largura)
        out[:, i, :] += corr_esq * peso
        out[:, W - 1 - i, :] += corr_dir * peso
    return out


def fundir_junta(a, largura):
    """Suaviza a diferenca de DESENHO (nao so de tom) bem na junta,
    cruzando uma faixa estreita com o outro lado."""
    H, W, C = a.shape
    out = a.copy()
    for i in range(largura):
        t = smoothstep(0.5 * (1.0 - i / largura))   # no maximo 0.5: nunca troca de lado
        out[:, i, :] = (1 - t) * a[:, i, :] + t * a[:, W - 1 - i, :]
        out[:, W - 1 - i, :] = (1 - t) * a[:, W - 1 - i, :] + t * a[:, i, :]
    return out


def convergir_polos(a, raio_base=2.0):
    H, W, C = a.shape
    out = a.copy().astype(np.float64)
    for y in range(H):
        theta = np.pi * (y + 0.5) / H
        s = max(np.sin(theta), 1e-6)
        raio = int(min(raio_base * (1.0 / s - 1.0), W // 2))
        if raio < 1:
            continue
        linha = out[y]
        est = np.concatenate([linha[-raio:], linha, linha[:raio + 1]], axis=0)
        acum = np.concatenate([np.zeros((1, C)), np.cumsum(est, axis=0)], axis=0)
        larg = 2 * raio + 1
        out[y] = (acum[larg:larg + W] - acum[0:W]) / larg
    return out


def relatorio(a, titulo):
    H, W, _ = a.shape
    diffs = np.abs(a[:, 1:, :] - a[:, :-1, :]).mean(axis=(0, 2))
    base = float(np.median(diffs))
    costura = float(np.abs(a[:, 0, :] - a[:, -1, :]).mean())
    print(f"  {titulo:26} costura {costura:7.2f}  normal {base:5.2f}  "
          f"razao {costura/base if base else 0:6.2f}x  "
          f"topo {float(a[0].std(axis=0).mean()):5.2f}  "
          f"base {float(a[-1].std(axis=0).mean()):5.2f}")


src, dst = sys.argv[1], sys.argv[2]
LARG_NIVEL = int(sys.argv[3]) if len(sys.argv) > 3 else 260
LARG_JUNTA = int(sys.argv[4]) if len(sys.argv) > 4 else 70

a = np.asarray(Image.open(src).convert("RGB")).astype(np.float64)
relatorio(a, "entrada")
a = nivelar_bordas(a, LARG_NIVEL)
relatorio(a, f"nivelado ({LARG_NIVEL}px)")
a = fundir_junta(a, LARG_JUNTA)
relatorio(a, f"junta fundida ({LARG_JUNTA}px)")
a = convergir_polos(a, 2.0)
relatorio(a, "polos convergidos")

Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(dst)
print(f"\nSalvo: {dst}")
