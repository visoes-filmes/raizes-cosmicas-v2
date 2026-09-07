# -*- coding: utf-8 -*-
"""
Servidor de teste da obra — para abrir no Quest pelo cabo.

    python fontes/servir.py            (porta 8765)

POR QUE NAO O http.server DE PRATELEIRA. Ele atende UMA conexao por vez, e
a obra tem 7 MB num arquivo so. Enquanto ela desce, o icone, o manifesto e
os relatos ficam na fila -- e o navegador do Quest, cansado de esperar,
derruba a conexao no meio. Do lado de dentro do capacete isso aparece como
"fica carregando as imagens e nada acontece", que foi exatamente o que
custou uma rodada inteira de teste.

Aqui cada pedido tem sua propria linha, e nada mais espera nada.

E TUDO VAI SEM CACHE. Em teste, cache e so uma forma de olhar a versao de
ontem achando que e a de agora.
"""
import os
import ssl
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 8765


class Servidor(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def log_message(self, formato, *args):
        # Os relatos da obra sao o que interessa ler; o resto e ruido.
        linha = formato % args
        if "_relato" in linha:
            from urllib.parse import unquote
            assunto = unquote(linha.split("_relato/")[1].split(" ")[0])
            print(f"  >> {assunto}", flush=True)
        elif " 200 " in linha or " 404 " in linha:
            print(f"     {linha}", flush=True)


servidor = ThreadingHTTPServer(("0.0.0.0", PORTA), partial(Servidor, directory=RAIZ))
servidor.daemon_threads = True

# TLS QUANDO HOUVER CERTIFICADO.
#
# O WebXR so existe em contexto seguro. Pelo cabo, localhost ja conta como
# seguro e nao precisa de nada. Mas quando o cabo cai -- e ele cai -- resta a
# rede, e na rede http nao serve: o botao de entrar em RM simplesmente nao
# aparece. Com um certificado, mesmo autoassinado, ele volta a existir.
#
# O certificado nao e nosso: e o que o servidor da praca ja gerou. So se le.
CERT = os.environ.get("CERT")
if CERT and os.path.exists(os.path.join(CERT, "cert.pem")):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(os.path.join(CERT, "cert.pem"), os.path.join(CERT, "key.pem"))
    servidor.socket = ctx.wrap_socket(servidor.socket, server_side=True)
    print(f"a obra em https://<ip-do-pc>:{PORTA}/   (certificado proprio: o Quest avisa uma vez)")

print(f"a obra em http://localhost:{PORTA}/  (pasta: {RAIZ})")
print("os relatos do headset aparecem aqui com >>\n", flush=True)
servidor.serve_forever()
