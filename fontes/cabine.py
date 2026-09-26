# -*- coding: utf-8 -*-
"""A CABINE: este computador controla a experiência no estande — 24/09.

    python fontes/cabine.py                 # sobe tudo e abre a Cabine no navegador
    python fontes/cabine.py --sem-navegador # só sobe (a tarefa de logon usa assim)

O QUE ELA É. Uma página local (http://localhost:8790) com o que o operador
precisa no dia, em botões: a rede interna (o Ponto de Acesso Móvel deste
Windows), o Quest (achar, liberar pela Wi-Fi, túneis), a obra (abrir no
capacete, entrar em RM, reiniciar, encerrar, saltar no tempo), e a leitura
de dentro do headset (relatos, cenário, segundo, quadros, bateria).

O QUE ELA REÚNE, sem repetir código:
  - servir.py em MODO ESTANDE (cache ligado), como filho — é ele que serve a
    obra na porta 8765 e recebe os relatos; a Cabine lê a saída dele;
  - o mesmo caminho do adb do estande.py (achar_adb);
  - o trabalho do guardiao_quest.py: quando o Quest aparece, refaz os túneis
    (reverse 8765, forward 9222) e, no cabo, libera o adb pela Wi-Fi e
    guarda o ip em guardiao_quest.ip (o mesmo arquivo do guardião);
  - quest_eval.mjs para falar com o navegador do Quest pelo DevTools (é ele
    que clica "Iniciar em RM" com gesto humano, e lê raizes.onde());
  - hotspot.ps1 para a rede.

A REDE DO DIA. O Quest entra no Ponto de Acesso deste computador (nome e
senha aparecem na Cabine). Aí o adb alcança o Quest pela Wi-Fi, e o túnel
`adb reverse` faz `localhost:8765` dentro do headset ser esta máquina —
localhost é contexto seguro, então o botão de RM aparece sem certificado.
O cabo continua servindo: é por ele que a Wi-Fi do adb se libera na
primeira vez (e depois de cada reinício do Quest).

Andaime de operação: a Cabine escuta só nesta máquina (127.0.0.1).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
# o estande.py lê a porta de sys.argv ao ser importado; esconde-se o nosso argv
_argv, sys.argv = sys.argv, sys.argv[:1]
from estande import achar_adb  # noqa: E402
sys.argv = _argv

PORTA_CABINE = 8790
PORTA_OBRA = 8765
PORTA_DEVTOOLS = 9222
LOG = os.path.join(AQUI, "cabine.log")
IP_GUARDADO = os.path.join(AQUI, "guardiao_quest.ip")   # o mesmo do guardião
NAVEGADOR_QUEST = "com.oculus.browser"
VERSOES = {"v6": "v6.html", "v52": "v52.html", "v2": "", "v4": "v4.html", "v5": "v5.html", "oficina": "oficina.html",
           "proxima": "proxima.html"}   # 26/09: a proxima versao, preparada do ramo (fontes/proxima.py), sem publicar
NOMES_CENAS = {1: "floresta", 2: "cosmos", 3: "planeta rosa", 4: "papel"}

# no Windows sem console (pythonw), nenhum subprocesso pode abrir janela
SEM_JANELA = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
# O MACBOOK (24/09): a Cabine roda igual no macOS. O que muda e o que o
# sistema oferece -- nao ha "Ponto de Acesso Movel" por linha de comando (o
# Compartilhamento de Internet se liga nos Ajustes do Sistema, e a Cabine so
# abre a janela e le se esta ligado), os monitores vem do system_profiler
# (sem posicao: o segundo e posto a direita do principal) e o navegador e o
# Chrome/Edge do /Applications. adb e scrcpy vem do Homebrew (fontes/instalar_mac.sh).
MAC = sys.platform == "darwin"

ESTADO = {
    "hora": "", "servidor": {"porta": PORTA_OBRA, "de_pe": False},
    "rede": {"hotspot": {}, "wifi_pc": {}},
    "quest": {"lista": [], "escolhido": None, "via": None, "bateria": None,
              "ip": None, "tuneis": False, "acordado": False, "ip_guardado": None},
    "obra": {"aba": False, "url": None, "portao": None, "versao": "", "programas": "",
             "onde": None, "fps": None, "app_ms": None, "duracao": 600},
    "relatos": [], "scrcpy": None, "avisos": [],
    "projecao": {"ativa": False, "saida": None, "monitor": None, "espelhar": False},
    "monitores": [], "tela": None,
}
OUVINTES = []            # filas dos clientes do /eventos (a pagina de projecao)
PROJECAO = None          # o processo da projecao (navegador em quiosque ou scrcpy)
PROJECAO_PEDIDA = None   # (o ultimo pedido, quando) -- para o clique repetido nao reiniciar
TRAVA = threading.Lock()
ADB = None
SERVIDOR_OBRA = None


def log(msg):
    linha = f"{datetime.now():%d/%m %H:%M:%S} {msg}"
    try:
        print(linha, flush=True)
    except Exception:
        pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def relatar(texto, origem="cabine"):
    r = {"h": f"{datetime.now():%H:%M:%S}", "de": origem, "t": texto}
    with TRAVA:
        ESTADO["relatos"].append(r)
        del ESTADO["relatos"][:-400]
        for fila in OUVINTES:
            if len(fila) < 200:
                fila.append(r)


def rodar(cmd, timeout=25, **kw):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, creationflags=SEM_JANELA, **kw)
        return (p.stdout + p.stderr).strip(), p.returncode
    except subprocess.TimeoutExpired:
        return "tempo esgotado", 124
    except FileNotFoundError as e:
        return str(e), 127


def adb(*args, serial=None, timeout=25):
    base = [ADB] + (["-s", serial] if serial else [])
    saida, _ = rodar(base + list(args), timeout=timeout)
    return saida


# ── o Quest ──────────────────────────────────────────────────────────────

def aparelhos():
    """So os oculos. 26/09: o modem 4G UFI plugado no USB e um Android com
    adb ligado ('model:UFI') e a Cabine o tomou pelo Quest -- tuneis, tcpip,
    abrir a obra: tudo no modem. Quem diz o modelo e nao e Quest fica de fora;
    'unauthorized' nao diz o modelo e fica (pode ser o Quest pedindo licenca)."""
    lista = []
    for linha in adb("devices", "-l").splitlines()[1:]:
        partes = linha.split()
        if len(partes) < 2:
            continue
        m = re.search(r"\bmodel:(\S+)", linha)
        modelo = m.group(1) if m else ""
        if modelo and "quest" not in modelo.lower():
            continue
        lista.append({"serial": partes[0], "estado": partes[1], "modelo": modelo,
                      "via": "wifi" if ":" in partes[0] else "cabo"})
    return lista


def escolher(lista):
    prontos = [a for a in lista if a["estado"] == "device"]
    prontos.sort(key=lambda a: a["via"] != "cabo")   # o cabo primeiro
    return prontos[0] if prontos else None


def tuneis(serial):
    adb("reverse", f"tcp:{PORTA_OBRA}", f"tcp:{PORTA_OBRA}", serial=serial)
    adb("forward", f"tcp:{PORTA_DEVTOOLS}", "localabstract:chrome_devtools_remote", serial=serial)
    ok = f"tcp:{PORTA_OBRA}" in adb("reverse", "--list", serial=serial)
    return ok


def ip_do_quest(serial):
    m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)",
                  adb("shell", "ip", "-f", "inet", "addr", "show", "wlan0", serial=serial))
    return m.group(1) if m else None


def liberar_wifi(serial):
    """No cabo: liga o adb pela Wi-Fi (tcpip 5555) e conecta pelo ip do Quest."""
    ip = ip_do_quest(serial)
    if not ip:
        return {"ok": False, "erro": "o Quest não está em nenhuma rede Wi-Fi — no capacete, Configurações › Wi-Fi: "
                                     "entre na mesma rede deste computador (ou na rede interna da Cabine)"}
    adb("tcpip", "5555", serial=serial)
    time.sleep(3)
    with open(IP_GUARDADO, "w") as f:
        f.write(ip)
    tipo, r = tentar_wifi(ip)
    relatar(f"Wi-Fi liberada em {ip}: {r}")
    if tipo == "ok":
        return {"ok": True, "ip": ip, "resposta": r}
    return {"ok": False, "ip": ip, "resposta": r, "erro": FRASE_WIFI.get(tipo, r).format(ip=ip)}


# ── OS DOIS CAMINHOS (24/09) ─────────────────────────────────────────────
#
# "Precisa ter esses dois caminhos possiveis para conectar; se nao conseguir
# um, tenta o outro. E precisa ter um aviso adequado de erros assim."
#
# O cabo e a Wi-Fi sao dois caminhos para o MESMO adb do oculos, e cada um
# falha por um motivo proprio: o cabo por autorizacao, por cabo que so
# carrega, pelo Meta Quest Link segurando a porta; a Wi-Fi porque o Quest
# fecha o acesso a cada reinicio, porque o ip mudou, porque os dois nao estao
# na mesma rede. O vigia tenta os dois a cada volta, usa o que estiver bom
# (o cabo primeiro) e escreve, para cada um, o que houve e o que fazer.

FRASE_WIFI = {
    "fechada": "o Quest responde em {ip}, mas o acesso pela Wi-Fi está fechado — ele fecha sempre que o Quest "
               "reinicia. Com o cabo bom, a Cabine abre sozinha (quando a obra está parada) ou pelo botão Liberar Wi-Fi",
    "nao_autorizado": "chegou ao Quest em {ip}, mas ele não autorizou — no capacete, aceite “Permitir depuração” "
                      "marcando “Sempre permitir deste computador”",
    "sem_rede": "o Quest não responde em {ip} — ele está ligado e acordado? na mesma rede deste computador? "
                "o ip pode ter mudado: ligue o cabo uma vez e a Cabine descobre o novo",
    "sem_resposta": "{ip} responde, mas o adb não atende — ligue o cabo e aperte Liberar Wi-Fi",
}
CAMINHOS = {"tentativa": None, "ping": None, "link": False, "windows_ve": None, "armados": {}}


def tentar_wifi(ip):
    """Uma tentativa pela Wi-Fi, com o motivo da falha em uma palavra."""
    # uma entrada 'offline' velha faz o connect responder 'already connected'
    # sem conectar nada: tira antes
    adb("disconnect", f"{ip}:5555", timeout=5)
    r = adb("connect", f"{ip}:5555", timeout=6)
    b = r.lower()
    if "connected to" in b or "already connected" in b:
        return "ok", r
    if "authenticate" in b or "unauthorized" in b:
        return "nao_autorizado", r
    if "10061" in r or "refused" in b or "recus" in b:
        return "fechada", r
    return "sem_resposta", r


def responde_ping(ip):
    if MAC:
        saida, _ = rodar(["ping", "-c", "1", "-t", "2", ip], timeout=5)
    else:
        saida, _ = rodar(["ping", "-n", "1", "-w", "1500", ip], timeout=5)
    return "ttl=" in saida.lower()


def link_aberto():
    """O Meta Quest Link rodando neste PC toma o cabo e esconde a caixa de
    permissao -- foi o que prendeu o Quest em 'unauthorized' por uma hora."""
    if MAC:
        return False
    saida, _ = rodar(["tasklist", "/FI", "IMAGENAME eq OVRServer_x64.exe"], timeout=8)
    return "OVRServer_x64.exe" in saida


def windows_ve_quest():
    """Se o Windows enxerga o Quest no USB mesmo quando o adb nao."""
    if MAC:
        return None
    saida, _ = rodar(["powershell", "-NoProfile", "-Command",
                      "@(Get-PnpDevice -PresentOnly | Where-Object { $_.FriendlyName -match 'Quest|Reality Labs' }).Count"],
                     timeout=15)
    try:
        return int(saida.strip().splitlines()[-1]) > 0
    except Exception:
        return None


def diagnosticar(lista, ip):
    """Cada caminho em uma frase: nivel (ok, aviso, erro, fora) e o que fazer."""
    cabo = next((a for a in lista if a["via"] == "cabo"), None)
    wifi = next((a for a in lista if a["via"] == "wifi" and (not ip or a["serial"].startswith(ip))), None) \
        or next((a for a in lista if a["via"] == "wifi"), None)
    d = {"extra": []}

    if cabo and cabo["estado"] == "device":
        d["cabo"] = {"nivel": "ok", "msg": "conectado"}
    elif cabo and cabo["estado"] == "unauthorized":
        d["cabo"] = {"nivel": "aviso", "msg": "esperando autorização — no capacete, aceite “Permitir depuração USB” marcando "
                     "“Sempre permitir deste computador”. Sem caixa: veja o sino de notificações; ou Configurações › Sistema › "
                     "Desenvolvedor › “Caixa de diálogo de conexão USB” ligada, e tire e ponha o cabo"}
    elif cabo:
        d["cabo"] = {"nivel": "erro", "msg": f"o Quest está no cabo mas não responde ({cabo['estado']}) — tire e ponha o cabo; "
                     "se repetir, reinicie o Quest"}
    elif CAMINHOS["windows_ve"]:
        d["cabo"] = {"nivel": "erro", "msg": "o Windows vê o Quest no USB, mas o adb não — o modo de desenvolvedor pode ter "
                     "desligado (app Meta Horizon › Dispositivos › Modo de desenvolvedor), ou o Link está segurando o cabo"}
    else:
        d["cabo"] = {"nivel": "fora", "msg": "sem cabo — ou o cabo só carrega e não passa dados (use um cabo de dados, "
                     "direto numa porta do computador)"}

    if wifi and wifi["estado"] == "device":
        d["wifi"] = {"nivel": "ok", "msg": f"conectado ({wifi['serial']})"}
    elif wifi and wifi["estado"] == "unauthorized":
        d["wifi"] = {"nivel": "aviso", "msg": FRASE_WIFI["nao_autorizado"].format(ip=ip or wifi["serial"])}
    elif not ip:
        d["wifi"] = {"nivel": "fora", "msg": "ainda sem o ip do Quest — com o cabo ligado uma vez, a Cabine descobre e guarda"}
    else:
        tipo = (CAMINHOS["tentativa"] or ("sem_resposta", ""))[0]
        if tipo == "sem_resposta" and CAMINHOS["ping"] is False:
            tipo = "sem_rede"
        d["wifi"] = {"nivel": "erro" if tipo == "sem_rede" else "aviso", "msg": FRASE_WIFI.get(tipo, "").format(ip=ip)}

    if CAMINHOS["link"]:
        d["extra"].append("O Meta Quest Link está aberto neste computador: ele toma o cabo e esconde a caixa de permissão. "
                          "Feche-o (ícone perto do relógio › Sair) ou pare o serviço “Oculus VR Runtime Service”.")
    bons = [k for k in ("cabo", "wifi") if d[k]["nivel"] == "ok"]
    if len(bons) == 2:
        d["nivel"], d["resumo"] = "ok", "os dois caminhos estão de pé: se o cabo sair, a Wi-Fi assume"
    elif bons:
        outro = "wifi" if bons[0] == "cabo" else "cabo"
        nome = {"cabo": "cabo", "wifi": "Wi-Fi"}
        d["nivel"] = "aviso"
        d["resumo"] = f"conectado pelo {nome[bons[0]]}; o caminho reserva ({nome[outro]}) não está de pé"
    else:
        d["nivel"], d["resumo"] = "erro", "nenhum caminho funcionou — veja abaixo o motivo de cada um"
    return d


def bateria(serial):
    m = re.search(r"level: (\d+)", adb("shell", "dumpsys", "battery", serial=serial, timeout=10))
    return int(m.group(1)) if m else None


def quadros(serial):
    saida = adb("logcat", "-d", "-t", "300", "-s", "VrApi", serial=serial, timeout=10)
    ultimas = [l for l in saida.splitlines() if "FPS=" in l]
    if not ultimas:
        return None, None
    fps = re.search(r"FPS=(\d+)/", ultimas[-1])
    app = re.search(r"App=([\d.]+)ms", ultimas[-1])
    return (int(fps.group(1)) if fps else None), (float(app.group(1)) if app else None)


def acordado(serial, ligar):
    if ligar:
        adb("shell", "am", "broadcast", "-a", "com.oculus.vrpowermanager.prox_close", serial=serial)
        adb("shell", "settings", "put", "global", "stay_on_while_plugged_in", "7", serial=serial)
    else:
        adb("shell", "am", "broadcast", "-a", "com.oculus.vrpowermanager.automation_disable", serial=serial)
    with TRAVA:
        ESTADO["quest"]["acordado"] = bool(ligar)
    relatar("Quest pensa que está na cabeça (mesa)" if ligar else "Quest volta a dormir ao sair da cabeça")
    return {"ok": True}


# ── o navegador do Quest, pelo DevTools ──────────────────────────────────

def abas():
    try:
        with urlopen(f"http://localhost:{PORTA_DEVTOOLS}/json", timeout=3) as r:
            return [t for t in json.load(r) if t.get("type") == "page"]
    except Exception:
        return None


def aba_da_obra():
    lista = abas() or []
    for t in lista:
        if f"localhost:{PORTA_OBRA}" in t.get("url", ""):
            return t
    return None


def trazer_aba(aba):
    try:
        urlopen(f"http://localhost:{PORTA_DEVTOOLS}/json/activate/{aba['id']}", timeout=3).read()
    except Exception:
        pass


def avaliar(expr, gesto=False, timeout=12):
    """Roda JS na aba da obra pelo quest_eval.mjs (a ferramenta da casa)."""
    args = ["node", os.path.join(AQUI, "quest_eval.mjs"), f"localhost:{PORTA_OBRA}", expr]
    if gesto:
        args.append("gesto")
    saida, cod = rodar(args, timeout=timeout, cwd=RAIZ)
    if cod != 0:
        return None, saida
    try:
        return json.loads(saida), None
    except Exception:
        return saida, None


LEITURA = ("(function(){var q=function(i){var e=document.getElementById(i);return e?e.textContent.trim():''};"
           "var p=document.getElementById('portao');"
           "return {portao: !!p && getComputedStyle(p).display!=='none', versao:q('portaoVersao'),"
           "programas:q('portaoProgramas'), erro:q('portaoErro'), aviso:q('portaoAviso'),"
           "onde:(window.raizes&&raizes.onde)?raizes.onde():null, url:location.pathname,"
           "tela:(window.raizes&&raizes.tela)?raizes.tela.onde():null}})()")


# ── seis ou dez minutos (26/09) ─────────────────────────────────────────
# "Coloca um controle de tempo pra gente poder alterar o tempo da experiencia, um de
# 6 minutos e 10 minutos." A escolha fica guardada aqui (por maquina), vai no endereco
# ao abrir a obra (?min=6|10) e, com a obra aberta e o portao a vista, e aplicada na
# hora pelo gancho raizes.duracao(). A obra so tem o controle a partir da versao que
# o trouxe (ramo proxima-deusas-rosa); nas anteriores o endereco e ignorado.
DURACAO_ARQ = os.path.join(AQUI, "duracao_min.txt")


def minutos_escolhidos():
    try:
        m = int(open(DURACAO_ARQ).read().strip())
        return m if m in (6, 10) else 10
    except Exception:
        return 10


def escolher_duracao(minutos):
    if minutos not in (6, 10):
        return {"ok": False, "erro": "so 6 ou 10 minutos"}
    if experiencia_acontecendo():
        return {"ok": False, "erro": "no meio da obra não muda — escolha quando o portão voltar"}
    with open(DURACAO_ARQ, "w") as f:
        f.write(str(minutos))
    with TRAVA:
        ESTADO["duracao_min"] = minutos
    resposta = f"{minutos} minutos: valem na próxima vez que a obra abrir"
    if ESTADO["obra"].get("aba"):
        r, e = avaliar(f"(window.raizes&&raizes.duracao)?raizes.duracao({minutos}):'sem controle'")
        if r == minutos:
            resposta = f"{minutos} minutos: já valem para a próxima pessoa"
        elif r == "sem controle":
            resposta = f"{minutos} minutos guardados — esta versão da obra ainda não tem o controle (chega com a próxima)"
    relatar("duração: " + resposta)
    return {"ok": True, "resposta": resposta}


def abrir_no_quest(serial, versao):
    arquivo = VERSOES.get(versao, "")
    url = f"http://localhost:{PORTA_OBRA}/{arquivo}?min={minutos_escolhidos()}"
    aba = aba_da_obra()
    if aba:
        avaliar(f"location.href={json.dumps(url)}; 'indo'")
    else:
        adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url,
            NAVEGADOR_QUEST, serial=serial)
    time.sleep(1.5)
    aba = aba_da_obra()
    if aba:
        trazer_aba(aba)
    relatar(f"abrindo {url} no Quest")
    return {"ok": True, "url": url}


def clicar(id_botao):
    aba = aba_da_obra()
    if not aba:
        return {"ok": False, "erro": "a obra não está aberta no navegador do Quest"}
    trazer_aba(aba)                     # aba atrás = SecurityError no WebXR
    time.sleep(0.6)
    r, erro = avaliar(f"(function(){{var b=document.getElementById('{id_botao}');"
                      f"if(!b) return 'sem botao';b.click();return 'clicado'}})()", gesto=True)
    relatar(f"{id_botao}: {r or erro}")
    return {"ok": r == "clicado", "resposta": r or erro}


# ── a rede ───────────────────────────────────────────────────────────────

def hotspot_mac(acao="status"):
    """O Compartilhamento de Internet do macOS. Ligado, ele cria a ponte
    bridge100 com o ip 192.168.2.1 e os aparelhos ganham 192.168.2.x. Nao ha
    como liga-lo por comando sem senha de administrador, entao 'on' e 'off'
    abrem a janela certa dos Ajustes e o operador vira a chave."""
    saida, _ = rodar(["ifconfig", "bridge100"], timeout=8)
    m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", saida)
    ligado = bool(m)
    if acao in ("on", "off"):
        # Ventura/Sonoma/Sequoia; se a URL nao abrir, cai no painel geral
        rodar(["open", "x-apple.systempreferences:com.apple.Sharing-Settings.extension"], timeout=8)
        aviso = ("nos Ajustes do Sistema > Geral > Compartilhamento, vire a chave "
                 "'Compartilhamento de Internet' " + ("para LIGADA (com Wi-Fi como saida)" if acao == "on" else "para DESLIGADA"))
    else:
        aviso = None
    ssid = None
    s2, _ = rodar(["defaults", "read", "/Library/Preferences/SystemConfiguration/com.apple.nat"], timeout=8)
    m2 = re.search(r'"?(?:NetworkName|SSID)"?\s*=\s*"?([^";\n]+)', s2)
    if m2:
        ssid = m2.group(1).strip()
    return {"ligado": ligado, "estado": "On" if ligado else "Off", "ssid": ssid or "(o nome da rede fica nos Ajustes > Compartilhamento de Internet > Wi-Fi)",
            "senha": None, "clientes": None, "ip": m.group(1) if m else None,
            "compartilha": "Compartilhamento de Internet do macOS", "erro": None, "aviso": aviso, "mac": True}


def hotspot(acao="status", ssid=None, senha=None):
    if MAC:
        return hotspot_mac(acao)
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
           os.path.join(AQUI, "hotspot.ps1"), acao]
    if ssid:
        cmd += ["-ssid", ssid]
    if senha:
        cmd += ["-senha", senha]
    saida, _ = rodar(cmd, timeout=40)
    try:
        return json.loads(saida.splitlines()[-1])
    except Exception:
        return {"ligado": False, "erro": saida[-300:]}


def wifi_do_mac():
    """A Wi-Fi em que o Mac esta (nome e ip). O dispositivo (en0, en1...) vem
    da lista de portas; o nome da rede, do networksetup."""
    portas, _ = rodar(["networksetup", "-listallhardwareports"], timeout=10)
    m = re.search(r"Hardware Port: Wi-Fi\s*\nDevice: (\w+)", portas)
    dev = m.group(1) if m else "en0"
    s1, _ = rodar(["networksetup", "-getairportnetwork", dev], timeout=10)
    ssid = s1.split(":", 1)[1].strip() if ":" in s1 and "not associated" not in s1.lower() else None
    ip, _ = rodar(["ipconfig", "getifaddr", dev], timeout=10)
    return {"ssid": ssid, "ip": ip if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", ip or "") else None}


def wifi_do_pc():
    if MAC:
        return wifi_do_mac()
    saida, _ = rodar(["netsh", "wlan", "show", "interfaces"], timeout=10)
    ssid = re.search(r"^\s*SSID\s*:\s*(.+)$", saida, re.M)
    ip = None
    s2, _ = rodar(["ipconfig"], timeout=10)
    m = re.search(r"Wi-Fi.*?IPv4[^\d]*(\d+\.\d+\.\d+\.\d+)", s2, re.S)
    if m:
        ip = m.group(1)
    return {"ssid": ssid.group(1).strip() if ssid else None, "ip": ip}


# ── o espelho (scrcpy) ───────────────────────────────────────────────────

def achar_scrcpy():
    import glob
    import shutil
    c = shutil.which("scrcpy")
    if c:
        return c
    for p in glob.glob(os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Genymobile.scrcpy*\**\scrcpy.exe"), recursive=True):
        return p
    return None


def recorte_de_um_olho(serial):
    """O Quest manda a tela INTEIRA do painel: os dois olhos lado a lado
    (no Quest 3, 4128 x 2208 -- dois quadros de 2064 x 2208). Projetado
    assim sai a imagem dupla (25/09: "quando apareceu tava mostrando os
    olhos separados"). O recorte e o olho esquerdo, no miolo, em 16:9 --
    o formato do projetor -- com uma folga de 12 % em volta, onde a lente
    ja deforma e escurece."""
    m = re.search(r"(\d+)x(\d+)", adb("shell", "wm", "size", serial=serial, timeout=8))
    if not m:
        return ""
    larg, alt = int(m.group(1)), int(m.group(2))
    if larg <= alt:                       # nao e painel de dois olhos
        return ""
    olho = larg // 2
    w = int(olho * 0.88) // 2 * 2
    h = int(w * 9 / 16) // 2 * 2
    if h > alt * 0.88:
        h = int(alt * 0.88) // 2 * 2
        w = int(h * 16 / 9) // 2 * 2
    return f"{w}:{h}:{(olho - w) // 2}:{(alt - h) // 2}"


# O GIRO DO ESPELHO (25/09): "o espelhamento fica torto". O scrcpy 3.2+ gira
# em qualquer angulo (--angle, horario). Vale para o espelho e para a
# projecao do oculos, e fica guardado por maquina em fontes/espelho_angulo.txt.
ANGULO_ARQ = os.path.join(AQUI, "espelho_angulo.txt")


def angulo_do_espelho():
    try:
        return float(open(ANGULO_ARQ).read().strip())
    except Exception:
        return 0.0


def args_do_giro():
    a = angulo_do_espelho()
    return [f"--angle={a:g}"] if abs(a) > 0.05 else []


def args_da_rede(serial, projetor=False):
    """O video do oculos conforme o caminho (26/09: "faca um buffer para
    funcionar melhor no wifi; o projetor e full hd").

    PELA WI-FI (serial ip:5555, a rede do modem 4G UFI, 2,4 GHz, dividida com
    o proprio oculos): um BUFFER segura os quadros 200 ms (250 no projetor)
    antes de mostrar -- as rajadas e buracos da Wi-Fi viram atraso constante
    em vez de engasgo; 8 Mbps a 30 quadros e o que um Full HD pede sem
    estourar a rede; e um quadro-chave por segundo (i-frame-interval=1) faz a
    imagem se recompor em 1 s quando um pacote se perde, em vez de borrar ate
    o proximo. O atraso total fica perto de meio segundo: para quem assiste
    na tela, nao se nota; para quem esta de oculos, a projecao nao conta.

    PELO CABO: sem buffer; no projetor, 12 Mbps (Full HD com folga)."""
    wifi = bool(serial and ":" in serial)
    if wifi:
        # 26/09: "conseguimos reduzir um pouco a resolucao para melhorar o
        # lag?" -- pelo ar, 1280 de largura (o projetor amplia para Full HD):
        # 55 % menos pixels para codificar no oculos e passar pela Wi-Fi.
        # 26/09, a tarde: "esta piscando o espelhamento". Era o quadro-chave a cada
        # segundo (i-frame-interval=1): na Wi-Fi do modem (ping de 9 a 214 ms) o
        # quadro grande chegava atrasado todo segundo e a imagem piscava no mesmo
        # ritmo. Volta o intervalo padrao do scrcpy; o buffer sobe para 400 ms no
        # projetor (cobre os picos da rede; a plateia nao sente atraso) e a taxa
        # desce para 5 Mbps, sem rajadas.
        # 26/09, mais tarde: "estabilizou, mas o delay ta bem forte; pode reduzir um pouco a
        # qualidade". O buffer de 400 ms somava quase meio segundo. Agora 1024 de largura e
        # 4 Mbps (menos para codificar no oculos e para passar pela rede) e 120 ms de buffer
        # no projetor (60 na janela do Mac, que alimenta o espelho estabilizado).
        return ["--max-size=1024", "--video-bit-rate=4M", "--max-fps=30", f"--video-buffer={120 if projetor else 60}"]
    return ["--video-bit-rate=12M"] if projetor else []


def fechar_espelhos():
    """Fecha os espelhos abertos (janela e projecao), para reabrir com o giro novo."""
    rodar(["pkill", "-f", "scrcpy.*Quest"], timeout=5) if MAC else None


def espelhar(serial, geometria=None):
    exe = achar_scrcpy()
    if not exe:
        return {"ok": False, "erro": "scrcpy não está instalado nesta máquina (winget install Genymobile.scrcpy)"}
    # ADB=<o nosso>: o scrcpy traz outro adb, e dois adbs diferentes derrubam
    # o servidor um do outro -- e com ele os túneis.
    amb = dict(os.environ, ADB=ADB)
    corte = recorte_de_um_olho(serial)
    # geometria (x, y, w, h): a janela-fonte do espelho estabilizado, num canto do Mac
    geo = ([f"--window-x={geometria[0]}", f"--window-y={geometria[1]}", f"--window-width={geometria[2]}",
            f"--window-height={geometria[3]}"] if geometria else [])
    subprocess.Popen([exe, "-s", serial] + geo + ([] if ":" in serial else ["--max-size", "1280"]) + ["--no-audio",
                      "--window-title", "Quest — espelho"] + (["--crop", corte] if corte else []) + args_do_giro() + args_da_rede(serial),
                     env=amb, creationflags=SEM_JANELA)
    relatar("espelho do Quest aberto (scrcpy)" + (f", um olho só ({corte})" if corte else ""))
    return {"ok": True}


# ── a projeção (6.0): o que vai para o projetor ──────────────────────────

def monitores_mac():
    """Os monitores pelo system_profiler. Ele nao diz a POSICAO de cada um;
    o principal fica em 0,0 e os outros sao postos a direita dele, um apos o
    outro -- e o arranjo padrao dos Ajustes. Se o projetor estiver arrumado
    de outro jeito, a pagina em quiosque abre no monitor errado: arraste-a e
    aperte F (tela cheia)."""
    saida, _ = rodar(["system_profiler", "SPDisplaysDataType", "-json"], timeout=30)
    lista, x = [], 0
    try:
        placas = json.loads(saida).get("SPDisplaysDataType", [])
        telas = []
        for placa in placas:
            for d in placa.get("spdisplays_ndrvs", []):
                res = d.get("_spdisplays_resolution") or d.get("spdisplays_resolution") or ""
                m = re.search(r"(\d+)\s*x\s*(\d+)", res)
                telas.append({"nome": d.get("_name", "monitor"), "w": int(m.group(1)) if m else 1920,
                              "h": int(m.group(2)) if m else 1080,
                              "principal": d.get("spdisplays_main") == "spdisplays_yes"})
        telas.sort(key=lambda t: not t["principal"])
        for t in telas:
            t["x"], t["y"] = x, 0
            x += t["w"]
            lista.append(t)
    except Exception:
        pass
    return lista


def monitores():
    """Os monitores, com posicao e tamanho (o projetor e um deles)."""
    if MAC:
        return monitores_mac()
    saida, _ = rodar(["powershell", "-NoProfile", "-Command",
                      "Add-Type -AssemblyName System.Windows.Forms; "
                      "[System.Windows.Forms.Screen]::AllScreens | ForEach-Object { [pscustomobject]@{ nome=$_.DeviceName; "
                      "x=$_.Bounds.X; y=$_.Bounds.Y; w=$_.Bounds.Width; h=$_.Bounds.Height; principal=$_.Primary } } "
                      "| ConvertTo-Json -Compress"], timeout=20)
    try:
        lista = json.loads(saida.splitlines()[-1])
        return lista if isinstance(lista, list) else [lista]
    except Exception:
        return []


def achar_navegador():
    if MAC:
        for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                  "/Applications/Chromium.app/Contents/MacOS/Chromium"]:
            if os.path.exists(c):
                return c
        return None
    for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]:
        if os.path.exists(c):
            return c
    return None


def projetar(saida, monitor, espelhar=False, recorte=""):
    """saida: 'pagina' (a agua da tela, projecao.html) ou 'espelho' (scrcpy, o que o oculos ve)."""
    global PROJECAO, PROJECAO_PEDIDA
    # 26/09: tres cliques em Projetar em tres segundos reiniciavam o espelho tres vezes
    # (pela Wi-Fi ele leva uns segundos para aparecer, e parecia que o botao nao fazia
    # nada). O mesmo pedido repetido em menos de 10 s, com o anterior vivo, e ignorado.
    pedido = (saida, monitor, bool(espelhar), recorte)
    if (PROJECAO_PEDIDA and PROJECAO_PEDIDA[0] == pedido and time.time() - PROJECAO_PEDIDA[1] < 10
            and PROJECAO and PROJECAO.poll() is None):
        return {"ok": True, "resposta": "já está abrindo — pela Wi-Fi leva alguns segundos"}
    PROJECAO_PEDIDA = (pedido, time.time())
    parar_projecao()
    lista = ESTADO["monitores"] or monitores()
    # JANELA DE TESTE (25/09): "e so pra saber se vai funcionar, depois vamos
    # selecionar o projetor". Sai exatamente o que iria para o projetor -- o
    # mesmo olho, o mesmo recorte, o mesmo espelhamento -- mas numa janela
    # comum, que se arrasta e redimensiona, em vez da tela cheia de um
    # monitor. Com um monitor so, e a unica forma de ver a projecao sem ela
    # cobrir a propria Cabine.
    janela = monitor == "janela"
    alvo = None
    for m in lista:
        if janela:
            if m.get("principal"):
                alvo = m
                break
        elif str(m.get("nome")) == str(monitor) or (monitor in (None, "", "auto") and not m.get("principal")):
            alvo = m
            break
    if not alvo and lista:
        alvo = lista[0]
    alvo = alvo or {}
    x, y, w, h = alvo.get("x", 0), alvo.get("y", 0), alvo.get("w", 1920), alvo.get("h", 1080)
    if janela:
        x, y, w, h = x + 120, y + 90, 960, 540
    onde = "numa janela de teste" if janela else f"no monitor {alvo.get('nome', '?')}"
    if saida == "pagina":
        nav = achar_navegador()
        if not nav:
            return {"ok": False, "erro": "não achei Chrome nem Edge para abrir a projeção"}
        perfil = os.path.join(os.environ.get("TEMP") or os.environ.get("TMPDIR") or AQUI, "raizes-projecao-perfil")
        url = (f"http://localhost:{PORTA_OBRA}/projecao.html?espelho={'1' if espelhar else '0'}"
               f"&cabine=http://localhost:{PORTA_CABINE}")
        # quiosque ocupa o monitor inteiro; a janela de teste e uma janela de
        # aplicativo (sem barra de endereco), do tamanho que se quiser
        modo = [f"--app={url}"] if janela else ["--kiosk", url]
        PROJECAO = subprocess.Popen([nav, f"--window-position={x},{y}", f"--window-size={w},{h}",
                                     f"--user-data-dir={perfil}", "--no-first-run", "--no-default-browser-check",
                                     "--autoplay-policy=no-user-gesture-required", "--disable-infobars"] + modo,
                                    creationflags=SEM_JANELA)
        relatar(f"projeção (página) aberta {onde} {w}x{h}" + (" espelhada" if espelhar else ""))
    elif saida == "estavel":
        # O ESPELHO ESTABILIZADO (26/09): "ainda esta oscilando a imagem do espelhamento".
        # A imagem balanca com a cabeca de quem esta de oculos (medido: 6 a 12 % da largura
        # entre fotos de 0,15 s). A pagina fontes/espelho.html (?auto=1) captura a janela
        # "Quest — espelho" do Mac, mede o pulo quadro a quadro e o desfaz, ficando so o
        # movimento lento. O Chrome escolhe a janela sozinho e a Cabine dispara a captura
        # pelo DevTools dele (porta 9333), com gesto. Pede, uma vez, a permissao de Gravacao
        # de Tela do Chrome nos Ajustes do Mac.
        s = ESTADO["quest"]["escolhido"]
        nav = achar_navegador()
        if not s:
            return {"ok": False, "erro": "nenhum Quest ao alcance para espelhar"}
        if not nav:
            return {"ok": False, "erro": "não achei Chrome nem Edge para a projeção estabilizada"}
        if not rodar(["pgrep", "-f", "window-title Quest — espelho"], timeout=5)[0].strip():
            principal = next((m for m in lista if m.get("principal")), {"x": 0, "y": 0, "w": 1440, "h": 900})
            espelhar(s, (principal.get("x", 0) + principal.get("w", 1440) - 980, principal.get("y", 0) + 60, 960, 540))
            time.sleep(3)
        perfil = os.path.join(os.environ.get("TEMP") or os.environ.get("TMPDIR") or AQUI, "raizes-projecao-perfil")
        url = (f"http://localhost:{PORTA_OBRA}/fontes/espelho.html?auto=1&estab=1&espelhar={'1' if espelhar else '0'}")
        modo = [f"--app={url}"] if janela else ["--kiosk", url]
        PROJECAO = subprocess.Popen([nav, f"--window-position={x},{y}", f"--window-size={w},{h}",
                                     f"--user-data-dir={perfil}", "--no-first-run", "--no-default-browser-check",
                                     "--remote-debugging-port=9333", "--auto-select-desktop-capture-source=Quest — espelho",
                                     "--autoplay-policy=no-user-gesture-required", "--disable-infobars"] + modo,
                                    creationflags=SEM_JANELA)
        threading.Thread(target=disparar_captura_estavel, daemon=True).start()
        relatar(f"projeção (espelho estabilizado) aberta {onde}" + (", espelhada" if espelhar else ""))
    elif saida == "espelho":
        s = ESTADO["quest"]["escolhido"]
        exe = achar_scrcpy()
        if not exe:
            return {"ok": False, "erro": "scrcpy não está instalado"}
        if not s:
            return {"ok": False, "erro": "nenhum Quest ao alcance para espelhar"}
        args = [exe, "-s", s, "--no-audio", f"--window-x={x}", f"--window-y={y}", "--max-fps", "30"]
        if janela:
            args += [f"--window-width={w}", f"--window-height={h}", "--window-title", "Quest — projeção (teste)"]
        else:
            args += ["--fullscreen", "--window-title", "Quest — projeção"]
        # sem recorte escrito na Cabine, um olho so -- nunca os dois lado a lado
        recorte = recorte or recorte_de_um_olho(s)
        if recorte:
            args += ["--crop", recorte]
        # retroprojecao (projetor atras do tule): a imagem sai espelhada na
        # horizontal, como a pagina ja fazia
        if espelhar:
            args += ["--display-orientation=flip0"]
        # o projetor e Full HD: o olho recortado (1816 x 1020) vai inteiro, sem reduzir
        rede = [x for x in args_da_rede(s, projetor=True) if not x.startswith('--max-fps')]
        args += ([] if any(x.startswith("--max-size") for x in rede) else ["--max-size=1920"]) + args_do_giro() + rede
        # so um monitor ligado: o espelho cobriria a propria tela da Cabine
        if not janela and alvo.get("principal") and len(lista) == 1:
            relatar("projeção: só há um monitor ligado -- ligue o projetor e ponha o Windows em Estender (tecla Windows + P)")
        PROJECAO = subprocess.Popen(args, env=dict(os.environ, ADB=ADB), creationflags=SEM_JANELA)
        relatar(f"projeção (espelho do óculos) aberta {onde}" + (f", recorte {recorte}" if recorte else "")
                + (", espelhada" if espelhar else ""))
    else:
        return {"ok": False, "erro": f"saída desconhecida: {saida}"}
    with TRAVA:
        ESTADO["projecao"] = {"ativa": True, "saida": saida, "espelhar": bool(espelhar),
                              "monitor": "janela de teste" if janela else alvo.get("nome")}
    return {"ok": True}


def disparar_captura_estavel():
    """Espera a pagina do projetor subir e dispara a captura da janela do espelho, com gesto."""
    amb = dict(os.environ, CDP_PORTA="9333")
    for _ in range(20):
        time.sleep(1)
        try:
            abas_p = json.loads(urlopen("http://localhost:9333/json", timeout=2).read())
        except Exception:
            continue
        if not any("espelho.html" in a.get("url", "") for a in abas_p):
            continue
        saida, cod = rodar(["node", os.path.join(AQUI, "quest_eval.mjs"), "espelho.html",
                            "capturar().then(()=>aoVivo?'ao vivo':document.getElementById('vazio').textContent)", "gesto"],
                           timeout=20, cwd=RAIZ, env=amb)
        relatar("espelho estabilizado: " + (saida.strip().strip('"')[:160] or "sem resposta"))
        return
    relatar("espelho estabilizado: a página do projetor não respondeu no DevTools (9333)")


def parar_projecao():
    global PROJECAO
    if PROJECAO and PROJECAO.poll() is None:
        try:
            PROJECAO.terminate()
        except Exception:
            pass
        relatar("projeção fechada")
    PROJECAO = None
    with TRAVA:
        ESTADO["projecao"] = {"ativa": False, "saida": None, "monitor": None, "espelhar": False}
    return {"ok": True}


def tela_js(expr):
    r, e = avaliar(f"(window.raizes&&raizes.tela)?JSON.stringify({expr}):'sem tela aqui'")
    if isinstance(r, str) and r[:1] in ('{', '[', '"'):
        try:
            r = json.loads(r)
        except Exception:
            pass
    return {"ok": r is not None and r != "sem tela aqui", "resposta": r if r is not None else e}


# ── o servidor da obra (servir.py como filho) ────────────────────────────

def subir_servidor_da_obra():
    global SERVIDOR_OBRA
    amb = dict(os.environ, ESTANDE="1", PYTHONIOENCODING="utf-8")
    SERVIDOR_OBRA = subprocess.Popen([sys.executable, "-u", os.path.join(AQUI, "servir.py"), str(PORTA_OBRA)],
                                     cwd=RAIZ, env=amb, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, encoding="utf-8", errors="replace", creationflags=SEM_JANELA)

    def ler():
        for linha in SERVIDOR_OBRA.stdout:
            linha = linha.rstrip()
            if linha.startswith("  >> "):
                relatar(linha[5:], origem="quest")
            elif "Address already in use" in linha or "Only one usage" in linha or "10048" in linha:
                relatar(f"a porta {PORTA_OBRA} já está em uso (outro estande.py/servir.py de pé?)")
        with TRAVA:
            ESTADO["servidor"]["de_pe"] = False
    threading.Thread(target=ler, daemon=True).start()
    time.sleep(1.0)
    with TRAVA:
        ESTADO["servidor"]["de_pe"] = SERVIDOR_OBRA.poll() is None


# ── o vigia: lê tudo de tempos em tempos ─────────────────────────────────

def vigiar():
    vistos = {}
    ciclo = 0
    while True:
        try:
            ciclo += 1
            lista = aparelhos()
            ip_guardado = open(IP_GUARDADO).read().strip() if os.path.exists(IP_GUARDADO) else None
            cabo_ok = any(a["via"] == "cabo" and a["estado"] == "device" for a in lista)
            wifi_ok = any(a["via"] == "wifi" and a["estado"] == "device" for a in lista)
            # A WI-FI E TENTADA A CADA VOLTA quando e o unico caminho possivel,
            # e a cada cinco quando o cabo esta bom -- para a reserva estar
            # pronta se o cabo sair. Sem resposta, um ping diz se e a rede.
            if ip_guardado and not wifi_ok and (not cabo_ok or ciclo % 5 == 1):
                CAMINHOS["tentativa"] = tentar_wifi(ip_guardado)
                CAMINHOS["ping"] = responde_ping(ip_guardado) if CAMINHOS["tentativa"][0] == "sem_resposta" else None
                lista = aparelhos()
            elif wifi_ok:
                CAMINHOS["tentativa"], CAMINHOS["ping"] = ("ok", ""), None
            if ciclo % 4 == 1:
                CAMINHOS["link"] = link_aberto()
            if not any(a["via"] == "cabo" for a in lista) and ciclo % 6 == 1:
                CAMINHOS["windows_ve"] = windows_ve_quest()
            elif any(a["via"] == "cabo" for a in lista):
                CAMINHOS["windows_ve"] = True
            alvo = escolher(lista)
            for a in lista:
                if a["estado"] == "unauthorized" and vistos.get(a["serial"]) != "unauthorized":
                    relatar("Quest NÃO AUTORIZADO: no capacete, aceitar 'Permitir depuração USB' com 'Sempre permitir'")
                    vistos[a["serial"]] = "unauthorized"
            q = {"lista": lista, "escolhido": None, "via": None, "bateria": None, "ip": None,
                 "tuneis": False, "acordado": ESTADO["quest"]["acordado"], "ip_guardado": ip_guardado}
            o = dict(ESTADO["obra"])
            if alvo:
                s = alvo["serial"]
                boot = adb("shell", "cat", "/proc/sys/kernel/random/boot_id", serial=s, timeout=8).strip()
                if re.fullmatch(r"[0-9a-f-]{36}", boot) and vistos.get(s) != boot:
                    relatar(f"Quest apareceu pelo {alvo['via']} ({s})")
                    tuneis(s)
                    relatar(f"túneis refeitos: {PORTA_OBRA} (obra) e {PORTA_DEVTOOLS} (DevTools)")
                    # NAO libera a Wi-Fi sozinha (24/09, "consegue evitar que
                    # fique pedindo permissao toda hora?"). O "adb tcpip" reinicia
                    # o adb do oculos: derruba os tuneis no meio da obra (a aba
                    # que carregou nesse instante ficou quebrada) e, sem o
                    # "Sempre permitir", faz o Quest pedir a autorizacao de novo.
                    # A Wi-Fi so se libera pelo botao, quando alguem quer.
                    vistos[s] = boot
                q.update(escolhido=s, via=alvo["via"], ip=ip_do_quest(s),
                         tuneis=f"tcp:{PORTA_OBRA}" in adb("reverse", "--list", serial=s, timeout=8))
                # TUNEL CAIDO SE REFAZ SOZINHO: antes so se refazia quando o Quest
                # reiniciava (boot novo); um adb que reiniciou no meio deixava a
                # obra sem servidor ate alguem apertar "Refazer tuneis".
                if not q["tuneis"]:
                    tuneis(s)
                    q["tuneis"] = f"tcp:{PORTA_OBRA}" in adb("reverse", "--list", serial=s, timeout=8)
                    relatar("túnel da obra tinha caído — refeito" if q["tuneis"] else "túnel da obra caiu e não voltou")
                # PELO CABO: o ip do Quest se confere a cada volta -- se mudou
                # (o roteador deu outro), a reserva passa a apontar para o novo.
                if alvo["via"] == "cabo" and q["ip"] and q["ip"] != ip_guardado:
                    with open(IP_GUARDADO, "w") as f:
                        f.write(q["ip"])
                    if ip_guardado:
                        relatar(f"o ip do Quest mudou: {ip_guardado} → {q['ip']}")
                    ip_guardado = q["ip_guardado"] = q["ip"]
                # E A RESERVA SE ARMA SOZINHA -- uma vez por ligada do Quest, e so
                # com a obra PARADA (portao a vista ou nenhuma aba). O "tcpip"
                # reinicia o adb do oculos: no meio da obra isso derrubava os
                # tuneis; parado, os tuneis se refazem na volta seguinte e
                # ninguem ve. Sem o "Sempre permitir", o Quest pede a caixa de
                # novo -- e o diagnostico diz isso.
                obra_parada = ESTADO["obra"].get("portao") is not False
                if (alvo["via"] == "cabo" and q["ip"] and not any(a["via"] == "wifi" and a["estado"] == "device" for a in lista)
                        and obra_parada and CAMINHOS["armados"].get(s) != boot):
                    CAMINHOS["armados"][s] = boot
                    relatar("preparando o caminho reserva: abrindo o acesso pela Wi-Fi (a obra está parada)")
                    r = liberar_wifi(s)
                    relatar("reserva pela Wi-Fi de pé" if r.get("ok") else ("reserva pela Wi-Fi falhou: " + r.get("erro", "")))
                if ciclo % 5 == 1:
                    q["bateria"] = bateria(s)
                else:
                    q["bateria"] = ESTADO["quest"]["bateria"]
                aba = aba_da_obra() if q["tuneis"] else None
                o["aba"] = bool(aba)
                if aba:
                    o["url"] = aba.get("url")
                    leitura, _ = avaliar(LEITURA, timeout=8)
                    if isinstance(leitura, dict):
                        o.update(portao=leitura.get("portao"), versao=leitura.get("versao", ""),
                                 programas=leitura.get("programas", ""), onde=leitura.get("onde"),
                                 erro=leitura.get("erro", ""), aviso=leitura.get("aviso", ""))
                        with TRAVA:
                            ESTADO["tela"] = leitura.get("tela")
                    if ciclo % 2 == 0:
                        o["fps"], o["app_ms"] = quadros(s)
                else:
                    o.update(portao=None, onde=None, fps=None, app_ms=None)
            else:
                o.update(aba=False, portao=None, onde=None, fps=None, app_ms=None)
            for serial in list(vistos):
                if serial not in [a["serial"] for a in lista]:
                    relatar(f"Quest sumiu ({serial})")
                    del vistos[serial]
            q["diag"] = diagnosticar(aparelhos(), ip_guardado)
            antes = (ESTADO["quest"].get("diag") or {}).get("resumo")
            if q["diag"]["resumo"] != antes:
                relatar("conexão: " + q["diag"]["resumo"])
            rede = dict(ESTADO["rede"])
            if ciclo % 4 == 1:
                rede["hotspot"] = hotspot("status")
                rede["wifi_pc"] = wifi_do_pc()
                with TRAVA:
                    ESTADO["monitores"] = monitores()
                    ESTADO["projecao"]["ativa"] = PROJECAO is not None and PROJECAO.poll() is None
            with TRAVA:
                ESTADO["quest"] = q
                ESTADO["obra"] = o
                ESTADO["rede"] = rede
                ESTADO["hora"] = f"{datetime.now():%H:%M:%S}"
                ESTADO["servidor"]["de_pe"] = SERVIDOR_OBRA is not None and SERVIDOR_OBRA.poll() is None
                ESTADO["scrcpy"] = bool(achar_scrcpy())
        except Exception as e:      # a cabine não morre por um tropeço
            log(f"tropeço no vigia: {e!r}")
        time.sleep(3)


# ── as ações que a página pede ───────────────────────────────────────────

def agir(nome, dados):
    s = ESTADO["quest"]["escolhido"]
    precisa_quest = {"liberar_wifi", "tuneis", "abrir", "espelhar", "acordado", "desconectar", "tela_cravar"}
    if nome in precisa_quest and not s:
        d = ESTADO["quest"].get("diag") or {}
        motivo = " · ".join(f"{k}: {d[k]['msg']}" for k in ("cabo", "wifi") if d.get(k))
        return {"ok": False, "erro": "nenhum Quest ao alcance" + (f" — {motivo}" if motivo else "")}
    if nome == "hotspot_on":
        r = hotspot("on")
    elif nome == "hotspot_off":
        r = hotspot("off")
    elif nome == "hotspot_config":
        r = hotspot("config", dados.get("ssid"), dados.get("senha"))
    elif nome == "liberar_wifi":
        return liberar_wifi(s)
    elif nome == "conectar_wifi":
        ip = (dados.get("ip") or ESTADO["quest"]["ip_guardado"] or "").strip()
        if not ip:
            return {"ok": False, "erro": "sem ip: libere a Wi-Fi pelo cabo uma vez"}
        tipo, r = tentar_wifi(ip)
        relatar(f"conectar {ip}: {r}")
        if tipo == "ok":
            with open(IP_GUARDADO, "w") as f:
                f.write(ip)
            return {"ok": True, "resposta": r}
        if tipo == "sem_resposta" and not responde_ping(ip):
            tipo = "sem_rede"
        return {"ok": False, "resposta": r, "erro": FRASE_WIFI[tipo].format(ip=ip)}
    elif nome == "desconectar":
        r = adb("disconnect", timeout=8)
        return {"ok": True, "resposta": r}
    elif nome == "tuneis":
        return {"ok": tuneis(s)}
    elif nome == "abrir":
        return abrir_no_quest(s, dados.get("versao", "v6"))
    elif nome == "iniciar":
        return clicar("bIniciar")
    elif nome == "reiniciar":
        return clicar("bReiniciar")
    elif nome == "encerrar":
        return clicar("bParar")
    elif nome == "recarregar":
        r, e = avaliar("location.reload(); 'recarregando'")
        return {"ok": r is not None, "resposta": r or e}
    elif nome == "ir":
        seg = int(dados.get("seg", 0))
        r, e = avaliar(f"(window.raizes&&raizes.ir)?(raizes.ir({seg}),'foi'):'sem salto aqui'")
        return {"ok": r == "foi", "resposta": r or e}
    elif nome == "cena":
        n = int(dados.get("n", 1))
        r, e = avaliar(f"(window.raizes&&raizes.cena)?(raizes.cena({n}),'foi'):'sem salto aqui'")
        return {"ok": r == "foi", "resposta": r or e}
    elif nome == "acordado":
        return acordado(s, bool(dados.get("ligar")))
    elif nome == "escanear":
        aba = aba_da_obra()
        if not aba:
            return {"ok": False, "erro": "a obra não está aberta no navegador do Quest"}
        trazer_aba(aba)
        time.sleep(0.6)
        r, e = avaliar("(window.raizes&&raizes.escanear)?raizes.escanear():'sem gancho aqui (abra pela Cabine)'", gesto=True)
        relatar(f"escaneamento do espaço: {r or e}")
        return {"ok": r == "pedido", "resposta": r or e}
    elif nome in ("proxima_preparar", "proxima_ver", "proxima_publicar"):
        r = proxima(nome.split("_", 1)[1])
        with TRAVA:
            ESTADO["proxima"] = dict(PROXIMA)
        return r
    elif nome == "duracao":
        return escolher_duracao(int(dados.get("min", 10)))
    elif nome == "atualizar":
        r = sincronizar("botão")
        with TRAVA:
            ESTADO["sync"] = dict(SYNC)
        return r
    elif nome == "luz_ligar":
        return luz_ligar(dados.get("modo", "segue"), dados.get("via", "auto"))
    elif nome == "luz_parar":
        relatar("luz da sala: parada")
        return luz_parar()
    elif nome == "luz_procurar_bt":
        # a Cabine vive no Terminal: e ele que o macOS deixa (ou nao) usar o Bluetooth
        if MAC:
            # pelo Terminal, que e quem tem a permissao; o resultado volta num arquivo
            import tempfile
            arq = os.path.join(tempfile.gettempdir(), "raizes_bt_busca.txt")
            try:
                os.remove(arq)
            except OSError:
                pass
            cmd = f"'{sys.executable}' '{os.path.join(AQUI, 'luz_bluetooth.py')}' 12 > '{arq}' 2>&1; echo FIM >> '{arq}'; exit"
            rodar(["osascript", "-e", f'tell application "Terminal" to do script "{cmd}"'], timeout=10)
            saida = ""
            for _ in range(40):
                time.sleep(1)
                if os.path.exists(arq) and "FIM" in open(arq, encoding="utf-8", errors="replace").read():
                    saida = open(arq, encoding="utf-8", errors="replace").read().replace("FIM", "").strip()
                    break
        else:
            saida, _ = rodar([sys.executable, os.path.join(AQUI, "luz_bluetooth.py"), "12"], timeout=40)
        try:
            lista = json.loads(saida.strip().splitlines()[-1])
        except Exception:
            return {"ok": False, "erro": "o Bluetooth nao respondeu -- o macOS pode ter negado ao Terminal (Ajustes > Privacidade > Bluetooth)", "saida": saida[-400:]}
        if isinstance(lista, dict):
            return {"ok": False, "erro": lista.get("erro")}
        for d in lista[:12]:
            relatar(f"bluetooth: {d['nome'] or '(sem nome)'} {d['sinal']} dBm  servicos={','.join(d['servicos']) or '-'}"
                    f"  fab={','.join(d['fabricantes']) or '-'}  {d['parece']}")
        return {"ok": True, "achados": lista}
    elif nome == "luz_estado":
        return {"ok": True, "luz": luz_estado()}
    elif nome == "girar_espelho":
        a = max(-180.0, min(180.0, float(dados.get("graus", 0) or 0)))
        with open(ANGULO_ARQ, "w") as f:
            f.write(f"{a:g}")
        proj = dict(ESTADO["projecao"])
        fechar_espelhos()
        time.sleep(0.8)
        relatar(f"giro do espelho: {a:g} graus")
        if s:
            espelhar(s)
            if proj.get("ativa") and proj.get("saida") == "espelho":
                projetar("espelho", proj.get("monitor"), proj.get("espelhar"))
        return {"ok": True, "resposta": f"{a:g}°"}
    elif nome == "alinhar":
        # O ESPELHO ALINHADO (25/09): "o espelhamento fica torto". A pagina
        # captura a janela do espelho e a redesenha com giro fino, zoom,
        # deslocamento e a curvatura da lente desfeita (fontes/espelho.html).
        abrir_pagina(f"http://localhost:{PORTA_OBRA}/fontes/espelho.html")
        return {"ok": True, "resposta": "escolha a janela 'Quest — espelho' na captura"}
    elif nome == "transmitir":
        # A TELA HORIZONTAL DO APP META (25/09): "na visualizacao do oculos
        # gostaria de ver uma tela horizontal como vejo no app Meta Horizon".
        # O scrcpy le o painel cru (um olho, com a curvatura da lente); a
        # imagem limpa e a TRANSMISSAO do proprio Quest, que o Chrome recebe
        # em oculus.com/casting -- pela Wi-Fi, sem adb. No oculos: Transmitir
        # -> Computador (a mesma conta Meta logada no Chrome).
        abrir_pagina("https://www.oculus.com/casting")
        relatar("transmissão do Quest: no óculos, Transmitir -> Computador")
        return {"ok": True, "resposta": "no óculos: Transmitir → Computador"}
    elif nome == "espelhar":
        return espelhar(s)
    elif nome == "projetar":
        return projetar(dados.get("saida", "pagina"), dados.get("monitor"), bool(dados.get("espelhar")), dados.get("recorte", ""))
    elif nome == "parar_projecao":
        return parar_projecao()
    elif nome == "tela_cravar":
        return tela_js("raizes.tela.cravar()")
    elif nome == "tela_ditar":
        w, h = float(dados.get("largura") or 3.0), float(dados.get("altura") or 2.0)
        return tela_js(f"raizes.tela.ditar({{largura:{w}, altura:{h}, rumo:{float(dados.get('rumo') or 0)}}})")
    elif nome == "tela_mostrar":
        modo = dados.get("modo")
        js = "true" if modo == "acender" else "false" if modo == "apagar" else "null"
        return tela_js(f"raizes.tela.mostrar({js})")
    elif nome == "tela_toque":
        u, v = float(dados.get("u", 0.5)), float(dados.get("v", 0.5))
        r = tela_js(f"raizes.tela.toque({u}, {v}, 1)")
        if not r.get("ok"):      # sem óculos, a projeção ainda recebe o toque de teste
            relatar(f"TOCOU-A-TELA {u:.3f} {v:.3f} 1.0 teste-cabine", origem="quest")
            r = {"ok": True, "resposta": "toque mandado só à projeção"}
        return r
    elif nome == "tela_soltar":
        return tela_js("raizes.tela.soltar()")
    elif nome == "tela_ver":
        return tela_js("raizes.tela.ver(%s)" % ("true" if dados.get("ver") else "false"))
    elif nome == "limpar_relatos":
        with TRAVA:
            ESTADO["relatos"] = []
        return {"ok": True}
    elif nome == "fechar":
        threading.Timer(0.5, encerrar_tudo).start()
        return {"ok": True}
    else:
        return {"ok": False, "erro": f"ação desconhecida: {nome}"}
    if r.get("erro"):
        relatar(f"hotspot: {r['erro']}")
    with TRAVA:
        ESTADO["rede"]["hotspot"] = r
    return {"ok": not r.get("erro"), "hotspot": r}


# ── a luz da sala (Tuya, pela Wi-Fi) ─────────────────────────────────────
# 25/09: "a luz nao esta conectando, como faremos?". A lampada de sempre e a
# Tuya Wi-Fi; no Mac quem fala com ela e fontes/lampada.py (a API do estudio
# do v1 na porta 8600), e quem a faz seguir a obra e a luz-segue-cena.mjs,
# lendo o cenario pelo mesmo DevTools (9222) que a Cabine ja abre.
LUZ = {"lampada": None, "ponte": None, "modo": None}
LUZ_LOG = os.path.join(AQUI, "luz.log")


# QUAL LAMPADA (25/09, a noite): a do estande anuncia-se no Bluetooth como
# "GATT--DEMO" (app SMART+, LED colorida; protocolo ELK: fontes/lampada_bt.py).
# A Tuya Wi-Fi (fontes/lampada.py) so e usada quando ha chaves dela.
def via_da_luz():
    if os.path.exists(os.path.join(AQUI, "lampada.json")) or os.path.exists(os.path.join(RAIZ, "devices.json")):
        return "wifi"
    return "bluetooth"


def luz_parar():
    for k in ("ponte", "lampada"):
        p = LUZ.get(k)
        if p and p != "terminal" and p.poll() is None:
            try:
                p.terminate()
            except Exception:
                pass
        LUZ[k] = None
    # a ponte Bluetooth mora numa janela do Terminal (e dele a permissao)
    rodar(["pkill", "-f", "fontes/lampada_bt.py"], timeout=5)
    LUZ["modo"] = None
    return {"ok": True}


def luz_ligar(modo="segue", via="auto"):
    luz_parar()
    # 26/09: quatro pontes orfas (de Cabines fechadas pelo X do Terminal) consultavam o
    # oculos pelo DevTools a cada 3 s, pela mesma Wi-Fi do espelho. Uma ponte so.
    rodar(["pkill", "-f", "fontes/luz-segue-cena.mjs"], timeout=5)
    time.sleep(0.5)
    via = via_da_luz() if via == "auto" else via
    log_f = open(LUZ_LOG, "a", encoding="utf-8")
    if via == "bluetooth" and MAC:
        script = os.path.join(AQUI, "lampada_bt.py")
        cmd = f"exec '{sys.executable}' '{script}' >> '{LUZ_LOG}' 2>&1"
        rodar(["osascript", "-e", f'tell application "Terminal" to do script "{cmd}"'], timeout=10)
        LUZ["lampada"] = "terminal"
    else:
        arq = "lampada_bt.py" if via == "bluetooth" else "lampada.py"
        LUZ["lampada"] = subprocess.Popen([sys.executable, os.path.join(AQUI, arq)], cwd=RAIZ,
                                          stdout=log_f, stderr=subprocess.STDOUT, creationflags=SEM_JANELA)
    LUZ["via"] = via
    time.sleep(2.0)
    node = shutil.which("node") or "node"
    LUZ["ponte"] = subprocess.Popen([node, os.path.join(AQUI, "luz-segue-cena.mjs")] + (["deriva"] if modo == "deriva" else []),
                                    cwd=RAIZ, stdout=log_f, stderr=subprocess.STDOUT, creationflags=SEM_JANELA)
    LUZ["modo"] = modo
    relatar(f"luz da sala pelo {'Bluetooth' if via == 'bluetooth' else 'Wi-Fi'}: "
            f"{'seguindo a obra' if modo != 'deriva' else 'deriva'}")
    return {"ok": True}


def luz_estado():
    """O que a lampada diz agora (pela API do lampada.py) e se os dois estao de pe."""
    def vivo(k):
        p = LUZ.get(k)
        if p == "terminal":
            return bool(rodar(["pgrep", "-f", "fontes/lampada_bt.py"], timeout=5)[0].strip())
        return bool(p and p.poll() is None)
    vivos = {k: vivo(k) for k in ("lampada", "ponte")}
    est = {"modo": LUZ["modo"], "via": LUZ.get("via"), **vivos, "lampada_diz": None}
    if vivos["lampada"]:
        try:
            r = json.loads(urlopen("http://127.0.0.1:8600/api/luz?acao=estado", timeout=6).read())
            est["lampada_diz"] = "respondendo" if r.get("ok") else (r.get("erro") or "sem resposta")
        except Exception as e:
            try:
                est["lampada_diz"] = json.loads(e.read()).get("erro")      # 503 com o motivo
            except Exception:
                est["lampada_diz"] = "a ponte da lampada ainda nao respondeu"
    try:
        est["ultimas"] = open(LUZ_LOG, encoding="utf-8").read().splitlines()[-3:]
    except Exception:
        est["ultimas"] = []
    return est


def encerrar_tudo():
    log("cabine encerrando")
    try:
        parar_projecao()
        luz_parar()
        if SERVIDOR_OBRA and SERVIDOR_OBRA.poll() is None:
            SERVIDOR_OBRA.terminate()
    finally:
        os._exit(0)


# ── o servidor da Cabine ─────────────────────────────────────────────────

class Cabine(BaseHTTPRequestHandler):
    def _json(self, obj, cod=200):
        corpo = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(cod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/index.html"):
            with open(os.path.join(AQUI, "cabine.html"), "rb") as f:
                corpo = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
        elif self.path.startswith("/estado"):
            with TRAVA:
                self._json(ESTADO)
        elif self.path.startswith("/eventos"):
            # os relatos ao vivo, para a página de projeção (Server-Sent Events)
            fila = []
            with TRAVA:
                OUVINTES.append(fila)
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b": oi\n\n"); self.wfile.flush()
                quieto = 0.0
                while True:
                    if fila:
                        with TRAVA:
                            lote, fila[:] = list(fila), []
                        for r in lote:
                            self.wfile.write(("data: " + json.dumps(r, ensure_ascii=False) + "\n\n").encode("utf-8"))
                        self.wfile.flush(); quieto = 0.0
                    else:
                        time.sleep(0.15); quieto += 0.15
                        if quieto >= 15:
                            self.wfile.write(b": vivo\n\n"); self.wfile.flush(); quieto = 0.0
            except Exception:
                pass
            finally:
                with TRAVA:
                    if fila in OUVINTES:
                        OUVINTES.remove(fila)
        elif self.path == "/icone.png":
            with open(os.path.join(RAIZ, "icone-192.png"), "rb") as f:
                corpo = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
        else:
            self.send_error(404)

    def do_POST(self):
        if not self.path.startswith("/acao/"):
            self.send_error(404)
            return
        nome = re.sub(r"[^a-z_]", "", self.path[6:])
        n = int(self.headers.get("Content-Length", 0) or 0)
        try:
            dados = json.loads(self.rfile.read(n) or b"{}") if n else {}
        except Exception:
            dados = {}
        try:
            r = agir(nome, dados)
        except Exception as e:
            log(f"erro na ação {nome}: {e!r}")
            r = {"ok": False, "erro": repr(e)}
        self._json(r)

    def log_message(self, *a):
        pass


def abrir_pagina(url):
    """A pagina da Cabine abre no CHROME no Mac (25/09): a luz da sala e
    Bluetooth pela propria pagina (Web Bluetooth), e o Safari -- o navegador
    padrao do Mac -- nao tem isso. Sem Chrome, o navegador padrao."""
    nav = achar_navegador() if MAC else None
    if nav:
        app = nav.split("/Contents/")[0]
        try:
            subprocess.Popen(["open", "-a", app, url])
            return
        except Exception:
            pass
    webbrowser.open(url)


# ── sempre igual ao GitHub (26/09) ────────────────────────────────────────
# "Deixe sempre a versao local atualizada com o GitHub; estaremos fazendo
# atualizacoes pelo Unreal." O desktop publica; este computador so PUXA.
# Ao subir e a cada 5 minutos: git pull --ff-only. Nunca mescla nem apaga:
# se houver mudanca local nao publicada, ou o historico tiver divergido, ele
# para e avisa, e o que esta aqui fica como esta.
SYNC = {"ultimo": None, "commit": None, "aviso": None}


def sincronizar(motivo="ciclo"):
    antes, _ = rodar(["git", "-C", RAIZ, "rev-parse", "--short", "HEAD"], timeout=10)
    # o .pyc que o Python reescreve ao rodar nao e mudanca de ninguem: volta ao do git
    rodar(["git", "-C", RAIZ, "checkout", "--", "fontes/__pycache__"], timeout=10)
    sujo, _ = rodar(["git", "-C", RAIZ, "status", "--porcelain", "--untracked-files=no"], timeout=10)
    sujo = "\n".join(l for l in sujo.splitlines() if "__pycache__" not in l)
    if sujo.strip():
        SYNC.update(ultimo=datetime.now().strftime("%H:%M"), aviso="há mudança local não publicada: não puxei (publique ou descarte)")
        return {"ok": False, "erro": SYNC["aviso"]}
    saida, _ = rodar(["git", "-C", RAIZ, "pull", "--ff-only", "-q", "origin", "main"], timeout=90)
    depois, _ = rodar(["git", "-C", RAIZ, "rev-parse", "--short", "HEAD"], timeout=10)
    falhou = ("fatal" in saida.lower() or "error" in saida.lower()) and antes.strip() == depois.strip()
    SYNC.update(ultimo=datetime.now().strftime("%H:%M"), commit=depois.strip(),
                aviso=("não consegui puxar: " + saida.strip()[-160:]) if falhou else None)
    if antes.strip() != depois.strip():
        titulo, _ = rodar(["git", "-C", RAIZ, "log", "-1", "--format=%s"], timeout=10)
        relatar(f"atualizado do GitHub ({motivo}): {antes.strip()} → {depois.strip()} · {titulo.strip()[:90]}")
    return {"ok": not falhou, "commit": SYNC["commit"], "mudou": antes.strip() != depois.strip(), "aviso": SYNC["aviso"]}


def sincronizar_sempre():
    while True:
        try:
            sincronizar()
        except Exception as e:
            SYNC["aviso"] = repr(e)[:160]
        with TRAVA:
            ESTADO["sync"] = dict(SYNC)
        time.sleep(300)


# ── a proxima versao, escolhida quando a experiencia nao estiver acontecendo (26/09) ──
# "Coloque um botao para selecionar quando a experiencia nao estiver acontecendo."
# Preparar monta o ramo em proxima.html (nada publicado); Ver abre no Quest;
# Publicar junta o ramo a main e publica. Os tres recusam com gente na obra.
PROXIMA = {"estado": "parada", "msg": "", "commit": None, "hora": None, "titulo": ""}


def experiencia_acontecendo():
    o = ESTADO["obra"]
    if not o.get("aba") or o.get("portao"):
        return False                     # sem obra aberta, ou com o portao a vista: ninguem dentro
    return bool((o.get("onde") or {}).get("andando"))


def _proxima_em_fundo(acao):
    PROXIMA.update(estado="preparando" if acao == "preparar" else "publicando", msg="", hora=datetime.now().strftime("%H:%M"))
    saida, _ = rodar([sys.executable, os.path.join(AQUI, "proxima.py"), acao], timeout=1500)
    try:
        r = json.loads(saida.strip().splitlines()[-1])
    except Exception:
        r = {"ok": False, "erro": saida.strip()[-300:] or "sem resposta"}
    if r.get("ok"):
        if acao == "preparar":
            PROXIMA.update(estado="pronta", commit=r.get("commit"), titulo=r.get("titulo", ""),
                           msg=f"pronta ({r.get('kb', 0) // 1024} MB) — abra no Quest para conferir; nada foi publicado")
            relatar(f"próxima versão pronta para ver no Quest ({r.get('commit')}) — nada publicado")
        else:
            PROXIMA.update(estado="publicada", commit=r.get("commit"), msg="publicada: o site e a main já têm a nova")
            relatar(f"próxima versão PUBLICADA ({r.get('commit')})")
            if ESTADO["obra"].get("aba") and not experiencia_acontecendo():
                abrir_no_quest(ESTADO["quest"]["escolhido"], "v6")   # o oculos passa para a nova, que agora e a de sempre
    else:
        PROXIMA.update(estado="erro", msg=r.get("erro", "falhou"))
        relatar("próxima versão: " + r.get("erro", "falhou"))
    with TRAVA:
        ESTADO["proxima"] = dict(PROXIMA)


def proxima(acao):
    if PROXIMA["estado"] in ("preparando", "publicando"):
        return {"ok": False, "erro": "já estou " + PROXIMA["estado"]}
    if experiencia_acontecendo():
        return {"ok": False, "erro": "tem gente dentro da obra agora — espere o portão voltar"}
    if acao == "ver":
        if not os.path.exists(os.path.join(RAIZ, "proxima.html")):
            return {"ok": False, "erro": "prepare a próxima antes"}
        if not ESTADO["quest"]["escolhido"]:
            return {"ok": False, "erro": "o Quest não está ao alcance"}
        return abrir_no_quest(ESTADO["quest"]["escolhido"], "proxima")
    threading.Thread(target=_proxima_em_fundo, args=(acao,), daemon=True).start()
    return {"ok": True, "resposta": ("preparando" if acao == "preparar" else "publicando") + " — leva alguns minutos"}


def ja_esta_de_pe():
    try:
        urlopen(f"http://127.0.0.1:{PORTA_CABINE}/estado", timeout=2).read()
        return True
    except Exception:
        return False


def main():
    global ADB
    abrir = "--sem-navegador" not in sys.argv
    if ja_esta_de_pe():
        log("a cabine já estava de pé; só abrindo a página")
        if abrir:
            abrir_pagina(f"http://localhost:{PORTA_CABINE}/")
        return
    ADB = achar_adb()
    if not ADB:
        with TRAVA:
            ESTADO["avisos"].append("adb não encontrado: ponha o platform-tools em fontes/ (ver estande.py)")
        log("SEM ADB")
    m = re.search(r"const DURACAO = (\d+)", open(os.path.join(AQUI, "mr.template.html"), encoding="utf-8").read())
    if m:
        ESTADO["obra"]["duracao"] = int(m.group(1))
    if not os.path.exists(os.path.join(RAIZ, "index.html")):
        ESTADO["avisos"].append("não há index.html: rode python fontes/montar_mr.py")
    log(f"cabine de pé (adb: {ADB})")
    # 26/09: nada da luz sobra de uma Cabine anterior; e fechar o Terminal (SIGHUP) ou um
    # kill (SIGTERM) encerram a luz e o espelho junto, em vez de deixa-los orfaos
    rodar(["pkill", "-f", "fontes/luz-segue-cena.mjs"], timeout=5)
    import signal
    for sig in (signal.SIGHUP, signal.SIGTERM):
        try:
            signal.signal(sig, lambda *_: encerrar_tudo())
        except Exception:
            pass
    threading.Thread(target=sincronizar_sempre, daemon=True).start()
    ESTADO["duracao_min"] = minutos_escolhidos()
    if os.path.exists(os.path.join(RAIZ, "proxima.html")):   # uma proxima ja preparada antes
        PROXIMA.update(estado="pronta", msg="preparada antes — abra no Quest para conferir")
        ESTADO["proxima"] = dict(PROXIMA)
    subir_servidor_da_obra()
    if ADB:
        threading.Thread(target=vigiar, daemon=True).start()
    servidor = ThreadingHTTPServer(("127.0.0.1", PORTA_CABINE), Cabine)
    servidor.daemon_threads = True
    if abrir:
        threading.Timer(0.8, lambda: abrir_pagina(f"http://localhost:{PORTA_CABINE}/")).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        encerrar_tudo()


if __name__ == "__main__":
    main()
