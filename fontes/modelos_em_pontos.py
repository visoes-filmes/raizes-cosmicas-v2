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
#
# ISSO MUDOU, E O PARAGRAFO ACIMA ERA O CONTRARIO. Dizia que a alga no
# fundo do mar continua melhor como nuvem "porque la a nuvem E o assunto".
# No fundo do mar continua verdade -- mas os seres tambem flutuam ENTRE OS
# PLANETAS, e la eles nao sao assunto de nuvem: sao bichos, e bicho em
# setenta mil pontos vira nevasca. A agua-viva e o coral saem tambem como
# superficie, e cada uso escolhe a sua.
COMO_MALHA = {"rocks-icon": "pedra", "cogumelo": "cogumelo",
              "crisalida_borboleta88_diaethria": "crisalida",
              "animated_butterfly": "borboleta",
              "jellyfish-icon": "agua-viva", "coral-icon": "coral",
              "star": "estrela-mar",
              # OS QUE ESTAVAM BAIXADOS E NUNCA ENTRARAM. Viram superficie
              # para receber o neon: em nuvem de pontos nao ha silhueta, e
              # neon sem silhueta e so um borrao aceso.
              "mao_cosmica_teia": "mao-cosmica", "tree-icon": "arvore-icone",
              "seashells-icon": "conchas", "berry-pick": "frutos",
              # AS TRES ALGAS. O fundo do mar deixa de ser nuvem: no cenario
              # 3 os objetos ficam no CHAO, com forma, e so os bichos sobem.
              "seaweed-icon": "alga-a", "seaweed-icon-13702": "alga-b",
              "seaweed-icon-17190": "alga-c",
              # A concha e o objeto que a pessoa TOCA no cenario 3, e era
              # o unico interativo da obra ainda feito de pontos.
              "scallop-icon": "concha",
              # O ser alienigena. Ele vai ser MUITO grande, e uma nuvem de
              # pontos espalhada por vinte metros deixa de ler como corpo.
              "ser_alienigena_rigged": "alien"}

# QUEM SAI MONTADO, e nao peca por peca.
#
# O normalizar comum centra CADA peca no proprio centro e poe o pe dela em
# y = 0. Para pedra e o certo: cada uma e plantada sozinha, num lugar
# diferente do chao, e ter o proprio pe no zero e o que torna isso simples.
#
# Para um bicho e fatal. A borboleta sai em cinco pecas -- corpo, duas asas
# dianteiras, duas traseiras -- e normalizadas uma por uma elas voltariam
# empilhadas na origem, cada uma com a sua escala. Deixariam de ser um bicho.
#
# Montado, o enquadramento e UM: medido no modelo inteiro e aplicado igual a
# todas as pecas. Cada uma guarda o lugar que tem no corpo.
#
# E a escala vem do MAIOR lado, e nao da altura. A borboleta e achatada --
# tres centimetros de espessura contra dois metros e meio de envergadura --,
# e dividir pela altura a inflaria vinte vezes. O maior lado e a
# envergadura, que e a medida que significa algo para quem olha.
#
# A AGUA-VIVA E O CORAL entram pelo mesmo motivo da borboleta, e o motivo e
# literal: a agua-viva sai em dezessete pecas -- o sino e as tentaculas --, e
# o coral em cinquenta, uma por ramo. Normalizadas uma a uma, cada tentacula
# e cada ramo voltaria centrado na origem com a escala dele: um monte de
# vermes empilhados. Ja aconteceu duas vezes neste arquivo, e a segunda foi
# hoje -- o coral saiu daqui por um minuto e voltou como um seixo.
MONTADO = {"borboleta", "agua-viva", "coral", "conchas", "frutos",
           "alga-a", "alga-b", "alga-c", "estrela-mar", "concha"}
#
# A ESTRELA-DO-MAR ENTRA AQUI POR UM MOTIVO DIFERENTE dos outros: ela e uma
# peca SO, entao nao ha o que montar. O que ela precisa e da ESCALA, que no
# montado vem do maior lado e no normalizar comum vem da altura.
#
# E ela e uma chapa: 0,007 de espessura contra 0,080 de vao, 8,7%.
# Normalizada pela altura, virava onze vezes mais larga do que alta -- a
# 0,25 de escala, dois metros e setenta e cinco de vao dentro de uma sala de
# quatro metros. Foi exatamente o que apareceu no cenario 3, e e o mesmo
# defeito que a borboleta ja tinha ensinado: "dividir pela altura a inflaria
# vinte vezes".

# QUANTO SUAVIZAR cada um. A pedra vinha facetada como cristal e precisava
# de mao pesada; o cogumelo ja chega com a forma certa em 138 triangulos, e
# a mesma mao pesada o transformava num ovo -- sumia o pe, sumia o rebordo.
# A borboleta NAO se suaviza: as asas dela sao chapas de proposito, e o
# contorno delas e o desenho do autor. Alisar uma asa arredonda a ponta e
# apaga o loboo -- estraga justamente o que se foi buscar no modelo.
# A agua-viva e a estrela-do-mar vao no 0,50: o pedido foi "o mais curva
# possivel", e num bicho de agua nao ha uma quina que signifique alguma coisa
# -- ao contrario da asa da borboleta, onde a quina E o desenho.
#
# O CORAL PRECISA DE TODAS AS PECAS, e por isso existe o PECAS_POR abaixo.
# O modelo tem cinquenta -- cada ramo e uma --, e com o teto de oito
# chegavam a obra oito varetas soltas e dois seixos, que nao leem como coral
# nenhum. Isso so apareceu DESENHANDO as pecas geradas: no numero, oito
# malhas de duzentos triangulos pareciam certas.
#
# A ESTRELA-DO-MAR NAO SE SIMPLIFICA, e o 200 e o mesmo "nao mexa" da
# borboleta. Ela e uma CHAPA de 8,7% de espessura, e a decimacao por grade
# junta a face de cima com a de baixo antes de tirar qualquer detalhe:
# medido, na grade 18 a celula mede 5,6% da caixa -- quase a espessura
# inteira -- e ela sai rasgada, com buraco no meio dos bracos.
#
# E decimar essa peca nao compensa nem quando funciona: na grade 70 ela
# sobrevive, mas perde a granulacao dos bracos, que e o que a faz ler como
# estrela-do-mar e nao como estrela desenhada -- e ainda assim sao dezenove
# mil dos vinte e tres mil triangulos. Vinte por cento de economia pela
# textura inteira do bicho.
#
# Pelo mesmo motivo ela nao se suaviza nem se pole: o relevo E o modelo.
# O ALIEN SE SUAVIZA, e isto e uma correcao: eu tinha posto zero aqui pelo
# argumento da borboleta -- "a quina e o desenho do autor". Na asa e verdade,
# porque o contorno dela E a forma. No corpo dele, nao: o que se le a trinta
# e cinco metros, atraves de vinte e seis por cento de presenca, e a
# SILHUETA. As placas nunca chegaram ao olho, e as quinas chegavam -- as
# pernas liam como cascalho.
#
# 0,45 com quatro passadas foi escolhido comparando cinco graus lado a lado:
# o corpo fica liso, a crista e as placas do tronco sobrevivem, e em 0,60
# com sete ele comeca a virar manequim.
#
# E NAO CUSTA UM TRIANGULO. Polir e passada de media sem dividir de novo:
# vinte mil e trezentos em todos os graus, medido.
SUAVE = {"pedra": 0.62, "cogumelo": 0.28, "crisalida": 0.42, "borboleta": 0.0,
         "alien": 0.45,
         "agua-viva": 0.50, "coral": 0.50, "estrela-mar": 0.0,
         "mao-cosmica": 0.0, "arvore-icone": 0.30,
         "conchas": 0.30, "frutos": 0.35,
         "alga-a": 0.45, "alga-b": 0.45, "alga-c": 0.45, "concha": 0.32}

# QUANTAS DIVISOES antes de suavizar. Subdividir sozinho nao arredonda nada
# -- os pontos novos caem em cima das faces velhas --, mas MUDA o que a
# suavizacao seguinte consegue fazer: numa malha grossa ela puxa o corpo
# inteiro e o objeto vira ovo; numa malha fina ela so alisa a quina, que e
# o que se quer. O cogumelo vem com 138 triangulos e a silhueta dele e um
# poligono visivel; duas divisoes o levam a 2 208 e o contorno fecha.
DIVISOES = {"pedra": 1, "cogumelo": 2, "crisalida": 0, "borboleta": 0,
            # ZERO DIVISOES nestes dois, e nao uma. Dividir multiplica por
            # quatro para ganhar SILHUETA, e silhueta e o unico lugar onde a
            # faceta aparece -- a curva do corpo quem faz e a normal suave, e
            # ela nao custa triangulo. A 1,70 m de altura, entre planetas, o
            # sino ocupa poucos pixels de contorno: nove mil e quinhentos
            # triangulos por bicho seriam pagos para nada.
            "agua-viva": 0, "coral": 0, "estrela-mar": 0,
            "mao-cosmica": 0, "arvore-icone": 0,
            "conchas": 0, "frutos": 0, "alien": 0,
            "alga-a": 0, "alga-b": 0, "alga-c": 0, "concha": 1}

# POLIMENTO: passadas de media SEM dividir de novo. Dividir custa
# triangulos; polir nao custa nada, e e o que tira a quina depois que a
# malha ja esta fina. O cogumelo precisa disto porque, aceso e quase sem
# sombreamento, a forma dele e lida so pela SILHUETA -- e quina em silhueta
# nao tem onde se esconder.
# Tres passadas, pelo mesmo motivo do cogumelo: polir nao custa triangulo,
# e a quina que sobra depois de dividir sai de graca aqui.
POLIR = {"cogumelo": 3, "crisalida": 3, "agua-viva": 4, "coral": 4, "estrela-mar": 0,
         "mao-cosmica": 0, "arvore-icone": 2, "conchas": 2, "frutos": 2,
         "alga-a": 3, "alga-b": 3, "alga-c": 3, "concha": 3, "alien": 4}

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
# E QUANDO OITO NAO BASTA. O teto existe para nao carregar cinquenta malhas
# de um modelo que so precisa das maiores. No coral e o contrario: as peças
# SAO os ramos, e um coral com oito ramos de cinquenta nao e um coral com
# menos detalhe -- e um punhado de varetas.
PECAS_POR = {"coral": 60, "frutos": 48, "conchas": 8,
             # CADA FOLHA DE ALGA E UMA PECA, e aqui o teto e ao contrario
             # do coral. No coral, oito ramos de cinquenta nao era um coral
             # com menos detalhe -- era um punhado de varetas. Numa alga,
             # menos folhas e so uma alga mais rala, e continua alga. Com
             # todas as pecas ela custava dez mil triangulos, e o fundo do
             # mar tem dezenove: nao caberia.
             "alga-a": 22, "alga-b": 8, "alga-c": 16}

# O PEDESTAL FICA DE FORA, TAMBEM NA MALHA.
#
# A nuvem ja o descartava, pelos pontos abaixo de 12% da altura: estes
# modelos vem com um disco de terra ou uma pedra embaixo, que existe para o
# icone pousar numa pagina de catalogo. A MALHA nunca teve esse filtro, e o
# efeito so apareceu quando o coral passou a levar as cinquenta pecas: a
# maior delas e o disco, e o que chegava a obra era um seixo com os ramos
# escondidos dentro dele.
#
# LARGO E BAIXO E PEDESTAL; ESTREITO E ALTO E RAMO. So a altura nao separa
# -- medido no coral, o disco sobe ate 24% e um ramo comeca em 0,2%. O que
# separa e a PEGADA: os quarenta e oito ramos ocupam menos de 10% da area do
# modelo vista de cima, e as duas pecas do pedestal ocupam 31% e 40%.
SEM_PEDESTAL = {"coral", "alga-a", "alga-b", "alga-c"}


def sem_pedestal(partes, tris):
    todos = np.array(tris).reshape(-1, 3)
    y0, y1 = float(todos[:, 1].min()), float(todos[:, 1].max())
    alt = (y1 - y0) or 1.0
    area = ((todos[:, 0].max() - todos[:, 0].min())
            * (todos[:, 2].max() - todos[:, 2].min())) or 1.0
    ficam = []
    for q in partes:
        p = np.array(q).reshape(-1, 3)
        pegada = ((p[:, 0].max() - p[:, 0].min())
                  * (p[:, 2].max() - p[:, 2].min())) / area
        topo = (float(p[:, 1].max()) - y0) / alt
        if pegada >= 0.18 and topo <= 0.35:
            continue
        ficam.append(q)
    return ficam

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
# 200 na borboleta e um jeito de dizer NAO SIMPLIFIQUE: a celula fica menor
# que qualquer aresta do modelo, e o agrupamento nao agrupa nada. Ela ja
# chega com 2 144 triangulos -- decimar um bicho desse tamanho seria jogar
# fora a forma que se foi buscar, para economizar o que nao pesa.
# 30 na agua-viva e no coral: bem mais fino que os 70 de fabrica, porque uma
# divisao seguinte quadruplica o que sobrar -- decimar pouco e dividir
# uma vez da mais curva por triangulo do que decimar muito e dividir duas.
# A CRISALIDA SUBIU DE 26 PARA 70, e a diferenca se ve desenhando as duas.
# Em 26 ela chegava com 4 252 triangulos e VIRAVA UM CASULO LISO: sumiam as
# nervuras da asa, os aneis do abdome e o cremaster -- tudo o que faz aquilo
# ser uma pupa e nao um grao. Em 70 sao 20 164 e o relevo volta quase
# inteiro; em 110 seriam 30 030, e a diferenca para 70 ja nao se ve.
#
# Vinte mil triangulos e caro para um objeto qualquer, e barato para ESTE:
# ha um so na obra, ele fica ao alcance do braco, e e o unico que a obra
# inteira convida a tocar. O que se paga aqui se paga uma vez.
GRADES = {"crisalida": 70, "borboleta": 200, "agua-viva": 30, "coral": 30, "estrela-mar": 200,
          # A MAO NAO SE SIMPLIFICA: a teia entre os dedos e feita de fios
          # de um triangulo de largura, e qualquer agrupamento por grade os
          # come primeiro -- e a teia e o nome da peca.
          "mao-cosmica": 200, "arvore-icone": 60,
          "conchas": 60, "frutos": 40,
          "alga-a": 26, "alga-b": 34, "alga-c": 30, "concha": 70,
          # 60 guarda as placas e corta pela metade; ele vai ser um so
          "alien": 60}

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


def normalizar_junto(p, lo, hi):
    """O MESMO enquadramento para todas as pecas de um corpo.

    Centro no centro -- e nao o pe no chao: bicho voando nao tem pe -- e o
    maior lado valendo 1. Recebe o lo/hi do modelo INTEIRO, e nao da peca,
    e e so isso que faz as cinco pecas voltarem a ser uma borboleta."""
    centro = (lo + hi) / 2.0
    escala = max((hi - lo).max(), 1e-6)
    return (p - centro) / escala


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
    # ALGUNS MODELOS MORAM UM NIVEL ACIMA, soltos na pasta da Visoes, e nao
    # dentro da colecao. Entram pelo nome, e a lista e o unico lugar que
    # sabe deles.
    #
    # O COGUMELO ESTAVA FALTANDO AQUI, e o efeito era mudo: COMO_MALHA
    # pedia "cogumelo", o conversor nunca via o arquivo, o nuvens.js saia
    # sem a malha, o decodificarMalha devolvia nulo, o plantarMalha
    # devolvia zero, o montarCogumelos desistia sem reclamar e o desenho
    # nao acontecia. Treze cogumelos que o interruptor dizia estarem
    # ligados, que a documentacao descrevia, e que nao existiam.
    #
    # Do ser alienigena entra UMA versao so -- a "rigged" e a unica com
    # esqueleto, embora a obra use so a forma dele.
    extras = []
    acima = os.path.dirname(PASTA)
    for nome in ("cogumelo.glb",):
        c = os.path.join(acima, nome)
        if os.path.exists(c):
            extras.append(c)
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
                teto = PECAS_POR.get(COMO_MALHA[curto], PECAS)
                partes = [q for q in pecas(tris) if len(q) >= 60]
                if COMO_MALHA[curto] in SEM_PEDESTAL:
                    partes = sem_pedestal(partes, tris)
                partes = partes[:teto]
                montado = COMO_MALHA[curto] in MONTADO
                if montado:
                    todos = np.array(tris).reshape(-1, 3)
                    caixaLo, caixaHi = todos.min(axis=0), todos.max(axis=0)
                for k, parte in enumerate(partes):
                    mp, _mn, mi = simplificar(
                        parte, GRADES.get(COMO_MALHA[curto], GRADE))
                    mp, mi = arredondar(
                        mp, mi,
                        divisoes=DIVISOES.get(COMO_MALHA[curto], 1),
                        forca=SUAVE.get(COMO_MALHA[curto], 0.5),
                        polir=POLIR.get(COMO_MALHA[curto], 0))
                    mn = normais(mp, mi)
                    mp = (normalizar_junto(np.array(mp), caixaLo, caixaHi)
                          if montado else normalizar(mp))
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


# SO QUANDO CHAMADO PELO NOME, e nao ao ser importado.
#
# Sem esta guarda, "import modelos_em_pontos" para medir um modelo REGERAVA
# o nuvens.js inteiro como efeito colateral -- e ja aconteceu duas vezes,
# uma delas apagando uma configuracao que ainda nao estava commitada. Medir
# nao pode escrever.
if __name__ == "__main__":
    main()
