# -*- coding: utf-8 -*-
"""72 e o alvo: pedido explicito ao headset, e o medidor medindo contra ele."""
import io, os
AQUI = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(AQUI, 'mr.template.html')
s = io.open(p, encoding='utf-8').read()


def troca(a, b):
    global s
    assert a in s, 'NAO ACHOU: ' + a[:80]
    s = s.replace(a, b, 1)


# ── 1. pedir 72 ao headset, em vez de aceitar o que vier ──────────────
troca("""  camadaXR = new XRWebGLLayer(sessao, gl, { antialias: true });
  sessao.updateRenderState({ baseLayer: camadaXR });""",
"""  camadaXR = new XRWebGLLayer(sessao, gl, { antialias: true });
  sessao.updateRenderState({ baseLayer: camadaXR });

  /* 72 E O ALVO, E AGORA E PEDIDO.

     O Quest 3 sabe rodar a 72, 90 e 120. Sem pedir nada, o navegador
     escolhe — e se ele escolher 90, a obra passa a ter 11 ms por quadro em
     vez de 13,9. Sao 25% a mais de trabalho para uma peca que nao ganha
     nada com isso: aqui ninguem corre, ninguem mira, nao ha nada rapido o
     bastante para 90 mostrar e 72 esconder.

     Pedindo 72 explicitamente, esses 25% viram folga — que e exatamente o
     que falta para a nuvem, a agua e as sete camadas de papel.

     E o silencio embaixo disso importa: se a obra nao chegar a 72, o
     compositor do headset ainda reposiciona o ultimo quadro desenhado para
     onde a cabeca esta no instante de mostrar. Chama-se timewarp, e sempre
     ligado, e nao depende de nos. Por isso cair de quadros aqui deixa a
     ANIMACAO aos trancos, mas nao faz o mundo escorregar junto com a
     cabeca — que e o que enjoaria. */
  try{
    const taxas = sessao.supportedFrameRates;
    if(taxas && sessao.updateTargetFrameRate){
      // a taxa suportada mais proxima de 72, sem supor que 72 exista
      let alvo = taxas[0];
      for(const t of taxas) if(Math.abs(t - 72) < Math.abs(alvo - 72)) alvo = t;
      await sessao.updateTargetFrameRate(alvo);
      TAXA_ALVO = alvo;
    }
  }catch(e){ /* navegador sem a extensao: fica no padrao dele, e tudo bem */ }""")


# ── 2. o medidor mede contra o alvo, nao contra um numero solto ───────
troca("""// Conta quadros em janelas de meio segundo. Meio segundo é curto o
// bastante pra reagir e longo o bastante pra o número não tremer.
const eFps = document.getElementById('fps');
let quadrosContados = 0, marcaFps = performance.now();
function contarQuadro(){
  quadrosContados++;
  const agora = performance.now(), dt = agora - marcaFps;
  if(dt >= 500){
    const f = Math.round(quadrosContados * 1000 / dt);
    eFps.textContent = f + ' fps';
    eFps.classList.toggle('baixo', f < 30);
    quadrosContados = 0; marcaFps = agora;
  }
}""",
"""/* O ALVO DA OBRA. No headset ele vira o que o aparelho confirmar; no
   computador fica em 72 mesmo, porque e contra o headset que se mede —
   um monitor de 60 nunca passaria disso, e isso nao diria nada. */
let TAXA_ALVO = 72;

// Conta quadros em janelas de meio segundo. Meio segundo é curto o
// bastante pra reagir e longo o bastante pra o número não tremer.
const eFps = document.getElementById('fps');
let quadrosContados = 0, marcaFps = performance.now();
function contarQuadro(){
  quadrosContados++;
  const agora = performance.now(), dt = agora - marcaFps;
  if(dt >= 500){
    const f = Math.round(quadrosContados * 1000 / dt);
    eFps.textContent = f + ' / ' + TAXA_ALVO;
    /* Duas faixas, e as duas dizem uma coisa concreta.

       ABAIXO DE METADE do alvo o timewarp deixa de disfarcar: o que se
       move ganha rastro visivel, porque o compositor esta mostrando o
       mesmo quadro duas vezes seguidas. E a linha em que a obra deixa de
       parecer inteira — nada a ver com passar mal, e tudo a ver com
       aparencia.

       ENTRE METADE E O ALVO ja se perde quadro, mas ainda passa. */
    eFps.classList.toggle('baixo', f < TAXA_ALVO * 0.5);
    eFps.classList.toggle('meio', f >= TAXA_ALVO * 0.5 && f < TAXA_ALVO - 4);
    quadrosContados = 0; marcaFps = agora;
  }
}""")


# ── 3. a cor do meio-termo ───────────────────────────────────────────
troca("  #fps.baixo{color:var(--ember);opacity:.85;}",
      """  #fps.meio{opacity:.55;}
  #fps.baixo{color:var(--ember);opacity:.85;}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('72 pedido ao headset, e o medidor medindo contra ele')
