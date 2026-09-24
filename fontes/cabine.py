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
VERSOES = {"v6": "v6.html", "v52": "v52.html", "v2": "", "v4": "v4.html", "v5": "v5.html", "oficina": "oficina.html"}
NOMES_CENAS = {1: "floresta", 2: "cosmos", 3: "planeta rosa", 4: "papel"}

# no Windows sem console (pythonw), nenhum subprocesso pode abrir janela
SEM_JANELA = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

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
    lista = []
    for linha in adb("devices").splitlines()[1:]:
        partes = linha.split()
        if len(partes) >= 2:
            lista.append({"serial": partes[0], "estado": partes[1],
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
        return {"ok": False, "erro": "o Quest não está em nenhuma rede Wi-Fi — entre com ele no Ponto de Acesso primeiro"}
    adb("tcpip", "5555", serial=serial)
    time.sleep(3)
    r = adb("connect", f"{ip}:5555", timeout=15)
    with open(IP_GUARDADO, "w") as f:
        f.write(ip)
    relatar(f"Wi-Fi liberada: {r}")
    return {"ok": "connected" in r or "already" in r, "ip": ip, "resposta": r}


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


def abrir_no_quest(serial, versao):
    arquivo = VERSOES.get(versao, "")
    url = f"http://localhost:{PORTA_OBRA}/{arquivo}"
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

def hotspot(acao="status", ssid=None, senha=None):
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


def wifi_do_pc():
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


def espelhar(serial):
    exe = achar_scrcpy()
    if not exe:
        return {"ok": False, "erro": "scrcpy não está instalado nesta máquina (winget install Genymobile.scrcpy)"}
    # ADB=<o nosso>: o scrcpy traz outro adb, e dois adbs diferentes derrubam
    # o servidor um do outro -- e com ele os túneis.
    amb = dict(os.environ, ADB=ADB)
    subprocess.Popen([exe, "-s", serial, "--max-size", "1280", "--no-audio",
                      "--window-title", "Quest — espelho"], env=amb, creationflags=SEM_JANELA)
    relatar("espelho do Quest aberto (scrcpy)")
    return {"ok": True}


# ── a projeção (6.0): o que vai para o projetor ──────────────────────────

def monitores():
    """Os monitores do Windows, com posicao e tamanho (o projetor e um deles)."""
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
    global PROJECAO
    parar_projecao()
    lista = ESTADO["monitores"] or monitores()
    alvo = None
    for m in lista:
        if str(m.get("nome")) == str(monitor) or (monitor in (None, "", "auto") and not m.get("principal")):
            alvo = m
            break
    if not alvo and lista:
        alvo = lista[0]
    alvo = alvo or {}
    x, y, w, h = alvo.get("x", 0), alvo.get("y", 0), alvo.get("w", 1920), alvo.get("h", 1080)
    if saida == "pagina":
        nav = achar_navegador()
        if not nav:
            return {"ok": False, "erro": "não achei Chrome nem Edge para abrir a projeção"}
        perfil = os.path.join(os.environ.get("TEMP", AQUI), "raizes-projecao-perfil")
        url = (f"http://localhost:{PORTA_OBRA}/projecao.html?espelho={'1' if espelhar else '0'}"
               f"&cabine=http://localhost:{PORTA_CABINE}")
        PROJECAO = subprocess.Popen([nav, "--kiosk", f"--window-position={x},{y}", f"--window-size={w},{h}",
                                     f"--user-data-dir={perfil}", "--no-first-run", "--no-default-browser-check",
                                     "--autoplay-policy=no-user-gesture-required", "--disable-infobars", url],
                                    creationflags=SEM_JANELA)
        relatar(f"projeção (página) aberta no monitor {alvo.get('nome', '?')} {w}x{h}" + (" espelhada" if espelhar else ""))
    elif saida == "espelho":
        s = ESTADO["quest"]["escolhido"]
        exe = achar_scrcpy()
        if not exe:
            return {"ok": False, "erro": "scrcpy não está instalado"}
        if not s:
            return {"ok": False, "erro": "nenhum Quest ao alcance para espelhar"}
        args = [exe, "-s", s, "--no-audio", "--fullscreen", f"--window-x={x}", f"--window-y={y}",
                "--window-title", "Quest — projeção", "--max-fps", "30"]
        if recorte:
            args += ["--crop", recorte]
        PROJECAO = subprocess.Popen(args, env=dict(os.environ, ADB=ADB), creationflags=SEM_JANELA)
        relatar(f"projeção (espelho do óculos) aberta no monitor {alvo.get('nome', '?')}")
    else:
        return {"ok": False, "erro": f"saída desconhecida: {saida}"}
    with TRAVA:
        ESTADO["projecao"] = {"ativa": True, "saida": saida, "monitor": alvo.get("nome"), "espelhar": bool(espelhar)}
    return {"ok": True}


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
            alvo = escolher(lista)
            ip_guardado = open(IP_GUARDADO).read().strip() if os.path.exists(IP_GUARDADO) else None
            # só a Wi-Fi pode estar de pé: tenta o ip guardado
            if ip_guardado and not alvo and ciclo % 3 == 1:
                adb("connect", f"{ip_guardado}:5555", timeout=8)
                lista = aparelhos()
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
                boot = adb("shell", "cat", "/proc/sys/kernel/random/boot_id", serial=s, timeout=8)
                if re.fullmatch(r"[0-9a-f-]{36}", boot) and vistos.get(s) != boot:
                    relatar(f"Quest apareceu pelo {alvo['via']} ({s})")
                    tuneis(s)
                    relatar(f"túneis refeitos: {PORTA_OBRA} (obra) e {PORTA_DEVTOOLS} (DevTools)")
                    if alvo["via"] == "cabo":
                        r = liberar_wifi(s)
                        if not r.get("ok"):
                            relatar(r.get("erro") or r.get("resposta", ""))
                    vistos[s] = boot
                q.update(escolhido=s, via=alvo["via"], ip=ip_do_quest(s),
                         tuneis=f"tcp:{PORTA_OBRA}" in adb("reverse", "--list", serial=s, timeout=8))
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
        return {"ok": False, "erro": "nenhum Quest ao alcance"}
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
        r = adb("connect", f"{ip}:5555", timeout=12)
        relatar(f"conectar {ip}: {r}")
        return {"ok": "connected" in r or "already" in r, "resposta": r}
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


def encerrar_tudo():
    log("cabine encerrando")
    try:
        parar_projecao()
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
            webbrowser.open(f"http://localhost:{PORTA_CABINE}/")
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
    subir_servidor_da_obra()
    if ADB:
        threading.Thread(target=vigiar, daemon=True).start()
    servidor = ThreadingHTTPServer(("127.0.0.1", PORTA_CABINE), Cabine)
    servidor.daemon_threads = True
    if abrir:
        threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{PORTA_CABINE}/")).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        encerrar_tudo()


if __name__ == "__main__":
    main()
