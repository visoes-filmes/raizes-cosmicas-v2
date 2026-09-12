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
 *   3. a obra aberta no headset -- pelo cabo (localhost:8765) ou a publicada
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

/* AS TRES JANELAS, E POR QUE A LUZ SOBE NELAS.
 *
 * O teste de 06/09 deu negativo: no escuro do estande o Quest NAO acha as
 * maos. Era o risco que o roteiro ja apontava como o maior do projeto, e
 * ele se confirmou.
 *
 * O rastreamento de mao e por visao: sem luz, nao ha o que ver. Mas a obra
 * precisa do escuro — e a saida nao e escolher entre os dois, e sim nao
 * precisar dos dois AO MESMO TEMPO. A obra so pede as maos em tres
 * momentos, somando pouco mais de dois minutos dos dez.
 *
 * Entao a luz sobe so nesses tres, e desce de volta. Nos outros oito
 * minutos a sala continua escura como a obra pede.
 *
 * Os tempos sao os do roteiro. Se a partitura mudar, mudam aqui tambem —
 * e e por isso que estao escritos com o nome do momento ao lado. */
const JANELAS = [
  { de: 110, ate: 170, o_que: 'os cogumelos, o casulo' },
  { de: 330, ate: 380, o_que: 'pegar e dimensionar um planeta' },
  { de: 450, ate: 505, o_que: 'os seres, as pedras, a concha' },
];
/* BRILHO E COR SAO UM COMANDO SO -- consertado em 12/09.

   A lampada tem dois modos, "white" e "colour", e o brilho (dps 22) so vale
   no branco: mandar brilho a trocava para BRANCO, e ela ficava branca ate a
   proxima mudanca de cenario. Era por isso que a luz "perdia" o cenario na
   primeira janela e nao voltava. Agora tudo vai pela cor: o matiz e o do
   cenario, e o escuro e o claro sao o VALOR dessa mesma cor. A lampada
   nunca sai do modo de cor. */
/* "TEM QUE TER COR" -- 12/09, olhando a lampada: a 40% de valor a cor
   nao se lia, e a saturacao afrouxada na janela virava branco lavado.
   Saturacao cheia sempre; o escuro a 60%. Se a camera nao achar as maos
   com luz colorida a 100%, o que cede e o valor do escuro, nao a cor. */
const VALOR_OBRA   = 0.60;   // o escuro da obra, ainda com cor
const VALOR_JANELA = 1.00;   // o que a camera precisa para achar uma mao

/* AS CORES, MEDIDAS -- 12/09, "a cor dominante de cada um, mais intensa".
   Medido na bancada em tres olhares por cenario (histograma de matiz dos
   pixels com cor e luz): floresta 220-240 graus (a noite azul da pintura,
   52-77%); cosmos 200-220 (o azul da galactica; vermelho e magenta atras);
   planeta rosa 320-340 (45-62%); papel 210-260 (o ceu cosmico invertido).

   Tres dos quatro medem azul. Para a sala MUDAR a cada cenario, olhando a
   lampada em 12/09: a floresta e verde-turquesa ("falta um verde
   turquesa"; a regua ja a chamava de verde-azulado), o cosmos e o violeta
   do ceu cosmico, o rosa e o magenta medido, e o papel fica com o azul
   medido -- o ambar de vela "nao combina". Saturacao cheia: o pedido e
   intensidade. */
const COR_DA_CENA = {
  1: { matiz: 170, nome: 'verde-turquesa' },  // a floresta: "falta um verde turquesa" (12/09); mede azul, mas e a floresta
  2: { matiz: 262, nome: 'violeta' },         // o cosmos, a assinatura da regua (medido: azul 215)
  3: { matiz: 350, nome: 'rosa-claro', sat: 0.50 },  // o planeta rosa: medido 335; "mais avermelhado" e "mais suave, para o branco" (12/09)
  4: { matiz: 230, nome: 'azul' },            // o mundo de papel, o azul-violeta medido (o ambar "nao combina")
};

function hsvParaHex(h, s, v) {
  const c = v * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = v - c;
  const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x]
                  : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return '#' + [r, g, b].map(q => Math.round((q + m) * 255).toString(16).padStart(2, '0')).join('');
}

async function abaDaObra() {
  const alvos = await (await fetch(`${CDP}/json`, { signal: AbortSignal.timeout(4000) })).json();
  for (const t of alvos) {
    if (t.type !== 'page' || !t.webSocketDebuggerUrl) continue;
    // a obra pelo cabo (localhost:8765) ou a publicada, que mora no aparelho
    const url = t.url || '';
    if (!url.includes('localhost:8765') && !url.includes('visoes-filmes.github.io/raizes-cosmicas-v2')) continue;
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

function emJanela(segundos) {
  return JANELAS.find(j => segundos >= j.de && segundos <= j.ate) || null;
}

function paraSegundos(mmss) {
  const [m, s] = String(mmss).split(':').map(Number);
  return (m || 0) * 60 + (s || 0);
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

    const segundos = paraSegundos(onde.tempo);
    // na espera do fim a sala ja se prepara para a proxima pessoa: a floresta
    const cena = segundos >= 600 ? 1 : onde.cena;
    const janela = emJanela(segundos);
    const chave = `${cena}/${janela ? 'janela' : 'escuro'}`;
    if (chave !== ultima) {
      const c = COR_DA_CENA[cena];
      // a saturacao e cheia, salvo onde a direcao de arte pediu mais suave (sat na tabela)
      const cor = c && hsvParaHex(c.matiz, c.sat ?? 1.0, janela ? VALOR_JANELA : VALOR_OBRA);
      if (cor && await pintar(cor)) {
        console.log(`  ${onde.tempo}  cenario ${cena}  ${c.nome}  ${cor}` +
                    (janela ? `  — janela: ${janela.o_que}` : '  — o escuro da obra'));
        ultima = chave;
      }
    }
  } catch (e) {
    try { if (ws) ws.close(); } catch { /* nada */ }
    ws = null;
  }
  await espera(PAUSA);
}

function espera(ms) { return new Promise(r => setTimeout(r, ms)); }
