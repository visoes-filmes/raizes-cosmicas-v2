# -*- coding: utf-8 -*-
"""A PROXIMA VERSAO, ESCOLHIDA NA CABINE -- 26/09.

    python3 fontes/proxima.py preparar  [ramo]
    python3 fontes/proxima.py publicar  [ramo]

"Atualize so depois" e, em seguida, "coloque um botao para selecionar quando a
experiencia nao estiver acontecendo". O que fica pronto e ainda nao vai ao ar
mora num RAMO do GitHub (hoje: proxima-deusas-rosa). Daqui a Cabine:

  PREPARAR -- monta o ramo numa pasta temporaria (um worktree do git, fora do
  projeto) e deixa o resultado em proxima.html, na raiz: a Cabine o abre no
  Quest como qualquer versao. Nada e publicado, a main nao muda, e o que esta
  no ar continua no ar. Fora do endereco publicado a obra nao usa cache, entao
  a proxima nao se mistura com a de sempre. O portao diz "proxima".

  PUBLICAR -- junta o ramo a main (merge, sem apagar nada; se houver conflito,
  desfaz e avisa) e roda o publicar.py de sempre: verifica, marca o que esta no
  ar, monta, commita, empurra. Depois apaga o proxima.html.

A ultima linha impressa e um JSON com o resultado -- e o que a Cabine le.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
RAMO_PADRAO = "proxima-deusas-rosa"
TMP = os.path.join(tempfile.gettempdir(), "raizes-proxima")
ARQ = os.path.join(RAIZ, "proxima.html")


def rodar(args, cwd=RAIZ, timeout=120):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout + p.stderr).strip()


def fim(**r):
    print(json.dumps(r, ensure_ascii=False))
    sys.exit(0 if r.get("ok") else 1)


def preparar(ramo):
    cod, s = rodar(["git", "fetch", "-q", "origin", ramo])
    if cod:
        fim(ok=False, erro=f"nao achei o ramo {ramo} no GitHub: {s[-200:]}")
    alvo = f"origin/{ramo}"
    if os.path.isdir(os.path.join(TMP, ".git")) or os.path.isfile(os.path.join(TMP, ".git")):
        cod, s = rodar(["git", "checkout", "-q", "-f", "--detach", alvo], cwd=TMP)
    else:
        rodar(["git", "worktree", "prune"])
        cod, s = rodar(["git", "worktree", "add", "-f", "--detach", TMP, alvo])
    if cod:
        fim(ok=False, erro="nao consegui abrir o ramo: " + s[-200:])
    cod, s = rodar([sys.executable, os.path.join("fontes", "montar_mr.py")], cwd=TMP, timeout=900)
    fonte = os.path.join(TMP, "v6.html")
    if cod or not os.path.exists(fonte):
        fim(ok=False, erro="a montagem do ramo falhou: " + s[-300:])
    html = open(fonte, encoding="utf-8").read()
    # cache e nome proprios: quem abre sabe que e a proxima
    html = html.replace("var PREFIXO_CACHE = 'raizes-cosmicas-v6-';", "var PREFIXO_CACHE = 'raizes-cosmicas-proxima-';")
    html = re.sub(r"<title>Raízes Cósmicas ([^<]*)</title>", r"<title>Raízes Cósmicas \1 · próxima</title>", html, count=1)
    html = re.sub(r"Raízes Cósmicas <em>([^<]*)</em>", r"Raízes Cósmicas <em>\1 · próxima</em>", html, count=1)
    with open(ARQ, "w", encoding="utf-8") as f:
        f.write(html)
    _, commit = rodar(["git", "rev-parse", "--short", alvo])
    _, titulo = rodar(["git", "log", "-1", "--format=%s", alvo])
    fim(ok=True, ramo=ramo, commit=commit, titulo=titulo[:140], arquivo="proxima.html",
        kb=os.path.getsize(ARQ) // 1024)


def publicar(ramo):
    rodar(["git", "checkout", "--", "fontes/__pycache__"])
    _, sujo = rodar(["git", "status", "--porcelain", "--untracked-files=no"])
    sujo = "\n".join(l for l in sujo.splitlines() if "__pycache__" not in l)
    if sujo.strip():
        fim(ok=False, erro="ha mudanca local nao publicada na pasta do projeto; nao mexi em nada")
    cod, s = rodar(["git", "pull", "-q", "--ff-only", "origin", "main"], timeout=180)
    if cod:
        fim(ok=False, erro="nao consegui atualizar a main: " + s[-200:])
    cod, s = rodar(["git", "fetch", "-q", "origin", ramo])
    if cod:
        fim(ok=False, erro=f"nao achei o ramo {ramo}: {s[-200:]}")
    _, titulo = rodar(["git", "log", "-1", "--format=%s", f"origin/{ramo}"])
    cod, s = rodar(["git", "merge", "--no-ff", "-m", f"Publica a proxima ({ramo}): {titulo[:120]}", f"origin/{ramo}"])
    if cod:
        rodar(["git", "merge", "--abort"])
        fim(ok=False, erro="o ramo conflita com o que chegou do Unreal; desfiz o merge, nada mudou. Precisa juntar a mao.")
    cod, s = rodar([sys.executable, os.path.join("fontes", "publicar.py"), f"a proxima no ar: {titulo[:150]}"], timeout=1200)
    if cod:
        fim(ok=False, erro="o publicar parou (o merge ficou feito aqui, sem empurrar): " + s[-300:])
    try:
        os.remove(ARQ)
    except OSError:
        pass
    _, commit = rodar(["git", "rev-parse", "--short", "HEAD"])
    fim(ok=True, ramo=ramo, commit=commit, publicado=True)


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else ""
    ramo = sys.argv[2] if len(sys.argv) > 2 else RAMO_PADRAO
    if acao == "preparar":
        preparar(ramo)
    elif acao == "publicar":
        publicar(ramo)
    else:
        fim(ok=False, erro="uso: proxima.py preparar|publicar [ramo]")
