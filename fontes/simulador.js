/* ═══════════ UM APARELHO DE MENTIRA ═══════════

   Isto engana a obra: ela pensa que entrou num Quest, e entra no navegador.

   POR QUE ISTO EXISTE. Metade dos defeitos deste projeto so aparecem DENTRO
   da sessao imersiva -- o alfa que se comporta diferente no passthrough, as
   maos, o toque, a ordem de desenho no quadro do headset. Ate hoje, testar
   qualquer um deles exigia alguem de capacete na cabeca, e uma rodada de
   teste levava minutos e dependia de outra pessoa. O resultado foi previsivel:
   coisas dadas por feitas que nunca tinham rodado uma vez.

   O QUE ELE SIMULA, e o que nao.

   Simula: a sessao immersive-ar abrindo, o espaco de referencia, o laco de
   quadros do headset, DUAS VISTAS (olho esquerdo e direito) com a separacao
   real de 63 mm, as duas maos com posicao e o gatilho, e o quadro comecando
   com ALFA ZERO -- que e a coisa que mais quebrou esta obra.

   Nao simula: o rastreamento de verdade, a latencia, o custo de dois olhos
   numa placa movel, e o passthrough. Onde a camera mostraria a sala, aqui
   fica um xadrez -- de proposito: assim se ve na hora o que esta
   transparente e o que nao esta, que e justamente o que nao se enxerga num
   fundo preto.

   Ele NAO substitui o headset. Ele elimina as viagens ao headset que eram
   so para descobrir que alguma coisa nao desenhava. */
(function(){
  const params = new URLSearchParams(location.search);
  if(params.get('sim') === '0') return;

  const OLHOS = 0.063;          // a distancia entre as pupilas, em metros
  let sessaoViva = null;

  /* O XADREZ POR TRAS DE TUDO. No headset o que esta atras da obra e a sala,
     vista pelas cameras. Aqui e um xadrez: onde ele aparecer, a obra esta
     deixando passar -- e onde a obra deveria ser opaca e o xadrez aparece,
     ha um defeito de alfa. E o unico jeito de VER transparencia. */
  function porXadrez(){
    const c = document.createElement('canvas');
    c.width = c.height = 64;
    const g = c.getContext('2d');
    g.fillStyle = '#2a2a33'; g.fillRect(0,0,64,64);
    g.fillStyle = '#3a3a46'; g.fillRect(0,0,32,32); g.fillRect(32,32,32,32);
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;inset:0;z-index:-1;background-repeat:repeat;'
                    + 'background-size:64px 64px;background-image:url(' + c.toDataURL() + ')';
    document.body.appendChild(d);
    document.documentElement.style.background = 'transparent';
    document.body.style.background = 'transparent';
  }

  /* AS MAOS. Mouse move a direita; segurando Alt, a esquerda. A roda
     aproxima e afasta. Espaco e o gatilho. Sao coordenadas de mundo, na
     frente de quem olha. */
  const maos = [
    { x:-0.18, y:1.30, z:-0.42, apertando:false },
    { x: 0.18, y:1.30, z:-0.42, apertando:false },
  ];
  let profundidade = 0.42;
  function ligarMaos(){
    addEventListener('mousemove', e=>{
      const i = e.altKey ? 0 : 1;
      const px = (e.clientX / innerWidth  - 0.5) * 1.6;
      const py = (0.5 - e.clientY / innerHeight) * 1.1;
      maos[i].x = px; maos[i].y = 1.30 + py; maos[i].z = -profundidade;
    });
    addEventListener('wheel', e=>{
      profundidade = Math.max(0.12, Math.min(1.4, profundidade + e.deltaY*0.0012));
    }, {passive:true});
    addEventListener('keydown', e=>{ if(e.code==='Space'){ maos[0].apertando = maos[1].apertando = true; } });
    addEventListener('keyup',   e=>{ if(e.code==='Space'){ maos[0].apertando = maos[1].apertando = false; } });
  }

  const eixo = { yaw:0, pitch:0, x:0, z:0, alturaOlho:1.60 };
  function ligarCamera(){
    let arrastando = false, lx=0, ly=0;
    addEventListener('pointerdown', e=>{ if(e.button===0){ arrastando=true; lx=e.clientX; ly=e.clientY; } });
    addEventListener('pointerup',   ()=>{ arrastando=false; });
    addEventListener('pointermove', e=>{
      if(!arrastando) return;
      eixo.yaw   -= (e.clientX-lx)*0.005;
      eixo.pitch  = Math.max(-1.4, Math.min(1.4, eixo.pitch - (e.clientY-ly)*0.004));
      lx=e.clientX; ly=e.clientY;
    });
    const teclas = Object.create(null);
    addEventListener('keydown', e=>{ teclas[e.code]=true; });
    addEventListener('keyup',   e=>{ teclas[e.code]=false; });
    setInterval(()=>{
      let f=0,l=0;
      if(teclas.KeyW||teclas.ArrowUp) f+=1;
      if(teclas.KeyS||teclas.ArrowDown) f-=1;
      if(teclas.KeyD||teclas.ArrowRight) l+=1;
      if(teclas.KeyA||teclas.ArrowLeft) l-=1;
      if(!f && !l) return;
      const v = (teclas.ShiftLeft?0.06:0.028);
      const cy=Math.cos(eixo.yaw), sy=Math.sin(eixo.yaw);
      eixo.x +=  (sy*f + cy*l)*v;
      eixo.z += (-cy*f + sy*l)*v;
    }, 16);
  }

  // ── as matrizes ────────────────────────────────────────────────────
  function matrizDoOlho(desloc){
    const cy=Math.cos(eixo.yaw), sy=Math.sin(eixo.yaw);
    const cp=Math.cos(eixo.pitch), sp=Math.sin(eixo.pitch);
    // rotacao yaw*pitch, coluna a coluna
    const r = [ cy, 0, -sy,   sy*sp, cp, cy*sp,   sy*cp, -sp, cy*cp ];
    const px = eixo.x + r[0]*desloc, py = eixo.alturaOlho + r[1]*desloc,
          pz = eixo.z + r[2]*desloc;
    return { r, p:[px,py,pz] };
  }
  function inversaDe(m){
    const r = m.r, p = m.p;
    const out = [ r[0],r[3],r[6],0,  r[1],r[4],r[7],0,  r[2],r[5],r[8],0, 0,0,0,1 ];
    out[12] = -(r[0]*p[0] + r[1]*p[1] + r[2]*p[2]);
    out[13] = -(r[3]*p[0] + r[4]*p[1] + r[5]*p[2]);
    out[14] = -(r[6]*p[0] + r[7]*p[1] + r[8]*p[2]);
    return out;
  }
  function projecao(fov, aspecto, perto, longe){
    const f = 1/Math.tan(fov/2);
    return [ f/aspecto,0,0,0, 0,f,0,0, 0,0,(longe+perto)/(perto-longe),-1,
             0,0,2*longe*perto/(perto-longe),0 ];
  }

  function poseDe(p){
    return { transform: { position:{x:p[0],y:p[1],z:p[2]},
                          matrix: new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, p[0],p[1],p[2],1]),
                          inverse: { matrix: new Float32Array(inversaDe({r:[1,0,0,0,1,0,0,0,1], p})) } } };
  }

  // ── o falso navigator.xr ───────────────────────────────────────────
  const canvas = () => document.getElementById('gl');

  class CamadaFalsa {
    constructor(sessao, gl){ this.gl = gl; this.framebuffer = null; }
    getViewport(vista){
      const c = canvas();
      return { x: vista.olho === 'left' ? 0 : Math.floor(c.width/2), y: 0,
               width: Math.floor(c.width/2), height: c.height };
    }
  }
  self.XRWebGLLayer = CamadaFalsa;
  self.XRRigidTransform = function(pos){ this.position = pos || {x:0,y:0,z:0}; };

  class SessaoFalsa {
    constructor(){
      this.enabledFeatures = ['viewer','local','local-floor','hand-tracking','webxr'];
      this.supportedFrameRates = new Float32Array([72, 90, 120]);
      this.inputSources = [
        { handedness:'left',  gripSpace:{i:0}, targetRaySpace:{i:0} },
        { handedness:'right', gripSpace:{i:1}, targetRaySpace:{i:1} },
      ];
      this.ouvintes = {};
      this.renderState = {};
    }
    updateRenderState(e){ Object.assign(this.renderState, e); }
    updateTargetFrameRate(){ return Promise.resolve(); }
    requestReferenceSpace(){
      return Promise.resolve({
        getOffsetReferenceSpace(){ return this; },
      });
    }
    addEventListener(n, f){ (this.ouvintes[n] = this.ouvintes[n] || []).push(f); }
    emitir(n, e){ for(const f of (this.ouvintes[n]||[])) f(e); }
    requestAnimationFrame(cb){
      return requestAnimationFrame(agora => cb(agora, new QuadroFalso(this)));
    }
    end(){
      sessaoViva = null;
      this.emitir('end', {});
      return Promise.resolve();
    }
  }

  class QuadroFalso {
    constructor(s){ this.session = s; this.detectedPlanes = null; }
    getViewerPose(){
      const c = canvas();
      const aspecto = (c.width/2) / c.height;
      const pj = projecao(75*Math.PI/180, aspecto, 0.05, 90);
      const views = [];
      for(const [olho, d] of [['left', -OLHOS/2], ['right', OLHOS/2]]){
        const m = matrizDoOlho(d);
        views.push({
          olho, eye: olho,
          projectionMatrix: new Float32Array(pj),
          transform: { position:{x:m.p[0],y:m.p[1],z:m.p[2]},
                       inverse:{ matrix: new Float32Array(inversaDe(m)) } },
        });
      }
      return { views, transform:{ position:{x:eixo.x, y:eixo.alturaOlho, z:eixo.z} } };
    }
    getPose(espaco){
      const m = maos[espaco && espaco.i ? 1 : 0];
      return poseDe([m.x, m.y, m.z]);
    }
    getJointPose(){ return null; }   // sem esqueleto: cai no punho, como no Quest sem maos
  }

  /* navigator.xr E SOMENTE-LEITURA. Atribuir direto nao da erro e nao faz
     nada -- a obra continuava vendo o navegador sem RM e o simulador
     inteiro ficava inerte. Definir a propriedade e o unico caminho. */
  const falso = {
    isSessionSupported(){ return Promise.resolve(true); },
    requestSession(){
      const s = new SessaoFalsa();
      sessaoViva = s;
      // o canvas vira dois olhos lado a lado
      const c = canvas();
      if(c){ c.width = innerWidth; c.height = innerHeight; }
      return Promise.resolve(s);
    },
  };
  Object.defineProperty(navigator, 'xr', { value: falso, configurable: true });

  /* makeXRCompatible TAMBEM PRECISA MENTIR.

     Num navegador sem aparelho de verdade, essa promessa nao resolve: o
     driver nao tem para onde tornar o contexto compativel. A obra ficava
     presa entre "sessao aberta" e "primeiro quadro" -- exatamente onde ela
     ficou presa no Quest de manha, e pelo mesmo motivo: uma promessa que
     nao volta.

     E o simulador reproduzir esse travamento nao ensina nada, porque a
     causa aqui e a falta do aparelho e nao a obra. */
  if(self.WebGLRenderingContext){
    WebGLRenderingContext.prototype.makeXRCompatible = function(){
      return Promise.resolve();
    };
  }

  /* O QUADRO COMECA COM ALFA ZERO, como no headset. E a linha mais
     importante deste arquivo: foi o alfa que fez o primeiro teste no Quest
     nao mostrar nada, e e o que nenhum teste em tela pega. */
  addEventListener('load', ()=>{
    porXadrez(); ligarCamera(); ligarMaos();
    const c = canvas();
    if(!c) return;
    const gl = c.getContext('webgl');
    if(!gl) return;
    const limparOriginal = gl.clear.bind(gl);
    gl.clear = function(mascara){
      if(sessaoViva) gl.clearColor(0,0,0,0);
      return limparOriginal(mascara);
    };
    const aviso = document.createElement('div');
    aviso.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:99;'
      + 'font:11px/1.5 ui-monospace,monospace;color:#9f8fbe;background:rgba(10,8,18,.72);'
      + 'padding:8px 11px;border-radius:4px;pointer-events:none;max-width:320px';
    aviso.innerHTML = '<b style="color:#c9a8ff">aparelho de mentira</b><br>'
      + 'arrastar: olhar &nbsp; W A S D: andar<br>'
      + 'mouse: mao direita &nbsp; Alt+mouse: esquerda<br>'
      + 'roda: aproximar a mao &nbsp; espaço: gatilho<br>'
      + '<span style="opacity:.7">o xadrez e onde a obra deixa passar</span>';
    document.body.appendChild(aviso);
  });
})();
