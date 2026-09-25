# -*- coding: utf-8 -*-
"""A LAMPADA PELO BLUETOOTH -- 25/09. "Ela funciona com bluetooth... e do
app SMART+, uma lampada de LED colorida."

    python3 fontes/lampada_bt.py            # porta 8600, a mesma API do estudio
    LAMPADA_BT="outro nome" python3 fontes/lampada_bt.py

Achada no estande pela busca (fontes/luz_bluetooth.py): anuncia-se como
"GATT--DEMO" (servico 2022, fabricante 0xFFFF) e, conectada, oferece o
servico FFF0 com a caracteristica gravavel FFF3 -- o protocolo das lampadas
ELK-BLEDOM: 7e 00 05 03 RR GG BB 00 ef para a cor, 7e 00 04 f0 00 01 ff 00 ef
para ligar, 7e 00 04 00 00 00 ff 00 ef para desligar.

Mesma API do estudio do v1 e do lampada.py (Tuya), entao a ponte
luz-segue-cena.mjs roda sem mudar uma linha:

    GET /api/luz?acao=cor&v=%23RRGGBB     -> {"ok": true}
    GET /api/luz?acao=estado              -> conectada ou o motivo

A conexao fica aberta e se refaz sozinha se a lampada cair. No Mac o
Bluetooth e do Terminal: a Cabine abre isto numa janela do Terminal.
"""
import asyncio
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    sys.exit("falta o bleak:  python3 -m pip install --user bleak")

NOME = os.environ.get("LAMPADA_BT", "GATT--DEMO")
PORTA = int(os.environ.get("PORTA_LAMPADA", "8600"))
CAR = "0000fff3-0000-1000-8000-00805f9b34fb"
LIGAR = [0x7E, 0x00, 0x04, 0xF0, 0x00, 0x01, 0xFF, 0x00, 0xEF]
APAGAR = [0x7E, 0x00, 0x04, 0x00, 0x00, 0x00, 0xFF, 0x00, 0xEF]
cor_elk = lambda r, g, b: [0x7E, 0x00, 0x05, 0x03, r, g, b, 0x00, 0xEF]

LACO = None
CLIENTE = None
ESTADO = {"conectada": False, "cor": None, "erro": "procurando " + NOME, "nome": NOME}


async def manter_conectada():
    """Procura, conecta, liga; se cair, refaz. Nunca desiste."""
    global CLIENTE
    while True:
        if CLIENTE is None or not CLIENTE.is_connected:
            try:
                d = await BleakScanner.find_device_by_filter(
                    lambda d, a: (d.name or a.local_name or "") == NOME, timeout=10)
                if not d:
                    ESTADO.update(conectada=False, erro=f"{NOME} nao apareceu no Bluetooth")
                else:
                    c = BleakClient(d, disconnected_callback=lambda _c: ESTADO.update(conectada=False, erro="caiu; reconectando"))
                    await c.connect(timeout=15)
                    CLIENTE = c
                    await c.write_gatt_char(CAR, bytes(LIGAR), response=False)
                    ESTADO.update(conectada=True, erro=None)
                    print(f"conectada a {NOME}", flush=True)
            except Exception as e:
                CLIENTE = None
                ESTADO.update(conectada=False, erro=str(e)[:140])
        await asyncio.sleep(3)


async def escrever(b):
    if not (CLIENTE and CLIENTE.is_connected):
        raise RuntimeError(ESTADO.get("erro") or "lampada desconectada")
    await CLIENTE.write_gatt_char(CAR, bytes(b), response=False)


def pintar(cor_hex):
    h = cor_hex.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    pacote = APAGAR if max(r, g, b) == 0 else cor_elk(r, g, b)
    asyncio.run_coroutine_threadsafe(escrever(pacote), LACO).result(6)
    ESTADO["cor"] = "#" + h
    return True


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
                return self._json({"ok": ESTADO["conectada"], "estado": ESTADO, "erro": ESTADO["erro"]},
                                  200 if ESTADO["conectada"] else 503)
            return self._json({"ok": False, "erro": "acao: cor ou estado"}, 400)
        except Exception as e:
            return self._json({"ok": False, "erro": str(e)[:200]}, 503)

    def log_message(self, *a):
        pass


def main():
    global LACO
    LACO = asyncio.new_event_loop()
    asyncio.set_event_loop(LACO)
    srv = ThreadingHTTPServer(("127.0.0.1", PORTA), Api)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"lampada Bluetooth ({NOME}): API em http://localhost:{PORTA}/api/luz  (Ctrl+C para parar)", flush=True)
    try:
        LACO.run_until_complete(manter_conectada())      # o laco do Bluetooth fica na linha principal
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
