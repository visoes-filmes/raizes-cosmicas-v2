# -*- coding: utf-8 -*-
"""Gera um visualizador 360 (WebGL puro) com a imagem embutida."""
import base64
import io
import sys
from PIL import Image

src, dst, titulo = sys.argv[1], sys.argv[2], sys.argv[3]
src_fluxo = sys.argv[4] if len(sys.argv) > 4 else None


def embutir(caminho, qualidade=88, png=False):
    """2048x1024 = 2^11 x 2^10. Potencia de dois e obrigatorio: o WebGL 1 so
    aceita textura repetida (que e o que faz a esfera fechar a volta) se as
    duas medidas forem potencia de dois. Fora disso a textura sai preta."""
    img = Image.open(caminho).convert("RGB").resize((2048, 1024), Image.LANCZOS)
    b = io.BytesIO()
    if png:
        img.save(b, format="PNG", optimize=True)
        tipo = "png"
    else:
        img.save(b, format="JPEG", quality=qualidade, optimize=True)
        tipo = "jpeg"
    print(f"  {caminho.split(chr(92))[-1]}: {len(b.getvalue())//1024} KB")
    return f"data:image/{tipo};base64," + base64.b64encode(b.getvalue()).decode("ascii")


print("Texturas embutidas:")
b64 = embutir(src)
# o mapa de fluxo vai em JPEG de qualidade alta: direcao aceita leve perda,
# e PNG dobraria o tamanho do arquivo sem ganho visivel
b64_fluxo = embutir(src_fluxo, qualidade=94) if src_fluxo else b64

HTML = """<title>Esfera Raízes Cósmicas</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
  /* Instrumento de conferência: o painel é escuro por decisão, não por tema.
     Qualquer fundo claro falsearia a leitura de uma obra que é quase toda preta. */
  :root{
    --ground:#08060e;
    --panel:rgba(21,15,38,.88);
    --line:#2c2245;
    --ink:#efe8f8;
    --ink-dim:#9f8fbe;
    --accent:#c9a8ff;
    --ember:#ff9d5c;
  }
  *{box-sizing:border-box;}
  html,body{height:100%;margin:0;}
  body{
    background:var(--ground);
    color:var(--ink);
    font-family:"IBM Plex Sans",-apple-system,Segoe UI,Roboto,sans-serif;
    overflow:hidden;
  }
  #gl{position:fixed;inset:0;width:100%;height:100%;display:block;cursor:grab;}
  #gl:active{cursor:grabbing;}

  .card{
    position:fixed;
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:10px;
    backdrop-filter:blur(10px);
    padding:12px 14px;
  }
  #head{top:16px;left:16px;max-width:330px;}
  #head h1{
    margin:0 0 5px;font-size:13px;font-weight:600;letter-spacing:.01em;
    text-wrap:balance;
  }
  #head p{margin:0;font-size:11.5px;line-height:1.55;color:var(--ink-dim);}

  #hud{
    top:16px;right:16px;
    font-family:"IBM Plex Mono",ui-monospace,Consolas,monospace;
    font-size:11px;color:var(--ink-dim);
    font-variant-numeric:tabular-nums;
    display:grid;grid-template-columns:auto auto;gap:3px 12px;
  }
  #hud b{color:var(--ink);font-weight:500;text-align:right;}

  #ctl{
    bottom:16px;left:50%;transform:translateX(-50%);
    display:flex;gap:7px;align-items:center;flex-wrap:wrap;justify-content:center;
    max-width:calc(100vw - 32px);
  }
  button{
    background:#241a3d;color:var(--ink);
    border:1px solid var(--line);border-radius:7px;
    padding:8px 13px;font-size:12px;font-weight:500;cursor:pointer;
    font-family:inherit;
  }
  button:hover{background:#2f2350;border-color:#3d3060;}
  button:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
  button.on{background:var(--accent);color:#1c1030;border-color:var(--accent);}
  .tag{
    display:inline-block;margin-left:5px;padding:1px 6px;border-radius:4px;
    font-family:"IBM Plex Mono",monospace;font-size:9.5px;
    background:rgba(255,157,92,.14);color:var(--ember);
  }
  #lbl{
    display:flex;align-items:center;gap:8px;
    font-size:11px;color:var(--ink-dim);
    padding:0 4px 0 8px;border-left:1px solid var(--line);
  }
  #lbl b{
    font-family:"IBM Plex Mono",monospace;color:var(--ink);
    font-weight:500;font-variant-numeric:tabular-nums;min-width:34px;
  }
  #sCorrente{width:88px;accent-color:var(--accent);}
  #sCorrente:focus-visible{outline:2px solid var(--accent);outline-offset:3px;}
</style>

<canvas id="gl"></canvas>

<div class="card" id="head">
  <h1>Conferência da esfera</h1>
  <p>Arraste pra olhar em volta. Isto é a esfera de verdade, não a imagem
  achatada: é assim que a pessoa vai ver dentro do headset. A aquarela
  escorre na direção das próprias formas, e o loop fecha a cada 63 segundos.</p>
</div>

<div class="card" id="hud">
  <span>giro</span><b id="vYaw">0°</b>
  <span>altura</span><b id="vPitch">0°</b>
  <span>campo</span><b id="vFov">85°</b>
</div>

<div class="card" id="ctl">
  <button id="bFront">Frente (estrela)</button>
  <button id="bSeam">Ver a emenda<span class="tag">costas</span></button>
  <button id="bUp">Topo (zênite)</button>
  <button id="bDown">Base (nadir)</button>
  <button id="bSpin">Girar sozinho</button>
  <button id="bAnim">Animação ligada</button>
  <label id="lbl">corrente
    <input id="sCorrente" type="range" min="0" max="250" value="100">
    <b id="vCorrente">1.0×</b>
  </label>
</div>

<script>
(function(){
const cv = document.getElementById('gl');
const gl = cv.getContext('webgl');
if(!gl){ document.body.innerHTML = '<p style="padding:24px">WebGL indisponivel neste navegador.</p>'; return; }

const VS = `
attribute vec2 p;
varying vec2 uv;
void main(){ uv = p; gl_Position = vec4(p, 0.0, 1.0); }
`;

// Converte cada pixel da tela num raio 3D, acha onde ele bate na esfera,
// e le a cor correspondente na imagem equirretangular. E o mesmo calculo
// que o headset faz.
const FS = `
precision highp float;
varying vec2 uv;
uniform sampler2D tex;
uniform sampler2D fluxo;
uniform vec2 res;
uniform float yaw, pitch, fov, time, anim, corrente;
const float PI = 3.14159265359;
// 63 = 9 x 7. Tem que ser multiplo do ciclo da corrente (7s), senao o loop
// da um salto: a corrente voltaria ao inicio fora de hora.
const float CICLO = 63.0;

float hash13(vec3 p){
  p = fract(p * 0.1031);
  p += dot(p, p.yzx + 33.33);
  return fract((p.x + p.y) * p.z);
}

// Poeira cosmica: pontos esparsos no espaco em volta da pessoa (camada 4).
// Procedural de proposito: e atmosfera, nao arte.
float poeira(vec3 dir, float w){
  // Recebe a FASE (0..2pi), nao o relogio. Assim tudo aqui dentro so usa
  // multiplos inteiros dela e o campo inteiro volta ao inicio no fim do loop.
  float soma = 0.0;
  for(int i = 0; i < 3; i++){
    float esc = 22.0 + float(i) * 17.0;
    float giro = w * (1.0 + float(i));      // 1, 2 e 3 voltas por ciclo
    vec3 d = vec3(dir.x * cos(giro) + dir.z * sin(giro),
                  dir.y,
                  -dir.x * sin(giro) + dir.z * cos(giro));
    vec3 cel = floor(d * esc);
    float h = hash13(cel);
    if(h > 0.9955){
      vec3 centro = (cel + 0.5) / esc;
      float dist = length(normalize(centro) - d);
      // O raio TEM que ser bem menor que a celula (1/esc), senao o ponto
      // encosta na borda dela e vira quadrado em vez de graozinho redondo.
      float raio = 0.30 / esc;
      float ponto = smoothstep(raio, raio * 0.15, dist);
      float pisca = 0.55 + 0.45 * sin(w * 6.0 + h * 40.0);
      soma += ponto * pisca * (0.35 + 0.65 * h);
    }
  }
  return soma;
}

void main(){
  float aspect = res.x / res.y;
  float tf = tan(fov * 0.5);
  vec3 dir = normalize(vec3(uv.x * tf * aspect, uv.y * tf, -1.0));

  float cp = cos(pitch), sp = sin(pitch);
  dir = vec3(dir.x, dir.y * cp - dir.z * sp, dir.y * sp + dir.z * cp);
  float cy = cos(yaw), sy = sin(yaw);
  dir = vec3(dir.x * cy + dir.z * sy, dir.y, -dir.x * sy + dir.z * cy);

  float lon = atan(dir.x, -dir.z);
  float lat = asin(clamp(dir.y, -1.0, 1.0));

  float w = 2.0 * PI * time / CICLO;   // fase que fecha o loop

  // DERIVA DA AQUARELA
  // So uso seno/cosseno de MULTIPLOS INTEIROS da longitude. Isso e o que
  // garante que a distorcao volte exatamente ao mesmo valor depois da volta
  // completa, ou seja, a emenda continua fechada mesmo animando.
  float polo = cos(lat);                       // some nos polos, senao borra o zenite
  float du = (sin(3.0 * lon + w) * 0.55 + sin(5.0 * lon - 1.4 * w) * 0.28
              + sin(2.0 * lon + 0.6 * w) * 0.35) * 0.0022 * anim * polo;
  float dv = (cos(2.0 * lon - 0.8 * w) * 0.5 + cos(4.0 * lon + 1.2 * w) * 0.25)
             * 0.0018 * anim * polo * polo;

  vec2 st = vec2(fract(lon / (2.0 * PI) + 0.5 + du),
                 clamp(0.5 - lat / PI + dv, 0.001, 0.999));

  // ---- CORRENTE: a pintura escorre NA DIRECAO DAS PROPRIAS FORMAS ----
  // O mapa de fluxo guarda, em cada ponto, pra onde corre o traco da
  // aquarela. Empurro a leitura da textura por esse caminho.
  vec3 fl = texture2D(fluxo, st).rgb;
  vec2 dirFluxo = (fl.rg - 0.5) * 2.0;
  float forcaFluxo = fl.b * corrente * anim;

  // Duas leituras defasadas em meio ciclo, cruzadas por uma onda triangular.
  // E o que permite escorrer pra sempre sem nunca dar um salto de volta:
  // quando uma leitura chega ao fim do trecho, a outra ja esta no meio.
  float ciclo = time / 7.0;
  float f1 = fract(ciclo);
  float f2 = fract(ciclo + 0.5);
  // 0.012 em coordenada de textura = uns 12px numa esfera de 2048 de largura.
  // Acima disso o cruzamento das duas leituras vira fantasma visivel.
  float amp = 0.012 * forcaFluxo;

  vec2 passo1 = dirFluxo * (f1 - 0.5) * amp;
  vec2 passo2 = dirFluxo * (f2 - 0.5) * amp;
  vec2 st1 = vec2(fract(st.x + passo1.x), clamp(st.y + passo1.y, 0.001, 0.999));
  vec2 st2 = vec2(fract(st.x + passo2.x), clamp(st.y + passo2.y, 0.001, 0.999));

  vec3 c1 = texture2D(tex, st1).rgb;
  vec3 c2 = texture2D(tex, st2).rgb;
  vec3 escorrido = mix(c1, c2, abs(1.0 - 2.0 * f1));

  vec3 parado = texture2D(tex, st).rgb;
  // onde nao ha forma definida, fica a imagem original, sem borrao
  vec3 cor = mix(parado, escorrido, clamp(forcaFluxo * 1.6, 0.0, 1.0));

  // RESPIRO: a pintura clareia e escurece de leve, como aguada secando
  float respiro = 1.0 + anim * 0.045 * sin(w + lon * 2.0);
  cor *= respiro;

  // CINTILAR: so os pontos ja brilhantes (estrelas e a linha dourada) pulsam
  float brilho = max(cor.r, max(cor.g, cor.b));
  float faisca = smoothstep(0.62, 0.95, brilho);
  cor += cor * faisca * anim * 0.35 * (0.5 + 0.5 * sin(w * 4.0 + lon * 30.0 + lat * 20.0));

  // POEIRA COSMICA por cima de tudo
  float p = poeira(dir, w) * anim;
  cor += vec3(0.82, 0.76, 1.0) * p * 0.30;

  gl_FragColor = vec4(cor, 1.0);
}
`;

function sh(type, src){
  const s = gl.createShader(type);
  gl.shaderSource(s, src); gl.compileShader(s);
  if(!gl.getShaderParameter(s, gl.COMPILE_STATUS)) console.error(gl.getShaderInfoLog(s));
  return s;
}
const prog = gl.createProgram();
gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS));
gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
gl.linkProgram(prog); gl.useProgram(prog);

const buf = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, buf);
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
const loc = gl.getAttribLocation(prog, 'p');
gl.enableVertexAttribArray(loc);
gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

const uTex = gl.getUniformLocation(prog, 'tex');
const uRes = gl.getUniformLocation(prog, 'res');
const uYaw = gl.getUniformLocation(prog, 'yaw');
const uPitch = gl.getUniformLocation(prog, 'pitch');
const uFov = gl.getUniformLocation(prog, 'fov');
const uTime = gl.getUniformLocation(prog, 'time');
const uAnim = gl.getUniformLocation(prog, 'anim');
const uFluxo = gl.getUniformLocation(prog, 'fluxo');
const uCorrente = gl.getUniformLocation(prog, 'corrente');

function novaTextura(preenchimento){
  const t = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, t);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, 1, 1, 0, gl.RGB, gl.UNSIGNED_BYTE,
                new Uint8Array(preenchimento));
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  return t;
}
function carregar(t, url){
  const img = new Image();
  img.onload = function(){
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  };
  img.src = url;
}

const tex = novaTextura([10, 8, 16]);
const texFluxo = novaTextura([128, 128, 0]);   // direcao neutra, forca zero
carregar(tex, '__B64__');
carregar(texFluxo, '__B64_FLUXO__');

let yaw = 0, pitch = 0, fov = 85 * Math.PI / 180;
let tYaw = 0, tPitch = 0;
let spin = false;
const CICLO = 63;              // mesmo valor do shader: o loop fecha em 63s
let relogio = 0, animar = true, forca = 0, corrente = 1.0;

function resize(){
  const d = Math.min(window.devicePixelRatio || 1, 2);
  const w = cv.clientWidth || window.innerWidth;
  const h = cv.clientHeight || window.innerHeight;
  const nw = Math.max(1, Math.floor(w * d));
  const nh = Math.max(1, Math.floor(h * d));
  if(cv.width !== nw || cv.height !== nh){
    cv.width = nw; cv.height = nh;
    gl.viewport(0, 0, nw, nh);
  }
}
window.addEventListener('resize', resize); resize();

let drag = false, lx = 0, ly = 0;
cv.addEventListener('mousedown', e => { drag = true; lx = e.clientX; ly = e.clientY; spin = false; upd(); });
window.addEventListener('mouseup', () => drag = false);
window.addEventListener('mousemove', e => {
  if(!drag) return;
  tYaw -= (e.clientX - lx) * 0.005;
  tPitch = Math.max(-1.45, Math.min(1.45, tPitch + (e.clientY - ly) * 0.005));
  lx = e.clientX; ly = e.clientY;
});
cv.addEventListener('touchstart', e => { if(e.touches[0]){ drag = true; lx = e.touches[0].clientX; ly = e.touches[0].clientY; spin = false; upd(); } }, {passive:true});
window.addEventListener('touchend', () => drag = false);
window.addEventListener('touchmove', e => {
  if(!drag || !e.touches[0]) return;
  tYaw -= (e.touches[0].clientX - lx) * 0.006;
  tPitch = Math.max(-1.45, Math.min(1.45, tPitch + (e.touches[0].clientY - ly) * 0.006));
  lx = e.touches[0].clientX; ly = e.touches[0].clientY;
}, {passive:true});
cv.addEventListener('wheel', e => {
  e.preventDefault();
  fov = Math.max(0.35, Math.min(2.2, fov + e.deltaY * 0.0015));
}, {passive:false});

function go(y, p){ tYaw = y; tPitch = p; spin = false; upd(); }
document.getElementById('bFront').onclick = () => go(0, 0);
document.getElementById('bSeam').onclick  = () => go(Math.PI, 0);
document.getElementById('bUp').onclick    = () => go(tYaw, 1.4);
document.getElementById('bDown').onclick  = () => go(tYaw, -1.4);
const bSpin = document.getElementById('bSpin');
bSpin.onclick = () => { spin = !spin; upd(); };
const bAnim = document.getElementById('bAnim');
bAnim.onclick = () => { animar = !animar; upd(); };
const sCor = document.getElementById('sCorrente');
const vCor = document.getElementById('vCorrente');
sCor.addEventListener('input', () => {
  corrente = sCor.value / 100;
  vCor.textContent = corrente.toFixed(1) + '\\u00d7';
});
function upd(){
  bSpin.classList.toggle('on', spin);
  bAnim.classList.toggle('on', animar);
  bAnim.textContent = animar ? 'Animação ligada' : 'Animação desligada';
}
upd();

const eY = document.getElementById('vYaw'), eP = document.getElementById('vPitch'), eF = document.getElementById('vFov');
function deg(r){ return Math.round(r * 180 / Math.PI); }

const calmo = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const suave = calmo ? 1 : 0.12;

function frame(){
  resize();
  if(spin) tYaw += calmo ? 0.0007 : 0.0016;
  yaw += (tYaw - yaw) * suave;
  pitch += (tPitch - pitch) * suave;

  gl.useProgram(prog);
  gl.activeTexture(gl.TEXTURE0);
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.uniform1i(uTex, 0);
  gl.activeTexture(gl.TEXTURE1);
  gl.bindTexture(gl.TEXTURE_2D, texFluxo);
  gl.uniform1i(uFluxo, 1);
  gl.uniform1f(uCorrente, corrente);
  gl.uniform2f(uRes, cv.width, cv.height);
  gl.uniform1f(uYaw, yaw);
  gl.uniform1f(uPitch, pitch);
  gl.uniform1f(uFov, fov);
  relogio = (relogio + 1/60) % CICLO;      // volta a zero: o loop fecha
  gl.uniform1f(uTime, relogio);
  forca += ((animar ? 1 : 0) - forca) * 0.06;   // liga/desliga sem tranco
  gl.uniform1f(uAnim, forca);
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

  let d = ((deg(yaw) % 360) + 360) % 360;
  eY.textContent = d + '\\u00b0';
  eP.textContent = deg(pitch) + '\\u00b0';
  eF.textContent = deg(fov) + '\\u00b0';
  requestAnimationFrame(frame);
}
frame();
})();
</script>
"""

html = (HTML.replace("__B64_FLUXO__", b64_fluxo)
            .replace("__B64__", b64)
            .replace("__TITULO__", titulo))
with open(dst, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Gerado: {dst}  ({len(html)//1024} KB)")
