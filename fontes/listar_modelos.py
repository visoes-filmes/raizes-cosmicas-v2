# -*- coding: utf-8 -*-
"""A listagem dos modelos 3D: o que existe, como e feito, e como entra na obra.

    python fontes/listar_modelos.py

Escreve dois tipos de coisa:

  MODELOS-3D.md      a tabela -- triangulos, pecas, peso no nuvens.js, onde
  _fotos/modelagem-*.png   as folhas de contato, para VER a modelagem

POR QUE VER, E NAO SO CONTAR. Numero nao diz se um modelo esta inteiro.
Duas vezes hoje a conta parecia certa e a forma estava errada: o coral
chegava a obra como oito varetas soltas (o conversor guardava as oito
maiores pecas de cinquenta), e as suas pecas normalizadas uma a uma
voltavam empilhadas na origem. Nos dois casos as malhas tinham o tamanho
esperado. So desenhando se viu.

E O SOMBREAMENTO E POR VERTICE, e nao por face. Sombrear por face mostra
faceta em tudo, inclusive no que chega redondo -- foi assim que a primeira
folha fez o cogumelo, a agua-viva e a mao cosmica parecerem todos
facetados. O que sobra de quina aqui e do modelo.
"""
import base64
import glob
import io
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelos_em_pontos as M

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLECAO = M.PASTA
CEL, COLS, LINS, TETO = 300, 4, 3, 40000

# Onde cada um entra na obra. Escrito a mao porque o codigo nao sabe dizer
# "isto e a concha" -- ele so sabe que ha uma chamada com este nome.
ONDE = {
    "rocks-icon": "as onze pedras do chao, as montanhas do horizonte, o fundo do mar",
    "cogumelo": "os treze cogumelos, e a casca de luz que eles derramam",
    "crisalida_borboleta88_diaethria": "o casulo",
    "animated_butterfly": "a borboleta",
    "jellyfish-icon": "o fundo do mar, e os seres que flutuam entre os planetas",
    "coral-icon": "o fundo do mar, e os seres que flutuam entre os planetas",
    "seaweed-icon": "o fundo do mar",
    "seaweed-icon-13702": "o fundo do mar",
    "seaweed-icon-17190": "o fundo do mar",
    "scallop-icon": "a concha",
    "grass-icon": "a grama",
    "ser_alienigena_rigged": "o ser camuflado no ceu",
    "clover-icon": "trevo — atras de OBJETOS_NO_CHAO, hoje desligado",
    "soya-icon": "soja — atras de OBJETOS_NO_CHAO, hoje desligado",
    "autumn-leaves-icon": "folhas — atras de OBJETOS_NO_CHAO, hoje desligado",
    "autumn-leaves-icon-22705": "folhas — atras de OBJETOS_NO_CHAO, hoje desligado",
}
FORA = {
    "mao_cosmica_teia": "**a mao gigante que puxa, aos 8:25.** Esta no roteiro e nunca foi ligada.",
    "star": "apesar do nome, uma ESTRELA-DO-MAR. Bicho de verdade e peca unica — "
            "mas e uma chapa de 9% de espessura, e a decimacao por grade junta a "
            "face de cima com a de baixo antes de tirar detalhe: sai rasgada. "
            "Inteira custa treze mil triangulos.",
    "tree-icon": "outra arvore; a arvore-mae hoje e procedural, sem modelo.",
    "seashells-icon": "conchas; a obra usa a scallop-icon.",
    "hand-icon": "mao; em RM as maos sao as da pessoa, vistas pelas cameras.",
    "berry-pick": "frutos; nunca entraram no roteiro.",
    "crisalida_borboleta88_rigged": "a mesma crisalida com esqueleto; a obra usa a lisa.",
    "ser_alienigena_apose": "o mesmo ser em outra pose; a obra usa a rigged.",
    "ser_alienigena": "o mesmo ser sem esqueleto; a obra usa a rigged.",
}


def suavizar(v):
    """Normal por vertice: soma as faces vizinhas e normaliza.

    Solda por posicao arredondada -- o glTF costuma repetir o vertice em cada
    face, e sem soldar a media nao tem o que mediar."""
    p = v.reshape(-1, 3)
    _, inv = np.unique(np.round(p * 4096).astype(np.int64), axis=0,
                       return_inverse=True)
    fn = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
    acc = np.zeros((inv.max() + 1, 3))
    np.add.at(acc, inv, np.repeat(fn, 3, axis=0))
    c = np.linalg.norm(acc, axis=1)
    c[c == 0] = 1
    return (acc / c[:, None])[inv].reshape(-1, 3, 3)


def retrato(tris, tam=CEL):
    """Pintor: de tras para a frente, sem z-buffer. Basta para ver a forma."""
    v = np.array(tris, dtype=np.float64)
    if len(v) > TETO:
        v = v[np.random.default_rng(7).choice(len(v), TETO, replace=False)]
    vn = suavizar(v)
    p = v.reshape(-1, 3)
    lo, hi = p.min(axis=0), p.max(axis=0)
    v = (v - (lo + hi) / 2) / (max(hi - lo) or 1.0)
    g, t = math.radians(32), math.radians(-18)

    def gira(a):
        x, y, z = a[..., 0], a[..., 1], a[..., 2]
        x2 = x * math.cos(g) + z * math.sin(g)
        z2 = -x * math.sin(g) + z * math.cos(g)
        return np.stack([x2, y * math.cos(t) - z2 * math.sin(t),
                         y * math.sin(t) + z2 * math.cos(t)], -1)

    v, vn = gira(v), gira(vn)
    n = vn.mean(axis=1)
    c = np.linalg.norm(n, axis=1)
    c[c == 0] = 1
    luz = np.clip((n / c[:, None]) @ np.array([0.35, 0.72, 0.60]) / 1.02, 0, 1)
    xy = v[..., :2] * (tam - 36) * 0.94 + tam / 2
    xy[..., 1] = tam - xy[..., 1]
    im = Image.new("RGB", (tam, tam), (16, 16, 22))
    d = ImageDraw.Draw(im)
    for i in np.argsort(v[..., 2].mean(axis=1)):
        q = 0.10 + 0.90 * luz[i]
        d.polygon([tuple(x) for x in xy[i]],
                  fill=(int(38 + 200 * q), int(46 + 196 * q), int(58 + 190 * q)))
    return im


def main():
    nuv = io.open(os.path.join(RAIZ, "fontes", "nuvens.js"), encoding="utf-8").read()
    NUV = json.loads(re.search(r"const NUVENS = (\{.*?\});", nuv, re.S).group(1))
    MAL = json.loads(re.search(r"const MALHAS = (\{.*?\});", nuv, re.S).group(1))
    tpl = io.open(os.path.join(RAIZ, "fontes", "mr.template.html"),
                  encoding="utf-8").read()
    peso = lambda d: sum(len(v) for v in d.values() if isinstance(v, str))

    alvos = sorted(glob.glob(os.path.join(os.path.dirname(COLECAO), "*.glb"))
                   + glob.glob(os.path.join(COLECAO, "*.glb")))
    curtos, linhas, cels = set(), [], []
    for c in alvos:
        nome = M.nome_curto(c, curtos)
        curtos.add(nome)
        try:
            gltf, _ = M.ler_glb(c)
            tris = M.triangulos(c)
        except Exception as erro:
            print("  %-26s FALHOU: %s" % (nome, erro))
            continue
        if not len(tris):
            continue
        cels.append((nome, len(tris), retrato(tris)))
        pec = "—"
        if len(tris) <= 40000:
            try:
                pec = str(len(M.pecas(tris)))
            except Exception:
                pass
        ape = M.COMO_MALHA.get(nome)
        kMal = [k for k in MAL if ape and k.startswith(ape + "-")]
        kb = (peso(NUV[nome]) if nome in NUV else 0) + sum(peso(MAL[k]) for k in kMal)
        usado = ("'%s'" % nome) in tpl or any(("'%s'" % k) in tpl for k in kMal) \
            or (ape and ("'%s-'" % ape) in tpl) or (ape and "%s-' + " % ape in tpl)
        dentro = ", ".join(x for x in [
            "%d img" % len(gltf["images"]) if gltf.get("images") else "",
            "esqueleto" if gltf.get("skins") else "",
            "%d anim" % len(gltf["animations"]) if gltf.get("animations") else ""] if x)
        linhas.append(dict(nome=nome, tris=len(tris), pec=pec, kb=kb // 1024,
                           nuvem=nome in NUV, malha=len(kMal), usado=usado,
                           dentro=dentro or "so geometria"))
        print("  %-26s %7d tri  %4s pecas  %4d KB" % (nome, len(tris), pec, kb // 1024))

    for pag in range(0, len(cels), COLS * LINS):
        lote = cels[pag:pag + COLS * LINS]
        lin = (len(lote) + COLS - 1) // COLS
        f = Image.new("RGB", (COLS * CEL, lin * (CEL + 26)), (10, 10, 14))
        dd = ImageDraw.Draw(f)
        for i, (nome, nt, im) in enumerate(lote):
            cx, cy = (i % COLS) * CEL, (i // COLS) * (CEL + 26)
            f.paste(im, (cx, cy))
            dd.text((cx + 8, cy + CEL + 6), "%s  -  %d tri" % (nome[:34], nt),
                    fill=(196, 190, 212))
        destino = os.path.join(RAIZ, "_fotos",
                               "modelagem-%d.png" % (pag // (COLS * LINS) + 1))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        f.save(destino, optimize=True)
        print("folha:", os.path.basename(destino))

    uso = sorted([d for d in linhas if d["usado"]], key=lambda d: -d["kb"])
    fora = sorted([d for d in linhas if not d["usado"]], key=lambda d: -d["kb"])
    morto = sum(d["kb"] for d in fora if d["nuvem"] or d["malha"])
    L = ["# Os modelos 3D — o que existe e como entra na obra\n",
         "Gerado por `python fontes/listar_modelos.py`, que tambem escreve as "
         "folhas de contato em `_fotos/modelagem-*.png`. **Refaca depois de "
         "mexer no conversor** — os pesos saem do `fontes/nuvens.js`.\n",
         "Os arquivos vivem em `Downloads/Visões filmes/Modelos 3D/`, e alguns "
         "soltos um nivel acima. **Quem esta acima so entra se estiver citado "
         "pelo nome** na lista `extras` do conversor — foi assim que os treze "
         "cogumelos passaram a obra inteira sem existir.\n",
         "## Na obra\n",
         "| modelo | tri | peças | no `nuvens.js` | como entra | onde |",
         "|---|---:|---:|---:|---|---|"]
    for d in uso:
        como = " + ".join(x for x in [
            "nuvem" if d["nuvem"] else "",
            "malha (%d)" % d["malha"] if d["malha"] else ""] if x)
        L.append("| `%s` | %d | %s | %d KB | %s | %s |" % (
            d["nome"], d["tris"], d["pec"], d["kb"], como or "—",
            ONDE.get(d["nome"], "—")))
    L += ["\n## Baixados e nunca usados\n",
          "Somam **%d KB dentro do `nuvens.js`** — peso que o Quest baixa e "
          "decodifica a cada abertura sem nada aparecer na tela.\n" % morto,
          "| modelo | tri | no `nuvens.js` | o que é |", "|---|---:|---:|---|"]
    for d in fora:
        L.append("| `%s` | %d | %s | %s |" % (
            d["nome"], d["tris"], ("%d KB" % d["kb"]) if d["kb"] else "não embarcado",
            FORA.get(d["nome"], "—")))
    L.append("""
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
""")
    io.open(os.path.join(RAIZ, "MODELOS-3D.md"), "w",
            encoding="utf-8", newline="\r\n").write("\n".join(L))
    print("\nMODELOS-3D.md: %d na obra, %d fora, %d KB de peso morto"
          % (len(uso), len(fora), morto))


if __name__ == "__main__":
    main()
