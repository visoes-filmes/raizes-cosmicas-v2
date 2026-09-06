# -*- coding: utf-8 -*-
"""
Extrai texturas que repetem sem emenda dos quadros da Odara.

Nada é gerado nem redesenhado: é recorte da pintura real, tratado para
emendar sozinho nos dois eixos. A escolha da REGIÃO é automática — procuro
o trecho mais parecido consigo mesmo, porque textura que repete precisa de
estatística uniforme: um trecho com um assunto no meio denuncia a repetição
na primeira vez que o azulejo se encosta.
"""
import io, os, sys
import numpy as np
from PIL import Image

SRC = r"C:\Users\crisi\Desktop\Odara - Cosmos - frames\01_frames_chave"
AQUI = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(AQUI, "texturas")
os.makedirs(DEST, exist_ok=True)

# quadro, nome, para que serve
ALVOS = [
    ("chave_01", "ornamento", "filigrana — superfícies longas, casca"),
    ("chave_12", "galaxia",   "padrões geométricos — casca da árvore"),
    ("chave_25", "marmore",   "forma dos planetas, sobretudo o azul"),
    ("chave_27", "agua",      "a água do planeta rosa"),
    ("t_089",    "planeta",   "superfície de planeta"),
]

LADO = 512     # o azulejo final
PASSO = 48     # granularidade da busca


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def nivelar_eixo(a, eixo, margem):
    """Puxa as duas bordas opostas para o tom do meio do caminho.
    Só o tom escorrega; o desenho fica onde está."""
    out = a.copy()
    n = a.shape[eixo]
    ini = np.take(a, 0, axis=eixo).astype(np.float64)
    fim = np.take(a, n - 1, axis=eixo).astype(np.float64)
    meio = (ini + fim) / 2.0
    c_ini, c_fim = meio - ini, meio - fim
    for i in range(margem):
        peso = smoothstep(1.0 - i / margem)
        if eixo == 0:
            out[i] += c_ini * peso
            out[n - 1 - i] += c_fim * peso
        else:
            out[:, i] += c_ini * peso
            out[:, n - 1 - i] += c_fim * peso
    return out


def emenda(a, eixo):
    """Quanto a borda que se encosta destoa. Zero = invisível."""
    n = a.shape[eixo]
    return float(np.abs(np.take(a, 0, axis=eixo) - np.take(a, n - 1, axis=eixo)).mean())


def melhor_regiao(a, lado, passo):
    """Procura o quadrado mais uniforme e ao mesmo tempo mais detalhado.

    DETALHE alto garante que há pintura ali, e não um vazio.
    UNIFORMIDADE garante que a estatística não muda de um canto ao outro —
    é isso que faz o azulejo não denunciar onde ele começa.
    """
    H, W, _ = a.shape
    cinza = a.mean(axis=2)
    # laplaciano barato: quanto o pixel difere dos vizinhos
    lap = np.abs(4 * cinza[1:-1, 1:-1] - cinza[:-2, 1:-1] - cinza[2:, 1:-1]
                 - cinza[1:-1, :-2] - cinza[1:-1, 2:])
    melhor, nota_melhor = None, -1e9
    for y in range(0, H - lado + 1, passo):
        for x in range(0, W - lado + 1, passo):
            jan = cinza[y:y + lado, x:x + lado]
            det = float(lap[max(0, y - 1):y + lado - 1, max(0, x - 1):x + lado - 1].mean())
            # média em blocos de 64: se elas variam muito, há assunto no meio
            b = jan[:lado // 64 * 64, :lado // 64 * 64].reshape(lado // 64, 64, lado // 64, 64)
            blocos = b.mean(axis=(1, 3))
            desvio = float(blocos.std())
            brilho = float(jan.mean())
            if brilho < 22:            # quase preto não vira textura
                continue
            nota = det / (1.0 + desvio * 0.16)
            if nota > nota_melhor:
                nota_melhor, melhor = nota, (x, y, det, desvio, brilho)
    return melhor


print(f"{'quadro':10} {'nome':10} {'onde':>14}  {'emenda V':>16}  {'emenda H':>16}")
feitos = []
for quadro, nome, uso in ALVOS:
    im = Image.open(os.path.join(SRC, quadro + ".jpg")).convert("RGB")
    a = np.asarray(im).astype(np.float64)
    r = melhor_regiao(a, min(LADO, min(a.shape[:2])), PASSO)
    if r is None:
        print(f"{quadro:10} {nome:10}  nenhuma região com pintura suficiente")
        continue
    x, y, det, desvio, brilho = r
    lado = min(LADO, min(a.shape[:2]))
    corte = a[y:y + lado, x:x + lado].copy()
    if lado != LADO:
        corte = np.asarray(Image.fromarray(corte.astype(np.uint8))
                           .resize((LADO, LADO), Image.LANCZOS)).astype(np.float64)
    v0, h0 = emenda(corte, 0), emenda(corte, 1)
    corte = nivelar_eixo(corte, 0, 96)
    corte = nivelar_eixo(corte, 1, 96)
    v1, h1 = emenda(corte, 0), emenda(corte, 1)
    alvo = os.path.join(DEST, f"tex-{nome}.png")
    Image.fromarray(np.clip(corte, 0, 255).astype(np.uint8)).save(alvo)
    print(f"{quadro:10} {nome:10} {f'({x},{y})':>14}  {v0:7.2f} -> {v1:5.2f}  {h0:7.2f} -> {h1:5.2f}")
    feitos.append((nome, uso, alvo))

# folha de contato: cada textura repetida 2x2, que é onde a emenda apareceria
print("\nAzulejo 2x2 de cada uma, para conferir a repetição:")
for nome, uso, alvo in feitos:
    t = Image.open(alvo)
    folha = Image.new("RGB", (LADO * 2, LADO * 2))
    for i in range(2):
        for j in range(2):
            folha.paste(t, (i * LADO, j * LADO))
    fp = os.path.join(DEST, f"repete-{nome}.png")
    folha.resize((512, 512), Image.LANCZOS).save(fp)
    print(f"  {nome:10} {uso}")
