# -*- coding: utf-8 -*-
"""A LAMPADA DO ESTANDE, SEM O ESTUDIO DO V1 -- 25/09, no MacBook.

    python3 fontes/lampada.py            # porta 8600, a mesma API do estudio
    python3 fontes/lampada.py teste      # pinta violeta, espera, volta ao turquesa

A lampada e a Tuya de sempre (LDV SMART+ CLA60, RGBW, Wi-Fi). A ponte
fontes/luz-segue-cena.mjs falava com ela pelo estudio do v1 (raizes-display,
node estudio.mjs, porta 8600) -- que nao veio para o Mac. Este arquivo faz
o papel dele com a MESMA API, entao a ponte roda sem mudar uma linha:

    GET /api/luz?acao=cor&v=%23RRGGBB     -> {"ok": true}
    GET /api/luz?acao=estado              -> o que a lampada diz

O caminho e o local (tinytuya, sem nuvem e sem cota), e pede tres coisas da
lampada que NAO vao para o git: o id, a chave local e a versao do
protocolo. Ficam em fontes/lampada.json (no .gitignore):

    {"id": "...", "chave": "...", "versao": 3.5, "ip": "opcional"}

De onde vem: o lampada/config.json do estudio do v1 (no desktop ou no Acer),
ou `python3 -m tinytuya wizard` com a conta Tuya IoT. Sem "ip", a lampada e
procurada na rede pelo id (ela anuncia a si mesma por UDP).

Se a lampada piscar sem parar, ela esta em modo de pareamento: perdeu a
Wi-Fi. Volta pelo app (Smart Life / Tuya) no celular, na MESMA rede do Mac;
re-parear pode trocar a chave local -- ai o wizard busca a nova.
"""
import colorsys
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

AQUI = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(AQUI, "lampada.json")
PORTA = int(os.environ.get("PORTA_LAMPADA", "8600"))

try:
    import tinytuya
except ImportError:
    sys.exit("falta o tinytuya:  python3 -m pip install --user tinytuya")

TRAVA = threading.Lock()
BULBO = None


def ler_config():
    if not os.path.exists(CONFIG):
        raise RuntimeError("falta fontes/lampada.json (id, chave, versao) -- ver o alto deste arquivo")
    c = json.load(open(CONFIG, encoding="utf-8"))
    for k in ("id", "chave"):
        if not c.get(k):
            raise RuntimeError(f"fontes/lampada.json sem '{k}'")
    return c


def lampada():
    """Abre (uma vez) a conversa com a lampada; acha o ip pelo id se preciso."""
    global BULBO
    if BULBO is not None:
        return BULBO
    c = ler_config()
    ip = c.get("ip")
    versao = float(c.get("versao", 3.5))
    if not ip:
        achado = tinytuya.find_device(c["id"])
        ip = achado.get("ip") if achado else None
        if achado and achado.get("version"):
            versao = float(achado["version"])
        if not ip:
            raise RuntimeError("a lampada nao respondeu na rede (desligada, em pareamento, ou em outra Wi-Fi)")
    b = tinytuya.BulbDevice(c["id"], ip, c["chave"], version=versao)
    b.set_socketPersistent(True)
    b.set_socketTimeout(4)
    BULBO = b
    print(f"lampada em {ip} (protocolo {versao})", flush=True)
    return b


def pintar(cor_hex):
    """Tudo pela COR, nunca pelo brilho (licao de 12/09: o brilho troca a
    lampada para o branco). O escuro e o claro vem no valor da cor."""
    global BULBO
    h = cor_hex.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    with TRAVA:
        for tentativa in (1, 2):
            try:
                lb = lampada()
                if max(r, g, b) == 0:
                    lb.turn_off(nowait=True)
                else:
                    lb.set_colour(r, g, b, nowait=True)
                return True
            except Exception as e:
                BULBO = None           # reabre na proxima (ip mudou, socket caiu)
                if tentativa == 2:
                    raise e
    return False


class Api(BaseHTTPRequestHandler):
    def _json(self, obj, codigo=200):
        corpo = json.dumps(obj).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path != "/api/luz":
            return self._json({"ok": False, "erro": "so /api/luz"}, 404)
        try:
            if q.get("acao") == "cor":
                return self._json({"ok": pintar(q.get("v", "#000000"))})
            if q.get("acao") == "estado":
                with TRAVA:
                    return self._json({"ok": True, "estado": lampada().status()})
            return self._json({"ok": False, "erro": "acao: cor ou estado"}, 400)
        except Exception as e:
            return self._json({"ok": False, "erro": str(e)[:200]}, 503)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "teste":
        import time
        for cor in ("#5d00ff", "#009980"):
            print(cor, pintar(cor))
            time.sleep(3)
        sys.exit(0)
    print(f"lampada: API do estudio em http://localhost:{PORTA}/api/luz  (Ctrl+C para parar)")
    try:
        lampada()
    except Exception as e:
        print("ainda sem lampada:", e)
    ThreadingHTTPServer(("127.0.0.1", PORTA), Api).serve_forever()
