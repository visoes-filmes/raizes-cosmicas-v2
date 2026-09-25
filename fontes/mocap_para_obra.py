# -*- coding: utf-8 -*-
"""
A CAPTURA DE MOVIMENTO VIRA UM BEM DA OBRA (7.1).

    python fontes/mocap_para_obra.py D:\\_exportar_mocap_temp\\mocap_praia.json

Le o JSON que o Unreal escreveu (fontes/exportar_mocap_unreal.py, rodado como
commandlet: para cada quadro e cada uma das 21 juntas, a posicao em metros
com Y para cima e os tres eixos do osso girados, ainda na base do Unreal) e
escreve assets/mocap/deusa-danca.json, que o montador embute:

  - RECENTRADA: a media do quadril ao longo do take vai para a origem, o
    que sobra de deslocamento no chao e reduzido a metade, e o corpo e
    girado para que no primeiro quadro a frente dele seja -Z (a frente da
    obra) -- a bailarina cruzava o palco de qualquer jeito;
  - COM ROTACAO: os eixos viram uma matriz na base da obra (a troca de mao
    entre Unreal e WebGL feita em vetores, onde ela e obvia) e a matriz vira
    um quaternio -- e a rotacao que veste uma malha nos ossos;
  - MEDIDA: a altura (cabeca menos o pe mais baixo, no primeiro segundo) e o
    QUADRO DE DESCANSO (aquele em que as maos estao mais baixas: o mais
    parecido com a pose em que os modelos vem) saem junto;
  - COMPACTA: sete inteiros de 16 bits por junta e quadro (milimetros, e o
    quaternio em dez-milesimos), base64.

O que a obra faz com isso esta em "A DEUSA QUE DANCA", no template.
"""
import base64
import json
import math
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
POR = len(quadros[0]) // nj          # 3 (so posicao) ou 12 (posicao + eixos)
assert POR in (3, 12), POR
ip, ih = juntas.index("pelvis"), juntas.index("head")
isl, isr = juntas.index("shoulder_l"), juntas.index("shoulder_r")
print(f"origem: {d.get('origem')}  {len(quadros)} quadros a {fps:.2f} fps, {nj} juntas, {POR} numeros por junta")


def M(v):            # vetor do Unreal (x frente, y direita, z cima) para a obra (x direita, y cima, -z frente)
    return (v[1], v[2], -v[0])


def quat_de_matriz(c0, c1, c2):
    # colunas da matriz (os eixos x, y, z do osso na base da obra)
    m00, m10, m20 = c0; m01, m11, m21 = c1; m02, m12, m22 = c2
    tr = m00 + m11 + m22
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        return ((m21 - m12) / s, (m02 - m20) / s, (m10 - m01) / s, 0.25 * s)
    if m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2
        return (0.25 * s, (m01 + m10) / s, (m02 + m20) / s, (m21 - m12) / s)
    if m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2
        return ((m01 + m10) / s, 0.25 * s, (m12 + m21) / s, (m02 - m20) / s)
    s = math.sqrt(1.0 + m22 - m00 - m11) * 2
    return ((m02 + m20) / s, (m12 + m21) / s, 0.25 * s, (m10 - m01) / s)


# ── o recentrar e o girar ───────────────────────────────────────────────
mx = sum(q[ip*POR] for q in quadros) / len(quadros)
mz = sum(q[ip*POR+2] for q in quadros) / len(quadros)
primeiro = quadros[:max(1, int(fps))]
piso = min(min(q[k*POR+1] for k in range(nj)) for q in primeiro)
altura = max(q[ih*POR+1] for q in primeiro) - piso
# a frente no primeiro quadro: cima x (quadril direito - quadril esquerdo).
# PELOS QUADRIS, e nao pelos ombros: no rig Mixamo as duas claviculas nascem
# quase no mesmo ponto, e a diferenca delas e ruido -- a frente saia torta.
itl, itr = juntas.index("thigh_l"), juntas.index("thigh_r")
q0 = quadros[0]
lx, lz = q0[itr*POR] - q0[itl*POR], q0[itr*POR+2] - q0[itl*POR+2]
fx, fz = -lz, lx                       # (0,1,0) x (lx,0,lz) = (-lz, 0, lx)
giro = -math.atan2(fx, -fz)            # quanto girar para a frente cair em -Z
cg, sg = math.cos(giro), math.sin(giro)
print(f"quadril medio x={mx:.2f} z={mz:.2f}  piso={piso:.2f}  altura={altura:.2f} m  giro={math.degrees(giro):.0f} graus")


def girar(x, z):
    return x * cg + z * sg, -x * sg + z * cg


# ── o quadro de descanso: maos mais baixas em relacao ao quadril ────────
ihl, ihr = juntas.index("hand_l"), juntas.index("hand_r")
# O QUADRO MAIS PARECIDO COM A POSE DE REPOUSO DOS MODELOS: em pe, tronco
# vertical, pernas retas e juntas, bracos pendendo (uns 20 graus do corpo),
# cotovelos quase retos. E a esse quadro que a malha e presa; quanto mais
# parecido com o modelo em repouso, menos a pele rasga ao dancar.
def _j(q, nome): k = juntas.index(nome) * POR; return (q[k], q[k+1], q[k+2])
def _sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def _ang(a, b):
    la, lb = math.sqrt(sum(x*x for x in a)), math.sqrt(sum(x*x for x in b))
    c = (a[0]*b[0] + a[1]*b[1] + a[2]*b[2]) / (la * lb + 1e-9)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))
def _pontos(q):
    baixo, cima = (0, -1, 0), (0, 1, 0)
    s = 0.0
    for lado in ("l", "r"):
        s += abs(_ang(_sub(_j(q, "hand_" + lado), _j(q, "upperarm_" + lado)), baixo) - 20)
        s += _ang(_sub(_j(q, "lowerarm_" + lado), _j(q, "upperarm_" + lado)), _sub(_j(q, "hand_" + lado), _j(q, "lowerarm_" + lado)))
        s += _ang(_sub(_j(q, "calf_" + lado), _j(q, "thigh_" + lado)), baixo)
        s += _ang(_sub(_j(q, "calf_" + lado), _j(q, "thigh_" + lado)), _sub(_j(q, "foot_" + lado), _j(q, "calf_" + lado)))
    s += 2 * _ang(_sub(_j(q, "neck"), _j(q, "pelvis")), cima)
    pes = math.sqrt(sum(x*x for x in _sub(_j(q, "foot_l"), _j(q, "foot_r"))))
    return s + 100 * abs(pes - 0.12 * altura / 0.8)
descanso = min(range(len(quadros)), key=lambda k: _pontos(quadros[k]))
print(f"quadro de descanso: {descanso} ({descanso / fps:.1f} s)")

vals = []
for q in quadros:
    dx, dz = (q[ip*POR] - mx) * 0.5, (q[ip*POR+2] - mz) * 0.5      # metade do deslocamento do quadril
    for k in range(nj):
        x, y, z = q[k*POR] - mx - dx, q[k*POR+1] - piso, q[k*POR+2] - mz - dz
        x, z = girar(x, z)
        vals.extend([int(round(x * 1000)), int(round(y * 1000)), int(round(z * 1000))])
        if POR == 12:
            rx, ry, rz = q[k*POR+3:k*POR+6], q[k*POR+6:k*POR+9], q[k*POR+9:k*POR+12]
            # colunas na base da obra: x <- eixo y do Unreal, y <- z, z <- -x
            c0, c1, c2 = M(ry), M(rz), tuple(-v for v in M(rx))
            # e o giro do corpo, aplicado a cada coluna
            c0 = (girar(c0[0], c0[2])[0], c0[1], girar(c0[0], c0[2])[1])
            c1 = (girar(c1[0], c1[2])[0], c1[1], girar(c1[0], c1[2])[1])
            c2 = (girar(c2[0], c2[2])[0], c2[1], girar(c2[0], c2[2])[1])
            qx, qy, qz, qw = quat_de_matriz(c0, c1, c2)
            vals.extend([int(round(v * 10000)) for v in (qx, qy, qz, qw)])
        else:
            vals.extend([0, 0, 0, 10000])
mm = [max(-32000, min(32000, v)) for v in vals]
bruto = struct.pack("<%dh" % len(mm), *mm)
os.makedirs(os.path.dirname(saida), exist_ok=True)
with open(saida, "w", encoding="utf-8") as fh:
    json.dump({"origem": d.get("origem"), "fps": fps, "juntas": juntas, "altura": round(altura, 3),
               "quadros": len(quadros), "descanso": descanso, "por": 7, "rotacao": POR == 12,
               "dados": base64.b64encode(bruto).decode("ascii")}, fh)
print(f"escrito {saida}: {os.path.getsize(saida)//1024} KB")
