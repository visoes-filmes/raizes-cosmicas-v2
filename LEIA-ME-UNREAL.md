# Seguir no desktop (o computador "Unreal") — 19/09/2026

Este arquivo existe para a produção mudar de máquina sem perder nada:
o que instalar, o que trazer, como o trabalho funcionou até aqui, em que
estado a obra está hoje e o que está em aberto. Entrega: **22/09**.

Ele **não substitui** os outros dois — completa:

| arquivo | o que é |
|---|---|
| `CLAUDE.md` | as regras da casa, curtas, que não podem ser esquecidas nem por um minuto |
| `LEIA-ME-ACER.md` | o mapa completo da obra: a pasta arquivo por arquivo, a partitura, os quatro cenários, os shaders, as armadilhas, o que falta |
| **este** | a mudança de máquina + o estado de 19/09 + o jeito de trabalhar que a direção de arte pediu |

Um chat novo do Claude Code aberto **na pasta do projeto** lê o `CLAUDE.md`
sozinho. Peça a ele para ler o `LEIA-ME-ACER.md` e este arquivo antes de
mexer no código de verdade.

---

## 1. O que instalar no desktop

| o quê | para quê | como conferir |
|---|---|---|
| **Git** | trazer o repositório e publicar | `git --version` |
| **Python 3** (aqui é o 3.14) | verificar, montar, publicar, servir, bancada | `python --version` |
| **Pillow** | o montador mexe nas imagens; a bancada monta folhas de contato e GIFs | `pip install Pillow` |
| **Node.js** (aqui é o 24) | o verificador confere a sintaxe de cada `<script>` com `node --check`; a ponte da lâmpada; o estúdio do v1 | `node --version` |
| **Chrome** (ou Edge) | ver a obra na tela, a bancada, o `_prova.html` | — |
| **adb** (`platform-tools`) | testar no Quest pelo cabo | larga a pasta em `fontes/platform-tools/`; o `estande.py` diz o caminho se não achar |
| **tinytuya** | a lâmpada, pelo caminho local (é o estúdio do v1 que usa) | `pip install tinytuya` |
| **Claude Code** (o app) | o trabalho | abrir na pasta `Raizes Cósmicas` |

O login do GitHub é pedido na primeira vez que se empurra algo: conta
**Crisia-poria**, owner da organização `visoes-filmes`. O Git abre o
navegador para isso (Git Credential Manager) — não há senha para digitar no
terminal.

No Quest, uma vez: **modo de desenvolvedor ligado** (app Meta Horizon →
headset → configurações de desenvolvedor). Sem isso o `adb` não vê o
aparelho.

---

## 2. Trazer o projeto

**O jeito certo é clonar** — tudo o que a obra precisa para existir, ser
montada e publicada está no repositório, com o histórico inteiro:

```bash
git clone https://github.com/visoes-filmes/raizes-cosmicas-v2.git "Raizes Cósmicas"
```

**O ZIP no Drive** (`raizes-cosmicas-v2-completo-2026-09-19.zip`) tem o
mesmo repositório (com o `.git`) **mais o que nunca esteve nele**:

| pasta no ZIP | o que é | onde colocar no desktop |
|---|---|---|
| `Raizes Cósmicas/` | o projeto, com `.git` — dá para `git pull` e publicar direto dela | `Downloads\Raizes Cósmicas` (o nome com acento é o que está no `bancada.py` do ateliê antigo; o resto não depende do nome) |
| `raizes-display/` | **o estúdio do v1**: `node estudio.mjs` (porta 8600) é quem fala com a lâmpada do estande; `lampada/config.json` tem as chaves da lâmpada (**não compartilhe o ZIP fora da equipe**) | `Downloads\claude\raizes-display` |
| `Modelos 3D/` | os `.glb` de origem (algas, corais, cogumelos, a planta alienígena, o ser, a mão cósmica…). A obra **não** precisa deles para rodar — já estão assados em `fontes/nuvens.js`. Só para **converter um modelo novo** (`fontes/modelos_em_pontos.py`) | `Downloads\Visões filmes\Modelos 3D`, ou qualquer lugar com `MODELOS=<pasta>` no ambiente |

Ficaram de fora do ZIP, de propósito: `_fotos/` (700 MB de renders da
bancada — se refazem), `_dev.html`, `_prova.html`, `nova.html`,
`oficina.html`, `simulador.html` (o montador refaz todos), e as gravações e
capturas do estúdio do v1.

**Depois de trazer, confira que a máquina monta:**

```bash
python fontes/verificar.py
python fontes/montar_mr.py
```

Tem que dizer `nada a corrigir` e escrever `index.html`, `nova.html`,
`oficina.html`, `simulador.html` com uma versão de cache nova
(`raizes-cosmicas-2026-09-19a`, por exemplo). **Não publique só por ter
montado** — publicar é o passo 4 abaixo, e só quando algo mudou.

---

## 3. O ciclo de trabalho, como funcionou até aqui

### Editar

Só em `fontes/mr.template.html` (e `fontes/montar_mr.py` quando o montador
precisa mudar). Nunca no `index.html`. A regra do `gl.blendFunc` cru (só
`sobrepor()` e `somarLuz()`) está no `CLAUDE.md`, e o verificador a cobra.

O jeito que deu certo para mudanças grandes: um script Python de remendo
que troca trechos **exatos** do template (`s.count(trecho) == 1` antes de
trocar — se o trecho aparece duas vezes ou nenhuma, para). Os remendos
desta semana moram no scratchpad do Claude (não no repositório) e já foram
aplicados; a receita é o que vale, não os arquivos.

### Verificar e montar

```bash
python fontes/verificar.py        # estático: as armadilhas que já quebraram a obra, mais node --check
python fontes/provar_shaders.py   # escreve _prova.html: abrir na bancada; compila e linka os 18 programas de verdade
python fontes/montar_mr.py        # gera index.html + cópias, gira a versão do cache
```

O montador, **neste Windows, roda pelo PowerShell** (o caminho com acento
"Raízes Cósmicas" engasga no bash em alguns comandos). O `verificar.py` e o
`publicar.py` rodam de qualquer um.

### Olhar (a bancada)

Nada se decide sem olhar. A bancada é a obra na tela, com o relógio trocado
e ganchos para pôr o olho onde se quiser e tirar fotos de dentro do WebGL:

```bash
python fontes/montar_mr.py
python fontes/bancada.py            # escreve _dev.html a partir do nova.html
python fontes/servir.py 8791        # num terminal à parte; fica no ar. Aqui foi preciso
                                    # subi-lo "solto" (Start-Process, no PowerShell) para
                                    # não morrer junto com o comando que o chamou
```

Abrir `http://localhost:8791/_dev.html` numa **viewport de 1600 × 900**,
clicar em **Iniciar**, e no console (ou por uma ferramenta que execute JS
na página):

```js
const src = await (await fetch('/fontes/bancada.js')).text();
await (new (Object.getPrototypeOf(async function(){}).constructor)(src))();
raizes.ir(470);                          // salta na partitura (segundos); raizes.onde() diz onde está
for(let i=0;i<8;i++) __frame();          // deixa os alvos suaves assentarem
P.mvp = paraDe(1.6, 0, -10, 75);         // olho a 1,6 m; azimute 0 (a frente); 10° para baixo; lente de 75°
__frame(); __fotoRapida('nome.jpg');     // cai em _fotos/nome.jpg pelo servir.py
```

- **em pé** é `paraDe(1.6, …)`; **agachado/mergulhando** no planeta rosa é
  `paraDe(0.5, …)` — o gancho `__olhoY` faz a obra saber a altura (lâmina,
  véu, azul);
- **GIF**: uma foto a cada 600 ms (`await new Promise(r => setTimeout(r, 600))`
  entre elas — a obra continua correndo pelo relógio), 10–12 quadros, e
  a Pillow monta (`save_all=True, duration=600`), 900 × 506 para mandar;
- **folha de contato**: várias vistas coladas lado a lado com a Pillow, com
  o rótulo de cada uma. É o que a direção de arte julga;
- **medir** antes de decidir: média de pixels de uma região, diferença entre
  dois quadros, alturas de modelo pelos ganchos (`__malha('alga-c-0')`),
  contagem de triângulos em `raizes.onde()`;
- `__FIGURAS[1].tam = […]` muda a deusa vermelha ao vivo (as deusas são
  lidas por quadro), e assim se fez a comparação de proporção de 17/09.

A regra de ouro: **o que se vê na tela não prova nada sobre o headset.** Todo
relato termina com "nada visto no Quest" enquanto for verdade.

### Publicar

```bash
python fontes/publicar.py "o que mudou, na língua da casa"
```

Um comando: verifica, marca a versão que está no ar (`publicado-<versão>`),
monta, commita, empurra. A mensagem de commit termina com a linha

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

(no PowerShell, a mensagem de várias linhas vai numa here-string `@'…'@`).
Mudança que não toca a obra (só documentação, só a ponte da lâmpada) vai
por `git commit` + `git push` direto, sem girar a versão do cache.

**A versão do cache é o nome que o headset pede.** Depois de publicar, o
aparelho pode levar um minuto para ver a nova; um aparelho carregado antes
continua com a anterior até recarregar.

### Testar no Quest

```bash
python fontes/estande.py            # adb reverse: no headset, http://localhost:8765
```

No navegador do Quest, `localhost:8765` — e `localhost:8765/oficina.html`
para ver o **contador de quadros** (`68 / 72`) dentro do capacete. Os
relatos da obra (`>>` no terminal) dizem o que aconteceu lá dentro: `RM-ABRIU`,
`MAO-0 apareceu`, `TOCOU-A-CONCHA`, `PEGOU-O-ROSA`… **Feche o Meta Quest
Link antes**: ele disputa o cabo e derruba o `adb`.

### A lâmpada do estande

```bash
cd ..\claude\raizes-display && node estudio.mjs     # o estúdio do v1, porta 8600 (fala com a lâmpada)
node fontes/luz-segue-cena.mjs                      # segue o cenário da obra no headset; sem obra, deriva
node fontes/luz-segue-cena.mjs deriva               # só a deriva pelas quatro cores (em casa, sem headset)
```

A ponte lê o cenário pelo DevTools do Quest
(`adb forward tcp:9222 localabstract:chrome_devtools_remote`). Detalhes,
cores e o defeito do modo branco: `LEIA-ME-ACER.md`, "A lâmpada da sala".
A Alexa se desligou da lâmpada em 17/09; o vínculo só se refaz no app da
Alexa (skill do app onde a lâmpada foi cadastrada), com a conta da Crisia.
**Não reinicie a lâmpada** (liga-desliga 5×): troca a chave local e a ponte
para de falar com ela; se acontecer, `node lampada/nuvem.mjs` recupera.

### Documentos

Relatórios e tabelas vão para o **Google Drive**. O de 12/09 está em
`docs.google.com/document/d/1-CZem709TxKzCLwfnSp77nyzTVtkvLE8JuoydNNh0xo`;
o de 18/09 foi entregue como arquivo (`_fotos/2026-09-18 pendencias e
melhorias.html`) porque o conector do Drive estava só com leitura — vale
reconectar o Google Drive nas configurações do claude.ai com permissão de
escrita.

---

## 4. Como a direção de arte trabalha — o que ela pediu e o que aprendi

Isto não está no código e é o que mais custa perder numa mudança de chat.

- **Ela dita por voz.** As mensagens vêm com erros de transcrição
  ("comtinuarmos", "aerrilhadoa"). Ler pelo sentido, nunca corrigir.
- **Medir antes de decidir, e mostrar.** Toda rodada termina com uma folha de
  contato ou um GIF da bancada, mandados como arquivo, e um texto curto do
  que mudou, com números (metros, graus, segundos, triângulos). Ela julga
  pela imagem.
- **Nada visto no Quest** — dizer sempre, enquanto for verdade. Ela sabe que
  o passthrough é outro ambiente.
- **Ler os rabiscos com cuidado.** Em 14/09 ela circulou três coisas numa
  foto; uma bola foi aumentada por leitura errada de um círculo, e ela
  disse "não entendi o que é essa bola" — foi removida. Quando um círculo
  estiver ambíguo, perguntar custa menos do que fazer.
- **Antes de apagar o que ela pediu uma vez, perguntar.** "Retirar as
  partículas excessivas" virou, no minuto seguinte, "não é pra apagar os
  seres, é pra não fazer como partículas".
- **O vocabulário dela não é o do código** (tabela no `CLAUDE.md`): neblina
  marmorizada ≠ nuvem de pontos; um bicho, um corpo, um planeta é
  **superfície**; partícula só quando ela pede a palavra.
- **"Mais suave", "tirar ruídos e serrilhados", "menos opacidade"** são
  pedidos recorrentes: as bordas dos corpos se desfazem (`deFrente` no
  `FS_SOLIDA`), os planetas têm a silhueta suavizada, as pinturas têm beira
  de nuvem. O que entrar de novo entra já assim.
- **Movimento lento e orgânico**, sempre: a corrente das algas (15 s por
  volta), o nadar das águas-vivas (impulso e descida lenta), o ser de vidro
  ondulando como bolha e andando, a integra com o líquido e as asas, a
  lâmpada deslizando de cor. "Movimento que se vê denuncia o bicho".
- **Código enxuto**: apagar o que foi substituído, comentário diz o porquê e
  com as palavras dela (a data e a frase do pedido), nada de andaime para
  quem visita.
- **Ela decide; eu proponho.** Quando algo é escolha dela (proporção,
  cor, se a água sobe), mostrar as opções em imagem e esperar. Quando ela
  repete um pedido depois de uma ressalva minha, é decisão: fazer.
- **Ela não tem o Acer/desktop na mão quando fala comigo daqui**: "faça as
  mudanças no Acer" quer dizer "publique, que lá eu puxo".

---

## 5. O estado da obra em 19/09

No ar: **`raizes-cosmicas-2026-09-15b`** em
`visoes-filmes.github.io/raizes-cosmicas-v2/`. Último commit da obra
`437df9e` (a corrente); depois dele só documentação e a ponte da lâmpada.

### Os quatro cenários, em uma linha cada

1. **Floresta (0:00–3:16)** — a queda das estrelas, o nascimento (grama,
   cogumelo, a árvore-mãe), a janela do casulo (1:50–2:50), a borboleta
   sobe. Mata sólida (`MATA_SOLIDA`), 11 pedras, 13 cogumelos. Toque: mãe,
   cogumelos, casulo, borboleta.
2. **Cosmos (3:16–6:30)** — só planetas, o Sol, luas, o buraco negro no
   chão, os seres de luz; as duas deusas (galáctica azul a +43°, vermelha a
   −78°); janela: pegar e dimensionar o rosa (5:30–6:20). Entrar no
   planeta às 6:20.
3. **Planeta rosa (6:30–8:45)** — a água na cintura (0,80 m), o fundo do
   mar (colônia, cogumelos e planta alienígena de 2–3 m saindo da água,
   estrela grande, concha), as águas-vivas cor do céu nadando, o ser de
   vidro, o ser camuflado no céu, as serpentes e o azul debaixo da água,
   a corrente nas algas; janela: os seres, as pedras, a concha (7:30–8:25);
   a mão gigante/buraco final puxa às 8:25, furacões.
4. **Papel (8:45–10:00)** — céu inteiro, o teatro de papel em cinco camadas,
   o retorno inverso (a floresta do começo de cabeça para baixo a 11 m), a
   integra (9:16–9:54) se mexendo, a borboleta vem ao rosto, tudo se
   desmancha; a espera com o "rizomar".

### Como tudo surge no planeta rosa (é o que foi perguntado em 15/09)

| quando | o quê | como |
|---|---|---|
| 6:26 → 6:42 | o fundo inteiro (algas, corais, cogumelos, plantas, neon, águas-vivas, serpentes) | aparece no lugar, ganhando opacidade; não cresce |
| 6:30 → 6:36 | o céu rosa | travessia de 6 s; a tinta sobe junto |
| 6:30 → 7:05 | a água | **aparece já na cintura, ganhando opacidade** — não sobe (proposta em aberto: subir) |
| 6:40 → 7:50 | o ser camuflado no céu, de frente | aos poucos |
| 6:42 → 7:12 | os seres de luz | somando luz |
| 6:48 → 7:12 | o ser de vidro | boiando; 7:30 → 8:25 sobe 6 m ao céu; some 8:28 → 8:42 |
| 7:12 → 7:36 | a concha | pulsa até ser tocada; tocada, chama a mão gigante (salta para 8:25) |
| 8:16 → 8:40 | os furacões | a água gira |
| 8:25 | o buraco negro final cresce e engole | água some 8:28 → 8:46; fundo 8:36 → 8:50; cenário 4 às 8:45 |

### Onde as coisas moram no template (o que esta semana tocou)

| o quê | onde |
|---|---|
| os interruptores (`ANDAIME`, `MATA_SOLIDA`, …) | o alto do arquivo; tabela no `CLAUDE.md` |
| `CENAS` (céu, tinta, neblina, graduação `ini`/`fim`, `longe`), `MOMENTOS` (a partitura), `rampa()` | perto de `const CENAS = {` (~linha 7500) |
| a linha do tempo de tudo (`aguaPresenca`, `fundoDoMar`, `vidroPresenca`, `retornoInverso`…) | `function seguir…` perto de `fundoDoMar = rampa(386, 402, t)` (~linha 8670) |
| `VS_SOLIDA` / `FS_SOLIDA` — a pele de todo corpo | ~linhas 3140 / 3341. Uniformes do vértice: `balanca` (vento), `corrente` (alga na água), `nadar` (água-viva), `bolha` (ser de vidro), `serpente` + `serpentes[5]`, `brota`, `ondula`, `inflar`, `inverte`. Matérias do fragmento: 1 pedra, 8/15/17 pele da noite (17 = floresta do teto com fio dourado), 9 seres do fundo, 11 água-viva (rosa do céu), 12 neon, 13 camuflagem do céu, 18 vidro, 19 cristal; `lamina` = a altura da água (99 fora do cenário 3), `deFrente` = a beira que se desfaz |
| o fundo do mar: `montarFundoDoMar` (`emAnel`, listas de buffers fechando em 58 mil vértices, `bFundo` / `bFundoParado` / `bAlgaNeon` / `bSeresCeu`), `medidaDaMalha` + `plantarMedido` (o pé e o alto dos modelos centrados) | ~linha 1540 e ~2120 |
| as serpentes (`montarSerpentes`, `SERPENTES`), o ser de vidro (`montarSerDeVidro`, `ondeVidro`, `SER_VIDRO`) | antes de `let bHorizPedra` (~2270–2440) |
| a água: `VS_AGUA` / `FS_AGUA` (grade 96 × 96, `toque[2]`, `vAnel`), `NIVEL_AGUA = 0.80`, `CORRENTE_DO_MAR`, `TOQUE_AGUA`, `ressoarAgua` | ~5824 e ~7537 |
| debaixo da água: `mergulhoDe`, `FS_MERGULHO` (o véu), `FS_SOLO_AGUA` (o solo) | antes de `const VS_CONTORNO` |
| o bloco de desenho do fundo do mar (a ordem: horizonte, algas de fora, solo, fundo, serpentes, águas-vivas, concha, neon, vidro) | `if(fundoDoMar > 0.004){` (~11180) |
| as deusas: `FIGURAS` (`tam` é meia-largura/meia-altura em metros, lidos por quadro), `FS_FIGU` (`fluxo`, `asas` da integra) | ~7742 |
| o céu: `FS_SALA` (estereográfica com `abs(d.y)`, `longe` = estrelas finas) | procurar `const FS_SALA` |
| o relato para o servidor, `window.raizes` (`ir`, `cena`, `onde`) | ~9340 |

---

## 6. Pendências e decisões em aberto (18/09)

A lista inteira, com as melhorias sugeridas, está em
`_fotos/2026-09-18 pendencias e melhorias.html` (e no LEIA-ME-ACER,
"Decidido, mas não construído" e "Em aberto"). O essencial:

1. **O teste no Quest** — nada de 12/09 para cá foi visto no aparelho:
   quadros no planeta rosa (fundo ~181 mil triângulos + neon 51 mil +
   águas-vivas 28 mil + água + véu), o véu por cima do passthrough, os anéis
   com a mão de verdade, o ser de vidro, as serpentes, a corrente, o teatro,
   a floresta no alto, a integra. Um passe de 10 min pelo cabo.
2. **Decisões da direção de arte:** a água subindo ou não; a mão gigante por
   código (proposta de 17/09) ou fica o buraco; a vermelha a 1,5× (uns 18°
   mais à esquerda para o Sol ficar no vão); os links das sete imagens do
   Midjourney.
3. **Licenças:** seis `magnific_*` na obra, a crisálida e o ser alienígena
   de origem desconhecida; o crédito CC BY da borboleta no estande.
4. **Estande:** headset carregado por último; instalar como app; rede off;
   a lâmpada com estúdio + ponte.

---

## 7. Armadilhas que morderam esta semana (além das do CLAUDE.md)

- `smoothstep(a, b, x)` com `a > b` é indefinido: escrever `1.0 - smoothstep(b, a, x)`.
- Uma instrução entre um `if` e o `else if` seguinte quebra a cadeia — o
  shader não compila e **nenhuma superfície aparece**, sem erro.
- Uniforme com precisão diferente entre vértice e fragmento (`tempo`,
  `centro`) não linka. `provar_shaders.py` pega os três casos acima.
- Índices de 16 bits: uma malha passa de 65 mil vértices e o desenho vira
  lixo (vigas brancas de 5 m). As listas do fundo fecham em 58 mil.
- Modelos do Sketchfab/Magnific vêm **centrados** (pé em −0,5): plantados no
  chão ficam meio enterrados, e a altura no corpo (`aAlt`) fica de −0,5 a
  0,5 — `plantarMedido` corrige as duas coisas.
- Um remendo que corta "entre duas âncoras" leva junto o que estava no meio;
  e uma âncora que inclui a linha `if(…){` duplica o `if` — `node --check`
  pega o segundo caso, o primeiro só a obra morrendo ao abrir.
- O servidor de bancada iniciado de dentro de um comando morre com o
  comando; e outra sessão pode ocupar a porta (8767/8768 já foram tomadas):
  usar 8791 e subir solto.

---

## 8. Endereços e contas

| o quê | onde |
|---|---|
| repositório | `github.com/visoes-filmes/raizes-cosmicas-v2` (conta Crisia-poria) |
| a obra publicada | `visoes-filmes.github.io/raizes-cosmicas-v2/` |
| voltar a uma versão | `git checkout publicado-<versão>` (toda publicação marca a anterior) |
| relatório de 12/09 | Google Doc `1-CZem709TxKzCLwfnSp77nyzTVtkvLE8JuoydNNh0xo` |
| a lâmpada | Tuya `LDV SMART+ CLA60`, chaves em `raizes-display/lampada/config.json`; estúdio na porta 8600 |
| o Quest no cabo | `localhost:8765` (estande.py); DevTools em `localhost:9222` (`adb forward`) |
| a bancada | `localhost:8791/_dev.html` (servir.py 8791) |
| modelos de origem | `Downloads\Visões filmes\Modelos 3D` (ou `MODELOS=…`) |

Se algo aqui não bater com o código, **o código manda** — e este arquivo é
que precisa ser corrigido.
