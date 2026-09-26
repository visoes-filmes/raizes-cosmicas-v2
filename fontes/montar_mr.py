# -*- coding: utf-8 -*-
"""Monta a cena de realidade mista: injeta as texturas no template."""
import base64
import io
import os
import sys
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))          # .../fontes
RAIZ = os.path.dirname(AQUI)                                # a pasta do projeto
BENS = os.path.join(RAIZ, "assets")                         # onde moram as imagens

def bem(*partes):
    """Caminho dentro de assets/. Tudo resolve a partir da PASTA DO PROJETO,
    nunca do diretorio de onde se chamou o script — assim o comando e o mesmo
    em qualquer maquina e de qualquer lugar do terminal."""
    return os.path.join(BENS, *partes)


def embutir_audio(nome):
    """O audio vai embutido pelo mesmo motivo das imagens: a cena tem que
    ser UM arquivo. Publicada como artifact, ela nao pode buscar midia
    externa — a politica de seguranca bloqueia tudo que nao seja data:."""
    caminho = nome if os.path.isabs(nome) else os.path.abspath(nome)
    b = open(caminho, "rb").read()
    print(f"  {nome:22} {len(b)//1024:4d} KB  mp3")
    return "data:audio/mpeg;base64," + base64.b64encode(b).decode("ascii")


def embutir(nome, medidas, qualidade=90, com_alfa=False):
    modo = "RGBA" if com_alfa else "RGB"
    img = Image.open(nome if os.path.isabs(nome) else os.path.abspath(nome)).convert(modo).resize(medidas, Image.LANCZOS)
    b = io.BytesIO()
    if com_alfa:
        # PNG obrigatorio: JPEG nao guarda canal alfa, e e o alfa que faz
        # o recorte existir. Sem ele voltariam os retangulos.
        img.save(b, format="PNG", optimize=True)
        tipo = "png"
    else:
        img.save(b, format="JPEG", quality=qualidade, optimize=True)
        tipo = "jpeg"
    print(f"  {nome:22} {medidas[0]}x{medidas[1]:<5} {len(b.getvalue())//1024:4d} KB  {tipo}")
    return f"data:image/{tipo};base64," + base64.b64encode(b.getvalue()).decode("ascii")


# ── OS CEUS: PROPORCAO PRESERVADA, E O ALFA SE HOUVER ────────────────
#
# ANTES: embutir(..., (2048, 1024), qualidade=88). Duas coisas erradas numa
# linha. A medida forcava 2:1 -- e as pinturas sao 16:9, entao elas eram
# ACHATADAS antes de qualquer outra coisa acontecer. E o JPEG nao guarda
# canal alfa: nao havia transparencia no ceu, nem como haver.
#
# Agora a altura sai da propria imagem, e o formato sai de ela ter alfa ou
# nao. PNG so quando ha o que preservar: PNG de uma pintura de 2048 pesa
# muitos megabytes, e megabyte no ceu e megabyte que o Quest baixa antes de
# a obra comecar.
ASPECTOS = []


def embutir_mocap(caminho):
    """O JSON da captura vai inteiro, como literal de JavaScript."""
    if not os.path.exists(caminho):
        print("  (sem assets/mocap/deusa-danca.json: a deusa que danca fica de fora)")
        return "null"
    txt = open(caminho, encoding="utf-8").read()
    print(f"  {os.path.basename(caminho):22} {len(txt)//1024:4d} KB  mocap")
    return txt


def embutir_ceu(nome, largura=2048, qualidade=86):
    caminho = nome if os.path.isabs(nome) else os.path.abspath(nome)
    img = Image.open(caminho)
    com_alfa = img.mode in ("RGBA", "LA") or "transparency" in img.info
    lg, at = img.size
    altura = max(1, int(round(largura * at / lg)))
    ASPECTOS.append(round(largura / altura, 4))
    return embutir(nome, (largura, altura), qualidade, com_alfa)


# ── INTERRUPTOR DA TRILHA ────────────────────────────────────────────
# True deixaria o audio de fora do arquivo inteiro. Fica False: a trilha
# CONTINUA na cena — o que esta desligado e apenas o inicio automatico dela,
# em "somLigado" no template. O botao Som liga quando se quiser ouvir.
SEM_SOM = False

print("Texturas:")
mapa = {
    "__TEX_RAIZ__":     embutir(bem("texturas", "tex-raiz.png"), (256, 512)),
    # o panorama inteiro: a sala vira superficie de projecao dele, entao a
    # obra envolve o espaco uma vez so, sem azulejo repetido
    "__TEX_PANORAMA__": embutir_ceu(bem("ceus", "ceu-floresta-2048.png"), 2048, 88),
    "__CEU_COSMICO__":  embutir_ceu(bem("ceus", "ceu-cosmico-2048.png")),
    "__CEU_ROSA__":     embutir_ceu(bem("ceus", "ceu-rosa-2048.png")),
    # O QUARTO CEU: o da floresta encantada, trazido em 10/09. A ordem
    # aqui E o indice em CEUS -- ASPECTOS e preenchido na sequencia em que
    # embutir_ceu e chamado, entao acrescentar no meio renumeraria os ceus
    # sem avisar. Novo ceu entra no fim.
    "__CEU_MATA__":     embutir_ceu(bem("ceus", "ceu-mata-2048.png")),
    # A DEUSA QUE DANCA (7.1): a captura de movimento, ja compactada pelo
    # fontes/mocap_para_obra.py. Sem o arquivo, entra "null" e ela nao existe.
    "__MOCAP_DEUSA__":  embutir_mocap(bem("mocap", "deusa-danca.json")),
    # As peles dos planetas: recorte da propria pintura, ja tratado para
    # repetir. 512x512 e potencia de dois, entao aceita repeticao no WebGL 1.
    "__TEX_MARMORE__":  embutir(bem("texturas", "tex-marmore.png"),
                                (512, 512), qualidade=86),
    "__PELE_SOL__":       embutir(bem("peles", "pele-sol.jpg"),       (1024, 512), qualidade=86),
    "__PELE_ROSA__":      embutir(bem("peles", "pele-rosa.jpg"),      (1024, 512), qualidade=86),
    "__PELE_ASTEROIDE__": embutir(bem("peles", "pele-asteroide.jpg"), (1024, 512), qualidade=86),
    "__PELE_VERDE__":     embutir(bem("peles", "pele-verde.jpg"),     (1024, 512), qualidade=86),
    "__PELE_AGUA__":      embutir(bem("peles", "pele-agua.jpg"),      (1024, 512), qualidade=86),
    "__PELE_FOGO__":      embutir(bem("peles", "pele-fogo.jpg"),      (1024, 512), qualidade=86),
    "__TEX_AGUA__":     embutir(bem("texturas", "tex-agua.png"),
                                (512, 512), qualidade=86),
    "__PAPEL_COR__":     embutir(bem("texturas", "papel-teatro-cor.jpg"), (2560, 1037), qualidade=86),
    "__PAPEL_MASCARA__": embutir(bem("texturas", "papel-teatro-mascara.png"), (2560, 1037), com_alfa=True),
    # A PELE DA ASA DA BORBOLETA: sai de dentro do GLB na conversao (o
    # conversor a escreve aqui). 512 e potencia de dois: repete e tem mipmap.
    "__TEX_ASA_MORPHO__": embutir(bem("texturas", "tex-asa-morpho.png"), (512, 512), qualidade=90),
    # A DEUSA GALACTICA INTEIRA (11/09): o quadro todo, 16:9, em JPEG. Sem
    # canal alfa de proposito -- o alfa nasce no shader, so da beirada e do
    # preto da propria pintura. PNG com alfa desta pintura pesaria mais de
    # um megabyte; o JPEG fica em torno de cento e cinquenta kilobytes.
    # EXPANDIDA NO MAGNIFIC (11/09, pelo site -- o conector ignorava a
    # proporcao): 2048 x 1280, a pintura original no meio com nebulosa
    # continuada em volta e ceu sobre a cabeca. Em 2048 porque ela cobre
    # 106 graus do ceu: sao 19 pixels por grau, o que o Quest resolve.
    "__FIG_GALACTICO__": embutir(bem("figuras", "fig-galactica-ampliada.jpg"), (3072, 1921), qualidade=86),
    # AS OUTRAS DUAS DEUSAS PELO MESMO CAMINHO (12/09): o quadro inteiro do
    # mesmo momento da animacao, expandido e ampliado 2x no Magnific, em
    # JPEG sem alfa; 3072 de largura porque cada uma cobre uns oitenta
    # graus de ceu, e a ampliacao foi pedida para nao ficarem macias.
    "__FIG_DEUSA__":     embutir(bem("figuras", "fig-vermelha-cosmos.jpg"), (3072, 1920), qualidade=86),
    "__FIG_INTEGRA__":   embutir(bem("figuras", "fig-integra-ceu.jpg"),  (3072, 1891), qualidade=86),
    "__FIG_BORBOLETA__": embutir(bem("figuras", "fig-borboleta.png"), (512,512), com_alfa=True),
    "__TRILHA__":       "" if SEM_SOM else embutir_audio(
        bem("audio", "trilha-loop.mp3")),
}

with open(os.path.join(AQUI, "mr.template.html"), encoding="utf-8") as f:
    html = f.read()

# Os shaders moram dentro de template literal do JavaScript, que e delimitado
# por crase. Uma crase perdida num COMENTARIO do shader fecha a string no
# meio e quebra o arquivo inteiro — e o erro aparece longe dali, sem dizer
# de onde veio. Ja me pegou duas vezes; agora falha aqui.
import re
blocos = re.findall(r"const \w+ = `[\s\S]*?`;", html)
restante = re.sub(r"const \w+ = `[\s\S]*?`;", "", html)
sobra = restante.count("`")
print(f"Shaders: {len(blocos)}   crases fora de shader: {sobra}")
if sobra:
    # Mostrar a LINHA do texto despido nao ajuda: ela nao existe no arquivo.
    # Mostro o trecho, que da pra procurar direto no editor.
    culpados = [ln.strip()[:90] for ln in restante.splitlines() if "`" in ln]
    aviso = chr(10).join("    " + c for c in culpados)
    raise SystemExit(
        "ERRO: crase solta fora de shader. Troque por aspas." + chr(10) +
        "Uma crase perdida fecha o template literal do JavaScript no meio" + chr(10) +
        "e quebra o arquivo inteiro, com o erro aparecendo longe dali." + chr(10) +
        aviso)

for b in blocos:
    if "${" in b:
        raise SystemExit("ERRO: '${' dentro de shader — o JavaScript vai tentar interpolar.")

if SEM_SOM:
    # tira o elemento inteiro, nao so a fonte
    import re as _re
    html = _re.sub(r"<audio[^>]*id=\"trilha\"[^>]*>\s*</audio>", "", html)
    print("  trilha: FORA desta montagem (SEM_SOM = True)")

# AS NUVENS DOS MODELOS 3D. Geradas por modelos_em_pontos.py e embutidas
# aqui, para a obra continuar sendo um arquivo unico. Se o arquivo nao
# existir, a obra monta do mesmo jeito -- so sem os modelos.
_nuvens = os.path.join(AQUI, "nuvens.js")
if os.path.exists(_nuvens):
    mapa["__NUVENS__"] = open(_nuvens, encoding="utf-8").read()
    print(f"  nuvens dos modelos: {os.path.getsize(_nuvens)//1024} KB")
else:
    mapa["__NUVENS__"] = "const NUVENS = {};"
    print("  nuvens dos modelos: NAO ENCONTRADAS (rode modelos_em_pontos.py)")

# as proporcoes reais das pinturas, medidas na hora de embutir: assim o
# shader nunca discorda do arquivo, do mesmo jeito que a versao do cache
# nunca discorda da montagem 
mapa["__ASPECTOS_CEU__"] = "[" + ", ".join(str(a) for a in ASPECTOS) + "]"
print(f"  proporcoes dos ceus: {ASPECTOS}")

for k, v in mapa.items():
    html = html.replace(k, v)

# Sem argumento nenhum, escreve o index.html do proprio projeto — que e o
# que se quer em 99% das vezes. Um caminho como argumento continua valendo.
saida = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "index.html"))
saida = saida if os.path.isabs(saida) else os.path.abspath(saida)
with open(saida, "w", encoding="utf-8") as f:
    f.write(html)

faltando = [k for k in mapa if k in html]
print(f"\nMarcadores nao substituidos: {faltando if faltando else 'nenhum'}")
print(f"Gerado: {saida}  ({len(html)//1024} KB)")

# A COPIA DE TESTE, sempre junto.
#
# O headset carrega /nova.html e nao /index.html, por um motivo bobo e real:
# ha um service worker antigo instalado no aparelho que intercepta o
# index.html e serve a versao dele, do cache, ignorando o servidor. Um
# endereco que ele nao conhece passa direto.
#
# Ela era copiada a mao, e por duas vezes eu a apaguei ao limpar a pasta --
# o headset passou a receber 404 e a mostrar a versao de horas antes, e se
# perdeu tempo achando que a obra e que tinha quebrado. Agora o montador
# cuida disso.
if saida == os.path.join(RAIZ, "index.html"):
    import shutil
    shutil.copy(saida, os.path.join(RAIZ, "nova.html"))
    print("Copia de teste: nova.html (e esta que o headset abre)")

    # A OFICINA: a mesma obra, com o andaime ligado.
    #
    # A obra sai limpa -- sem regua, sem medidor, sem interruptores -- porque
    # e um ambiente e nao um editor. Mas quem trabalha nela PRECISA da regua:
    # sem ela nao ha como alcancar um cenario que so acontece aos 6:30, e
    # julgar a obra esperando dez minutos a cada ajuste e inviavel.
    #
    # Entao sai um segundo arquivo, com ANDAIME = true. E a mesma obra, o
    # mesmo codigo, a mesma montagem: muda uma palavra. Assim nunca ha
    # duvida sobre se a oficina e a obra -- ela e, com as ferramentas a
    # vista.
    # O SIMULADOR: a oficina, mais um aparelho de RM de mentira.
    #
    # Metade dos defeitos deste projeto so aparece DENTRO da sessao imersiva
    # -- o alfa do passthrough, as maos, o toque, a ordem de desenho no
    # quadro do headset. Testar qualquer um exigia alguem de capacete, e uma
    # rodada levava minutos: o resultado foi coisas dadas por feitas que
    # nunca tinham rodado uma vez.
    #
    # O simulador nao substitui o headset. Ele elimina as viagens ao headset
    # que eram so para descobrir que alguma coisa nao desenhava.
    _sim = os.path.join(AQUI, "simulador.js")
    if os.path.exists(_sim):
        shim = "<script>" + open(_sim, encoding="utf-8").read() + "</script>"
        simulador = html.replace("const ANDAIME = false;", "const ANDAIME = true;")
        # antes do script principal, para enganar o navigator.xr a tempo
        simulador = simulador.replace("<script>", shim + "<script>", 1)
        with open(os.path.join(RAIZ, "simulador.html"), "w", encoding="utf-8") as f:
            f.write(simulador)
        print("Simulador: simulador.html (entra em RM sem headset)")

    # O V4: a mesma obra, lendo o espaco de verdade.
    #
    # "Que aconteca um escaneamento do ambiente para posicionar os objetos
    # integrados com o espaco" -- 23/09. Ele nao substitui a obra: sai ao
    # lado dela, num arquivo proprio, para os dois poderem ser postos no
    # headset e comparados na mesma tarde. Sem o espaco configurado no
    # Quest nao vem plano nenhum, e ai o v4 e identico a obra.
    v4 = html.replace("const ESPACO_ESCANEADO      = false;",
                      "const ESPACO_ESCANEADO      = true;")
    # e ele se diz v4: na aba, no cartao e no portao (23/09 -- "no github
    # ainda esta raizes cosmicas v2"). Quem abre tem de saber qual e.
    v4 = (v4.replace("<title>Raízes Cósmicas v2</title>", "<title>Raízes Cósmicas v4</title>")
            .replace("<h1>Raízes Cósmicas v2</h1>", "<h1>Raízes Cósmicas v4</h1>")
            .replace('Raízes Cósmicas <em>v2</em>', 'Raízes Cósmicas <em>v4</em>'))
    if v4 == html:
        print("AVISO: nao achei o interruptor do v4 -- v4.html nao saiu")
    else:
        with open(os.path.join(RAIZ, "v4.html"), "w", encoding="utf-8") as f:
            f.write(v4)
        print("V4: v4.html (le o espaco e planta a obra nele)")

    # RAIZES COSMICAS 5.0 (24/09): o v4 mais as paredes rachadas, so o ceu
    # 100 % VR, metade da nevoa e a escala de desenho 0,7 (medida no Quest:
    # floresta 35 -> 54, planeta rosa 17 -> 26 quadros). Arquivo proprio,
    # nome proprio, cache proprio.
    v5 = (html.replace("const ESPACO_ESCANEADO      = false;", "const ESPACO_ESCANEADO      = true;")
              .replace("const PAREDES_RACHADAS      = false;", "const PAREDES_RACHADAS      = true;")
              .replace("const NEBLINA_FATOR         = 1.0;",   "const NEBLINA_FATOR         = 0.5;")
              .replace("const ESCALA_DESENHO        = 1.0;",   "const ESCALA_DESENHO        = 0.7;")
              .replace("<title>Raízes Cósmicas v2</title>", "<title>Raízes Cósmicas 5.1</title>")
              .replace("<h1>Raízes Cósmicas v2</h1>", "<h1>Raízes Cósmicas 5.1</h1>")
              .replace('Raízes Cósmicas <em>v2</em>', 'Raízes Cósmicas <em>5.1</em>')
              .replace("var PREFIXO_CACHE = 'raizes-cosmicas-';", "var PREFIXO_CACHE = 'raizes-cosmicas-v5-';"))
    if v5.count("= true;") < html.count("= true;") + 2:
        print("AVISO: os interruptores da 5.0 nao foram todos achados")
    with open(os.path.join(RAIZ, "v5.html"), "w", encoding="utf-8") as f:
        f.write(v5)
    print("5.1: v5.html (paredes rachadas, so o ceu e VR, menos nevoa, escala 0,7)")

    # RAIZES COSMICAS 5.2 (24/09): UM PASSO ATRAS NA SALA. Pedido da direcao
    # de arte, depois de ver a 5.1 no capacete: "a integracao com a sala, com
    # os objetos, nao deu certo; eu havia dito que era melhor so ser RA do
    # teto para cima -- quero voltar um passo atras, onde o ceu fazia fade com
    # as paredes. E nessa ultima versao o chao ficou preto, como se fosse o
    # ceu; isso so acontece no final. Precisamos ver o chao: a pessoa vai
    # caminhar pelo espaco."
    #
    # POR QUE O CHAO FICOU PRETO NA 5.1: com paredes lidas, o ceu recebia
    # inicio/fim negativos (-0,35 / -0,12) para descer abaixo do horizonte.
    # Mas o FS_CEU corta a direcao em zero (h = clamp(dir.y, 0, 1)), entao
    # abaixo do horizonte h vale 0 e smoothstep(-0,35, -0,12, 0) = 1: a cupula
    # inteira ficou opaca, o chao junto. E o mesmo mecanismo que o cenario 4
    # usa de proposito (-1 / -0,5) de 8:45 a 9:45, "estamos no espaco".
    #
    # A 5.2 e a v2 -- sem escaneamento, sem paredes rachadas, o ceu no degrade
    # de sempre por cenario, o chao real ate o cenario 4 -- com o que a 5.x
    # consertou e nao tem a ver com a sala: metade da nevoa, a escala 0,7
    # (o travamento ao mexer a cabeca) e o toque com folga e respiro (esse ja
    # esta no template, vale para todas).
    v52 = (html.replace("const NEBLINA_FATOR         = 1.0;",   "const NEBLINA_FATOR         = 0.5;")
               .replace("const ESCALA_DESENHO        = 1.0;",   "const ESCALA_DESENHO        = 0.8;")   # 7.7: era 0,7 ("pixelizado"); a escala viva ainda cede ate 0,82 disso
               .replace("<title>Raízes Cósmicas v2</title>", "<title>Raízes Cósmicas 5.2</title>")
               .replace("<h1>Raízes Cósmicas v2</h1>", "<h1>Raízes Cósmicas 5.2</h1>")
               .replace('Raízes Cósmicas <em>v2</em>', 'Raízes Cósmicas <em>5.2</em>')
               .replace("var PREFIXO_CACHE = 'raizes-cosmicas-';", "var PREFIXO_CACHE = 'raizes-cosmicas-v52-';"))
    if ("const ESPACO_ESCANEADO      = false;" not in v52 or "const PAREDES_RACHADAS      = false;" not in v52
            or "NEBLINA_FATOR         = 0.5;" not in v52 or "ESCALA_DESENHO        = 0.8;" not in v52
            or "raizes-cosmicas-v52-" not in v52):
        print("AVISO: os interruptores da 5.2 nao foram todos achados")
    with open(os.path.join(RAIZ, "v52.html"), "w", encoding="utf-8") as f:
        f.write(v52)
    print("5.2: v52.html (um passo atras: o ceu em fade com as paredes, sem ler a sala, o chao sempre visivel; nevoa 0,5, escala 0,7)")

    # RAIZES COSMICAS 6.0 (24/09): a 5.2 mais A TELA DE TULE. O oculos acha a
    # tela (plano rotulado na Configuracao de Espaco, ou dois cantos tocados),
    # estica nela o video "Odara - Cosmos" e cada toque vira onda; a pagina
    # projecao.html joga a mesma agua no projetor. O video NAO e embutido:
    # fica em assets/video/ e e servido ao lado (70 MB nao cabem num data:).
    # E LE O ESPACO (24/09, a noite): "e importante para reconhecer os espacos e
    # objetos" -- a 6.0 volta a plantar a obra na sala lida (o v4: cogumelo na
    # mesa, arvore em chao livre), SEM as paredes rachadas da 5.1. Sem espaco
    # configurado, a obra pede o escaneamento ao Quest (initiateRoomCapture).
    v6 = (v52.replace("const TELA_DE_TULE          = false;", "const TELA_DE_TULE          = true;")
             .replace("const ESPACO_ESCANEADO      = false;", "const ESPACO_ESCANEADO      = true;")
             .replace("const TELA_VISIVEL          = true;",  "const TELA_VISIVEL          = false;")
             .replace("<title>Raízes Cósmicas 5.2</title>", "<title>Raízes Cósmicas 7.7</title>")
             .replace("<h1>Raízes Cósmicas 5.2</h1>", "<h1>Raízes Cósmicas 7.7</h1>")
             .replace('Raízes Cósmicas <em>5.2</em>', 'Raízes Cósmicas <em>7.7</em>')
             .replace("var PREFIXO_CACHE = 'raizes-cosmicas-v52-';", "var PREFIXO_CACHE = 'raizes-cosmicas-v6-';"))
    if ("const TELA_DE_TULE          = true;" not in v6 or "raizes-cosmicas-v6-" not in v6
            or "const ESPACO_ESCANEADO      = true;" not in v6
            or "const TELA_VISIVEL          = false;" not in v6):
        print("AVISO: os interruptores da 6.0 nao foram todos achados")
    with open(os.path.join(RAIZ, "v6.html"), "w", encoding="utf-8") as f:
        f.write(v6)
    print("6.0: v6.html (a 5.2 + a tela de tule + o espaco lido: video da Odara na tela real, agua ao toque)")

    # A CAPA DO SITE E A 6.0 (24/09, a noite): "estamos na V6, atualize na capa
    # do site; no que esta no ar esta como v2". O index.html -- o endereco
    # publicado, o que o headset guarda -- passa a ser a 6.0, com o prefixo de
    # cache de sempre (o sw.js so conhece esse). O v6.html continua saindo ao
    # lado, para a Cabine; e o mesmo corpo com outro nome de cache.
    no_ar = v6.replace("var PREFIXO_CACHE = 'raizes-cosmicas-v6-';", "var PREFIXO_CACHE = 'raizes-cosmicas-';")
    if no_ar == v6:
        print("AVISO: nao achei o prefixo de cache da 6.0 -- o index.html ficou na v2")
    else:
        with open(saida, "w", encoding="utf-8") as f:
            f.write(no_ar)
        shutil.copy(saida, os.path.join(RAIZ, "nova.html"))
        print("No ar: index.html (e nova.html) = a 6.0, com o cache de sempre")

    # A PAGINA DE PROJECAO leva o MESMO shader da agua: copiado do template,
    # para o oculos e o projetor fazerem a mesma conta.
    ini = html.index("const FS_TELA = `") + len("const FS_TELA = `")
    fs_tela = html[ini:html.index("`;", ini)]
    with open(os.path.join(AQUI, "projecao.template.html"), encoding="utf-8") as f:
        proj = f.read()
    if proj.count("/*FS_TELA*/") != 1:
        print("AVISO: o marcador do shader nao esta na projecao.template.html -- projecao.html nao saiu")
    else:
        with open(os.path.join(RAIZ, "projecao.html"), "w", encoding="utf-8") as f:
            f.write(proj.replace("/*FS_TELA*/", fs_tela))
        print("Projecao: projecao.html (a agua da tela no projetor; toques chegam pela Cabine)")

    oficina = html.replace("const ANDAIME = false;", "const ANDAIME = true;")
    with open(os.path.join(RAIZ, "oficina.html"), "w", encoding="utf-8") as f:
        f.write(oficina)
    print("Oficina: oficina.html (a mesma obra, com a regua e os medidores)")


# --------------------- A VERSAO DO CACHE, SOZINHA ---------------------
#
# O sw.js serve cache primeiro, e o NOME do cache e o numero da versao. Sem
# troca-lo, o headset continua servindo a obra antiga e a nova nunca chega
# la -- sem erro, sem aviso, so a versao de antes teimando.
#
# Isso era feito a mao. E ser feito a mao significa esquecer: ja se perdeu
# uma tarde olhando um defeito que estava corrigido havia meia hora.
#
# Agora e o montador que troca. Ele nao pode esquecer, e a regra fica
# simples: quem monta, publica versao nova. A marca e a data mais uma letra,
# porque num dia de ajustes se monta muitas vezes.
def girar_versao():
    import datetime, re
    caminho = os.path.join(RAIZ, "sw.js")
    if not os.path.exists(caminho):
        return None
    texto = open(caminho, encoding="utf-8", newline="").read()
    achado = re.search(r"const VERSAO = '([^']+)'", texto)
    if not achado:
        return None
    atual = achado.group(1)
    base = "raizes-cosmicas-" + datetime.date.today().isoformat()
    if atual.startswith(base):
        sufixo = atual[len(base):]
        # a letra anda em base 26: a, b, ... z, aa, ab ... Antes eu fazia
        # chr(ord(ultima)+1), e depois de "aa" isso voltava para "b" -- uma
        # versao MAIS VELHA com nome novo, que e o pior dos dois mundos.
        letras = "abcdefghijklmnopqrstuvwxyz"
        if not sufixo:
            prox = "b"
        else:
            n = 0
            for c in sufixo:
                n = n * 26 + (letras.index(c) + 1)
            n += 1
            prox = ""
            while n:
                n, r = divmod(n - 1, 26)
                prox = letras[r] + prox
    else:
        prox = ""                      # primeira montagem do dia
    nova = base + prox
    if nova == atual:
        return atual
    open(caminho, "w", encoding="utf-8", newline="").write(
        texto.replace("const VERSAO = '" + atual + "'", "const VERSAO = '" + nova + "'"))
    return nova


_nova = girar_versao()
print("Versao do cache: " + (_nova + "   (e esta que o headset vai buscar)" if _nova
      else "NAO ACHEI o sw.js -- troque a mao antes de publicar"))
