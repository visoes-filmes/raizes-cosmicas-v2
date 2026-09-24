// Le o console do navegador do Quest (erros de GL, contexto perdido, avisos)
// pelo DevTools no cabo -- e o que achou o CONTEXT_LOST_WEBGL de 20/09.
//
//   adb forward tcp:9222 localabstract:chrome_devtools_remote
//   node fontes/quest_console.mjs <trecho da url> [segundos]
const [,, filtro, seg] = process.argv;
const tabs = await (await fetch('http://localhost:9222/json')).json();
const tab = tabs.find(t => t.type === 'page' && t.url.includes(filtro));
if (!tab) { console.error('aba nao achada:', filtro); process.exit(1); }
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
let id = 0; const send = (m, p = {}) => ws.send(JSON.stringify({ id: ++id, method: m, params: p }));
ws.onmessage = e => { const m = JSON.parse(e.data);
  if (m.method === 'Log.entryAdded') { const en = m.params.entry; if (!/_relato/.test(en.url || '')) console.log('[LOG]', en.level, (en.text || '').slice(0, 300)); }
  if (m.method === 'Runtime.consoleAPICalled') console.log('[CONSOLE]', m.params.type, m.params.args.map(a => a.value ?? a.description ?? '').join(' ').slice(0, 300));
  if (m.method === 'Runtime.exceptionThrown') { const d = m.params.exceptionDetails; console.log('[EXC]', d.text, d.exception?.description?.slice(0, 400)); }
};
send('Log.enable'); send('Runtime.enable');
await new Promise(r => setTimeout(r, (Number(seg) || 4) * 1000));
ws.close();
