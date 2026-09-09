# -*- coding: utf-8 -*-
"""A obra no Quest pelo cabo, sem rede nenhuma.

    python fontes/estande.py

POR QUE PELO CABO. Rede de feira cai, e rede de celular custa e cai também.
O cabo é a única ligação que não depende de terceiros: o Quest fala com este
computador e com mais ninguém.

COMO FUNCIONA. O `adb reverse` abre um túnel ao contrário: uma porta do
Quest passa a apontar para a mesma porta AQUI. Dentro do headset o endereço
é `http://localhost` -- e localhost é a peça que resolve o problema difícil.

  O WebXR só existe em contexto seguro, e https pede certificado. Mas o
  navegador considera `localhost` seguro por definição, e o túnel faz o
  endereço SER localhost do ponto de vista do Quest. Então o botão de entrar
  em realidade mista aparece sem certificado nenhum, sem aviso de segurança,
  sem ninguém ter de aceitar nada dentro do capacete.

  Pela Wi-Fi isso não acontece: o endereço passa a ser um IP, o IP não é
  contexto seguro, e sem certificado o botão simplesmente não existe.

E O CACHE FICA LIGADO. Oito megabytes num arquivo só: sem cache, cada pessoa
da fila espera o download inteiro outra vez. Com cache, a primeira espera um
segundo e as seguintes abrem na hora. É o contrário do que se quer testando,
e por isso o modo é explícito e mora aqui, não no servidor.

O QUE ISTO *NÃO* FAZ, e é de propósito: não mexe na regra do endereço. Em
`localhost` a obra se sabe em teste, e em teste ela apaga o service worker e
manda relatos. Medido: nada disso aparece para quem visita -- a régua e os
medidores estão atrás do ANDAIME, e o `window.raizes` só existe no console.
Os relatos, num estande, são justamente o que o operador quer ler.
"""
import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

# Onde procurar o adb, em ordem: o PATH, uma pasta largada aqui dentro, e os
# lugares onde as ferramentas da Meta e do Android costumam se instalar.
CANTOS = [
    os.path.join(AQUI, "platform-tools", "adb.exe"),
    os.path.join(AQUI, "platform-tools", "adb"),
    os.path.expanduser(r"~\AppData\Local\Android\Sdk\platform-tools\adb.exe"),
    r"C:\Program Files\Oculus\Support\oculus-drivers\adb.exe",
]

FALTA_ADB = """
NAO ACHEI O adb, e sem ele nao ha tunel pelo cabo.

Ele nao se instala: e um arquivo solto de dez megabytes.

  1. baixe  https://developer.android.com/studio/releases/platform-tools
  2. descompacte
  3. ponha a pasta 'platform-tools' dentro de 'fontes/'

Depois rode este comando de novo. O caminho procurado e:

  fontes/platform-tools/adb.exe

E NO HEADSET, uma vez so, antes de tudo: Configuracoes > Sistema >
Modo de desenvolvedor, ligado. Sem isso o cabo transmite arquivos mas nao
aceita depuracao, e o tunel nao sobe.
"""


def achar_adb():
    do_path = shutil.which("adb")
    if do_path:
        return do_path
    for c in CANTOS:
        if os.path.exists(c):
            return c
    return None


def falar(adb, *args):
    return subprocess.run([adb, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def main():
    adb = achar_adb()
    if not adb:
        sys.exit(FALTA_ADB)
    print(f"adb: {adb}")

    saida = falar(adb, "devices").stdout
    ligados = [l.split()[0] for l in saida.splitlines()[1:]
               if l.strip() and l.split()[-1] == "device"]
    esperando = [l for l in saida.splitlines()[1:] if "unauthorized" in l]

    if esperando:
        sys.exit("\nO QUEST ESTA LIGADO MAS NAO AUTORIZADO.\n"
                 "Ponha o capacete: ha uma caixa pedindo para permitir a\n"
                 "depuracao por USB. Marque 'sempre permitir' e aceite.")
    if not ligados:
        sys.exit("\nNENHUM QUEST NO CABO.\n"
                 "  - o cabo esta na porta do computador e no headset?\n"
                 "  - o headset esta LIGADO e desbloqueado?\n"
                 "  - o modo de desenvolvedor esta ligado nele?\n"
                 "Confira com:  adb devices")
    print(f"headset: {ligados[0]}")

    # o tunel ao contrario: localhost:PORTA no Quest -> localhost:PORTA aqui
    r = falar(adb, "reverse", f"tcp:{PORTA}", f"tcp:{PORTA}")
    if r.returncode != 0:
        sys.exit(f"\nO TUNEL NAO SUBIU:\n{r.stderr or r.stdout}")
    print(f"tunel: localhost:{PORTA} no headset  ->  esta maquina")

    if not os.path.exists(os.path.join(RAIZ, "index.html")):
        sys.exit("\nNAO HA index.html. Rode antes:  python fontes/montar_mr.py")

    print(f"""
────────────────────────────────────────────────────────────
  No navegador DENTRO do headset, abra:

      http://localhost:{PORTA}/

  Sem https, sem certificado, sem aviso: o tunel faz o
  endereco ser localhost, e localhost ja e contexto seguro.
  O botao de entrar em realidade mista aparece direto.

  Ctrl+C aqui derruba o tunel e o servidor.
────────────────────────────────────────────────────────────
""", flush=True)

    ambiente = dict(os.environ, ESTANDE="1")
    try:
        subprocess.run([sys.executable, os.path.join(AQUI, "servir.py"),
                        str(PORTA)], cwd=RAIZ, env=ambiente)
    except KeyboardInterrupt:
        pass
    finally:
        falar(adb, "reverse", "--remove", f"tcp:{PORTA}")
        print("\ntunel derrubado.")


if __name__ == "__main__":
    main()
