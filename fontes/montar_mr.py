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
    "__TEX_PANORAMA__": embutir(bem("ceus", "ceu-floresta-2048.png"), (2048, 1024), qualidade=88),
    "__CEU_COSMICO__":  embutir(bem("ceus", "ceu-cosmico-2048.png"),
                                (2048, 1024), qualidade=86),
    "__CEU_ROSA__":     embutir(bem("ceus", "ceu-rosa-2048.png"),
                                (2048, 1024), qualidade=86),
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
    "__FIG_GALACTICO__": embutir(bem("figuras", "fig-galactico.png"), (512,512), com_alfa=True),
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
