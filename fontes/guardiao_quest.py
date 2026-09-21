# -*- coding: utf-8 -*-
"""O guardiao do Quest: este computador cuida do headset sozinho.

    python fontes/guardiao_quest.py            # fica rodando; Ctrl+C para
    python fontes/guardiao_quest.py --acordado # e ainda ignora o sensor de proximidade

A cada vinte segundos ele procura o Quest -- pelo cabo ou pela Wi-Fi -- e,
sempre que o encontra DE NOVO (ligou, reiniciou, voltou ao cabo), faz o que
em 20/09 se fazia a mao e se perdia a cada reinicio:

  1. garante o sensor de proximidade NORMAL (o Quest dorme ao sair da
     cabeca, como de fabrica -- pedido de 21/09). So com --acordado ele
     manda o contrario (com.oculus.vrpowermanager.prox_close), para
     trabalhar com o headset na mesa;
  2. liga o adb pela Wi-Fi (tcpip 5555) quando ele esta no cabo, e conecta
     pelo ip: dai em diante este computador alcanca o Quest sem cabo;
  3. refaz os tuneis da obra (reverse 8765, forward 9222 para o DevTools).

O que ele NAO consegue, e por que: depois de um reinicio o adb do Quest
volta em modo USB -- sem cabo, so um app dentro do headset (o Quest Games
Optimizer, pago) religa a Wi-Fi sozinho. Com o cabo ligado, a autorizacao
("sempre permitir deste computador") sobrevive ao reinicio e o guardiao faz
o resto.

Para rodar sozinho a cada logon do Windows: fontes/guardiao_quest.ps1
(registra uma tarefa agendada). O registro do que fez fica em
fontes/guardiao_quest.log.
"""
import os
import re
import subprocess
import sys
import time
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from estande import achar_adb  # noqa: E402  (o mesmo caminho do estande.py)

ACORDADO = "--acordado" in sys.argv   # ignorar o sensor de proximidade (so para trabalhar na mesa)
PORTA_OBRA = 8765
LOG = os.path.join(AQUI, "guardiao_quest.log")
IP_GUARDADO = os.path.join(AQUI, "guardiao_quest.ip")
CADA = 20  # segundos


def log(msg):
    linha = f"{datetime.now():%d/%m %H:%M:%S} {msg}"
    print(linha, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def adb(*args, timeout=25):
    p = subprocess.run([ADB, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return (p.stdout + p.stderr).strip()


def aparelhos():
    """{serial: estado} do que o adb ve agora."""
    out = {}
    for linha in adb("devices").splitlines()[1:]:
        partes = linha.split()
        if len(partes) >= 2:
            out[partes[0]] = partes[1]
    return out


def cuidar(serial, pelo_cabo):
    # O sensor de proximidade so e ignorado se pedido (--acordado): em 21/09 a
    # Crisia pediu que o Quest volte a dormir ao sair da cabeca, como de fabrica.
    if ACORDADO:
        adb("-s", serial, "shell", "am", "broadcast", "-a",
            "com.oculus.vrpowermanager.prox_close")
        log(f"  {serial}: sensor de proximidade ignorado (pensa que esta na cabeca)")
    else:
        adb("-s", serial, "shell", "am", "broadcast", "-a",
            "com.oculus.vrpowermanager.automation_disable")
        log(f"  {serial}: sensor de proximidade normal (dorme ao sair da cabeca)")
    adb("-s", serial, "reverse", f"tcp:{PORTA_OBRA}", f"tcp:{PORTA_OBRA}")
    adb("-s", serial, "forward", "tcp:9222", "localabstract:chrome_devtools_remote")
    log(f"  {serial}: tuneis {PORTA_OBRA} e 9222 refeitos")
    if pelo_cabo:
        ip = re.search(r"inet (\d+\.\d+\.\d+\.\d+)",
                       adb("-s", serial, "shell", "ip", "-f", "inet", "addr", "show", "wlan0"))
        if ip:
            ip = ip.group(1)
            adb("-s", serial, "tcpip", "5555")
            time.sleep(3)
            r = adb("connect", f"{ip}:5555")
            log(f"  wi-fi: {r}")
            with open(IP_GUARDADO, "w") as f:
                f.write(ip)
        else:
            log("  wi-fi: o Quest nao esta numa rede")


def main():
    global ADB
    ADB = achar_adb()
    if not ADB:
        sys.exit("nao achei o adb -- ponha o platform-tools em fontes/ (ver estande.py)")
    log(f"guardiao de pe (adb: {ADB})")
    vistos = {}      # serial -> id do boot que ja cuidamos
    ip_guardado = open(IP_GUARDADO).read().strip() if os.path.exists(IP_GUARDADO) else None
    while True:
        try:
            atuais = aparelhos()
            # tenta a wi-fi se so ela pode estar de pe
            if ip_guardado and f"{ip_guardado}:5555" not in atuais and not any(
                    v == "device" for v in atuais.values()):
                adb("connect", f"{ip_guardado}:5555", timeout=10)
                atuais = aparelhos()
            for serial, estado in atuais.items():
                if estado == "unauthorized":
                    if vistos.get(serial) != "unauthorized":
                        log(f"  {serial}: UNAUTHORIZED -- aceitar no capacete com 'sempre permitir'")
                        vistos[serial] = "unauthorized"
                    continue
                if estado != "device":
                    continue
                boot = adb("-s", serial, "shell", "cat", "/proc/sys/kernel/random/boot_id")
                if not re.fullmatch(r"[0-9a-f-]{36}", boot):
                    continue      # o cabo piscou (o tcpip reinicia o adb do Quest): tenta na proxima
                chave = boot
                if vistos.get(serial) == chave:
                    continue
                pelo_cabo = ":" not in serial
                log(f"{serial} apareceu ({'cabo' if pelo_cabo else 'wi-fi'}), boot {chave[:8]}")
                cuidar(serial, pelo_cabo)
                vistos[serial] = chave
                if pelo_cabo and os.path.exists(IP_GUARDADO):
                    ip_guardado = open(IP_GUARDADO).read().strip()
            for serial in list(vistos):
                if serial not in atuais:
                    log(f"{serial} sumiu")
                    del vistos[serial]
        except KeyboardInterrupt:
            log("guardiao encerrado")
            return
        except Exception as e:  # o guardiao nao morre por um tropeco
            log(f"  tropeco: {e}")
        time.sleep(CADA)


if __name__ == "__main__":
    main()
