# -*- coding: utf-8 -*-
"""O que faltava para funcionar no headset: o alfa da composicao, um botao de
iniciar, e um painel que diga o que aconteceu quando nao acontece nada."""
import io, os, re
AQUI = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(AQUI, 'mr.template.html')
s = io.open(p, encoding='utf-8').read()


def troca(a, b, n=1):
    global s
    assert a in s, 'NAO ACHOU: ' + a[:80]
    assert s.count(a) == n, 'ESPERAVA %d, ACHOU %d: %s' % (n, s.count(a), a[:60])
    s = s.replace(a, b)


# ═══════════════════════════════════════════════════════════════════
# 1. O DEFEITO QUE APAGAVA A OBRA NO HEADSET
# ═══════════════════════════════════════════════════════════════════
# blendFunc trata os quatro canais igual. Para o ALFA isso da
#     dstA = srcA*srcA + dstA*(1 - srcA)
# e como o quadro do headset comeca com alfa ZERO (e o alfa que deixa a
# camera aparecer), o resultado e srcA AO QUADRADO.
#
# Uma cupula a 30% compunha a 9%. Uma nuvem a 15% compunha a 2%. No
# computador nada disso aparece, porque la o fundo e opaco e so o RGB
# conta. No headset, some quase tudo — e sobra a sala real.
#
# A conta certa e a de "over": dstA = srcA + dstA*(1 - srcA). Cor mistura
# como antes; so o alfa passa a somar em vez de se multiplicar por si.
troca("gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);",
      "sobrepor();", n=7)
troca("gl.blendFunc(gl.SRC_ALPHA, gl.ONE);", "somarLuz();", n=2)

troca("""/* ═══════════ WebXR ═══════════ */""",
"""/* ═══════════ WebXR ═══════════ */

/* AS DUAS MISTURAS DA OBRA, e por que precisam de blendFuncSeparate.

   No computador o quadro comeca opaco e so o RGB importa. No headset nao:
   o quadro comeca com ALFA ZERO, e e esse alfa que o compositor usa para
   decidir quanto da camera passa. Ou seja, o alfa deixa de ser um detalhe
   e passa a ser o canal que decide se a obra existe.

   blendFunc trata os quatro canais igual, entao no alfa ele fazia
       dstA = srcA*srcA + dstA*(1 - srcA)
   e partindo de zero isso e srcA AO QUADRADO. Uma cupula a 30% compunha a
   9%; uma nuvem a 15% compunha a 2%. Tudo o que nao fosse quase opaco
   sumia — e sobrava a sala real, que e exatamente o que se viu no teste.

   Com blendFuncSeparate a cor mistura como sempre e o alfa faz a conta de
   "over": dstA = srcA + dstA*(1 - srcA). */
function sobrepor(){
  gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA,
                       gl.ONE,       gl.ONE_MINUS_SRC_ALPHA);
}
/* Soma de luz (estrelas, brilho): a cor se acumula, e o alfa tambem —
   senao um ceu de estrelas em cima de nada continua sendo nada. */
function somarLuz(){
  gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE, gl.ONE, gl.ONE);
}
""")


# ═══════════════════════════════════════════════════════════════════
# 2. BOTAO DE INICIAR
# ═══════════════════════════════════════════════════════════════════
troca("""<div class="card oculto" id="hud">""",
"""<div id="portao">
  <div class="portao-caixa">
    <h1 class="portao-nome">Raízes Cósmicas <em>v2</em></h1>
    <p class="portao-sub">Visões Filmes · dez minutos</p>
    <button id="bIniciar">Iniciar</button>
    <p class="portao-dica" id="portaoDica">carregando as imagens…</p>
  </div>
</div>

<div class="card oculto" id="hud">""")

troca("""  <span>superfícies</span><b id="vPlanos">–</b>
</div>""",
"""  <span>superfícies</span><b id="vPlanos">–</b>
  <span>imagens</span><b id="vTex">–</b>
</div>""")

troca("""  #fps.meio{opacity:.55;}""",
"""  /* ── o portão ───────────────────────────────────────────────
     A obra tem hora de comecar. Antes, o relogio partia no instante em
     que a pagina abria — e no headset isso quer dizer que os primeiros
     minutos correm enquanto a pessoa ainda esta ajeitando a tira na
     cabeca e procurando o botao. Quem entrava chegava no meio.

     Agora nada anda ate alguem mandar. */
  #portao{
    position:fixed; inset:0; z-index:100; display:grid; place-items:center;
    background:rgba(8,6,14,.94); backdrop-filter:blur(6px);
    text-align:center; padding:24px;
  }
  #portao.foi{ display:none; }
  .portao-caixa{ max-width:420px; }
  .portao-nome{ font-family:Georgia,"Times New Roman",serif; font-weight:400;
                font-size:clamp(30px,7vw,46px); color:var(--ink);
                margin:0 0 6px; letter-spacing:-.01em; }
  .portao-nome em{ font-style:italic; color:var(--accent); }
  .portao-sub{ font-family:"IBM Plex Mono",ui-monospace,Consolas,monospace;
               font-size:11px; letter-spacing:.18em; text-transform:uppercase;
               color:var(--ink-dim); margin:0 0 30px; }
  #bIniciar{
    font-size:17px; padding:13px 40px; border-radius:3px; cursor:pointer;
    background:var(--accent); color:#1c1030; border:1px solid var(--accent);
    font-weight:600; font-family:inherit;
  }
  #bIniciar:disabled{ background:#241a3d; color:var(--ink-dim);
                      border-color:var(--line); cursor:default; }
  .portao-dica{ margin:20px 0 0; font-size:13px; color:var(--ink-dim);
                line-height:1.5; }

  #fps.meio{opacity:.55;}""")


# ═══════════════════════════════════════════════════════════════════
# 3. O RELOGIO SO ANDA DEPOIS DE INICIAR, E COMECA DO ZERO
# ═══════════════════════════════════════════════════════════════════
troca("let t = 0, andando = true, cenaAtual = 1, misturaCeu = 0, inverterCeu = 0;",
      "let t = 0, andando = false, cenaAtual = 1, misturaCeu = 0, inverterCeu = 0;")

troca("""const bTocar = document.getElementById('bTocar');
bTocar.onclick = ()=>{ andando = !andando; bTocar.textContent = andando ? 'pausar' : 'tocar'; };""",
"""const bTocar = document.getElementById('bTocar');
bTocar.onclick = ()=>{ andando = !andando; bTocar.textContent = andando ? 'pausar' : 'tocar'; };
bTocar.textContent = 'tocar';

/* ═══════════ o portão ═══════════
   Comecar do zero e explicito: quem inicia quer o inicio. E o relogio da
   obra e o relogio do shader zeram juntos, senao a partitura recomeca com
   as animacoes no meio do movimento. */
const ePortao  = document.getElementById('portao');
const bIniciar = document.getElementById('bIniciar');
const ePortaoDica = document.getElementById('portaoDica');

function iniciarObra(){
  t = 0; relogio = 0;
  cenaAtual = 1; misturaCeu = 0;
  ceuA = CENAS[1].ceu; ceuB = CENAS[1].ceu;
  andando = true;
  bTocar.textContent = 'pausar';
  ePortao.classList.add('foi');
  marca = performance.now();     // nao contar como dt o tempo parado
}
bIniciar.onclick = iniciarObra;""")


# ═══════════════════════════════════════════════════════════════════
# 4. O BOTAO SO LIBERA QUANDO AS IMAGENS ESTAO PRONTAS
# ═══════════════════════════════════════════════════════════════════
troca("""function carregar(t,url,ehCeu){
  const im = new Image();
  im.onerror = ()=> console.warn('textura nao carregou:', url.slice(0,60));
  im.onload = ()=>{""",
"""function carregar(t,url,ehCeu){
  const im = new Image();
  im.onerror = ()=>{ falharTex(url); };
  im.onload = ()=>{
    contarTex();""")

troca("""function carregarAlfa(t,url){
  const im = new Image();
  im.onerror = ()=> console.warn('textura nao carregou:', url.slice(0,60));
  im.onload = ()=>{""",
"""function carregarAlfa(t,url){
  const im = new Image();
  im.onerror = ()=>{ falharTex(url); };
  im.onload = ()=>{
    contarTex();""")

troca("""/* ═══════════ texturas ═══════════ */""",
"""/* ═══════════ texturas ═══════════ */

/* CONTAGEM DAS IMAGENS.

   Sao onze, todas embutidas no proprio arquivo. No computador decodificam
   num piscar; no headset o arquivo tem quase seis megabytes e demora. Se a
   obra comecar antes disso, os primeiros segundos rodam com cor chapada no
   lugar da pintura — e quem esta dentro conclui que nao funcionou.

   Por isso o botao so libera quando as onze chegam. E se alguma falhar,
   isso APARECE: falha silenciosa num cenario escuro passa despercebida ate
   alguem reparar que esta faltando uma coisa, e ai ja e no dia. */
const TEX_TOTAL = 11;
let texProntas = 0, texFalhas = [];
function relatarTex(){
  const e = document.getElementById('vTex');
  if(e) e.textContent = texProntas + '/' + TEX_TOTAL +
                        (texFalhas.length ? '  ✕' + texFalhas.length : '');
  const d = document.getElementById('portaoDica');
  const b = document.getElementById('bIniciar');
  if(!d || !b) return;
  if(texFalhas.length){
    d.textContent = texFalhas.length + ' imagem(ns) nao carregaram. A obra abre '
                  + 'assim mesmo, com cor chapada no lugar delas.';
    b.disabled = false;
  }else if(texProntas >= TEX_TOTAL){
    d.textContent = 'Ponha o capacete antes de iniciar: os dez minutos correm '
                  + 'sozinhos a partir daqui.';
    b.disabled = false;
  }else{
    d.textContent = 'carregando as imagens…  ' + texProntas + ' de ' + TEX_TOTAL;
    b.disabled = true;
  }
}
function contarTex(){ texProntas++; relatarTex(); }
function falharTex(url){
  texFalhas.push(url.slice(0, 40));
  console.warn('textura nao carregou:', url.slice(0, 60));
  relatarTex();
}
""")

troca("""const texRaiz = novaTex([80,75,120]);""",
      """relatarTex();
const texRaiz = novaTex([80,75,120]);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('alfa da composicao, portao de inicio, e contagem das imagens')
