# -*- coding: utf-8 -*-
"""PROCURAR A LUZ PELO BLUETOOTH -- 25/09. "Ela funciona com bluetooth."

    python3 fontes/luz_bluetooth.py [segundos]

Escuta os anuncios Bluetooth (BLE) por alguns segundos e diz quem esta
perto: nome, forca do sinal, servicos, fabricante -- e o que parece ser cada
um. E assim que se descobre COMO a lampada fala: a Tuya anuncia o
fabricante 0x07D0 ou o servico FD50/A201; as fitas baratas, FFF0 / FFD5 /
FFE5.

No Mac o Bluetooth e protegido: roda pela Cabine (que vive no Terminal), e
na primeira vez o macOS pergunta se o Terminal pode usar o Bluetooth.
"""
import asyncio
import json
import sys

try:
    from bleak import BleakScanner
except ImportError:
    sys.exit(json.dumps({"erro": "falta o bleak: python3 -m pip install --user bleak"}))


def o_que_parece(nome, servicos, fabricantes, dados_servico):
    s = " ".join(servicos + list(dados_servico)).lower()
    n = (nome or "").lower()
    if 0x07D0 in fabricantes or "fd50" in s or "a201" in s:
        return "Tuya BLE (a da Smart Life: criptografada, pede a chave da conta)"
    if "fff0" in s or "elk" in n or "bledom" in n:
        return "ELK-BLEDOM (o card Bluetooth da Cabine fala)"
    if "ffd5" in s or "triones" in n or "ledble" in n or "happy" in n:
        return "Triones/HappyLighting (o card Bluetooth da Cabine fala)"
    if "ffe5" in s or "zengge" in n or "magic" in n:
        return "Zengge/MagicHome (o card Bluetooth da Cabine fala)"
    if "fe0f" in s or "ledvance" in n or "smart+" in n:
        return "Ledvance SMART+ Bluetooth"
    if "fe03" in s or 0x0171 in fabricantes:
        return "Amazon/Alexa"
    if 0x004C in fabricantes:
        return "Apple"
    return ""


async def main(segundos):
    achados = await BleakScanner.discover(timeout=segundos, return_adv=True)
    lista = []
    for addr, (d, adv) in achados.items():
        nome = d.name or adv.local_name or ""
        servicos = [u[4:8] if u.startswith("0000") else u for u in adv.service_uuids]
        fabricantes = list(adv.manufacturer_data.keys())
        dados_serv = [u[4:8] if u.startswith("0000") else u for u in adv.service_data.keys()]
        lista.append({"nome": nome, "id": addr, "sinal": adv.rssi, "servicos": servicos,
                      "fabricantes": [f"0x{f:04X}" for f in fabricantes], "dados_servico": dados_serv,
                      "parece": o_que_parece(nome, servicos, fabricantes, dados_serv)})
    lista.sort(key=lambda x: -(x["sinal"] or -999))
    print(json.dumps(lista, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main(float(sys.argv[1]) if len(sys.argv) > 1 else 12.0))
