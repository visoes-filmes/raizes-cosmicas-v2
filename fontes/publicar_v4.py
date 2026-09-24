# -*- coding: utf-8 -*-
"""Publicar o v4 no repositorio proprio dele.

    python fontes/publicar_v4.py "o que mudou"

O v4 e a mesma obra com ESPACO_ESCANEADO ligado (ver CLAUDE.md). O codigo
continua morando AQUI, no repositorio da v2 -- um template so, um montador
so --, e o repositorio raizes-cosmicas-v4 guarda apenas a obra montada,
servida pelo GitHub Pages em visoes-filmes.github.io/raizes-cosmicas-v4/.
Duas copias vivas do mesmo codigo e como se perde trabalho (COMECE-AQUI);
uma fonte e dois enderecos, nao.

Faz, nesta ordem:
    1. verificar e montar aqui (o montador escreve o v4.html)
    2. escrever a pasta ../raizes-cosmicas-v4 com o que o Pages serve:
       index.html (o v4), sw.js, manifest, icones, .nojekyll, LEIA-ME
    3. commit + push la

O CACHE TEM PREFIXO PROPRIO. v2 e v4 moram no mesmo dominio, e o
armazenamento de cache e por dominio: o v4 guarda em
'raizes-cosmicas-v4-<data>' e o sw.js de cada um so apaga os caches com o
proprio prefixo (23/09). Sem isso, abrir um apagava o outro do aparelho.
"""
import io
import os
import re
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DESTINO = os.path.join(os.path.dirname(RAIZ), "raizes-cosmicas-v4")
REMOTO = "https://github.com/visoes-filmes/raizes-cosmicas-v4.git"

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
    msg = " ".join(sys.argv[1:]).strip() or "v4 atualizado"
    print("1/3  verificar e montar")
    rodar([sys.executable, os.path.join(AQUI, "verificar.py")], RAIZ)
    rodar([sys.executable, os.path.join(AQUI, "montar_mr.py")], RAIZ)

    print("2/3  escrever " + DESTINO)
    os.makedirs(DESTINO, exist_ok=True)
    v4 = io.open(os.path.join(RAIZ, "v4.html"), encoding="utf-8", newline="").read()
    if "const ESPACO_ESCANEADO      = true;" not in v4:
        sys.exit("v4.html sem o escaneamento ligado -- o montador mudou?")
    v4 = v4.replace("var PREFIXO_CACHE = 'raizes-cosmicas-';",
                    "var PREFIXO_CACHE = 'raizes-cosmicas-v4-';")
    io.open(os.path.join(DESTINO, "index.html"), "w", encoding="utf-8", newline="").write(v4)

    sw = io.open(os.path.join(RAIZ, "sw.js"), encoding="utf-8", newline="").read()
    versao = re.search(r"const VERSAO = 'raizes-cosmicas-([^']+)'", sw).group(1)
    sw = sw.replace("const VERSAO = 'raizes-cosmicas-" + versao + "'",
                    "const VERSAO = 'raizes-cosmicas-v4-" + versao + "'")
    io.open(os.path.join(DESTINO, "sw.js"), "w", encoding="utf-8", newline="").write(sw)

    man = io.open(os.path.join(RAIZ, "manifest.webmanifest"), encoding="utf-8").read()
    man = (man.replace('"name": "Raízes Cósmicas"', '"name": "Raízes Cósmicas v4"')
              .replace('"short_name": "Raízes"', '"short_name": "Raízes v4"'))
    io.open(os.path.join(DESTINO, "manifest.webmanifest"), "w", encoding="utf-8").write(man)

    for f in ("icone-192.png", "icone-512.png", ".nojekyll"):
        shutil.copy(os.path.join(RAIZ, f), os.path.join(DESTINO, f))
    io.open(os.path.join(DESTINO, "LEIA-ME.md"), "w", encoding="utf-8").write(
        "# Raízes Cósmicas v4\n\n"
        "A obra que lê o espaço de verdade e se planta nele (escaneamento do\n"
        "ambiente pelos planos do Meta Quest). Visões Filmes · FIL 2026.\n\n"
        "**Não se edita aqui.** Esta pasta é montada a partir do repositório\n"
        "`visoes-filmes/raizes-cosmicas-v2` (`fontes/mr.template.html`, com\n"
        "`ESPACO_ESCANEADO` ligado) por `python fontes/publicar_v4.py`.\n\n"
        "No ar: `visoes-filmes.github.io/raizes-cosmicas-v4/` — versão de cache\n"
        "`raizes-cosmicas-v4-" + versao + "`.\n")

    print("3/3  commit e push")
    if not os.path.isdir(os.path.join(DESTINO, ".git")):
        rodar(["git", "init", "-b", "main"], DESTINO)
        rodar(["git", "remote", "add", "origin", REMOTO], DESTINO)
    rodar(["git", "config", "user.name", "Crisia-poria"], DESTINO)
    rodar(["git", "config", "user.email", "admcrisia@gmail.com"], DESTINO)
    rodar(["git", "add", "-A"], DESTINO)
    if rodar(["git", "diff", "--cached", "--quiet"], DESTINO, calar=True).returncode == 0:
        print("     nada mudou no v4")
    else:
        rodar(["git", "commit", "-m", msg + " (v4 " + versao + ")\n\n"
               "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], DESTINO)
    p = rodar(["git", "push", "-u", "origin", "main"], DESTINO, calar=True)
    if p.returncode != 0:
        print("\nO PUSH NAO FOI -- o repositorio existe no GitHub?\n"
              "  crie vazio em github.com/organizations/visoes-filmes/repositories/new\n"
              "  com o nome raizes-cosmicas-v4, e rode de novo.\n" + (p.stderr or "")[-400:])
        return 1
    print("\nno ar (depois do Pages montar): https://visoes-filmes.github.io/raizes-cosmicas-v4/")
    print("versao de cache: raizes-cosmicas-v4-" + versao)
    return 0


if __name__ == "__main__":
    sys.exit(main())
