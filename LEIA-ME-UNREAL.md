# Seguir no desktop (o computador "Unreal") — 20/09/2026

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

## 0. Para o chat novo — o que ler, e o que vive fora da pasta

1. `CLAUDE.md` (regras) → **este arquivo** (a máquina, o jeito, o estado) →
   `LEIA-ME-ACER.md` (o mapa). Depois `CREDITOS.md` (licenças) e
   `NOTAS-2026-09-07.md` (a primeira lista da direção de arte, quase toda
   feita). `_fotos/2026-09-18 pendencias e melhorias.html` é o último
   relatório (não está no repositório: está no ZIP e no Drive).
2. **O que não está no repositório e vai no ZIP**: o estúdio do v1
   (`raizes-display/`, a lâmpada) e os modelos de origem (`Modelos 3D/`).
3. **O que não está em lugar nenhum da pasta e mora na conta do Claude**:
   duas *skills* pessoais da Crisia — `documentacao` ("tabelas e documentos
   sempre no Google Drive, como Google Docs/Sheets") e `slash-commands`
   (comandos com barra em português). Elas vêm com o login no claude.ai; se
   não vierem, a regra que importa está aqui: **documento é no Drive.** A
   memória do Claude para este projeto estava vazia — nada a trazer.
4. **O conector do Google Drive** da conta `admcrisia@gmail.com` recusava
   escrever em 18–20/09 — a conta estava **cheia** (2,6 TB de 2 TB), e é
   isso que o Drive responde como "sem permissão". Os documentos passaram a
   ir para a pasta **RAÍZES CÓSMICAS DEV** da outra conta (a de 5 TB), pelo
   navegador. O jeito que funcionou para subir arquivos grandes sem o
   conector: o Chrome da Crisia (extensão Claude in Chrome) na página do
   Drive; o "Upload de arquivo" cria um `input type=file` — interceptar o
   `click`/`showPicker` dele, alimentar o input com o arquivo (em partes de
   9 MB coladas num `File` só, porque a ferramenta sobe no máximo 10 MB por
   vez) e disparar `change`: o Drive faz o upload com o uploader dele.

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

**No Drive** — pasta **RAÍZES CÓSMICAS DEV** da conta com espaço
(`drive.google.com/drive/u/0/folders/1KSLMJoW2me4ku42fJZsGRNKmodDbc8wR`;
a conta `admcrisia@gmail.com` estava cheia, 2,6 TB de 2 TB, e por isso o
conector recusava escrever). Subido em 20/09, pelo próprio navegador:

| arquivo | o que é |
|---|---|
| `raizes-cosmicas-v2-completo-2026-09-20.zip` (598 MB) | o projeto com o `.git` na versão 20b + o estúdio do v1 + os modelos de origem + este guia (a versão do guia de dentro é a de 20/09 de manhã; a mais nova é a do repositório) |
| `Modelos-3D-origem-2026-09-20.zip` (66 MB) | só os `.glb` de origem, para quem não quiser o pacote inteiro |
| `raizes-cosmicas-v2-extras-2026-09-20.zip` (1,8 MB) | só o que não está no repositório e é pequeno: o estúdio do v1 (sem chaves), os quatro MDs, o relatório de 18/09 e as folhas de contato. `_extras.zip` é o mesmo arquivo, duplicado — pode apagar |
| `LEIA-ME-UNREAL.md` | este guia, solto, para ler antes de baixar |

O pacote completo tem o mesmo repositório (com o `.git`) **mais o que nunca
esteve nele**:

| pasta no ZIP | o que é | onde colocar no desktop |
|---|---|---|
| `Raizes Cósmicas/` | o projeto, com `.git` — dá para `git pull` e publicar direto dela | `Downloads\Raizes Cósmicas` (o nome com acento é o que está no `bancada.py` do ateliê antigo; o resto não depende do nome) |
| `raizes-display/` | **o estúdio do v1**: `node estudio.mjs` (porta 8600) é quem fala com a lâmpada do estande. **As chaves da lâmpada não viajam no ZIP** (`lampada/config.json` e `lampada/luzes.json` ficaram de fora de propósito): copie os dois deste computador ou do Acer, ou refaça a chave com `node lampada/nuvem.mjs <AccessID> <AccessSecret> us` (a conta Tuya IoT) | `Downloads\claude\raizes-display` |
| `Modelos 3D/` | os `.glb` de origem (algas, corais, cogumelos, a planta alienígena, o ser, a mão cósmica…). A obra **não** precisa deles para rodar — já estão assados em `fontes/nuvens.js`. Só para **converter um modelo novo** (`fontes/modelos_em_pontos.py`) | `Downloads\Visões filmes\Modelos 3D`, ou qualquer lugar com `MODELOS=<pasta>` no ambiente |

Ficaram de fora do ZIP, de propósito: `_fotos/` (700 MB de renders da
bancada — se refazem), `_dev.html`, `_prova.html`, `nova.html`,
`oficina.html`, `simulador.html` (o montador refaz todos), as gravações e
capturas do estúdio do v1, e as chaves da lâmpada.

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

## 5. O estado da obra em 20/09

No ar: **`raizes-cosmicas-2026-09-20f`** em
`visoes-filmes.github.io/raizes-cosmicas-v2/`. A obra em si continua a de
15/09 (`437df9e`, a corrente); de 20b a 20f só entraram salvaguardas —
nenhuma muda o que se vê: a linha dos 18 programas no portão (20b), o
prazo do `local-floor` e o erro no portão (20c), o contorno pela
profundidade desligado (20d, o que fazia a obra morrer no Quest — abaixo),
a versão nova que entra sozinha no portão, o contexto perdido que se
relata e recarrega, e o aviso de chão não mapeado (20e/20f).

### O primeiro teste em RM pelo cabo, no desktop (20/09) — o que se viu

**A obra morria no primeiro quadro em RM, muda.** A RM abria (`RM-ABRIU`
com `local-floor`, mãos rastreadas, `QUADRO-1` desenhado) e então o
contador travava em `52 / 72` e o relógio em `0:00` para sempre. Nenhum
erro de JavaScript, nenhum shader falhando (18/18). O console do navegador
do Quest, lido pelo DevTools no cabo, dizia:

```
>> PROFUNDIDADE 320x320 unsigned-short texture-array x1
GL ERROR GL_INVALID_ENUM : glBindTexture: target was GL_TEXTURE_2D_ARRAY
WebGL: CONTEXT_LOST_WEBGL: context lost
```

O contorno pela profundidade (12/09) pedia `depth-sensing` em
`gpu-optimized`; o Quest 3 entrega o mapa como **texture-array** (uma
camada por olho), coisa de WebGL 2, e a obra é WebGL 1. O navegador tenta
amarrar a textura num alvo que o WebGL 1 não tem e **derruba o contexto
inteiro** — dentro do próprio `getDepthInformation()`, antes de o código
poder recusar (ele recusava: `textureType !== 'texture'`). Desde 20d
`CONTORNO_PROFUNDIDADE = false` e o `depth-sensing` só é pedido com ele
ligado; o contorno das mãos pelas juntas continua. Para religar: contexto
WebGL 2 (`sampler2DArray` no `FS_CONTORNO`) ou `cpu-optimized` com o mapa
subido a uma `TEXTURE_2D` por quadro. **Provado no aparelho**: com a 20d,
RM aberta, relógio correndo pelos quatro cenários, contexto íntegro.

**Quadros em RM, medidos pela primeira vez** (`adb logcat -s VrApi`, dois
olhos a 1680 × 1760, 4× MSAA; GPU do navegador presa em 456 MHz, nível 2,
e `powerPreference: 'high-performance'` não a move — testado e tirado):

| cenário | quadros / 72 | GPU |
|---|---|---|
| 1 floresta | **17–33** | 99 %, ~38 ms por quadro |
| 2 cosmos | 57–61 | — |
| 3 planeta rosa | **18–34** | 99 % |
| 4 papel | 61–65 | — |

Neblina, poeira, raízes e sala desligados pelo cabo, um de cada vez: nenhum
mexe no número. O peso é a mata sólida (1) e o fundo do mar (3). Abaixo de
36 o movimento ganha rastro, e dez minutos a 99 % de GPU, pessoa após
pessoa, é calor (44 °C em minutos de teste). A lista de corte do
`LEIA-ME-ACER` (§10) vale, mas é decisão de direção de arte: escala de
desenho 0,8, `ANISO_ALVO` 4 → 0, menos do que não se vê de pé. O número
final só sai no aparelho.

**O que mais o dia ensinou** (tudo já aplicado):

- **A aba atrás dá `SecurityError`.** Com outra aba na frente do navegador
  do Quest (havia uma da Netflix), `requestSession` é recusado e a obra
  corre achatada (`RM-RECUSOU SecurityError`). No estande: só a aba da
  obra, ou instalada como app. Pelo cabo: `curl localhost:9222/json/activate/<id>`
  antes de clicar.
- **Este Quest tinha a 15b guardada.** Uma recarga com Wi-Fi trouxe a
  versão nova — é o caso do Plínio. Desde 20e a página se recarrega sozinha
  no portão quando o guardião novo assume (`controllerchange`; confere a
  cada dez minutos com `registration.update()`; sem rede não acha nada).
- **O GitHub Pages não montou a 20d.** O push chegou (`bc1e6d9`) e nenhum
  "pages build and deployment" disparou em meia hora; um commit vazio
  empurrado em seguida montou em um minuto. Conferir sempre:
  `curl -s https://api.github.com/repos/visoes-filmes/raizes-cosmicas-v2/actions/runs?per_page=1`
  e o `md5` do `index.html` publicado contra o do commit.
- **A autorização do cabo não sobrevive ao reinício** se a caixa "Permitir
  depuração USB" foi aceita sem **"Sempre permitir deste computador"**. O
  Quest reiniciou à tarde, voltou `unauthorized`, e sem ninguém perto dele
  não há como aceitar de fora — nem app Horizon, nem MQDH, nem Wi-Fi (o
  `adb tcpip` só se liga *depois* de uma autorização por cabo). Sempre
  marcar; e, com o cabo de pé, deixar `adb tcpip 5555` + `adb connect
  <ip>:5555` para alcançar o Quest pela Wi-Fi da casa.
- **O Quest dorme fora da cabeça** e some do DevTools. Para trabalhar com
  ele na mesa: `adb shell am broadcast -a com.oculus.vrpowermanager.prox_close`
  (o sensor de proximidade passa a ser ignorado até o reinício;
  `…automation_disable` devolve).
- **Clique pelo cabo conta como gesto.** `Runtime.evaluate` com
  `userGesture: true` no DevTools do Quest abre a sessão de RM sem
  ninguém tocar — a obra roda inteira na mesa, e o `raizes.ir()` salta
  os cenários. O que continua precisando de gente: o toque, o pegar, e
  ver.
- **No Windows, `estande.py` com a saída redirecionada** morre no acento
  (`cp1252`): `PYTHONIOENCODING=utf-8`. E `adb` não vem com nada — o
  `platform-tools` foi largado em `fontes/platform-tools/` (fora do git).

### "Só um céu cósmico e um carregamento que nunca acontece" (20/09)

Relato da Crisia com o Quest no desktop, num lugar novo: a sessão abre e
fica na **tela de espera do navegador do Quest** (um céu escuro de
estrelas com um indicador de carregamento) para sempre. "Tem a ver com o
limite de área?" Tem: essa tela fica até a obra entregar o primeiro
quadro, e o primeiro quadro só é pedido depois de `await
requestReferenceSpace('local-floor')` — que, num lugar onde o Quest não
tem o espaço mapeado, **pendura** (não rejeita, não resolve — o mesmo
gênero de defeito do dom-overlay e da taxa de quadros). Desde
`2026-09-20c` o pedido tem prazo de 8 s e cai para `local` (relato
`SEM-CHAO`), e a obra abre torta em vez de não abrir. O certo no estande
continua: **configurar o limite de área do Quest no lugar da montagem**,
para haver `local-floor` e o chão ficar onde está. E, desde a mesma
versão, **todo erro de JavaScript vira relato (`ERRO …`) e linha no
portão** (`portaoErro`), que reaparece quando se tira o capacete — uma
foto do portão passa a dizer versão, programas compilados e o último erro.

### O relato do Plínio (20/09) e como se responde

"A deusa do final não aparece; não parece ser a última versão, várias
mudanças que pedi não estão lá; olhar no celular não é o mesmo que no
Quest." O que se fez: a obra publicada foi conferida **byte a byte** contra
a montagem (`md5` do `index.html` no endereço = o do commit) — o site está
certo — e os quatro cenários foram rodados na bancada
(`_fotos/todas-as-cenas-15b.jpg`): a integra está lá, de frente, às 9:16 →
9:54. O que sobra é o aparelho dele, e um aparelho tem dois jeitos de não
mostrar o novo:

- **cache velho** — o portão diz a versão que ele tem na mão (tem que ser
  `2026-09-20b`); com Wi-Fi, abrir de novo; se teimar, limpar os dados do
  site no navegador do Quest e abrir outra vez;
- **um programa que não linka naquela GPU** — não dá erro em lugar nenhum,
  a coisa só não aparece. Por isso o portão agora diz também **"18 programas
  de desenho compilados neste aparelho"** (ou "ATENÇÃO: n de 18 não
  compilaram: nomes"). Com 18/18 e a versão certa, o que ele vê **é** a
  obra; com menos, é o cabo (`estande.py`, `_prova.html` no navegador do
  Quest, o relato `PROGRAMAS`).

Uma foto do portão dele responde as duas. Se as duas estiverem certas e ainda
assim faltar coisa, aí é a lista dele, mudança por mudança, contra
`_fotos/todas-as-cenas-15b.jpg` — pode ser a janela curta da integra
(9:16–9:54; entra 31 s depois do teatro), e mudar isso é `de: 556` em
`FIGURAS`.

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

## 5b. O v4: a obra lida com o espaço de verdade (23/09)

"Que aconteça um escaneamento do ambiente para posicionar os objetos
integrados com o espaço. É importante evitar que coloque uma árvore em cima
de algum objeto físico. Um cogumelo pode ficar em cima da mesa, mas não
através/dentro dela."

Sai num arquivo próprio — **`v4.html`**, escrito pelo montador com
`ESPACO_ESCANEADO = true` — e a obra de sempre continua como está. O motivo
de serem dois: sem a configuração de espaço feita no Quest não vem plano
nenhum, e uma obra que dependesse de um escaneamento que pode não vir seria
uma obra que às vezes não abre. **Sem planos, o v4 é idêntico ao v2.**

**Como funciona.** Dentro da RM, a obra já pedia `plane-detection` e o Quest
já concedia — só que ninguém lia. Agora lê: dois segundos depois do primeiro
plano chegar (eles vêm aos poucos), monta-se a sala em `SALA` — o **piso**
(o horizontal mais baixo), os **móveis** (horizontais acima dele, até 2,2 m)
e as **paredes** (os verticais) — tudo como polígonos em x,z do mundo da
obra. Não se usa `mesh-detection`: a pergunta aqui é de duas dimensões, "o
que está embaixo deste ponto e a que altura", e polígono responde isso com
uma conta de escola.

Com a sala lida, a obra **replanta**, uma vez:

| o quê | regra |
|---|---|
| cogumelos, pedras | pousam na superfície que estiver embaixo (`alturaEm`); a menos de 12 cm da quina, entram 18 cm para dentro — meio chapéu no ar lê pior do que atravessar |
| a árvore-mãe | se o lugar de sempre tem móvel embaixo ou encosta na parede, ela **gira** em volta da pessoa até o chão livre mais próximo em ângulo (girar preserva o vão e o enquadramento do céu melhor do que afastar). O casulo vai junto, pelo mesmo deslocamento |
| as outras onze | moram no anel de 2,9 a 5,0 m e atravessam a parede de propósito; delas só se cobra não nascerem de cima de um móvel — e fogem para fora |

**Provado na bancada** (`raizes.sala({...})` dita uma sala de mentira, e o
replantio corre igual): com uma mesa onde a mãe fica hoje, ela saiu de
(−1,35, −1,75) para (0,32, −1,48) e o casulo foi junto; com uma mesa de
centro de 42 cm dentro do anel dos cogumelos, dois deles subiram para
`y = 0,42` — o pé no tampo. **Nada disso foi visto no Quest.**

**O que falta no v4:**

- **ver no aparelho** — é tudo o que importa: a leitura de planos de verdade,
  o tempo dela, e se a mãe cai num lugar que faça sentido numa sala real;
- a grama e a mancha de solo continuam no piso (não sobem na mesa);
- `v4.html` não está no cache do `sw.js` — no estande sem rede ele não abre.
  Entrar na lista se o v4 for o que vai à feira;
- o replantio custa uma montagem de malha (uns poucos décimos de segundo),
  dois segundos depois de entrar em RM. Medir no aparelho.

---

## 5c. Raízes Cósmicas 5.0 (24/09)

Pedido: "a interatividade ainda não está rolando bem e ainda está com um
pouco de travamento quando eu mexo a cabeça; deixe mais integrado com o
espaço — preciso que entenda as paredes e faça rachaduras e buracos por onde
podemos visualizar a outra realidade; diminua a névoa para ficar mais limpo;
determine que o único espaço 100 % VR é o teto/céu; retome a interface de
visualização no computador; se ficar muito pesado faça uma versão
instalável." E: "faça backups da versão e denomine sempre uma nova versão —
essa é Raízes Cósmicas 5.0."

**Backups:** marcas `v2.0` (a obra base) e `v4.0` (a que lê o espaço) no
repositório, antes de qualquer mudança; `v5.0` na 5.0 publicada.

**O travamento ao mexer a cabeça** é o timewarp abaixo de 36 quadros. Medido
no Quest com a obra de sempre, cenários 1 e 3: escala 1,0 → 35/17; 0,8 →
46/23; **0,7 → 54/26**; suavização desligada → 32/17 (não ajuda); névoa
pela metade → 19/17 (não ajuda nos quadros). **A 5.0, com escala 0,7 e as
paredes tampando o que está atrás delas: floresta 58, planeta rosa 47.**
Acima da linha nos dois. A escala de desenho é a alavanca; em RM, com a
câmera em resolução nativa, 0,7 quase não se vê.

**As paredes rachadas** (`PAREDES_RACHADAS`, pede o escaneamento): cada
parede lida vira malha (leque do polígono, coordenadas em metros ao longo
dela e na altura) e é desenhada logo depois do céu em dois passes — a
TAMPA, sem mistura, alfa zero e profundidade (ali o céu some e a câmera
aparece; o que vier atrás é cortado), descartando onde a rachadura está
aberta; e a LUZ DA BORDA, somada, sem profundidade, na cor do cenário. A
rachadura é ruído dobrado elevado (fios, duas escalas) mais manchas de baixa
frequência (buracos) que ganham com a abertura — 0,06 na chegada, +0,22 na
floresta, +0,22 no cosmos, +0,20 no rosa, +0,30 no papel, onde a sala quase
some ("estamos no espaço"). O teto não recebe tampa: é o único espaço 100 %
VR. O chão continua como era (a obra some ao descer).

**Lido no Quest desta casa (24/09):** 37 planos — chão, 11 móveis, 22
pedaços de parede (66 triângulos); a mãe teve de girar para o outro lado da
sala (não havia chão livre onde ela fica); nenhum cogumelo caiu em móvel.
**A imagem dentro do capacete ainda não foi vista por ninguém.**

**Interface no computador:** `python fontes/servir.py 8791` e a oficina em
`localhost:8791/oficina.html` (ou pelo estande em 8765). A bancada com
`_dev5.html` (o `_dev.html` com os interruptores da 5.0 trocados) é o que
gerou `_fotos/v5-cenas.jpg`.

**Versão instalável:** a obra já é instalável como app no Quest pelo
manifesto (menu ⋮ → Instalar app); com a escala 0,7 o peso ficou dentro do
alvo. Um APK só se o navegador deixar de servir.

**Em aberto na 5.0:** a interatividade "não está rolando bem" — falta o
relato dela do que viu (toque, pegar o rosa, som); o cache do `sw.js` não
inclui `v5.html` (no estande sem rede só o `index.html` abre); as marcas de
móvel do Quest vêm em pedaços (11 móveis, 22 paredes) e o replantio pode
levar a mãe para longe — ver se o lugar faz sentido na sala real.

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

## 6b. Ideias propostas e soluções achadas — para não se perderem

**Ideias (propostas, à espera de "sim"):**
- **A água subindo de verdade** (6:30 → 7:05) sobre o fundo que já está
  lá: `nivel` deixa de ser `NIVEL_AGUA` fixo e sobe com uma rampa; a
  `lamina` e o `mergulhoDe` seguem o mesmo nível — o azul chega com ela.
- **A mão gigante por código**: dedos em tubos ao longo de curvas (a receita
  das serpentes: malha reta, o vértice a põe na curva), uma palma
  elipsoidal, pele da noite + fio dourado (matéria 17), translúcida; vem
  do lado do buraco às 8:25, fecha em volta da pessoa sem tocar (~8:37), e
  no puxão é o mundo que corre (água, fundo, céu deslizam para o buraco)
  enquanto `buracoFinal` engole (8:45). Fazer depois do teste no Quest.
- **A vermelha a 1,5×** com o centro uns 18° mais à esquerda (azimute ≈ −96)
  para o Sol continuar no vão; `FIGURAS[1].tam` e `centro`.
- **Uma válvula de quadros** no planeta rosa: medir o tempo de quadro em RM
  e, abaixo do alvo por alguns segundos, tirar o neon e metade da colônia
  (`bAlgaNeon`, metade de `bFundo`). Só depois da medida no aparelho.
- **As montanhas do horizonte do planeta rosa** (`bHorizPedra`, matéria 1,
  presença 0,62) leem como manchas cinza-escuras atrás da água quando se
  está de pé: mais longe, mais baixas, ou com o rosa do céu por cima.
- **A integra desde o começo do papel**: `de: 556 → 525` se a janela curta
  for o problema.
- **A deriva da lâmpada** já é solução; a ideia que sobra é ela **mudar de
  cor com o toque** na obra (o `relato('TOCOU-…')` já existe pelo cabo).

**Soluções que valem de método:**
- **Remendo por trecho exato** (`s.count(trecho) == 1`) em vez de editar à
  mão ou cortar entre âncoras; o script fica no scratchpad, a receita no
  commit.
- **`provar_shaders.py` + a linha do portão**: o que o verificador estático
  não vê (GLSL) se prova compilando de verdade — na bancada e no aparelho.
- **A bancada com fotos de dentro do WebGL** (`bancada.py`/`bancada.js`):
  vistas em pé e agachado, GIFs em tempo real, folhas de contato com
  rótulo, diferença entre quadros e média de pixels para medir em vez de
  achar.
- **Modelos centrados**: medir o pé e o alto (`medidaDaMalha`) e reescrever
  a altura no corpo de 0 a 1 (`plantarMedido`) — sem isso nem o chão nem o
  balanço batem.
- **Listas de buffers** fechando em 58 mil vértices, para o índice de 16 bits.
- **Conferir o publicado byte a byte** (`curl` do `index.html` + `md5`
  contra o commit) antes de discutir "versão velha".
- **Servidor da bancada solto** (`Start-Process`) numa porta própria (8791);
  outra sessão pode ocupar 8767/8768.
- **A lâmpada pelo caminho local** (tinytuya 3.5, ~1,8 s por comando): sem
  nuvem, sem cota; a nuvem da Tuya serve para conferir `online` e a chave.

## 7. Armadilhas que morderam esta semana (além das do CLAUDE.md)

- `smoothstep(a, b, x)` com `a > b` é indefinido: escrever `1.0 - smoothstep(b, a, x)`.
- Uma instrução entre um `if` e o `else if` seguinte quebra a cadeia — o
  shader não compila e **nenhuma superfície aparece**, sem erro.
- Uniforme com precisão diferente entre vértice e fragmento (`tempo`,
  `centro`) não linka. `provar_shaders.py` pega os três casos acima.
- Índices de 16 bits: uma malha passa de 65 mil vértices e o desenho vira
  lixo (vigas brancas de 5 m). As listas do fundo fecham em 58 mil.
- **Uma textura que o WebGL 1 não conhece derruba o contexto inteiro**, sem
  erro de JavaScript — foi o `depth-sensing` em texture-array (20/09). O
  contexto perdido agora se relata (`CONTEXTO-PERDIDO`) e recarrega; mas
  toda extensão nova do WebXR que entregue textura deve ser provada no
  aparelho antes de ficar ligada.
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
