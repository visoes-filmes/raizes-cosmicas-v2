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

**O Quest pelo cabo:**

```bash
python fontes/estande.py            # adb reverse: no headset, http://localhost:8765 ; os relatos saem com >>
```

Com dois aparelhos no `adb` (cabo + Wi-Fi), rodar com `ANDROID_SERIAL=<serial>`.
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
