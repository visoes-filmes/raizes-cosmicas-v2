# -*- coding: utf-8 -*-
"""Publicar uma versao (v4, 5.0...) no repositorio proprio dela.

    python fontes/publicar_versao.py 5 "o que mudou"
    python fontes/publicar_versao.py 4 "o que mudou"

Cada versao e a mesma obra com interruptores ligados (ver CLAUDE.md): o
v4 le o espaco; a 5.0 le o espaco, racha as paredes, tira metade da nevoa e
desenha em escala 0,7. O codigo continua morando AQUI, no repositorio da v2
-- um template so, um montador so --, e o repositorio raizes-cosmicas-vN
guarda apenas a obra montada, servida pelo GitHub Pages em
visoes-filmes.github.io/raizes-cosmicas-vN/. Duas copias vivas do mesmo
codigo e como se perde trabalho (COMECE-AQUI); uma fonte e varios enderecos,
nao.

Faz, nesta ordem:
    1. verificar e montar aqui (o montador escreve o vN.html)
    2. escrever a pasta ../raizes-cosmicas-vN com o que o Pages serve:
       index.html (o vN), sw.js, manifest, icones, .nojekyll, LEIA-ME
    3. commit + push la

O CACHE TEM PREFIXO PROPRIO. Todas as versoes moram no mesmo dominio, e o
armazenamento de cache e por dominio: a vN guarda em
'raizes-cosmicas-vN-<data>' e o sw.js de cada uma so apaga os caches com o
proprio prefixo (23/09). Sem isso, abrir uma apagava a outra do aparelho.
"""
import io
import os
import re
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
N = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].isdigit() else "4"
NOME = "5.1" if N == "5" else "v" + N            # como a versao se chama para gente
DESTINO = os.path.join(os.path.dirname(RAIZ), "raizes-cosmicas-v" + N)
REMOTO = "https://github.com/visoes-filmes/raizes-cosmicas-v" + N + ".git"

for _fluxo in (sys.stdout, sys.stderr):      # o acento do caminho no console
    try:
        _fluxo.reconfigure(errors="replace")
    except Exception:
        pass


def rodar(args, cwd, calar=False):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode != 0 and not calar:
        sys.exit("PAROU em: " + " ".join(args) + "\n" + (p.stderr or p.stdout))
    return p


def main():
    msg = " ".join(a for a in sys.argv[1:] if a != N).strip() or (NOME + " atualizada")
    print("1/3  verificar e montar")
    rodar([sys.executable, os.path.join(AQUI, "verificar.py")], RAIZ)
    rodar([sys.executable, os.path.join(AQUI, "montar_mr.py")], RAIZ)

    print("2/3  escrever " + DESTINO)
    os.makedirs(DESTINO, exist_ok=True)
    obra = io.open(os.path.join(RAIZ, "v" + N + ".html"), encoding="utf-8", newline="").read()
    if "const ESPACO_ESCANEADO      = true;" not in obra:
        sys.exit("v" + N + ".html sem o escaneamento ligado -- o montador mudou?")
    prefixo = "raizes-cosmicas-v" + N + "-"
    if "var PREFIXO_CACHE = '" + prefixo + "';" not in obra:
        obra = obra.replace("var PREFIXO_CACHE = 'raizes-cosmicas-';",
                            "var PREFIXO_CACHE = '" + prefixo + "';")
    io.open(os.path.join(DESTINO, "index.html"), "w", encoding="utf-8", newline="").write(obra)

    sw = io.open(os.path.join(RAIZ, "sw.js"), encoding="utf-8", newline="").read()
    versao = re.search(r"const VERSAO = 'raizes-cosmicas-([^']+)'", sw).group(1)
    sw = sw.replace("const VERSAO = 'raizes-cosmicas-" + versao + "'",
                    "const VERSAO = '" + prefixo + versao + "'")
    io.open(os.path.join(DESTINO, "sw.js"), "w", encoding="utf-8", newline="").write(sw)

    man = io.open(os.path.join(RAIZ, "manifest.webmanifest"), encoding="utf-8").read()
    man = (man.replace('"name": "Raízes Cósmicas"', '"name": "Raízes Cósmicas ' + NOME + '"')
              .replace('"short_name": "Raízes"', '"short_name": "Raízes ' + NOME + '"'))
    io.open(os.path.join(DESTINO, "manifest.webmanifest"), "w", encoding="utf-8").write(man)

    for f in ("icone-192.png", "icone-512.png", ".nojekyll"):
        shutil.copy(os.path.join(RAIZ, f), os.path.join(DESTINO, f))
    io.open(os.path.join(DESTINO, "LEIA-ME.md"), "w", encoding="utf-8").write(
        "# Raízes Cósmicas " + NOME + "\n\n"
        "Obra em realidade mista para Meta Quest 3. Visões Filmes · FIL 2026.\n\n"
        "**Não se edita aqui.** Esta pasta é montada a partir do repositório\n"
        "`visoes-filmes/raizes-cosmicas-v2` (`fontes/mr.template.html`, com os\n"
        "interruptores desta versão ligados) por `python fontes/publicar_versao.py " + N + "`.\n\n"
        "No ar: `visoes-filmes.github.io/raizes-cosmicas-v" + N + "/` — versão de cache\n"
        "`" + prefixo + versao + "`.\n")

    # A montagem aqui gira a versao do sw.js da v2 mesmo quando a obra da v2
    # nao mudou -- e um sw.js so com a versao nova faria todo headset baixar
    # de novo a mesma obra. Se o index da v2 saiu igual ao do commit e a
    # unica diferenca no sw.js e a linha da versao, ela volta.
    if rodar(["git", "diff", "--quiet", "HEAD", "--", "index.html"], RAIZ, calar=True).returncode == 0:
        antigo = rodar(["git", "show", "HEAD:sw.js"], RAIZ).stdout
        atual = io.open(os.path.join(RAIZ, "sw.js"), encoding="utf-8", newline="").read()
        sem_versao = lambda t: re.sub(r"const VERSAO = '[^']+'", "", t).replace("\r\n", "\n")
        if sem_versao(antigo) == sem_versao(atual):
            rodar(["git", "checkout", "--", "sw.js"], RAIZ)

    print("3/3  commit e push")
    if not os.path.isdir(os.path.join(DESTINO, ".git")):
        rodar(["git", "init", "-b", "main"], DESTINO)
        rodar(["git", "remote", "add", "origin", REMOTO], DESTINO)
    rodar(["git", "config", "user.name", "Crisia-poria"], DESTINO)
    rodar(["git", "config", "user.email", "admcrisia@gmail.com"], DESTINO)
    rodar(["git", "add", "-A"], DESTINO)
    if rodar(["git", "diff", "--cached", "--quiet"], DESTINO, calar=True).returncode == 0:
        print("     nada mudou na " + NOME)
    else:
        rodar(["git", "commit", "-m", msg + " (" + NOME + " " + versao + ")\n\n"
               "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"], DESTINO)
    p = rodar(["git", "push", "-u", "origin", "main"], DESTINO, calar=True)
    if p.returncode != 0:
        print("\nO PUSH NAO FOI -- o repositorio existe no GitHub?\n"
              "  crie vazio em github.com/organizations/visoes-filmes/repositories/new\n"
              "  com o nome raizes-cosmicas-v" + N + ", e rode de novo.\n" + (p.stderr or "")[-400:])
        return 1
    print("\nno ar (depois do Pages montar): https://visoes-filmes.github.io/raizes-cosmicas-v" + N + "/")
    print("versao de cache: " + prefixo + versao)
    return 0


if __name__ == "__main__":
    sys.exit(main())
