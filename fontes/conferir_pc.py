# -*- coding: utf-8 -*-
"""
CONFERIR O PC -- o padrao de instalacao do Raizes Cosmicas, item por item.

    python fontes/conferir_pc.py

25/09, a direcao de arte: "coloque esse padrao de instalacao para nosso
projeto em outros PCs nos MDs, pra garantir que tudo isso vai ser lembrado e
requisitado". O MD lembra; este script REQUISITA: roda em qualquer maquina e
diz, para cada peca, se esta la e o que fazer se nao estiver. A lista e a do
LEIA-ME-SEGUIR.md, secao 1 -- se uma mudar, a outra muda junto.

Nao instala nada e nao muda nada: so olha. O que pede administrador ou
senha fica escrito para a pessoa fazer.
"""
import glob
import os
import platform
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
WIN = platform.system() == "Windows"
faltas = []


def rodar(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return f"__erro__ {e}"


def item(nome, ok, detalhe, como=""):
    print(f"  [{'ok' if ok else '--'}] {nome}: {detalhe}")
    if not ok:
        faltas.append((nome, como))


print("\nRaizes Cosmicas -- conferindo este computador\n")

# ── 1. os programas ──────────────────────────────────────────────────────
print("1. Programas")
g = rodar(["git", "--version"])
item("Git", g.startswith("git version"), g.strip()[:40] or "nao achado",
     "winget install --id Git.Git -e")
item("Python 3.10+", sys.version_info >= (3, 10), sys.version.split()[0],
     "winget install --id Python.Python.3.12 -e")
try:
    import PIL  # noqa: F401
    item("Pillow", True, "instalado")
except Exception:
    item("Pillow", False, "nao instalado", "python -m pip install Pillow")
n = rodar(["node", "--version"])
item("Node.js", n.strip().startswith("v"), n.strip()[:20] or "nao achado",
     "winget install --id OpenJS.NodeJS.LTS -e")
nav = [c for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                   os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
                   r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"] if os.path.exists(c)]
item("Chrome ou Edge", bool(nav), os.path.basename(nav[0]) if nav else "nao achado",
     "instalar o Chrome (a oficina, a bancada e a projecao em quiosque)")

# ── 2. o Quest pelo computador ───────────────────────────────────────────
print("\n2. O Quest pelo computador")
adb = os.path.join(AQUI, "platform-tools", "adb.exe" if WIN else "adb")
item("adb do projeto", os.path.exists(adb), adb if os.path.exists(adb) else "fontes/platform-tools/ vazio",
     "baixar platform-tools (developer.android.com/studio/releases/platform-tools) e largar a pasta em fontes/platform-tools/")
scr = shutil.which("scrcpy") or next(iter(glob.glob(os.path.expanduser(
    r"~\AppData\Local\Microsoft\WinGet\Packages\Genymobile.scrcpy*\**\scrcpy.exe"), recursive=True)), None)
item("scrcpy (espelho e projecao)", bool(scr), scr or "nao achado", "winget install --id Genymobile.scrcpy -e")
if WIN:
    link = rodar(["powershell", "-NoProfile", "-Command",
                  "(Get-Service -Name OVRService -ErrorAction SilentlyContinue | "
                  "ForEach-Object { $_.Status.ToString() + '/' + $_.StartType.ToString() })"])
    link = link.strip()
    sem_link = (not link) or link.endswith("/Disabled")
    item("Meta Quest Link desligado", sem_link,
         "servico nao instalado" if not link else f"OVRService {link}",
         "o Link toma o cabo e esconde a caixa de depuracao USB. PowerShell como administrador: "
         "Stop-Service OVRService; Set-Service OVRService -StartupType Disabled")
if os.path.exists(adb):
    d = rodar([adb, "devices"])
    linhas = [l for l in d.splitlines()[1:] if l.strip()]
    ok = [l for l in linhas if l.endswith("device")]
    nao = [l for l in linhas if "unauthorized" in l]
    if ok:
        item("Quest conectado", True, ", ".join(l.split()[0] for l in ok))
    elif nao:
        item("Quest conectado", False, "aparece como unauthorized",
             "no capacete: aceitar 'Permitir depuracao USB' MARCANDO 'Sempre permitir deste computador'")
    else:
        item("Quest conectado", False, "nenhum (normal se ele estiver desligado)",
             "ligar o Quest e o cabo USB-C; modo de desenvolvedor ligado no app Meta Horizon")

# ── 3. o projeto ─────────────────────────────────────────────────────────
print("\n3. O projeto")
rem = rodar(["git", "-C", RAIZ, "remote", "get-url", "origin"]).strip()
item("repositorio", "raizes-cosmicas-v2" in rem, rem or "sem git aqui",
     "git clone https://github.com/visoes-filmes/raizes-cosmicas-v2.git \"Raizes Cosmicas\"")
quem = rodar(["git", "-C", RAIZ, "config", "user.name"]).strip()
item("git sabe quem publica", bool(quem), quem or "sem user.name",
     'git config user.name "Crisia-poria"; git config user.email "admcrisia@gmail.com"')
v = rodar([sys.executable, os.path.join(AQUI, "verificar.py")], timeout=120)
item("o verificador passa", "nada a corrigir" in v, "nada a corrigir" if "nada a corrigir" in v else v.strip()[-120:],
     "consertar o que ele apontar antes de montar")
video = os.path.join(RAIZ, "assets", "video", "odara-cosmos.mp4")
item("video da tela de tule", os.path.exists(video), "assets/video/odara-cosmos.mp4",
     "vem com o repositorio; se faltar, git pull")

# ── 4. o acesso de longe (opcional) ──────────────────────────────────────
if WIN:
    print("\n4. Acesso de longe (opcional)")
    ad = [c for c in [r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe", r"C:\Program Files\AnyDesk\AnyDesk.exe"]
          if os.path.exists(c)]
    item("AnyDesk", bool(ad), "instalado" if ad else "nao instalado",
         "winget install --id AnyDesk.AnyDesk -e  (pede administrador); depois, no AnyDesk: "
         "Configuracoes > Seguranca > Acesso nao supervisionado, com uma senha SUA")

# ── o que falta ──────────────────────────────────────────────────────────
print()
if not faltas:
    print("Tudo no lugar. Para o estande: python fontes/cabine.py\n")
else:
    print(f"FALTAM {len(faltas)}:")
    for nome, como in faltas:
        print(f"  - {nome}" + (f"\n      {como}" if como else ""))
    print("\nO que pede administrador, senha ou o capacete na cabeca, a pessoa faz; o resto, um chat do Claude Code faz.\n")
