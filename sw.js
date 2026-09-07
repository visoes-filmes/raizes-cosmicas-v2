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

const VERSAO = 'raizes-cosmicas-2026-09-07n';

/**
 * O que é baixado na instalação, sem esperar ninguém pedir.
 *
 * A obra inteira são 2,4 MB num arquivo só: as imagens e o som já vão
 * embutidos nele. Por isso a lista é curta — não há assets soltos a buscar.
 */
const ESSENCIAL = [
  './',
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
