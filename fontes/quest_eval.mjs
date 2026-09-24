// Executa JavaScript dentro do navegador do Quest, pelo DevTools no cabo.
//
//   adb forward tcp:9222 localabstract:chrome_devtools_remote     (uma vez)
//   node fontes/quest_eval.mjs <trecho da url> '<expressao js>' [gesto]
//
// Exemplos:
//   node fontes/quest_eval.mjs localhost:8765 "raizes.onde()"
//   node fontes/quest_eval.mjs localhost:8765 "document.getElementById('bIniciar').click()" gesto
//   node fontes/quest_eval.mjs github.io "[...document.querySelectorAll('.portao-dica')].map(p=>p.textContent).join(' | ')"
//
// "gesto" faz o navegador tratar a chamada como toque humano: e o que deixa
// abrir a sessao de RM sem ninguem de capacete (20/09). A aba precisa estar
// na frente -- senao o WebXR responde SecurityError; para trazer:
//   curl -s http://localhost:9222/json/activate/<id da aba>
const [,, filtro, expr, gesto] = process.argv;
const tabs = await (await fetch('http://localhost:9222/json')).json();
const tab = tabs.find(t => t.type === 'page' && t.url.includes(filtro));
if (!tab) { console.error('aba nao achada:', filtro, tabs.map(t => t.url)); process.exit(1); }
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
ws.send(JSON.stringify({ id: 1, method: 'Runtime.evaluate',
  params: { expression: expr, returnByValue: true, awaitPromise: true, userGesture: gesto === 'gesto' } }));
const msg = await new Promise(r => ws.onmessage = e => r(JSON.parse(e.data)));
console.log(JSON.stringify(msg.result?.result?.value ?? msg, null, 1));
ws.close();
