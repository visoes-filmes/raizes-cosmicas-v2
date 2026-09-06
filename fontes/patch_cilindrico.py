# -*- coding: utf-8 -*-
"""Billboard cilindrico: a figura acompanha a pessoa, mas nunca deita."""
import io, os
AQUI = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(AQUI, 'mr.template.html')
s = io.open(p, encoding='utf-8').read()

def troca(a, b):
    global s
    assert a in s, 'NAO ACHOU: ' + a[:80]
    s = s.replace(a, b, 1)

# ── 1. as figuras ────────────────────────────────────────────────────
troca("""const VS_FIGU = `
attribute vec2 aXY;
uniform mat4 mvp;
uniform vec3 camDir, camCima, centro;
uniform vec2 tamanho;
uniform float espelho, balanco, tempo;
varying vec2 vUV;
varying float vAltura;
void main(){
  vec2 q = aXY;
  // o balanco cresce com a altura: o pe fica, a cabeca oscila
  float alt = q.y * 0.5 + 0.5;
  q.x += sin(tempo * 0.4 + centro.x * 2.0) * 0.05 * alt * balanco;

  vec3 cima = camCima * (espelho > 0.5 ? -1.0 : 1.0);
  vec3 p = centro + camDir * (q.x * tamanho.x) + cima * (q.y * tamanho.y);""",
"""const VS_FIGU = `
attribute vec2 aXY;
uniform mat4 mvp;
uniform vec3 olhoPos, centro;
uniform vec2 tamanho;
uniform float espelho, balanco, tempo;
varying vec2 vUV;
varying float vAltura;
void main(){
  vec2 q = aXY;
  // o balanco cresce com a altura: o pe fica, a cabeca oscila
  float alt = q.y * 0.5 + 0.5;
  q.x += sin(tempo * 0.4 + centro.x * 2.0) * 0.05 * alt * balanco;

  /* GIRO CILINDRICO. A figura vira para a pessoa, mas so em torno do
     proprio eixo vertical: o alto continua sendo o alto.

     A diferenca em relacao a encarar a camera inteira e a que importa.
     Encarando a camera inteira, ao olhar para cima a figura DEITA junto —
     e uma figura deitada atravessa o chao, corta a arvore ao lado e se
     embaralha com o que estiver perto. Presa ao eixo vertical, ela se
     comporta como um recorte de teatro em pe: gira no lugar e pronto.

     E ela gira para a POSICAO da pessoa, nao para o plano da tela. Quem
     esta de lado ve a figura virada para si, e nao de esguelha. Isso e o
     que impede a sensacao de que ela escorrega quando a pessoa anda: o
     centro nunca sai do lugar, so a face muda. */
  vec3 paraMim = olhoPos - centro;
  paraMim.y = 0.0;
  float dist = length(paraMim);
  // de frente para cima, se a pessoa estiver exatamente em cima do centro
  vec3 frente = dist > 0.0005 ? paraMim / dist : vec3(0.0, 0.0, 1.0);
  vec3 lado = vec3(frente.z, 0.0, -frente.x);   // horizontal, sempre
  vec3 cima = vec3(0.0, espelho > 0.5 ? -1.0 : 1.0, 0.0);

  vec3 p = centro + lado * (q.x * tamanho.x) + cima * (q.y * tamanho.y);""")

troca("""const locFi = {mvp:uFi('mvp'), camDir:uFi('camDir'), camCima:uFi('camCima'),
               centro:uFi('centro'),""",
      """const locFi = {mvp:uFi('mvp'), olhoPos:uFi('olhoPos'),
               centro:uFi('centro'),""")

troca("""      gl.uniform3f(locFi.camDir, camDir[0], camDir[1], camDir[2]);
      gl.uniform3f(locFi.camCima, camCima[0], camCima[1], camCima[2]);""",
      """      gl.uniform3f(locFi.olhoPos, olhoPos[0], olhoPos[1], olhoPos[2]);""")

# ── 2. as camadas de papel ───────────────────────────────────────────
troca("""const VS_PAPEL = `
attribute vec2 aXY;              // -1..1 no plano da camada
uniform mat4 mvp;
uniform vec3 camDir, camCima;
uniform vec3 centro;
uniform vec2 tamanho;
uniform float subir;             // 0 = ainda embaixo, 1 = no lugar
varying vec2 vXY;
void main(){
  vXY = aXY;
  // A camada encara a pessoa, como a nuvem: assim nunca se ve que e chapa.
  vec3 p = centro + camDir * (aXY.x * tamanho.x) + camCima * (aXY.y * tamanho.y);""",
"""const VS_PAPEL = `
attribute vec2 aXY;              // -1..1 no plano da camada
uniform mat4 mvp;
uniform vec3 olhoPos;
uniform vec3 centro;
uniform vec2 tamanho;
uniform float subir;             // 0 = ainda embaixo, 1 = no lugar
varying vec2 vXY;
void main(){
  vXY = aXY;
  /* Mesmo giro cilindrico das figuras. Camada de papel recortado e
     cenario de teatro: fica em pe. Encarando a camera inteira, ao olhar
     para cima as sete camadas deitavam juntas e o empilhamento — que e
     a coisa toda — desmanchava. */
  vec3 paraMim = olhoPos - centro;
  paraMim.y = 0.0;
  float dist = length(paraMim);
  vec3 frente = dist > 0.0005 ? paraMim / dist : vec3(0.0, 0.0, 1.0);
  vec3 lado = vec3(frente.z, 0.0, -frente.x);
  vec3 p = centro + lado * (aXY.x * tamanho.x) + vec3(0.0, aXY.y * tamanho.y, 0.0);""")

troca("""const locPa = {mvp:uPa('mvp'), camDir:uPa('camDir'), camCima:uPa('camCima'),
               centro:uPa('centro'),""",
      """const locPa = {mvp:uPa('mvp'), olhoPos:uPa('olhoPos'),
               centro:uPa('centro'),""")

troca("""    gl.uniform3f(locPa.camDir, camDir[0], camDir[1], camDir[2]);
    gl.uniform3f(locPa.camCima, camCima[0], camCima[1], camCima[2]);""",
      """    gl.uniform3f(locPa.olhoPos, olhoPos[0], olhoPos[1], olhoPos[2]);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('billboard cilindrico: figuras e camadas de papel')
