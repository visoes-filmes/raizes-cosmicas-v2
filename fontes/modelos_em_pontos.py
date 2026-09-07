# -*- coding: utf-8 -*-
"""
Transforma modelos GLB em NUVENS DE PONTOS, para a obra usar.

    python fontes/modelos_em_pontos.py

POR QUE ISTO EXISTE. A obra desenha por pontos, nao por malha — foi assim
que "os objetos parecem cubas" deixou de existir, porque ponto nao tem UV
para distorcer. Entao um modelo 3D nao precisa CHEGAR como malha: basta que
a forma dele vire pontos.

E isso resolve tres coisas de uma vez:

  1. nao ha carregador de GLB em tempo de execucao — nada de biblioteca,
     nada de material, nada de sistema de cena; a obra continua sendo um
     arquivo HTML sem dependencia
  2. o modelo entra na MESMA linguagem visual do resto: pigmento, e nao
     superficie fotografada colada no meio de uma aquarela
  3. o peso cai de megabytes de malha e textura para poucos kilobytes de
     coordenadas

O modelo entra so como FORMA. A cor continua vindo da pintura da Odara, que
e o que a obra tem de proprio.

A amostragem e POR AREA: um triangulo grande recebe mais pontos que um
pequeno. Sem isso, um modelo com muitos triangulos miudos num canto fica
denso ali e ralo no resto — a forma se desequilibra sem que se saiba por que.

Saida: fontes/nuvens.js, que o montador embute.
"""
import base64
import json
import os
import struct

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA = os.environ.get(
    "MODELOS", r"C:\Users\crisi\Downloads\Visões filmes\Modelos 3D")

# Quantos pontos por modelo. Nao e por metro quadrado como na mata, porque
# cada modelo vem numa escala propria: aqui o que importa e quantos pontos o
# olho precisa para reconhecer a forma, e isso e por objeto.
QUANTOS = {
    "grass-icon":       2600,
    "star":             1800,
    "hand-icon":        3200,   # a mao precisa de contorno legivel
    "jellyfish-icon":   2600,
    "coral-icon":       2600,
    "seaweed-icon":     2200,
    "seashells-icon":   2000,
    "scallop-icon":     1800,
    "rocks-icon":       2000,
    "tree-icon":        3000,
    "autumn-leaves-icon": 2400,
    "clover-icon":      1600,
    "berry-pick":       1800,
    "soya-icon":        1600,
    "rutabaga":         1800,
}
PADRAO = 2000

TIPOS = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2),
         5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}
ITENS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def ler_glb(caminho):
    """GLB e simples: cabecalho, um pedaco JSON e um pedaco binario."""
    with open(caminho, "rb") as f:
        dados = f.read()
    magica, versao, _total = struct.unpack_from("<III", dados, 0)
    if magica != 0x46546C67:
        raise ValueError("nao e GLB")
    pos, js, binario = 12, None, None
    while pos < len(dados):
        tam, tipo = struct.unpack_from("<II", dados, pos)
        pedaco = dados[pos + 8: pos + 8 + tam]
        if tipo == 0x4E4F534A:
            js = json.loads(pedaco.decode("utf-8"))
        elif tipo == 0x004E4942:
            binario = pedaco
        pos += 8 + tam + (-tam % 4)
    return js, binario


def acessar(gltf, binario, indice):
    """Le um acessor inteiro como array numpy."""
    ac = gltf["accessors"][indice]
    itens = ITENS[ac["type"]]
    fmt, tam = TIPOS[ac["componentType"]]
    vista = gltf["bufferViews"][ac["bufferView"]]
    inicio = vista.get("byteOffset", 0) + ac.get("byteOffset", 0)
    passo = vista.get("byteStride") or (itens * tam)
    saida = np.empty((ac["count"], itens), dtype=np.float64)
    for i in range(ac["count"]):
        p = inicio + i * passo
        saida[i] = struct.unpack_from("<" + fmt * itens, binario, p)
    return saida


def triangulos(caminho):
    """Todos os triangulos do arquivo, ja no lugar onde o no os poe."""
    gltf, binario = ler_glb(caminho)
    tris = []

    def andar(no_id, matriz):
        no = gltf["nodes"][no_id]
        m = np.array(no["matrix"], dtype=np.float64).reshape(4, 4).T \
            if "matrix" in no else np.eye(4)
        if "translation" in no or "rotation" in no or "scale" in no:
            m = np.eye(4)
            if "scale" in no:
                m[:3, :3] = np.diag(no["scale"])
            if "rotation" in no:
                x, y, z, w = no["rotation"]
                r = np.array([
                    [1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w)],
                    [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w)],
                    [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y)]])
                m[:3, :3] = r @ m[:3, :3]
            if "translation" in no:
                m[:3, 3] = no["translation"]
        m = matriz @ m

        if "mesh" in no:
            for prim in gltf["meshes"][no["mesh"]]["primitives"]:
                if prim.get("mode", 4) != 4:      # so triangulos
                    continue
                pos = acessar(gltf, binario, prim["attributes"]["POSITION"])
                pos = (m[:3, :3] @ pos.T).T + m[:3, 3]
                if "indices" in prim:
                    idx = acessar(gltf, binario, prim["indices"]).astype(int).ravel()
                else:
                    idx = np.arange(len(pos))
                tris.append(pos[idx].reshape(-1, 3, 3))
        for filho in no.get("children", []):
            andar(filho, m)

    cena = gltf.get("scene", 0)
    for no_id in gltf["scenes"][cena].get("nodes", []):
        andar(no_id, np.eye(4))
    return np.concatenate(tris) if tris else np.zeros((0, 3, 3))


def amostrar(tris, quantos, semente):
    """Pontos espalhados na superficie, por area."""
    rnd = np.random.default_rng(semente)
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    areas = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    total = areas.sum()
    if total <= 0:
        return np.zeros((0, 3)), np.zeros((0, 3))
    escolhidos = rnd.choice(len(tris), size=quantos, p=areas / total)
    r1 = np.sqrt(rnd.random(quantos))[:, None]
    r2 = rnd.random(quantos)[:, None]
    p = (a[escolhidos] * (1 - r1)
         + b[escolhidos] * (r1 * (1 - r2))
         + c[escolhidos] * (r1 * r2))
    n = np.cross(b[escolhidos] - a[escolhidos], c[escolhidos] - a[escolhidos])
    comp = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.divide(n, comp, out=np.zeros_like(n), where=comp > 0)
    return p, n


def normalizar(p):
    """Centro no chao, altura 1. Assim a obra escala em metros e nao precisa
    saber em que unidade cada autor modelou."""
    minimo, maximo = p.min(axis=0), p.max(axis=0)
    altura = max(maximo[1] - minimo[1], 1e-6)
    centro = (minimo + maximo) / 2
    q = p.copy()
    q[:, 0] -= centro[0]
    q[:, 2] -= centro[2]
    q[:, 1] -= minimo[1]           # o pe fica em y = 0
    return q / altura


def empacotar(p, n):
    """Posicao em int16 (milesimos de altura) e normal em int8. Float32 seria
    quatro vezes maior sem que ninguem visse a diferenca num ponto de tres
    pixels."""
    pos = np.clip(np.round(p * 8000), -32768, 32767).astype("<i2")
    nor = np.clip(np.round(n * 127), -127, 127).astype("<i1")
    return (base64.b64encode(pos.tobytes()).decode(),
            base64.b64encode(nor.tobytes()).decode())


def nome_curto(arquivo, ja_usados):
    """O nome de uso. Ha tres "seaweed-icon" e duas "autumn-leaves-icon" na
    colecao, e sem desempate a segunda apagava a primeira em silencio --
    perdiam-se modelos sem que nada avisasse. Quando repete, entra o numero
    do arquivo, que e o que de fato os distingue."""
    base = os.path.splitext(os.path.basename(arquivo))[0]
    numero = ""
    for pedaco in ("magnific_", "free3d_"):
        if base.startswith(pedaco):
            partes = base.split("_", 2)
            numero = partes[1]
            base = partes[-1]
    if base in ja_usados:
        base = f"{base}-{numero}"
    return base


def main():
    if not os.path.isdir(PASTA):
        raise SystemExit(f"nao achei a pasta de modelos: {PASTA}")
    saida = {}
    for arquivo in sorted(os.listdir(PASTA)):
        if not arquivo.lower().endswith(".glb"):
            continue
        caminho = os.path.join(PASTA, arquivo)
        curto = nome_curto(arquivo, saida)
        quantos = next((v for k, v in QUANTOS.items() if k in curto), PADRAO)
        try:
            tris = triangulos(caminho)
            if len(tris) == 0:
                print(f"  {curto:24} sem triangulos, pulado")
                continue
            p, n = amostrar(tris, quantos, abs(hash(curto)) % 100000)
            p = normalizar(p)
            b64p, b64n = empacotar(p, n)
            saida[curto] = {"n": len(p), "pos": b64p, "nor": b64n}
            print(f"  {curto:24} {len(tris):7d} tri  ->  {len(p):5d} pontos")
        except Exception as erro:
            print(f"  {curto:24} FALHOU: {erro}")

    destino = os.path.join(AQUI, "nuvens.js")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("/* Gerado por fontes/modelos_em_pontos.py — nao editar a mao.\n")
        f.write("   Modelos 3D reduzidos a nuvens de pontos: posicao em int16\n")
        f.write("   (milesimos de altura, pe em y=0) e normal em int8. */\n")
        f.write("const NUVENS = " + json.dumps(saida, separators=(",", ":")) + ";\n")
    kb = os.path.getsize(destino) // 1024
    print(f"\nGerado: {destino}  ({kb} KB, {len(saida)} modelos)")


main()
