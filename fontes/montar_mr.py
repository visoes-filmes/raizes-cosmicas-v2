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
    caminho = os.path.join(AQUI, nome)
    b = open(caminho, "rb").read()
    print(f"  {nome:22} {len(b)//1024:4d} KB  mp3")
    return "data:audio/mpeg;base64," + base64.b64encode(b).decode("ascii")


def embutir(nome, medidas, qualidade=90, com_alfa=False):
    modo = "RGBA" if com_alfa else "RGB"
    img = Image.open(os.path.join(AQUI, nome)).convert(modo).resize(medidas, Image.LANCZOS)
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


print("Texturas:")
mapa = {
    "__TEX_RAIZ__":     embutir(sys.argv[1], (256, 512)),
    # o panorama inteiro: a sala vira superficie de projecao dele, entao a
    # obra envolve o espaco uma vez so, sem azulejo repetido
    "__TEX_PANORAMA__": embutir(sys.argv[2], (2048, 1024), qualidade=88),
    "__TRILHA__":       embutir_audio("trilha-loop.mp3"),
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
    linhas = [str(i+1) for i, ln in enumerate(restante.splitlines()) if "`" in ln]
    raise SystemExit(f"ERRO: crase solta fora de shader (linhas {', '.join(linhas)}). "
                     f"Provavelmente num comentario dentro do GLSL — troque por aspas.")
for b in blocos:
    if "${" in b:
        raise SystemExit("ERRO: '${' dentro de shader — o JavaScript vai tentar interpolar.")

for k, v in mapa.items():
    html = html.replace(k, v)

saida = os.path.join(AQUI, sys.argv[3])
with open(saida, "w", encoding="utf-8") as f:
    f.write(html)

faltando = [k for k in mapa if k in html]
print(f"\nMarcadores nao substituidos: {faltando if faltando else 'nenhum'}")
print(f"Gerado: {saida}  ({len(html)//1024} KB)")
