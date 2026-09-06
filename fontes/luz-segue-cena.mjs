/**
 * A LUZ DA SALA SEGUINDO A OBRA.
 *
 * A lampada fisica do estande muda de cor junto com o cenario. Nao e
 * enfeite: o roteiro pede luz rasante de chao, e o chao real e a metade de
 * baixo da obra em realidade mista. Se ele fica azul quando a obra esta no
 * planeta agua, a sala inteira entra na cena — e o que a camera do headset
 * enxerga tambem muda, o que ajuda o rastreamento a nao se perder no escuro.
 *
 * COMO FUNCIONA. Esta ponte nao fala com a lampada: fala com o estudio do
 * Raizes v1, que ja sabe faze-lo, pela porta 8600. E le o cenario da nossa
 * obra pelo DevTools do proprio Quest, na porta 9222.
 *
 *      obra no headset  --(9222, CDP)-->  esta ponte  --(8600)-->  estudio  -->  lampada
 *
 * Nada do sistema do v1 e alterado: so se usa a API que ele ja expoe.
 *
 * ANTES DE RODAR
 *   1. o estudio no ar          (raizes-display: node estudio.mjs)
 *   2. a ponte do DevTools      adb forward tcp:9222 localabstract:chrome_devtools_remote
 *   3. a obra aberta no headset servida de localhost
 *
 * USO
 *   node fontes/luz-segue-cena.mjs
 *
 * As cores sao as mesmas da regua da partitura: cada cenario tem a sua, e
 * quem olha a sala de fora reconhece em que ponto da obra a pessoa esta.
 */

const ESTUDIO = process.env.ESTUDIO ?? 'http://localhost:8600';
const CDP     = process.env.CDP     ?? 'http://localhost:9222';
const PAUSA   = Number(process.env.PAUSA ?? 2000);

const COR_DA_CENA = {
  1: '#6fa0a8',   // a floresta — verde-azulado de agua parada
  2: '#9a8cd0',   // o sistema solar — o violeta do ceu cosmico
  3: '#d98aa8',   // o planeta rosa
  4: '#d0b088',   // o mundo de papel — luz de vela sobre papel velho
};

async function abaDaObra() {
  const alvos = await (await fetch(`${CDP}/json`, { signal: AbortSignal.timeout(4000) })).json();
  for (const t of alvos) {
    if (t.type !== 'page' || !t.webSocketDebuggerUrl) continue;
    if (!(t.url || '').includes('localhost:8765')) continue;
    // Ha abas de erro com a mesma URL: a boa e a que tem o controle.
    const ws = new WebSocket(t.webSocketDebuggerUrl);
    try { await new Promise((ok, ruim) => { ws.onopen = ok; ws.onerror = ruim; setTimeout(ruim, 4000); }); }
    catch { continue; }
    const tem = await perguntar(ws, `!!(window.raizes && window.raizes.onde)`);
    if (tem === true) return ws;
    try { ws.close(); } catch { /* nada */ }
  }
  return null;
}

let numero = 0;
function perguntar(ws, expressao) {
  return new Promise(res => {
    const meu = ++numero;
    const ouvir = e => {
      const m = JSON.parse(e.data);
      if (m.id === meu) { ws.removeEventListener('message', ouvir); res(m.result?.result?.value); }
    };
    ws.addEventListener('message', ouvir);
    ws.send(JSON.stringify({ id: meu, method: 'Runtime.evaluate',
                             params: { returnByValue: true, expression: expressao } }));
    setTimeout(() => res(undefined), 5000);
  });
}

async function pintar(cor) {
  const r = await fetch(`${ESTUDIO}/api/luz?acao=cor&v=${encodeURIComponent(cor)}`,
                        { signal: AbortSignal.timeout(6000) });
  return (await r.json())?.ok === true;
}

console.log('a luz segue a obra — Ctrl+C para parar');
let ws = null, ultima = null;

for (;;) {
  try {
    if (!ws) {
      ws = await abaDaObra();
      if (!ws) { console.log('  esperando a obra abrir no headset…'); await espera(4000); continue; }
      console.log('  ligada a obra');
      ultima = null;                       // ao reconectar, repinta
    }
    const onde = await perguntar(ws, `window.raizes.onde()`);
    if (!onde) { try { ws.close(); } catch { /* nada */ } ws = null; continue; }

    if (onde.cena !== ultima) {
      const cor = COR_DA_CENA[onde.cena];
      if (cor && await pintar(cor)) {
        console.log(`  ${onde.tempo}  cenario ${onde.cena}  ->  ${cor}`);
        ultima = onde.cena;
      }
    }
  } catch (e) {
    try { if (ws) ws.close(); } catch { /* nada */ }
    ws = null;
  }
  await espera(PAUSA);
}

function espera(ms) { return new Promise(r => setTimeout(r, ms)); }
