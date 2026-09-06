# -*- coding: utf-8 -*-
"""Auditoria das texturas: marcador transparente, unidade fixa no carregamento,
falha que avisa, e filtragem anisotropica."""
import io, os
AQUI = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(AQUI, 'mr.template.html')
s = io.open(p, encoding='utf-8').read()


def troca(a, b):
    global s
    assert a in s, 'NAO ACHOU: ' + a[:80]
    s = s.replace(a, b, 1)


troca("""/* ═══════════ texturas ═══════════ */
function novaTex(c){""",
"""/* ═══════════ texturas ═══════════ */

/* FILTRAGEM ANISOTROPICA.

   O mipmap resolve o cintilar, mas resolve BORRANDO: ele escolhe um nivel
   so, e de raspao os dois eixos da imagem se comprimem de forma muito
   diferente — o horizonte esmaga a largura e deixa a altura quase intacta.
   Obrigado a um nivel unico, o hardware escolhe pelo eixo pior e borra
   tambem o eixo que estava bom. E por isso que o ceu, ja com mipmap, fica
   nitido em cima e lavado na linha do horizonte.

   A anisotropia deixa a placa tirar varias amostras ao longo do eixo
   comprimido. O cintilar continua resolvido, e a nitidez volta — que e
   exatamente o que falta na cupula perto do horizonte e na agua vista
   rasante, os dois lugares onde a obra passa mais tempo sendo olhada.

   4 e o ponto de equilibrio: quase todo o ganho visivel, e uma fracao do
   custo de 16. Se algum dia faltar quadro, este numero e a primeira coisa
   a baixar — e um numero so, e a obra continua inteira sem ele. */
const ANISO_ALVO = 4;
const extAniso = gl.getExtension('EXT_texture_filter_anisotropic')
              || gl.getExtension('WEBKIT_EXT_texture_filter_anisotropic')
              || gl.getExtension('MOZ_EXT_texture_filter_anisotropic');
const ANISO = extAniso
  ? Math.min(ANISO_ALVO, gl.getParameter(extAniso.MAX_TEXTURE_MAX_ANISOTROPY_EXT))
  : 0;

function novaTex(c){""")


# ── marcador transparente para as figuras ────────────────────────────
troca("""/* Textura COM ALFA. Precisa de RGBA e de premultiplicacao desligada: com""",
"""/* MARCADOR TRANSPARENTE, para o que e recorte.

   O novaTex faz um pixel RGB — e RGB nao tem alfa, entao o shader le alfa
   igual a 1. Enquanto a imagem de verdade nao chega, a figura desenha como
   um QUADRADO OPACO no lugar dela. Sao milissegundos no computador, mas o
   arquivo tem quase seis megabytes e no headset a decodificacao demora: e
   exatamente a classe de defeito de "aparece do nada e some" que nao pode
   acontecer com visitante dentro.

   Um pixel RGBA com alfa zero resolve: antes de carregar, a figura nao
   existe em vez de existir errada. */
function novaTexAlfa(){
  const t = gl.createTexture();
  gl.activeTexture(gl.TEXTURE0);
  gl.bindTexture(gl.TEXTURE_2D, t);
  gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,1,1,0,gl.RGBA,gl.UNSIGNED_BYTE,
                new Uint8Array([0,0,0,0]));
  for(const [k,v] of [[gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE],
                      [gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE],
                      [gl.TEXTURE_MIN_FILTER,gl.LINEAR],
                      [gl.TEXTURE_MAG_FILTER,gl.LINEAR]])
    gl.texParameteri(gl.TEXTURE_2D,k,v);
  return t;
}

/* Textura COM ALFA. Precisa de RGBA e de premultiplicacao desligada: com""")

troca("const FIGS = [novaTex([0,0,0]), novaTex([0,0,0]), novaTex([0,0,0]), novaTex([0,0,0])];",
      "const FIGS = [novaTexAlfa(), novaTexAlfa(), novaTexAlfa(), novaTexAlfa()];")


# ── unidade fixa no carregamento, e falha que avisa ──────────────────
troca("""function carregarAlfa(t,url){
  const im = new Image();
  im.onload = ()=>{
    gl.bindTexture(gl.TEXTURE_2D,t);""",
"""function carregarAlfa(t,url){
  const im = new Image();
  im.onerror = ()=> console.warn('textura nao carregou:', url.slice(0,60));
  im.onload = ()=>{
    /* A UNIDADE PRECISA SER FIXADA AQUI.

       bindTexture liga a textura na unidade ATIVA no momento, e este
       codigo roda quando a imagem termina de decodificar — que pode ser no
       meio de um quadro, com a unidade ativa em 5 ou em 7, onde o laco de
       desenho deixou. Ligar ali substitui a textura que o desenho estava
       usando, e sai um quadro com a pele errada no planeta.

       Um quadro so, porque o laco religa tudo no seguinte. Mas um quadro
       errado num vernissage e um quadro errado. */
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D,t);""")

troca("""function carregar(t,url){
  const im = new Image();
  im.onload = ()=>{
    gl.bindTexture(gl.TEXTURE_2D,t);""",
"""function carregar(t,url){
  const im = new Image();
  im.onerror = ()=> console.warn('textura nao carregou:', url.slice(0,60));
  im.onload = ()=>{
    gl.activeTexture(gl.TEXTURE0);   // pelo mesmo motivo do carregarAlfa
    gl.bindTexture(gl.TEXTURE_2D,t);""")


# ── anisotropia onde ha mipmap ───────────────────────────────────────
troca("""    gl.generateMipmap(gl.TEXTURE_2D);
    for(const [k,v] of [[gl.TEXTURE_WRAP_S,gl.REPEAT],[gl.TEXTURE_WRAP_T,gl.REPEAT],
                        [gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR],
                        [gl.TEXTURE_MAG_FILTER,gl.LINEAR]])
      gl.texParameteri(gl.TEXTURE_2D,k,v);""",
"""    gl.generateMipmap(gl.TEXTURE_2D);
    for(const [k,v] of [[gl.TEXTURE_WRAP_S,gl.REPEAT],[gl.TEXTURE_WRAP_T,gl.REPEAT],
                        [gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR],
                        [gl.TEXTURE_MAG_FILTER,gl.LINEAR]])
      gl.texParameteri(gl.TEXTURE_2D,k,v);

    /* So aqui: anisotropia sem mipmap nao faz nada, e as figuras nao tem
       mipmap de proposito. */
    if(ANISO > 1)
      gl.texParameterf(gl.TEXTURE_2D, extAniso.TEXTURE_MAX_ANISOTROPY_EXT, ANISO);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('texturas: marcador transparente, unidade fixa, falha avisada, anisotropia')
