/* O ARNES DA BANCADA -- carregado na pagina _dev.html depois de "Iniciar":
 *
 *   const src = await (await fetch('/fontes/bancada.js')).text();
 *   await (new (Object.getPrototypeOf(async function(){}).constructor)(src))();
 *
 * O que ele da:
 *   P.mvp            se nao for null, TODA chamada de desenho recebe esta matriz no lugar da da obra
 *   M.para(az, el, fov)          matriz para olhar de [0, 1.6, 0] num azimute (graus, 0 = -z,
 *                                positivo a direita) e elevacao (graus)
 *   paraDe(ey, az, el, fov)      o mesmo, com o olho a ey metros -- e avisa a obra (__olhoY),
 *                                para o mergulho e a lamina lerem a altura certa
 *   __frame()        desenha um quadro agora
 *   __fotoRapida(nome)   le os pixels do WebGL e manda para o servir.py, que grava em _fotos/<nome>
 *   __espera(ms)     espera ocupada (segura o quadro; para GIFs use await setTimeout)
 *
 * Coordenadas do espaco da obra: x para a direita, y para cima, -z para a frente.
 * A viewport da pagina tem que ser 1600 x 900 (a lente e feita nesse aspecto). */
const GL = WebGLRenderingContext.prototype;
if(!GL.__origDE){ GL.__origDE = GL.drawElements; GL.__origDA = GL.drawArrays; }
window.P = { mvp:null };
const pos = (gl) => { if(P.mvp){ const pr=gl.getParameter(gl.CURRENT_PROGRAM);
  const l=gl.getUniformLocation(pr,'mvp'); if(l) gl.uniformMatrix4fv(l,false,P.mvp); } };
const de = GL.__origDE;
GL.drawElements = function(m,cn,t,o){ window.__gl=this; pos(this); return de.call(this,m,cn,t,o); };
GL.drawArrays  = function(m,f,cn){ window.__gl=this; pos(this); return GL.__origDA.call(this,m,f,cn); };
if(!window.__capt){
  const raf = window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame = function(fn){ window.__quadro = fn; return raf(fn); };
  window.__capt = true;
}
window.__frame = () => window.__quadro(performance.now());
window.__espera = (ms) => { const t = performance.now(); while(performance.now() - t < ms){} };
window.__fotoRapida = function(nome){
  const gl = window.__gl, w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
  const px = new Uint8Array(w*h*4);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px);
  const cv = document.createElement('canvas'); cv.width=w; cv.height=h;
  const cx = cv.getContext('2d'), id = cx.createImageData(w,h);
  for(let y=0;y<h;y++) id.data.set(px.subarray((h-1-y)*w*4,(h-y)*w*4), y*w*4);
  cx.putImageData(id,0,0);
  const url = cv.toDataURL('image/jpeg', 0.92);
  const bin = atob(url.split(',')[1]); const buf = new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++) buf[i] = bin.charCodeAt(i);
  const xhr = new XMLHttpRequest(); xhr.open('POST', '/_foto/'+nome, false); xhr.send(buf);
  return xhr.status;
};
window.M = {
  persp(fy,asp,n,f){ const t=1/Math.tan(fy/2);
    return new Float32Array([t/asp,0,0,0, 0,t,0,0, 0,0,(f+n)/(n-f),-1, 0,0,2*f*n/(n-f),0]); },
  olhar(e,a,up){ const s=(q,r)=>[q[0]-r[0],q[1]-r[1],q[2]-r[2]];
    const x1=(q,r)=>[q[1]*r[2]-q[2]*r[1],q[2]*r[0]-q[0]*r[2],q[0]*r[1]-q[1]*r[0]];
    const nz=v=>{const L=Math.hypot(...v)||1;return[v[0]/L,v[1]/L,v[2]/L];};
    const z=nz(s(e,a)), x=nz(x1(up,z)), y=x1(z,x);
    return new Float32Array([x[0],y[0],z[0],0, x[1],y[1],z[1],0, x[2],y[2],z[2],0,
      -(x[0]*e[0]+x[1]*e[1]+x[2]*e[2]), -(y[0]*e[0]+y[1]*e[1]+y[2]*e[2]),
      -(z[0]*e[0]+z[1]*e[1]+z[2]*e[2]), 1]); },
  mul(a,b){ const o=new Float32Array(16);
    for(let cc=0;cc<4;cc++)for(let r=0;r<4;r++){let v=0;
      for(let k=0;k<4;k++)v+=a[k*4+r]*b[cc*4+k]; o[cc*4+r]=v;} return o; },
  // olhar para um azimute (graus, 0 = -z, positivo para a direita) e elevacao (graus)
  para(az, el, fov){ const a=az*Math.PI/180, e=el*Math.PI/180;
    const alvo=[Math.sin(a)*Math.cos(e), 1.6+Math.sin(e), -Math.cos(a)*Math.cos(e)];
    return M.mul(M.persp((fov||60)*Math.PI/180,1600/900,0.05,900), M.olhar([0,1.6,0],alvo,[0,1,0])); }
};
window.paraDe = (ey, az, el, fov) => {
  const a = az*Math.PI/180, e = el*Math.PI/180;
  window.__olhoY = ey;
  const alvo = [Math.sin(a)*Math.cos(e), ey + Math.sin(e), -Math.cos(a)*Math.cos(e)];
  return M.mul(M.persp((fov||60)*Math.PI/180, 1600/900, 0.05, 900), M.olhar([0, ey, 0], alvo, [0, 1, 0]));
};
'bancada pronta'
