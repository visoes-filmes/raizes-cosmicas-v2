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
    "__TEX_PAPEL__":    embutir(bem("texturas", "tex-papel.png"),
                                (1024, 512), qualidade=84),
    # A PELE DA ASA DA BORBOLETA: sai de dentro do GLB na conversao (o
    # conversor a escreve aqui). 512 e potencia de dois: repete e tem mipmap.
    "__TEX_ASA_MORPHO__": embutir(bem("texturas", "tex-asa-morpho.png"), (512, 512), qualidade=90),
    # A DEUSA GALACTICA INTEIRA (11/09): o quadro todo, 16:9, em JPEG. Sem
    # canal alfa de proposito -- o alfa nasce no shader, so da beirada e do
    # preto da propria pintura. PNG com alfa desta pintura pesaria mais de
    # um megabyte; o JPEG fica em torno de cento e cinquenta kilobytes.
    "__FIG_GALACTICO__": embutir(bem("figuras", "fig-galactica-inteira.jpg"), (1024, 576), qualidade=92),
    "__FIG_DEUSA__":     embutir(bem("figuras", "fig-deusa-vermelha.png"), (512,512), com_alfa=True),
    "__FIG_INTEGRA__":   embutir(bem("figuras", "fig-deusa-integra.png"), (512,512), com_alfa=True),
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
