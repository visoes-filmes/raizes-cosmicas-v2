# -*- coding: utf-8 -*-
"""A CHAVE DA LED PELA WI-FI -- 27/09.

"A nossa LED, voce consegue conectar ela agora? Ela esta no Wi-Fi" -- "esta
conectada no iPhone do Plinio". A lampada e Tuya (protocolo 3.5): ela se anuncia
na rede do modem por UDP e a Cabine a acha sozinha. Para mandar cor pela Wi-Fi e
preciso a CHAVE LOCAL dela, que so a conta do app conhece. Este ajudante busca a
chave pelo mesmo caminho do Home Assistant, sem conta de desenvolvedor:

    python3 fontes/luz_chave_tuya.py <codigo de usuario>

1. No app do iPhone (Smart Life ou Tuya Smart): Eu -> engrenagem -> Conta e
   seguranca -> Codigo de usuario. E um codigo curto, nao e senha.
2. Um QR abre na tela do Mac. No app, o botao de escanear le o QR e pede para
   autorizar; autorizado, este ajudante le a lista de aparelhos da conta.
3. A chave da lampada vai para fontes/lampada.json (fora do git), que o
   fontes/lampada.py usa -- e a Cabine, no botao Wi-Fi da luz. Nada mais e
   guardado: nem o codigo, nem o acesso a conta.

Re-parear a lampada no app troca a chave: ai e so rodar de novo.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "lampada.json")
CLIENTE = "HA_3y9q4ak7g4ephrvke"      # o cliente publico do Home Assistant para o app Smart Life
ESQUEMA = "haauthorize"
LUZES = {"dj", "dd", "xdd", "fwd", "dc", "fsd", "tgq", "tyndj"}   # categorias Tuya de lampada e fita


def na_rede():
    """{id: (ip, versao)} dos aparelhos Tuya que se anunciam na rede agora."""
    import tinytuya
    achados = {}
    try:
        r = tinytuya.deviceScan(False, 12, False, False) or {}
        for ip, d in r.items():
            i = d.get("gwId") or d.get("id")
            if i:
                achados[i] = (d.get("ip") or ip, float(d.get("version") or 3.3))
    except Exception as e:
        print("a busca na rede falhou:", e)
    return achados


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        sys.exit(__doc__)
    codigo = sys.argv[1].strip()
    try:
        import qrcode
        from tuya_sharing import LoginControl, Manager
    except ImportError:
        sys.exit("falta:  python3 -m pip install --user tuya-device-sharing-sdk qrcode")

    lc = LoginControl()
    r = lc.qr_code(CLIENTE, ESQUEMA, codigo)
    if not r.get("success"):
        sys.exit("o app recusou o codigo de usuario: " + str(r.get("msg") or r)[:200])
    token = r["result"]["qrcode"]
    png = os.path.join(tempfile.gettempdir(), "raizes-luz-qr.png")
    qrcode.make("tuyaSmart--qrLogin?token=" + token).save(png)
    subprocess.run(["open", "-a", "Preview", png])
    print("QR aberto na tela do Mac: escaneie com o app do iPhone e autorize (ate 3 minutos)", flush=True)

    info = None
    for _ in range(90):
        time.sleep(2)
        ok, resp = lc.login_result(token, CLIENTE, codigo)
        if ok:
            info = resp
            break
    subprocess.run(["osascript", "-e", 'tell application "Preview" to close (every window whose name contains "raizes-luz-qr")'],
                   capture_output=True)
    if not info:
        sys.exit("o QR nao foi autorizado a tempo; rode de novo")

    m = Manager(CLIENTE, codigo, info["terminal_id"], info["endpoint"], info)
    m.update_device_cache()
    rede = na_rede()
    luzes = [d for d in m.device_map.values() if getattr(d, "category", "") in LUZES]
    print(f"{len(m.device_map)} aparelho(s) na conta; {len(luzes)} lampada(s)/fita(s); {len(rede)} Tuya na rede agora")
    for d in m.device_map.values():
        print(f"  - {d.name} ({getattr(d, 'category', '?')}, {getattr(d, 'product_name', '')})"
              + ("  <- na rede, " + rede[d.id][0] if d.id in rede else ""))
    escolha = next((d for d in luzes if d.id in rede), None) or next((d for d in m.device_map.values() if d.id in rede), None) \
        or (luzes[0] if luzes else None)
    if not escolha:
        sys.exit("nenhuma lampada na conta")
    ip, versao = rede.get(escolha.id, (None, 3.5))
    conf = {"id": escolha.id, "chave": escolha.local_key, "versao": versao, "nome": escolha.name}
    if ip:
        conf["ip"] = ip
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(conf, f, ensure_ascii=False, indent=1)
    print(f"chave de '{escolha.name}' gravada em fontes/lampada.json" + (f" (na rede em {ip})" if ip else " (fora da rede agora)"))

    # a prova: so le o estado (nao muda a cor)
    try:
        import tinytuya
        b = tinytuya.BulbDevice(escolha.id, ip or "Auto", escolha.local_key, version=versao)
        b.set_socketTimeout(5)
        st = b.status()
        print("a lampada respondeu:" if "dps" in (st or {}) else "a lampada nao respondeu:", json.dumps(st)[:160])
    except Exception as e:
        print("a prova falhou:", e)


if __name__ == "__main__":
    main()
