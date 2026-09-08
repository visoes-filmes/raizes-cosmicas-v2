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
    "alienigena":       4200,   # camuflado no ceu: precisa de silhueta legivel
}
PADRAO = 2000

# QUAIS SAEM TAMBEM COMO MALHA, e nao so como nuvem.
#
# A obra passou a desenhar a mata como SUPERFICIE, com tinta triplanar. Ao
# lado de um tronco solido, um objeto feito de pontos le como confete -- a
# diferenca de materia grita. Entao o que divide o chao com as arvores
# precisa ser da mesma materia que elas.
#
# Nao e todo modelo: uma alga no fundo do mar continua melhor como nuvem,
# porque la a nuvem E o assunto. Aqui entra o que e macico.
COMO_MALHA = {"rocks-icon": "pedra", "cogumelo": "cogumelo",
              "crisalida_borboleta88_diaethria": "crisalida"}

# QUANTO SUAVIZAR cada um. A pedra vinha facetada como cristal e precisava
# de mao pesada; o cogumelo ja chega com a forma certa em 138 triangulos, e
# a mesma mao pesada o transformava num ovo -- sumia o pe, sumia o rebordo.
SUAVE = {"pedra": 0.62, "cogumelo": 0.28, "crisalida": 0.42}

# QUANTAS DIVISOES antes de suavizar. Subdividir sozinho nao arredonda nada
# -- os pontos novos caem em cima das faces velhas --, mas MUDA o que a
# suavizacao seguinte consegue fazer: numa malha grossa ela puxa o corpo
# inteiro e o objeto vira ovo; numa malha fina ela so alisa a quina, que e
# o que se quer. O cogumelo vem com 138 triangulos e a silhueta dele e um
# poligono visivel; duas divisoes o levam a 2 208 e o contorno fecha.
DIVISOES = {"pedra": 1, "cogumelo": 2, "crisalida": 0}

# POLIMENTO: passadas de media SEM dividir de novo. Dividir custa
# triangulos; polir nao custa nada, e e o que tira a quina depois que a
# malha ja esta fina. O cogumelo precisa disto porque, aceso e quase sem
# sombreamento, a forma dele e lida so pela SILHUETA -- e quina em silhueta
# nao tem onde se esconder.
POLIR = {"cogumelo": 3, "crisalida": 3}

# QUEM TAMBEM SAI EM VERSAO CRUA, sem dividir nem polir.
#
# As cascas de brilho do cogumelo sao desenhadas TRES vezes por cima do
# corpo. Feitas da malha detalhada, treze cogumelos custavam 114 mil
# triangulos por olho -- quase metade da cena, e para desenhar um borrao
# que nao tem forma nenhuma. Brilho e macio por definicao: a quina da malha
# crua nao aparece nele. Com a versao crua o mesmo brilho custa 5 mil.
CRU = {"cogumelo"}

# O cogumelo veio de poly.pizza (Quaternius), CC0 -- dominio publico, sem
# exigencia de credito. Escolhido entre cinco por ser o unico numa PECA SO:
# os outros traziam chapeus e pes como partes separadas, que nao dao para
# plantar como um corpo.

# QUANTAS PECAS APROVEITAR de cada modelo, da maior para a menor. Oito da
# variedade de sobra para onze pedras no chao sem que se reconheca a
# repeticao; as menores que sobram sao lascas de poucos triangulos, que na
# escala da obra nao chegariam a ser nada.
PECAS = 8

# A GRADE DA SIMPLIFICACAO. O modelo vem com quase seis mil triangulos, que
# e detalhe de icone de catalogo: numa pedra de quinze centimetros vista a um
# metro e meio nada disso chega ao olho, e onze pedras assim estourariam o
# limite de indice de 16 bits antes de melhorar coisa alguma.
#
# A conta e por AGRUPAMENTO EM GRADE: o espaco do modelo vira uma grade de N
# por N por N, os vertices que caem numa mesma celula viram um so, e os
# triangulos que perdem dois cantos na mesma celula somem. E grosseiro, e e
# o que se quer -- a silhueta sobrevive, a microgeometria some, e nao ha
# biblioteca nenhuma envolvida.
# Medido: 22 dava 850 vertices e uma pedra FACETADA -- cara de cristal, e
# nao de pedra. 70 devolve 1 792 vertices e 3 728 triangulos, dois tercos do
# modelo original, e onze delas somam 19 712 vertices: folga confortavel
# diante dos 65 535 do indice de 16 bits. Simplificar mais nao economizava
# nada que fizesse falta, e custava a forma.
GRADE = 70

# A GRADE POR MODELO, quando a global nao serve.
#
# 70 foi calibrada para a pedra: seis mil triangulos de entrada. A crisalida
# entra com QUARENTA mil -- e um escaneamento, nao um icone -- e na mesma
# grade sairia com uns dez mil, dez vezes o que um objeto de vinte
# centimetros pendurado merece.
#
# 26 devolve por volta de mil e duzentos, que e da ordem do torno feito a
# mao que ela substitui (1 440). Trocar a forma nao pode custar quadro.
#
# E ela nao se subdivide: subdividir quadruplicaria a conta para tirar uma
# faceta que tres passadas de POLIMENTO tiram de graca.
GRADES = {"crisalida": 26}

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


def pecas(tris):
    """Separa a malha nas PARTES QUE NAO SE TOCAM, da maior para a menor.

    POR QUE ISTO EXISTE. O modelo chamado "rocks-icon" nao e uma pedra: sao
    VINTE E UMA pedras soltas num monte, e a caixa dele e duas vezes mais
    larga que alta. Plantado inteiro e escalado pela altura, cada "pedra" da
    obra virava um amontoado de quarenta centimetros -- que de cima le como
    entulho anguloso, e nao como pedra.

    Separadas, cada peca e uma pedra de verdade, com forma organica e um
    vigesimo da geometria. E de quebra vem variedade de graca: onze pedras
    no chao, cada uma com o corpo de uma peca diferente."""
    chave = {}
    pai = []

    def achar(a):
        while pai[a] != a:
            pai[a] = pai[pai[a]]
            a = pai[a]
        return a

    ids = np.empty((len(tris), 3), dtype=int)
    for i, t in enumerate(tris):
        for j, ponto in enumerate(t):
            k = (round(ponto[0], 5), round(ponto[1], 5), round(ponto[2], 5))
            if k not in chave:
                chave[k] = len(pai)
                pai.append(len(pai))
            ids[i, j] = chave[k]
        for j in (1, 2):
            ra, rb = achar(ids[i, 0]), achar(ids[i, j])
            if ra != rb:
                pai[rb] = ra

    grupos = {}
    for i in range(len(tris)):
        grupos.setdefault(achar(ids[i, 0]), []).append(i)
    saida = [tris[np.array(v)] for v in grupos.values()]
    saida.sort(key=len, reverse=True)
    return saida


def simplificar(tris, grade):
    """Malha reduzida por agrupamento em grade: devolve (pos, nor, idx)."""
    v = tris.reshape(-1, 3)
    lo, hi = v.min(axis=0), v.max(axis=0)
    tam = np.maximum(hi - lo, 1e-9)
    cel = np.clip(((v - lo) / tam * grade).astype(int), 0, grade - 1)
    chave = cel[:, 0] * grade * grade + cel[:, 1] * grade + cel[:, 2]

    unicos, inverso = np.unique(chave, return_inverse=True)
    # O representante da celula e a MEDIA dos vertices dela, e nao o centro
    # da celula: o centro faria a superficie pular para a grade e a pedra
    # ficaria com cara de voxel.
    soma = np.zeros((len(unicos), 3))
    np.add.at(soma, inverso, v)
    conta = np.bincount(inverso, minlength=len(unicos))[:, None]
    pos = soma / conta

    idx = inverso.reshape(-1, 3)
    # fora os que colapsaram: dois cantos na mesma celula nao e triangulo
    bom = ((idx[:, 0] != idx[:, 1]) & (idx[:, 1] != idx[:, 2])
           & (idx[:, 0] != idx[:, 2]))
    idx = idx[bom]

    """A ORIENTACAO VEM DA FACE ORIGINAL.

    Agrupar vertices muda a forma dos triangulos, e mudando a forma muda o
    SENTIDO de alguns deles: o que era horario vira anti-horario. Com o
    descarte de face traseira ligado, cada triangulo virado abre um buraco na
    superficie -- e pelo buraco se ve o avesso da pedra, escuro. O resultado
    parece pedra facetada, cara de cristal, e nao ha nada de facetado nela.

    O conserto e comparar cada triangulo novo com a face de onde ele veio e
    trocar dois cantos quando discordam."""
    n_velho = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])[bom]
    a, b, c = pos[idx[:, 0]], pos[idx[:, 1]], pos[idx[:, 2]]
    virado = (n_velho * np.cross(b - a, c - a)).sum(axis=1) < 0
    idx[virado] = idx[virado][:, [0, 2, 1]]

    # NORMAIS POR ACUMULO das faces, ja ponderadas pela area (o produto
    # vetorial tem modulo proporcional a ela). Sem normal a triplanar nao
    # sabe de que plano ler, e a pedra sai chapada.
    nor = np.zeros_like(pos)
    a, b, c = pos[idx[:, 0]], pos[idx[:, 1]], pos[idx[:, 2]]
    face = np.cross(b - a, c - a)
    for k in range(3):
        np.add.at(nor, idx[:, k], face)
    comp = np.linalg.norm(nor, axis=1, keepdims=True)
    nor = np.divide(nor, comp, out=np.zeros_like(nor), where=comp > 0)
    return pos, nor, idx


def normais(pos, idx):
    """Normal por vertice, acumulando as faces ponderadas pela area."""
    nor = np.zeros_like(pos)
    a, b, c = pos[idx[:, 0]], pos[idx[:, 1]], pos[idx[:, 2]]
    face = np.cross(b - a, c - a)
    for k in range(3):
        np.add.at(nor, idx[:, k], face)
    comp = np.linalg.norm(nor, axis=1, keepdims=True)
    return np.divide(nor, comp, out=np.zeros_like(nor), where=comp > 0)


def arredondar(pos, idx, divisoes=1, forca=0.62, polir=0):
    """Subdivide uma vez e suaviza: tira a cara de cristal.

    POR QUE. As pedras deste modelo sao ESTILIZADAS -- trezentos triangulos
    cada, em faces largas e chapadas. Sombreamento suave nao salva: a
    silhueta continua sendo um poliedro, e um poliedro no chao le como
    cristal, nao como pedra. Nenhuma quantidade de tinta conserta forma.

    Entao a forma muda. Cada triangulo vira quatro pelos pontos medios das
    arestas, e depois cada vertice caminha na direcao da media dos vizinhos.
    A subdivisao sozinha nao arredonda nada -- os pontos novos caem em cima
    das faces antigas; e a media dos vizinhos que puxa as quinas para dentro
    e devolve o corpo rolado que uma pedra tem.

    Uma volta basta: trezentos triangulos viram mil e duzentos, e onze
    pedras somam treze mil -- metade do que a floresta inteira custa."""
    for _ in range(divisoes):
        pos, idx = _dividir_e_alisar(pos, idx, forca)
    for _ in range(polir):
        pos, _lixo = _alisar(pos, idx, forca * 0.8)
    return pos, idx


def _dividir_e_alisar(pos, idx, forca):
    """Uma divisao seguida de uma passada de media dos vizinhos."""
    pos = [list(map(float, q)) for q in pos]
    meio = {}

    def ponto_medio(a, b):
        k = (min(a, b), max(a, b))
        if k not in meio:
            meio[k] = len(pos)
            pos.append([(pos[a][i] + pos[b][i]) / 2 for i in range(3)])
        return meio[k]

    novos = []
    for t in idx:
        a, b, c = int(t[0]), int(t[1]), int(t[2])
        ab, bc, ca = ponto_medio(a, b), ponto_medio(b, c), ponto_medio(c, a)
        novos += [[a, ab, ca], [ab, b, bc], [ca, bc, c], [ab, bc, ca]]

    pos = np.array(pos)
    idx = np.array(novos, dtype=int)

    vizinhos = [set() for _ in range(len(pos))]
    for a, b, c in idx:
        vizinhos[a].update((b, c))
        vizinhos[b].update((a, c))
        vizinhos[c].update((a, b))

    return _alisar(pos, idx, forca)


def _alisar(pos, idx, forca):
    """Cada vertice caminha para a media dos vizinhos. Nao muda a malha."""
    vizinhos = [set() for _ in range(len(pos))]
    for a, b, c in idx:
        vizinhos[a].update((b, c))
        vizinhos[b].update((a, c))
        vizinhos[c].update((a, b))
    media = np.array([pos[list(v)].mean(axis=0) if v else pos[i]
                      for i, v in enumerate(vizinhos)])
    return pos * (1 - forca) + media * forca, idx


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
    saida, malhas = {}, {}
    # O ser alienigena mora um nivel acima, solto na pasta da Visoes. Ele
    # entra pelo nome porque nao esta na colecao -- e a versao "rigged", que
    # e a unica com esqueleto, embora a obra use so a forma dele.
    extras = []
    acima = os.path.dirname(PASTA)
    for nome in ("ser_alienigena_rigged.glb", "ser_alienigena.glb"):
        c = os.path.join(acima, nome)
        if os.path.exists(c):
            extras.append(c)
            break

    caminhos = [os.path.join(PASTA, a) for a in sorted(os.listdir(PASTA))
                if a.lower().endswith(".glb")] + extras
    for caminho in caminhos:
        arquivo = os.path.basename(caminho)
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

            if curto in COMO_MALHA:
                partes = [q for q in pecas(tris) if len(q) >= 60][:PECAS]
                for k, parte in enumerate(partes):
                    mp, _mn, mi = simplificar(
                        parte, GRADES.get(COMO_MALHA[curto], GRADE))
                    mp, mi = arredondar(
                        mp, mi,
                        divisoes=DIVISOES.get(COMO_MALHA[curto], 1),
                        forca=SUAVE.get(COMO_MALHA[curto], 0.5),
                        polir=POLIR.get(COMO_MALHA[curto], 0))
                    mn = normais(mp, mi)
                    mp = normalizar(mp)
                    if len(mp) > 65535:
                        raise ValueError("vertices demais para 16 bits")
                    b64mp, b64mn = empacotar(mp, mn)
                    nome = f"{COMO_MALHA[curto]}-{k}"
                    malhas[nome] = {
                        "n": len(mp), "t": len(mi),
                        "pos": b64mp, "nor": b64mn,
                        "idx": base64.b64encode(
                            mi.astype("<u2").tobytes()).decode()}
                    print(f"  {nome:24} {len(parte):7d} tri  ->  {len(mi):5d}"
                          f" tri  ({len(mp):5d} vertices)   MALHA")

                if curto in CRU:
                    cp, _c, ci = simplificar(tris, GRADE)
                    # UMA divisao e dois polimentos: crua de verdade a
                    # silhueta do brilho sai hexagonal, e brilho hexagonal
                    # e pior que brilho caro. Com 552 triangulos o contorno
                    # ja fecha, e ainda e um quarto do corpo.
                    cp, ci = arredondar(cp, ci, divisoes=1, forca=0.34, polir=2)
                    cn = normais(cp, ci)
                    cp = normalizar(cp)
                    b64cp, b64cn = empacotar(cp, cn)
                    nome = f"{COMO_MALHA[curto]}-cru"
                    malhas[nome] = {
                        "n": len(cp), "t": len(ci),
                        "pos": b64cp, "nor": b64cn,
                        "idx": base64.b64encode(
                            ci.astype("<u2").tobytes()).decode()}
                    print(f"  {nome:24} {len(tris):7d} tri  ->  {len(ci):5d}"
                          f" tri  ({len(cp):5d} vertices)   CRUA")
        except Exception as erro:
            print(f"  {curto:24} FALHOU: {erro}")

    destino = os.path.join(AQUI, "nuvens.js")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("/* Gerado por fontes/modelos_em_pontos.py — nao editar a mao.\n")
        f.write("   Modelos 3D reduzidos a nuvens de pontos: posicao em int16\n")
        f.write("   (milesimos de altura, pe em y=0) e normal em int8. */\n")
        f.write("const NUVENS = " + json.dumps(saida, separators=(",", ":")) + ";\n")
        f.write("/* E as MALHAS: os mesmos modelos como SUPERFICIE,\n")
        f.write("   para o programa triplanar. Posicao int16, normal\n")
        f.write("   int8, indice uint16, ja simplificados. */\n")
        f.write("const MALHAS = " + json.dumps(malhas, separators=(",", ":")) + ";\n")
    kb = os.path.getsize(destino) // 1024
    print(f"\nGerado: {destino}  ({kb} KB, {len(saida)} modelos," f" {len(malhas)} malhas)")


main()
