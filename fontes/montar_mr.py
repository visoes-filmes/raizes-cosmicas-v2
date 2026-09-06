# -*- coding: utf-8 -*-
"""Monta a cena de realidade mista: injeta as texturas no template."""
import base64
import io
import os
import sys
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))


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
    "__TEX_RAIZ__":     embutir(sys.argv[1], (256, 512)),
    # o panorama inteiro: a sala vira superficie de projecao dele, entao a
    # obra envolve o espaco uma vez so, sem azulejo repetido
    "__TEX_PANORAMA__": embutir(sys.argv[2], (2048, 1024), qualidade=88),
    "__CEU_COSMICO__":  embutir(os.path.join(AQUI, "ceus/ceu-cosmico-2048.png"),
                                (2048, 1024), qualidade=86),
    "__CEU_ROSA__":     embutir(os.path.join(AQUI, "ceus/ceu-rosa-2048.png"),
                                (2048, 1024), qualidade=86),
    # As peles dos planetas: recorte da propria pintura, ja tratado para
    # repetir. 512x512 e potencia de dois, entao aceita repeticao no WebGL 1.
    "__TEX_MARMORE__":  embutir(os.path.join(AQUI, "texturas/tex-marmore.png"),
                                (512, 512), qualidade=86),
    "__TEX_AGUA__":     embutir(os.path.join(AQUI, "texturas/tex-agua.png"),
                                (512, 512), qualidade=86),
    "__TEX_PAPEL__":    embutir(os.path.join(AQUI, "tex-papel.png"),
                                (1024, 512), qualidade=84),
    "__FIG_GALACTICO__": embutir("figuras/fig-galactico.png", (512,512), com_alfa=True),
    "__FIG_DEUSA__":     embutir("figuras/fig-deusa-vermelha.png", (512,512), com_alfa=True),
    "__FIG_INTEGRA__":   embutir("figuras/fig-deusa-integra.png", (512,512), com_alfa=True),
    "__FIG_BORBOLETA__": embutir("figuras/fig-borboleta.png", (512,512), com_alfa=True),
    "__TRILHA__":       "" if SEM_SOM else embutir_audio(
        sys.argv[4] if len(sys.argv) > 4
        else os.path.join(AQUI, "trilha-loop.mp3")),
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

for k, v in mapa.items():
    html = html.replace(k, v)

saida = sys.argv[3] if os.path.isabs(sys.argv[3]) else os.path.abspath(sys.argv[3])
with open(saida, "w", encoding="utf-8") as f:
    f.write(html)

faltando = [k for k in mapa if k in html]
print(f"\nMarcadores nao substituidos: {faltando if faltando else 'nenhum'}")
print(f"Gerado: {saida}  ({len(html)//1024} KB)")
