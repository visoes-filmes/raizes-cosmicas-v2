# -*- coding: utf-8 -*-
"""
A CAPTURA DE MOVIMENTO VIRA UM BEM DA OBRA (7.1).

    python fontes/mocap_para_obra.py D:\\_exportar_mocap_temp\\mocap_praia.json

Le o JSON que o Unreal escreveu (fontes/exportar_mocap_unreal.py, rodado como
commandlet: posicoes das 21 juntas por quadro, em metros, Y para cima) e
escreve assets/mocap/deusa-danca.json, que o montador embute:

  - RECENTRADA: a media do quadril ao longo do take vai para a origem, e o
    que sobra de deslocamento no chao e reduzido a metade -- a bailarina
    cruzava o palco, e a deusa tem de dancar num lugar;
  - MEDIDA: a altura dela (cabeca menos o pe mais baixo, no primeiro
    segundo) sai junto, para a obra escalar sem adivinhar;
  - COMPACTA: milimetros em inteiros de 16 bits, base64 -- 3500 quadros de
    21 juntas cabem em meio megabyte, em vez de dois de texto.

O que a obra faz com isso esta em "A DEUSA QUE DANCA", no template.
"""
import base64
import json
import os
import struct
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
origem = sys.argv[1] if len(sys.argv) > 1 else r"D:\_exportar_mocap_temp\mocap_praia.json"
saida = os.path.join(RAIZ, "assets", "mocap", "deusa-danca.json")

with open(origem, encoding="utf-8") as fh:
    d = json.load(fh)
juntas, quadros, fps = d["juntas"], d["quadros"], float(d["fps"])
nj = len(juntas)
ip = juntas.index("pelvis")
print(f"origem: {d.get('origem')}  {len(quadros)} quadros a {fps:.2f} fps, {nj} juntas")
print("ossos:", d.get("ossos"))

# a media do quadril, e o deslocamento pela metade
mx = sum(q[ip*3] for q in quadros) / len(quadros)
mz = sum(q[ip*3+2] for q in quadros) / len(quadros)
piso = min(min(q[k*3+1] for k in range(nj) if q[k*3] or q[k*3+1] or q[k*3+2]) for q in quadros[:max(1, int(fps))])
ih = juntas.index("head")
altura = max(q[ih*3+1] for q in quadros[:int(fps)]) - piso
print(f"quadril medio x={mx:.2f} z={mz:.2f}  piso={piso:.2f}  altura={altura:.2f} m")

vals = []
for q in quadros:
    for k in range(nj):
        x, y, z = q[k*3], q[k*3+1], q[k*3+2]
        x = (x - mx) * 0.5 + (x - mx) * 0.0 if False else (x - mx)
        z = (z - mz)
        # o deslocamento do quadril pela metade: cada junta anda com ele
        vals.append((x - (q[ip*3] - mx) * 0.5))
        vals.append(y - piso)
        vals.append((z - (q[ip*3+2] - mz) * 0.5))
mm = [max(-32000, min(32000, int(round(v * 1000)))) for v in vals]
bruto = struct.pack("<%dh" % len(mm), *mm)
os.makedirs(os.path.dirname(saida), exist_ok=True)
with open(saida, "w", encoding="utf-8") as fh:
    json.dump({"origem": d.get("origem"), "fps": fps, "juntas": juntas, "altura": round(altura, 3),
               "quadros": len(quadros), "dados": base64.b64encode(bruto).decode("ascii")}, fh)
print(f"escrito {saida}: {os.path.getsize(saida)//1024} KB")
