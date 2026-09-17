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
 *   node fontes/luz-segue-cena.mjs            segue a obra; sem obra, deriva
 *   node fontes/luz-segue-cena.mjs deriva     so a deriva, sem procurar a obra
 *
 * As cores sao as mesmas da regua da partitura: cada cenario tem a sua, e
 * quem olha a sala de fora reconhece em que ponto da obra a pessoa esta.
 *
 * A LUZ NUNCA SALTA, E SEM A OBRA ELA DERIVA -- 17/09, "voce consegue
 * colocar ela mudando de cor lentamente, como uma alternativa?" (a Alexa
 * tinha se desligado da lampada). Duas coisas:
 *
 *   - toda mudanca e um DESLIZE: a cor atual anda para a cor pedida um
 *     pouco por passo (a cada 3 s, que e o que a lampada leva para
 *     responder pelo caminho local). Seguindo a obra, a troca de cenario
 *     leva uns 8 s, como a travessia do ceu; a luz das janelas sobe em 6 s.
 *   - sem obra ao alcance (o headset ainda nao abriu, ou o modo "deriva"),
 *     a lampada passeia pelas quatro cores da partitura, na ordem dela,
 *     devagar: meio grau de matiz por segundo, meio minuto parada em cada
 *     cor -- uma volta inteira leva uns catorze minutos. E a sala viva
 *     antes de alguem entrar, e a lampada de casa sem a Alexa.
 */

const ESTUDIO = process.env.ESTUDIO ?? 'http://localhost:8600';
const CDP     = process.env.CDP     ?? 'http://localhost:9222';
const PASSO   = Number(process.env.PASSO ?? 3000);      // ms entre dois comandos a lampada
const MODO    = process.argv[2] === 'deriva' ? 'deriva' : 'segue';

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

/* O DESLIZE. A cor atual (h, s, v) anda para o alvo um tanto por passo, e
   no matiz pelo caminho mais curto da roda. As taxas sao por passo de 3 s:
   seguindo a obra, 12 graus (um cenario para o outro em uns 8 s) e o valor
   em dois passos (a janela das maos nao pode esperar); na deriva, um grau e
   meio -- meio grau por segundo, que e o "lentamente". */
const TAXA = {
  segue:  { h: 12,  s: 0.12, v: 0.35 },
  deriva: { h: 1.5, s: 0.02, v: 0.05 },
};
function deslizar(de, para, taxa) {
  const passo = (a, b, max) => a + Math.max(-max, Math.min(max, b - a));
  let dh = ((para.h - de.h + 540) % 360) - 180;          // -180..180: o caminho curto
  dh = Math.max(-taxa.h, Math.min(taxa.h, dh));
  return { h: (de.h + dh + 360) % 360, s: passo(de.s, para.s, taxa.s), v: passo(de.v, para.v, taxa.v) };
}
const chegou = (a, b) => Math.abs(((a.h - b.h + 540) % 360) - 180) < 0.01
                      && Math.abs(a.s - b.s) < 0.001 && Math.abs(a.v - b.v) < 0.001;
const corDe = (n, v) => { const c = COR_DA_CENA[n]; return { h: c.matiz, s: c.sat ?? 1.0, v }; };

/* A DERIVA: as quatro cores na ordem da partitura, e uma parada em cada.
   O valor e o escuro da obra; em casa, VALOR=0.9 clareia. */
const VOLTA  = [1, 2, 3, 4];
const PARADA = 30000;           // ms parada em cada cor
const VALOR_DERIVA = Number(process.env.VALOR ?? VALOR_OBRA);
let voltaI = 0, paradaAte = 0;
function alvoDaDeriva(luz) {
  const alvo = corDe(VOLTA[voltaI], VALOR_DERIVA);
  if (luz && chegou(luz, alvo)) {
    if (!paradaAte) paradaAte = Date.now() + PARADA;
    else if (Date.now() >= paradaAte) { paradaAte = 0; voltaI = (voltaI + 1) % VOLTA.length; }
  }
  return { alvo: corDe(VOLTA[voltaI], VALOR_DERIVA),
           nome: `deriva: ${COR_DA_CENA[VOLTA[voltaI]].nome}` };
}

console.log(MODO === 'deriva' ? 'a luz deriva pelas cores da obra — Ctrl+C para parar'
                              : 'a luz segue a obra (e deriva enquanto ela nao abre) — Ctrl+C para parar');
let ws = null, luz = null, ultimoNome = null;

for (;;) {
  let pedido = null;                       // { alvo, nome }, de onde vier
  if (MODO === 'segue') {
    try {
      if (!ws) {
        ws = await abaDaObra();
        if (ws) console.log('  ligada a obra');
      }
      if (ws) {
        const onde = await perguntar(ws, `window.raizes.onde()`);
        if (!onde) { try { ws.close(); } catch { /* nada */ } ws = null; }
        else {
          const segundos = paraSegundos(onde.tempo);
          // na espera do fim a sala ja se prepara para a proxima pessoa: a floresta
          const cena = segundos >= 600 ? 1 : onde.cena;
          const janela = emJanela(segundos);
          if (COR_DA_CENA[cena]) pedido = {
            alvo: corDe(cena, janela ? VALOR_JANELA : VALOR_OBRA),
            nome: `${onde.tempo}  cenario ${cena}  ${COR_DA_CENA[cena].nome}` +
                  (janela ? `  — janela: ${janela.o_que}` : '  — o escuro da obra'),
          };
        }
      }
    } catch {
      try { if (ws) ws.close(); } catch { /* nada */ }
      ws = null;
    }
  }
  if (!pedido) pedido = alvoDaDeriva(luz);

  if (pedido.nome !== ultimoNome) { console.log('  ' + pedido.nome); ultimoNome = pedido.nome; }
  // o primeiro comando vai direto: nao ha de onde deslizar
  const proxima = luz ? deslizar(luz, pedido.alvo, TAXA[ws ? 'segue' : 'deriva']) : pedido.alvo;
  if (!luz || !chegou(luz, proxima)) {
    const cor = hsvParaHex(proxima.h, proxima.s, proxima.v);
    try { if (await pintar(cor)) luz = proxima; }
    catch { /* o estudio caiu ou a lampada nao respondeu: tenta no proximo passo */ }
  }
  await espera(PASSO);
}

function espera(ms) { return new Promise(r => setTimeout(r, ms)); }
