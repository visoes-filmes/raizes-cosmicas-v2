/* eslint-env serviceworker */

/**
 * A OBRA GUARDADA NO APARELHO.
 *
 * Depois da primeira abertura, tudo o que a experiência precisa mora no
 * headset. Ela abre sem rede — e, o que importa mais na prática, abre
 * DEPRESSA e não trava no meio porque o wi-fi da feira oscilou.
 *
 * ESTRATÉGIA: cache primeiro, rede como reserva.
 *
 * Não é a escolha automática para um site, mas é a certa para este. Aqui não
 * há conteúdo que envelhece — nenhuma notícia, nenhum dado de visitante. O
 * que existe é uma versão inteira, que muda quando eu publico outra. Servir
 * do cache é servir o que já foi conferido.
 *
 * A TROCA DE VERSÃO é o nome do cache. Publicar uma versão nova cria um cache
 * novo, baixa tudo dentro dele, e só então apaga o antigo. Nunca existe um
 * momento em que metade da obra é de uma versão e metade de outra.
 */

const VERSAO = 'raizes-cosmicas-2026-09-10u';

/**
 * O que é baixado na instalação, sem esperar ninguém pedir.
 *
 * A obra inteira é UM arquivo — as imagens, os modelos e o som vão
 * embutidos nele. Por isso a lista é curta: não há assets soltos a buscar,
 * e guardar o index é guardar a obra.
 *
 * Ele tinha 2,4 MB quando isto foi escrito e hoje tem 8; com os céus em
 * 4096 vai a onze. O número não muda nada aqui, e é justamente esse o
 * ponto: numa rede local onze megabytes levam um segundo, e depois da
 * primeira abertura levam zero — a obra passa a morar no aparelho.
 */
/* UMA COPIA SO, e nao duas.
 *
 * Aqui havia './' E './index.html'. Sao endereços diferentes com o MESMO
 * corpo de oito megabytes, e o cache guardava os dois: dezesseis megabytes
 * para servir uma obra de oito.
 *
 * Isso não é só desperdício de espaço. Quanto maior a pegada da origem,
 * maior a chance de o navegador decidir despejá-la quando o aparelho
 * aperta — e despejar o cache é a única coisa que faz a obra parar de abrir
 * sem rede. Metade da pegada é metade do risco.
 *
 * Quem cobre o './' agora é o desvio de navegação no fetch, logo abaixo. */
const ESSENCIAL = [
  './index.html',
  './manifest.webmanifest',
  './icone-512.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(VERSAO)
      .then((c) => c.addAll(ESSENCIAL))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((nomes) => Promise.all(
        nomes.filter((n) => n !== VERSAO).map((n) => caches.delete(n)),
      ))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  /* QUALQUER NAVEGACAO NO ESCOPO E A OBRA.
   *
   * Abrir './', './index.html', './?v=2' ou o endereço com qualquer coisa
   * atrás dele é sempre pedir a mesma coisa — a obra é um arquivo só. Então
   * todas essas navegações são respondidas pela ÚNICA cópia guardada.
   *
   * É isto que permite guardar uma cópia em vez de uma por endereço, e é
   * isto que faz a obra abrir com o aparelho sem rede nenhuma: a navegação
   * nunca chega a consultar a rede, e por isso não importa que o DNS não
   * resolva. */
  if (req.mode === 'navigate') {
    e.respondWith(
      caches.match('./index.html').then((guardado) => guardado || fetch(req)),
    );
    return;
  }

  e.respondWith(
    caches.match(req).then((guardado) => {
      if (guardado) return guardado;

      return fetch(req).then((resposta) => {
        /* A fonte do Google vem de outro domínio e chega como resposta
           OPACA: não dá para ler o conteúdo nem o código de status. Guardo
           assim mesmo, porque uma fonte opaca guardada funciona; o que não
           pode é guardar erro de rede achando que é conteúdo. Por isso a
           resposta do próprio domínio só entra no cache se vier com 200. */
        const opaca = resposta.type === 'opaque';
        const boa = resposta.ok && resposta.status === 200;
        if (opaca || boa) {
          const copia = resposta.clone();
          caches.open(VERSAO).then((c) => c.put(req, copia)).catch(() => {});
        }
        return resposta;
      }).catch(() => caches.match('./index.html'));
    }),
  );
});
