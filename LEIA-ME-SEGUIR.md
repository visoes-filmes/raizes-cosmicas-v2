# Seguir em outro computador — 24/09/2026

Este é o arquivo para **mudar de máquina sem perder nada**: o que instalar,
como trazer o projeto, em que estado a obra está, como se trabalha e o que
está em aberto. Ele completa os outros; não os substitui:

| arquivo | o que é |
|---|---|
| `CLAUDE.md` | as regras da casa e a tabela dos interruptores — um chat novo do Claude Code aberto na pasta lê sozinho |
| **este** | a mudança de máquina e o estado de 24/09 |
| `LEIA-ME-UNREAL.md` | o diário de 19 a 24/09: o primeiro teste em RM, o v4, a 5.0, as armadilhas, o jeito da direção de arte |
| `LEIA-ME-ACER.md` | o mapa completo da obra, arquivo por arquivo |

Peça ao chat novo para ler **este** e depois o `LEIA-ME-UNREAL.md` antes
de mexer no código.

---

## 1. Instalar

| o quê | para quê | conferir |
|---|---|---|
| Git | trazer e publicar | `git --version` |
| Python 3 (3.12 serve) + `pip install Pillow` | verificar, montar, publicar, bancada | `python --version` |
| Node.js | o verificador confere cada `<script>` com `node --check`; os scripts do DevTools do Quest | `node --version` |
| Chrome ou Edge | a oficina e a bancada | — |
| `platform-tools` (adb) | o Quest pelo cabo e pela Wi-Fi | baixar de developer.android.com/studio/releases/platform-tools e largar a pasta em `fontes/platform-tools/` (fica fora do git) |
| Claude Code | o trabalho | abrir na pasta do projeto |

Login do GitHub: pedido na primeira vez que se empurra (o Git abre o
navegador). Conta **Crisia-poria**, owner da organização `visoes-filmes`.

Git precisa saber quem você é, uma vez, dentro da pasta:

```bash
git config user.name "Crisia-poria"
git config user.email "admcrisia@gmail.com"
```

## 2. Trazer o projeto

```bash
git clone https://github.com/visoes-filmes/raizes-cosmicas-v2.git "Raizes Cósmicas"
```

Tudo o que a obra precisa para existir, ser montada e publicada está no
repositório — as três versões (v2, v4, 5.1) saem do **mesmo** template.
Fora dele, de propósito: `_fotos/` (renders da bancada, refazem-se),
`_dev*.html`, `_prova.html`, `nova.html`, `oficina.html`, `simulador.html`
(o montador refaz), `fontes/platform-tools/`, e o estúdio do v1 com as
chaves da lâmpada (está no ZIP do Drive — ver `LEIA-ME-UNREAL.md` §2).

Depois de clonar, confira que a máquina monta:

```bash
python fontes/verificar.py     # tem de dizer "nada a corrigir"
python fontes/montar_mr.py     # escreve index.html, v4.html, v5.html, nova, oficina, simulador
```

No Windows o montador roda melhor pelo PowerShell (o caminho com acento
engasga no bash em alguns comandos). **Não publique só por ter montado.**

## 3. O estado em 24/09

| versão | o que é | endereço | marca no git |
|---|---|---|---|
| **v2** | a obra base, sem escaneamento | `visoes-filmes.github.io/raizes-cosmicas-v2/` | `v2.0` |
| **v4** | lê o espaço: cogumelos e pedras pousam em mesa/banco; a árvore-mãe procura chão livre | `…/raizes-cosmicas-v2/v4.html` | `v4.0` |
| **5.1** | v4 + paredes lidas com rachaduras e buracos por onde a outra realidade aparece; só o teto é 100 % VR; metade da névoa; escala de desenho 0,7 (floresta 54, planeta rosa 45 quadros no Quest); toque com respiro | `…/raizes-cosmicas-v2/v5.html` | `v5.1` (a 5.0 em `v5.0`) |
| **6.0** | **a 5.2 + a tela de tule** (24/09): o óculos acha a tela real (plano rotulado como tela/janela na Configuração de Espaço, ou dois cantos beliscados a pedido da Cabine) e lê o toque da mão nela; cada toque vira onda no vídeo "Odara - Cosmos" **projetado no tule** pela `projecao.html`, que recebe os toques da Cabine (`/eventos`). **Dentro do óculos a tela é invisível** (`TELA_VISIVEL = false`: "o vídeo já vai ser visto na realidade") — o Quest nem baixa o vídeo; `raizes.tela.ver(true)` liga só para conferir o encaixe. Provada na bancada (tela ditada, cosmos, toque, projeção recebendo); **nada visto no Quest** | `…/raizes-cosmicas-v2/v6.html` · projeção em `…/projecao.html` | `v6.0` |
| **5.2** | **um passo atrás na sala** (24/09, depois de ela ver a 5.1 no capacete): sem escaneamento e sem paredes rachadas — o céu volta a fazer *fade* com as paredes reais no degradê de sempre, e **o chão real aparece o tempo todo** até o cenário 4. Fica o que não tem a ver com a sala: metade da névoa, escala 0,7, toque com folga e respiro | `…/raizes-cosmicas-v2/v52.html` | `v5.2` |

> **Por que o chão ficou preto na 5.1.** Com paredes lidas, o céu recebia
> `inicio/fim` negativos para descer abaixo do horizonte; mas o `FS_CEU`
> corta a direção em zero (`h = clamp(dir.y, 0, 1)`), então abaixo do
> horizonte `h` vale 0 e `smoothstep(-0,35, -0,12, 0)` dá 1: cúpula opaca,
> chão junto. É o mesmo mecanismo que o cenário 4 usa de propósito
> (`ini:-1, fim:-0.5`, 8:45–9:45, "estamos no espaço"). Na 5.2 a floresta
> volta a `0,22/0,72`, o cosmos `0,12/0,58`, o rosa `0/0,85`: olhando para
> baixo o céu não chega, e a sala real está lá. **A bancada não prova isso**
> (na tela, transparente e preto saem iguais); só o Quest.

A obra em si (partitura, cenários, seres) é a de 15/09. De 20/09 para cá
entraram salvaguardas e a interatividade (23/09): o sino do toque delicado e
cósmico, o **chamado** (tudo o que é tocável sabe que a mão está vindo e
sussurra uma vez), as veias da árvore-mãe acendendo com a aproximação, os
planetas acendendo, o rosa pegável por pousar a mão e a entrada nele por
crescer ou trazê-lo ao rosto.

Último commit: `d7b01c7`. Versão de cache da v2 no ar: `raizes-cosmicas-2026-09-24f`.
**Toda publicação marca a anterior** (`publicado-<versão>`); voltar é
`git checkout publicado-…`.

**Regras que a direção de arte deu nesta semana e que valem sempre:**
- tudo o que for feito localmente vai para o repositório na hora (commit + push), sem esperar pedido;
- cada rodada grande ganha **número de versão novo** e uma marca (`git tag`) antes de começar — próxima: 5.2 ou 6.0, ela decide o nome.

## 4. Como se trabalha

```bash
python fontes/verificar.py          # sempre antes de montar
python fontes/montar_mr.py          # gera as versões
python fontes/provar_shaders.py     # _prova.html: abrir no navegador, compila os 19 programas
python fontes/publicar.py "o que mudou"   # verifica, marca, monta, commita, empurra (v2 e as páginas v4/v5)
python fontes/publicar_versao.py 5 "…"    # monta a pasta ../raizes-cosmicas-v5 para o repositório próprio
```

Só se edita `fontes/mr.template.html` (e `fontes/montar_mr.py` quando o
montador precisa mudar). As versões são **interruptores** no alto do template
(`ESPACO_ESCANEADO`, `PAREDES_RACHADAS`, `NEBLINA_FATOR`, `ESCALA_DESENHO`…)
que o montador liga ao escrever `v4.html` e `v5.html` — tabela completa no
`CLAUDE.md`. Mudança grande vai por **remendo de trecho exato** (um script
que exige `s.count(trecho) == 1` antes de trocar).

**A bancada** (olhar e medir sem headset):

```bash
python fontes/montar_mr.py
python fontes/bancada.py            # escreve _dev.html com os ganchos
python fontes/servir.py 8791        # num terminal à parte
```

Abrir `localhost:8791/_dev.html` numa viewport de 1600 × 900 e, no console:

```js
const src = await (await fetch('/fontes/bancada.js')).text();
await (new (Object.getPrototypeOf(async function(){}).constructor)(src))();
raizes.ir(470); __frame();                 // salta na partitura
P.mvp = paraDe(1.6, 0, -10, 75); __frame(); __fotoRapida('nome.jpg');   // cai em _fotos/
raizes.mao(x, y, z, false, 0);             // uma mão de mentira
raizes.chamado('mae'); raizes.astro(0);    // medir a aproximação; onde está o rosa
raizes.sala({ chao:[-2,-2.35,2,2.35], moveis:[{y:0.42, r:[0.3,-1.2,1.25,-0.3]}],
              paredes:[{r:[-2,-2.35,2,-2.35]}] });   // uma sala de mentira, para o v4/5.x
raizes.plantas();                          // onde tudo ficou
```

Para provar o v4/5.x na bancada, troque os interruptores no `_dev.html`
copiado (`_dev5.html`: `ESPACO_ESCANEADO`, `PAREDES_RACHADAS` e
`NEBLINA_FATOR` trocados a mão) — na bancada a parede sai preta; no Quest é
a sala real pela câmera.

**A Cabine — o computador do estande (24/09, no Lenovo):**

```bash
python fontes/cabine.py             # sobe a obra (servir.py em modo estande, 8765) e a página de controle em localhost:8790
```

No Lenovo há um atalho na área de trabalho, **"Raízes Cósmicas - Cabine"**,
que faz isso sem janela (pythonw) e abre a página. A Cabine reúne, em botões,
o que antes eram quatro terminais: a **rede interna** (o Ponto de Acesso
Móvel deste Windows, por `fontes/hotspot.ps1` — nome e senha aparecem na
página; o Quest entra nela e ganha 192.168.137.x), o **Quest** (achar pelo
cabo ou pela Wi-Fi, *Liberar Wi-Fi* = `adb tcpip 5555` + `connect`, refazer
túneis, ficar acordado na mesa, espelhar na tela com o scrcpy), a **obra**
(abrir v2/v4/5.1/oficina no navegador do Quest, *Iniciar em RM* com gesto
pelo DevTools, reiniciar, encerrar, saltar de cena) e a **leitura de dentro
do capacete** (relatos `>>`, cena e segundo por `raizes.onde()`, quadros do
`VrApi`, bateria, 18/18 programas do portão).

Ela faz sozinha o trabalho do guardião quando o Quest aparece (túneis e, no
cabo, a liberação da Wi-Fi), e guarda o ip no mesmo `guardiao_quest.ip`.

**A projeção (6.0).** O card "Projeção · tela de tule" escolhe **o que o
projetor mostra** e em que monitor: *tela: desenho + água* abre a
`projecao.html` em quiosque (Chrome/Edge com perfil próprio) no monitor
escolhido — é a água da tela, parada e alinhada ao tule, recebendo cada
toque do óculos pelo `/eventos` (Server-Sent Events) da Cabine; *espelho do
óculos* abre o scrcpy em tela cheia (o que a pessoa vê, com ~0,15 s de
atraso e balançando com a cabeça). "Espelhar horizontalmente" é para
retroprojeção (projetor atrás do tule). Os botões da tela falam com a obra
pelo DevTools (`raizes.tela.*`): cravar pelos cantos, acender/apagar/seguir
a partitura, ditar uma tela de teste, toque de teste (sem óculos, o toque
vai só à projeção), soltar. Na página de projeção: F tela cheia, M espelho,
A acende sem esperar o óculos (para enquadrar o projetor), clique = onda.
**Atenção:** `adb tcpip 5555` (que a Cabine roda ao ver o Quest no cabo)
reinicia o adb do óculos; se a caixa de depuração foi aceita sem "Sempre
permitir", a autorização cai e volta a "unauthorized" — aceitar de novo,
marcando a caixinha.
O roteiro do dia está numerado na própria página: 1 ligar a rede · 2 o
Quest entra nela · 3 cabo uma vez → Liberar Wi-Fi · 4 abrir a versão ·
5 Iniciar em RM. Pela Wi-Fi o endereço no headset continua `localhost:8765`
(o `adb reverse` vale pela rede também), por isso o botão de RM aparece sem
certificado. Registro em `fontes/cabine.log`.

**O Quest pelo cabo (à mão, sem a Cabine):**

```bash
python fontes/estande.py            # adb reverse: no headset, http://localhost:8765 ; os relatos saem com >>
```

Com dois aparelhos no `adb` (cabo + Wi-Fi), rodar com `ANDROID_SERIAL=<serial>`.

As ferramentas do cabo, em `fontes/` (24/09):

```bash
node fontes/quest_eval.mjs localhost:8765 "raizes.onde()"                    # JS dentro do navegador do Quest
node fontes/quest_eval.mjs localhost:8765 "document.getElementById('bIniciar').click()" gesto   # abre a RM sem ninguem tocar
node fontes/quest_console.mjs localhost:8765 6                                # o console dele (erros de GL, contexto perdido)
bash fontes/medir_quadros.sh v5.html                                          # os quadros nos cenarios 1 e 3
```

As folhas de contato desta semana (veias da mãe, o rosa acendendo, o v4 com a
mesa, os quatro cenários da 5.0) estão em `fotos/2026-09-23-24/`.
Os relatos (`RM-ABRIU`, `ESPACO-LIDO`, `PAREDES`, `TOCOU-…`, `PEGOU-O-ROSA`,
`ENTROU-NO-ROSA`, `CAMADA`, `ERRO`, `CONTEXTO-PERDIDO`) são o que se lê de
dentro do capacete. O DevTools do navegador do Quest fica em
`adb forward tcp:9222 localabstract:chrome_devtools_remote`; um
`Runtime.evaluate` com `userGesture:true` clica o "Iniciar em RM" sem ninguém
tocar. Os quadros: `adb logcat -d -s VrApi | tail -1` (o `FPS=`).

**O guardião do Quest** (`fontes/guardiao_quest.py`): fica rodando e, quando
o Quest reaparece (cabo ou Wi-Fi), liga o adb pela Wi-Fi, refaz os túneis e
garante o sensor de proximidade normal (`--acordado` para ignorá-lo, só na
mesa). `fontes/guardiao_quest.ps1` registra a tarefa de logon do Windows —
**rodar uma vez, à mão** (é mudança de sistema).

## 5. O Quest — o que se aprendeu a duras penas

- Aceitar a caixa "Permitir depuração USB" **com "Sempre permitir deste
  computador"**; sem isso qualquer reinício apaga e, sem alguém perto do
  headset, não há como aceitar de fora.
- Se a caixa não aparece: sino de notificações; ou Configurações → Sistema →
  Desenvolvedor → **Caixa de diálogo de conexão USB** ligada; ou desligar e
  religar o modo de desenvolvedor no app Horizon; e reencaixar o cabo.
- **Meta Quest Link** aberto no PC toma o cabo e derruba o adb. Fechar.
- Aba atrás no navegador do Quest → `SecurityError` e a obra abre achatada.
  Só a aba da obra (ou instalada como app: menu ⋮ → Instalar app).
- Cache velho: com Wi-Fi, recarregar até o portão dizer a versão certa; desde
  20/09 a página se recarrega sozinha no portão quando há versão nova. **A
  5.x e o v4 têm prefixo de cache próprio**, senão uma apagava a outra.
- O GitHub Pages às vezes não monta depois do push: conferir em
  `api.github.com/repos/visoes-filmes/raizes-cosmicas-v2/actions/runs?per_page=1`
  e o `md5` do `index.html` publicado contra o commit. Um commit vazio destrava.
- Ficar acordado na mesa: `adb shell am broadcast -a com.oculus.vrpowermanager.prox_close`
  (desfaz com `…automation_disable` ou reiniciando) e
  `adb shell settings put global stay_on_while_plugged_in 7`.
- WebGL 1 + `depth-sensing` em texture-array derruba o contexto — o contorno
  pela profundidade fica desligado (`CONTORNO_PROFUNDIDADE`).

## 6. Em aberto

1. **Ver a 5.1 dentro do capacete** — as rachaduras nas paredes de verdade,
   a onda de luz da leitura, e onde a árvore-mãe caiu (nesta casa ela girou
   para o outro lado da sala: 11 móveis lidos, pouco chão livre).
2. **A interatividade, pelo relato dela**: o que exatamente "não rolava bem"
   — o serrar do toque está resolvido (5.1); casulo, concha e o rosa
   precisam de um passe com gente na cabeça.
3. **Repositórios próprios** `raizes-cosmicas-v4` e `raizes-cosmicas-v5`:
   as pastas estão montadas ao lado (`../raizes-cosmicas-v5`); falta criá-los
   vazios no GitHub e rodar `publicar_versao.py` de novo.
4. O `sw.js` guarda só o `index.html`: no estande sem rede, `v4.html`/`v5.html`
   não abrem — se a 5.x for à feira, ela vira o `index` (ou entra na lista `ESSENCIAL`).
5. Grama e solo continuam no piso (não sobem na mesa); a mão gigante por
   código, a água subindo, a vermelha a 1,5× — decisões antigas ainda abertas
   (`LEIA-ME-UNREAL.md` §6).
6. Licenças (`CREDITOS.md`): seis `magnific_*`, a crisálida e o ser sem origem.

Se algo aqui não bater com o código, **o código manda** — e este arquivo é
que precisa ser corrigido.
