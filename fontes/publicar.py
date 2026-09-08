# -*- coding: utf-8 -*-
"""Publicar a obra, guardando antes o que estava no ar.

    python fontes/publicar.py "o que mudou"

Faz, nesta ordem:

    1. verificar    -- se reclamar, para aqui e nao publica nada
    2. MARCAR o commit que esta no ar agora, com o nome da versao de cache
       dele: e o ponto de volta
    3. montar       -- gera index.html e gira a versao do cache
    4. commit + push da marca e da obra

O PASSO 2 E A RAZAO DESTE ARQUIVO EXISTIR. Publicar era tres comandos
decorados, e o backup era o quarto -- o que se esquece. Uma marca no git
custa zero byte, e sem ela voltar ao que estava no ar significa procurar um
commit no meio de trinta pela data. Com ela:

    git checkout publicado-2026-09-07ci

O nome da marca e a VERSAO DE CACHE, e nao a data, porque e a versao que o
headset pede. Quando alguem disser "no aparelho esta a de ontem e quebrou",
a versao esta escrita na tela do relato e a marca tem o mesmo nome.

Nada aqui e destrutivo: so cria marca e empurra. Se o push falhar, o
trabalho continua todo aqui, commitado.
"""
import io
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rodar(*args, **kw):
    """Executa e devolve a saida; estoura se der errado (salvo se calar=True)."""
    calar = kw.pop("calar", False)
    p = subprocess.run(args, cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode and not calar:
        sys.stdout.write(p.stdout or "")
        sys.stderr.write(p.stderr or "")
        sys.exit("\nPAROU em: " + " ".join(args))
    return (p.stdout or "").strip()


def versao_no_ar():
    """A versao de cache do que esta publicado agora, lida do proprio remoto.

    Do REMOTO e nao do arquivo local: o local ja pode ter sido montado de
    novo, e ai a versao seria a nova -- marcaria o passado com o nome do
    presente, que e pior que nao marcar."""
    sw = rodar("git", "show", "origin/main:sw.js", calar=True)
    achado = re.search(r"VERSAO\s*=\s*'([^']+)'", sw)
    return achado.group(1) if achado else None


def main():
    if len(sys.argv) < 2:
        sys.exit('uso: python fontes/publicar.py "o que mudou"')
    recado = sys.argv[1]

    print("1/4  verificando")
    print(rodar(sys.executable, "fontes/verificar.py"))

    print("2/4  guardando o que esta no ar")
    rodar("git", "fetch", "origin", "main", calar=True)
    vivo = rodar("git", "rev-parse", "origin/main", calar=True)
    versao = versao_no_ar()
    if not vivo:
        print("     ainda nao ha nada no ar -- nada a guardar")
    elif not versao:
        print("     nao achei a VERSAO no sw.js do remoto -- SEM MARCA")
    else:
        marca = "publicado-" + versao.replace("raizes-cosmicas-", "")
        if rodar("git", "tag", "-l", marca, calar=True):
            print("     %s ja existe" % marca)
        else:
            rodar("git", "tag", "-a", marca, vivo,
                  "-m", "A obra como ficou no ar. Cache %s.\n\n"
                        "Para voltar:  git checkout %s" % (versao, marca))
            print("     marca %s  ->  %s" % (marca, vivo[:7]))

    print("3/4  montando")
    print(rodar(sys.executable, "fontes/montar_mr.py"))

    print("4/4  publicando")
    rodar("git", "add", "-A")
    if rodar("git", "status", "--porcelain", calar=True):
        rodar("git", "commit", "-m", recado)
        print("     " + rodar("git", "log", "--oneline", "-1", calar=True))
    else:
        print("     nada mudou desde o ultimo commit")
    rodar("git", "push", "origin", "--tags", calar=True)
    print("     " + (rodar("git", "push", "origin", "main") or "main enviada"))

    print("\nno ar em https://visoes-filmes.github.io/raizes-cosmicas-v2/")
    print("o headset pode levar um minuto para ver a versao nova")


if __name__ == "__main__":
    main()
