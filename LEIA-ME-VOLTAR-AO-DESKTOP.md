# Voltar ao desktop — 24/09/2026, fim de tarde

O Lenovo ficou lento demais para esta rodada; o trabalho segue no desktop
("Unreal"). Este arquivo é o que o chat novo, aberto na pasta do projeto no
desktop, precisa ler **primeiro**. Depois dele, na ordem: `CLAUDE.md` (regras
e a tabela dos interruptores), `LEIA-ME-SEGUIR.md` (estado por versão, a
Cabine), `LEIA-ME-UNREAL.md` (o diário até 24/09 de manhã), `LEIA-ME-ACER.md`
(o mapa da obra).

---

## 1. O que existe agora (tudo no repositório, nada solto)

Último commit: `39f1473`. Marcas: `v2.0`, `v4.0`, `v5.0`, `v5.1`, `v5.2`,
`v6.0`. Endereço base: `visoes-filmes.github.io/raizes-cosmicas-v2/`.

| versão | arquivo | o que é |
|---|---|---|
| v2 | `index.html` | a obra base |
| v4 | `v4.html` | lê o espaço (cogumelos em mesa, mãe procura chão livre) |
| 5.1 | `v5.html` | paredes rachadas — **descartada pela direção de arte** (o chão ficou preto) |
| **5.2** | `v52.html` | um passo atrás: sem escaneamento, céu em *fade* com as paredes reais, **chão visível** até o cenário 4; névoa 0,5; escala 0,7 |
| **6.0** | `v6.html` | a 5.2 + **a tela de tule**: o óculos reconhece a tela real e lê o toque; o vídeo "Odara - Cosmos" é **projetado** no tule pela `projecao.html` e ondula a cada toque. **Invisível dentro do óculos** (decisão dela: "o vídeo já vai ser visto na realidade") |

Todas saem do mesmo `fontes/mr.template.html` por interruptores que o
`fontes/montar_mr.py` liga. **Nada visto no Quest desde a 5.2** — o Quest
ficou "unauthorized" o dia inteiro (ver §4).

**As regras que ela deu hoje:**
- só RA **do teto para cima**; **ver o chão é o mais importante** (a pessoa
  caminha); chão preto só no final (cenário 4, 8:45 em diante);
- a tela de tule **não aparece no óculos**; a tela tem de ser **reconhecida**
  para o toque fazer o vídeo projetado reagir como água;
- o projetor agora é um **ViewSonic laser Full HD, 5.000 lúmens** (16:9);
- cada rodada grande ganha número e marca antes de começar (próxima: ela
  nomeia); tudo vai para o repositório na hora.

## 2. Trazer para o desktop

O desktop já tem a pasta (`Downloads\Raizes Cósmicas`, com `.git`). Basta:

```bash
git pull --tags origin main
python fontes/verificar.py        # "nada a corrigir"
python fontes/montar_mr.py        # escreve index, v4, v5, v52, v6, projecao.html, oficina, simulador
```

O que veio novo de arquivo (24/09): `fontes/cabine.py`, `fontes/cabine.html`,
`fontes/cabine.ico`, `fontes/hotspot.ps1`, `fontes/projecao.template.html`,
`assets/video/odara-cosmos.mp4` (70 MB — o `git pull` demora um pouco),
`v52.html`, `v6.html`, `projecao.html`, `fotos/2026-09-23-24/`,
`fontes/quest_eval.mjs`, `quest_console.mjs`, `medir_quadros.sh`.

**Fora do git, por máquina:** `fontes/platform-tools/` (o adb — o desktop
já tinha? conferir com `python fontes/estande.py`), `fontes/*.log`,
`fontes/guardiao_quest.ip`, `_dev*.html`, `_fotos/`. O scrcpy (espelho do
Quest) se instala com `winget install Genymobile.scrcpy`.

## 3. A Cabine — o computador do estande

```bash
python fontes/cabine.py           # obra em 8765 (modo estande) + página de controle em localhost:8790
```

No Lenovo há um atalho na área de trabalho ("Raízes Cósmicas - Cabine",
`pythonw fontes\cabine.py`, ícone `fontes\cabine.ico`). **No desktop o atalho
ainda não existe**: criar igual (alvo `pythonw.exe "<pasta>\fontes\cabine.py"`,
pasta de trabalho = a do projeto).

O que ela faz, em cards, com o roteiro numerado na própria tela:
1. **Rede interna** — liga o Ponto de Acesso Móvel do Windows
   (`fontes/hotspot.ps1`, WinRT). Nome e senha aparecem na página; o Quest
   entra nela e ganha `192.168.137.x`. Exige alguma conexão de pé no PC
   (Wi-Fi, cabo ou o modem 4G), não internet. **No desktop, conferir se a
   placa Wi-Fi dele aceita hotspot** (`hotspot.ps1 status`).
2. **Quest** — acha pelo cabo ou pela Wi-Fi; ao ver o Quest no cabo, refaz
   os túneis (8765 obra, 9222 DevTools) e libera a Wi-Fi (`adb tcpip 5555`
   + `connect`), guardando o ip em `guardiao_quest.ip`. Botões: Liberar
   Wi-Fi, Conectar pela Wi-Fi, Refazer túneis, Ficar acordado na mesa,
   Espelhar na tela (scrcpy), Desconectar.
3. **Obra** — abrir 6.0 / 5.2 / v2 / v4 / 5.1 / oficina no navegador do
   Quest; **Iniciar em RM** com gesto pelo DevTools (`quest_eval.mjs`);
   Reiniciar, Encerrar, Recarregar, saltar de cena. Leitura ao vivo: cena e
   segundo (`raizes.onde()`), quadros/72 (`VrApi`), bateria, 18/18 programas
   do portão, versão.
4. **Projeção · tela de tule (6.0)** — escolhe **o que o projetor mostra**
   ("tela: desenho + água" = `projecao.html` em quiosque no monitor
   escolhido; ou "espelho do óculos" = scrcpy tela cheia), "espelhar" para
   retroprojeção, Projetar / Parar. Botões da tela (falam com a obra pelo
   DevTools, `raizes.tela.*`): **Cravar pelos cantos**, Acender / Seguir a
   partitura / Apagar, Toque de teste, Ditar tela (teste), Ver no óculos
   (só para conferir o encaixe), Soltar.
5. **Relatos** de dentro do capacete, ao vivo; `/eventos` (Server-Sent
   Events) leva os mesmos relatos à página de projeção.

Registro em `fontes/cabine.log`. Segundo clique no atalho só reabre a página.

## 4. O Quest — o que aconteceu hoje e o que fazer

- Ele **autorizou e perdeu a autorização**: a caixa "Permitir depuração
  USB" foi aceita **sem** "Sempre permitir deste computador", e o
  `adb tcpip 5555` (que a Cabine roda ao ver o Quest no cabo) reinicia o adb
  do óculos — voltou a `unauthorized` no cabo **e** na Wi-Fi. **Aceitar de
  novo, marcando a caixinha.** No desktop a autorização é outra (é por
  computador): vai pedir de novo lá.
- Serial: `2G0YC1ZG2307ZW`. Em casa ele fica na Wi-Fi "Plinio 2.4G"
  (`192.168.15.157`).
- Ligar/desligar o hotspot derrubou a Wi-Fi do Lenovo uma vez;
  `netsh wlan connect name="Plinio 2.4G"` religou. No dia: ligar a rede
  antes de tudo e não mexer mais.
- Continua valendo tudo do `LEIA-ME-SEGUIR.md` §5 (Link toma o cabo, aba
  atrás, cache velho, ficar acordado na mesa).

## 5. A 6.0 por dentro (para mexer)

- Interruptores no alto do template: `TELA_DE_TULE` (v6 liga),
  `TELA_VISIVEL` (v6 desliga), `TELA_LARGURA`/`TELA_ALTURA` (3 × 2 m quando
  cravada pelos cantos ou ditada), `TELA_QUANDO` (`'cosmos'` = 3:06–6:32;
  `'papel'`; `'sempre'`), `TELA_VIDEO`.
- Módulo antes de `let bParede`: `TELA`, `cravarTela`, `montarTela`,
  `lerATela` (só planos verticais com `semanticLabel` tela/janela/quadro; o
  maior), `cravarPelosCantos` (dois beliscões: canto de cima à esquerda,
  depois à direita), `presencaDaTela`, `atualizarTela` (vídeo só quando
  visível), `ondaNaTela`, `tocarATela` (ponta do dedo a < 8 cm do plano,
  dentro do retângulo; arrastando, onda a cada 10 cm, máx. 8/s por mão;
  relato `TOCOU-A-TELA u v forca`).
- Shaders `VS_TELA`/`FS_TELA` antes de `progParede`; desenho logo depois
  das paredes (bloco "1c"). As ondas são **soma de anéis** por (u, v,
  instante, força) — sem simulação em textura, para a `projecao.html`
  (gerada de `fontes/projecao.template.html` com o **mesmo** `FS_TELA`
  colado pelo montador) fazer a mesma conta a partir dos relatos.
- Ganchos: `raizes.tela.onde() / cravar() / ditar({largura, altura, rumo,
  centro}) / mostrar(true|false|null) / toque(u, v, f) / ver(b) / soltar()`.
- Relatos novos: `TELA-CRAVADA`, `TELA-CANTO n`, `TELA-NAO-ACHADA`,
  `TELA-ACESA`/`TELA-APAGADA`, `TELA-VIDEO`, `TOCOU-A-TELA`.
- Provado na bancada (`_dev6.html` = `_dev.html` com `TELA_DE_TULE = true`):
  tela ditada no cosmos, vídeo rodando, toque virando anéis; escondida, o
  toque continua nascendo onda e sendo relatado; a `projecao.html` recebe o
  toque de teste pela Cabine. Foto: `_fotos/60-tela-cosmos-toque.jpg` (no
  Lenovo; refaz-se).
- **A `projecao.html` não anima no navegador interno do Claude** (o
  `requestAnimationFrame` não dispara ali, o mesmo motivo da bancada trocar
  o relógio); no Chrome de verdade anima.

## 6. Em aberto — o roteiro do teste no desktop

1. Quest autorizado **com "sempre permitir"**.
2. Cabine → Abrir no Quest (6.0) → Iniciar em RM. Ler no portão: versão e
   18/18… agora são **20 programas** (dois da tela); o portão diz quantos
   linkaram no aparelho.
3. **Ver a 5.2 no capacete**: o chão real aparece? o céu faz *fade* com as
   paredes? (é a prova que a bancada não consegue dar).
4. **Cravar a tela**: primeiro tentar a Configuração de Espaço do Quest com
   a tela marcada como "Tela/Janela" (relato `TELA-CRAVADA espaco:…`); senão,
   Cabine → Cravar pelos cantos. Conferir o encaixe com "Ver no óculos" e
   desligar depois.
5. **Tocar o tule** de capacete com a `projecao.html` aberta (numa aba
   mesmo, F = tela cheia): a onda tem de nascer onde a mão tocou. Medir o
   atraso a olho; se passar de meio segundo, é a rede.
6. Projetor de verdade: monitor no card de projeção, "espelhar" se for
   retroprojeção. Tule 3 × 2 m (3:2) em projetor 16:9: a página deixa barras
   pretas dos lados sozinha. Confirmar as medidas reais do tule com ela.
7. O relato dela da **interatividade** (casulo, concha, rosa) segue pendente
   desde a 5.1.
8. `sw.js` só guarda o `index.html`: sem rede, `v6.html`/`projecao.html`
   não abrem do cache — no estande a obra é servida pela Cabine (localhost
   pelo túnel), então isso não pesa; pesa se algum dia a 6.0 for à feira
   pelo endereço publicado.
9. Repositórios próprios `raizes-cosmicas-v4/-v5`, grama/solo na mesa,
   licenças: como estavam no `LEIA-ME-SEGUIR.md` §6.

Se algo aqui não bater com o código, **o código manda** — e este arquivo é
que precisa ser corrigido.
