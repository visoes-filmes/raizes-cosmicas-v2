# -*- coding: utf-8 -*-
"""A BANCADA: a obra na tela do computador, com o relogio trocado e ganchos
para olhar de onde se quiser e tirar fotos de dentro do WebGL.

    python fontes/montar_mr.py          # primeiro: e o nova.html que se usa
    python fontes/bancada.py            # escreve _dev.html
    python fontes/servir.py 8791        # num terminal a parte, e fica no ar
    abrir http://localhost:8791/_dev.html, clicar em "Iniciar"

Depois, no console do navegador (ou por uma ferramenta que execute JS na
pagina):

    const src = await (await fetch('/fontes/bancada.js')).text();
    await (new (Object.getPrototypeOf(async function(){}).constructor)(src))();
    raizes.ir(470);                       // salta na partitura (segundos)
    for(let i=0;i<8;i++) __frame();       // deixa os alvos assentarem
    P.mvp = paraDe(1.6, 0, -10, 75);      // olho a 1,6 m, azimute 0, olhando 10 graus para baixo, lente de 75
    __frame(); __fotoRapida('minha-foto.jpg');   // cai em _fotos/ pelo servir.py

POR QUE O RELOGIO E TROCADO. O painel de navegacao das ferramentas nao compoe
quadro, e sem composicao o requestAnimationFrame nunca dispara: a obra fica
parada em 0:00 achando que anda. Aqui o rAF vira setTimeout. O WebGL desenha
do mesmo jeito -- o que falta e so a apresentacao na tela, e o que se quer e
ler os pixels.

OS GANCHOS. A obra nao expoe nada para quem visita (regra da casa). A bancada
abre quatro janelas, so no _dev.html:
    window.__olhoY      a altura do olho (a obra usa OLHO = 1,6 m): 0,5 e mergulhar
    window.__FIGURAS    a tabela das deusas (tam e centro sao lidos por quadro: da para
                        experimentar escala ao vivo)
    window.__semearMata, __BASES, __malha    para medir a mata e os modelos

A FONTE E A OBRA, e nao a oficina: nova.html e o index montado, sem a regua e
os medidores, e como nao esta no endereco publicado ele ainda traz o
raizes.ir() de que a bancada precisa.

Andaime de bancada: _dev.html esta no .gitignore.
"""
import io
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fonte = os.path.join(RAIZ, "nova.html")
alvo = os.path.join(RAIZ, "_dev.html")
if not os.path.exists(fonte):
    raise SystemExit("nao achei nova.html: rode python fontes/montar_mr.py antes")

RELOGIO = """
<script>
/* BANCADA: relogio de setTimeout no lugar do de composicao. */
(function () {
  var proxima = 1, pendentes = {}, t0 = performance.now();
  window.requestAnimationFrame = function (fn) {
    var id = proxima++;
    pendentes[id] = setTimeout(function () {
      delete pendentes[id];
      fn(performance.now() - t0);
    }, 16);
    return id;
  };
  window.cancelAnimationFrame = function (id) {
    clearTimeout(pendentes[id]); delete pendentes[id];
  };
  window.__bancada = true;
})();
</script>
"""

# cada gancho: (o trecho da obra, o que entra no lugar). Se um deles nao for
# achado uma vez so, a obra mudou e a bancada precisa ser revista -- melhor
# parar do que fingir.
GANCHOS = [
    ('<meta charset="utf-8">', '<meta charset="utf-8">' + RELOGIO),
    ("const vis = janelaMagica ? visaoDoCelular() : visaoOrbita(yaw, pitch, OLHO);",
     "const vis = janelaMagica ? visaoDoCelular() : visaoOrbita(yaw, pitch, (window.__olhoY === undefined ? OLHO : window.__olhoY));"),
    ("subirRaizes(semearMata(11), 11);",
     "subirRaizes(semearMata(11), 11);\n"
     "window.__semearMata = semearMata; window.__BASES = BASES; window.__malha = decodificarMalha;"),
    ("    fluxo:[0.502, 0.405, 0.02, 0.12], asas:[0.465, 0.535, 0.415, 0.135] },\n];",
     "    fluxo:[0.502, 0.405, 0.02, 0.12], asas:[0.465, 0.535, 0.415, 0.135] },\n];\n"
     "window.__FIGURAS = FIGURAS;"),
]

s = io.open(fonte, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in s else "\n"
s = s.replace("\r\n", "\n")
for velho, novo in GANCHOS:
    n = s.count(velho)
    if n != 1:
        raise SystemExit("gancho nao achado uma vez so (%d): %r" % (n, velho[:60]))
    s = s.replace(velho, novo, 1)
io.open(alvo, "w", encoding="utf-8", newline="").write(s.replace("\n", nl))
print("_dev.html escrito: %.1f MB" % (os.path.getsize(alvo) / 1048576))
