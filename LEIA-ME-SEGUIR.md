# Seguir em outro computador — 24/09/2026 (atualizado em 25/09, 6.2)

Este é o arquivo para **mudar de máquina sem perder nada**: o que instalar,
como trazer o projeto, em que estado a obra está, como se trabalha e o que
está em aberto. Ele completa os outros; não os substitui.

> **Num PC novo, o primeiro comando é sempre:**
>
> ```bash
> python fontes/conferir_pc.py
> ```
>
> Ele confere cada peça da seção 1 e diz o que falta e como resolver. Pedido
> da direção de arte em 25/09: *"pra garantir que tudo isso vai ser lembrado
> e requisitado"*. Um chat do Claude Code aberto na pasta roda isso sozinho
> (está no `CLAUDE.md`) e **pede** o que só a pessoa pode fazer.

| arquivo | o que é |
|---|---|
| `CLAUDE.md` | as regras da casa e a tabela dos interruptores — um chat novo do Claude Code aberto na pasta lê sozinho |
| **este** | a mudança de máquina e o estado de 24/09 |
| `LEIA-ME-UNREAL.md` | o diário de 19 a 24/09: o primeiro teste em RM, o v4, a 5.0, as armadilhas, o jeito da direção de arte |
| `LEIA-ME-ACER.md` | o mapa completo da obra, arquivo por arquivo |

Peça ao chat novo para ler **este** e depois o `LEIA-ME-UNREAL.md` antes
de mexer no código.

---

## 1. O padrão de instalação (conferido por `fontes/conferir_pc.py`)

**a) Programas**

| o quê | para quê | instalar |
|---|---|---|
| Git | trazer e publicar | `winget install --id Git.Git -e` |
| Python 3.10+ (3.12 serve) + Pillow | verificar, montar, publicar, bancada, Cabine | `winget install --id Python.Python.3.12 -e` e `python -m pip install Pillow` |
| Node.js | o verificador (`node --check`) e as ferramentas do DevTools do Quest (`quest_eval.mjs`) | `winget install --id OpenJS.NodeJS.LTS -e` |
| Chrome ou Edge | oficina, bancada e a projeção em quiosque | — |
| `platform-tools` (adb) | o Quest pelo cabo e pela Wi-Fi | baixar de developer.android.com/studio/releases/platform-tools e largar a pasta em **`fontes/platform-tools/`** (fora do git). **Um adb só**: a Cabine e o scrcpy usam este (`ADB=`); dois adbs diferentes derrubam o servidor um do outro, e com ele os túneis |
| scrcpy | espelho do óculos e projeção do espelho | `winget install --id Genymobile.scrcpy -e` |
| Claude Code | o trabalho | abrir na pasta do projeto |

Login do GitHub: pedido na primeira vez que se empurra (o Git abre o
navegador). Conta **Crisia-poria**, owner da organização `visoes-filmes`.
Git precisa saber quem você é, uma vez, dentro da pasta:

```bash
git config user.name "Crisia-poria"
git config user.email "admcrisia@gmail.com"
```

**b) O Quest, uma vez por aparelho e por computador**

1. Modo de desenvolvedor ligado (app Meta Horizon no celular).
2. Cabo USB-C no computador → no capacete, **"Permitir depuração USB"
   marcando "Sempre permitir deste computador"**. Sem a caixinha, cada
   reinício do Quest pede de novo — e de longe ninguém aceita.
3. Se a caixa não aparece: o sino de notificações; Configurações → Sistema →
   Desenvolvedor → **Caixa de diálogo de conexão USB** ligada; reencaixar o cabo.
4. **Meta Quest Link desligado no PC.** Ele toma o cabo e esconde a caixa.
   Neste desktop o serviço está parado e desativado; num PC novo, no
   PowerShell **como administrador**:
   `Stop-Service OVRService; Set-Service OVRService -StartupType Disabled`.
5. A Wi-Fi é a reserva do cabo: com o Quest no cabo e a obra parada, a
   Cabine liga o `adb tcpip 5555` uma vez por inicialização, e daí em
   diante acha o óculos pelo ip (neste apartamento, `192.168.15.133`).
   Depois de reiniciar o Quest, a Wi-Fi só volta passando pelo cabo uma vez.

**c) A Cabine — o controle pelo computador** (`python fontes/cabine.py`,
página em `localhost:8790`): abre a obra no Quest, *Iniciar em RM* sem
ninguém tocar, relatos, cena, quadros, bateria, espelho e projeção. **Dois
caminhos, cabo e Wi-Fi**: se um cai, ela tenta o outro e diz na página por
que cada um falhou (cabo sem autorização, Wi-Fi fechada, sem resposta…).
A rede interna (hotspot) só existe em PC **com adaptador Wi-Fi** — este
desktop não tem; em casa não precisa (Quest e PC no mesmo roteador).

**d) Espelho e projeção**
- **Espelho** (card do Quest): janela com **um olho só** — o Quest 3 manda
  os dois olhos lado a lado (4128 × 2208), e a Cabine recorta o miolo do
  olho esquerdo em 16:9 (`1816:1020:124:594`, calculado do `wm size`).
- **Projetar** (card da Projeção): o mesmo olho em **tela cheia no monitor
  escolhido**. Ligar o projetor, **Windows + P → Estender**, escolher
  *espelho do óculos* e o monitor, *Projetar*. *Espelhar horizontalmente* só
  para retroprojeção (projetor atrás do tule). Com um monitor só, a Cabine
  avisa — a projeção cobriria a própria Cabine.
- **Testar numa janela**: o mesmo que iria ao projetor, numa janela comum
  que se arrasta e redimensiona — para conferir sem projetor.
- **Cada espelho aberto custa ao Quest**: ele codifica vídeo enquanto roda
  a obra. Um de cada vez; fechar o teste antes de medir quadros.

**e) O atalho da obra no Quest, como app**: no navegador do Quest abrir
`visoes-filmes.github.io/raizes-cosmicas-v2/`, esperar o portão, menu **⋮ →
Instalar app**. Abre sem rede depois disso. O escaneamento automático da
sala acontece **uma vez por aparelho e por endereço** (localStorage): uma no
endereço publicado, outra no da Cabine (`localhost:8765`).

**f) De longe (opcional)**: **AnyDesk** neste PC (instalado como serviço,
liga com o Windows). Falta sempre uma coisa que só a pessoa faz: no AnyDesk,
Configurações → Segurança → **Acesso não supervisionado**, com uma senha
dela. O ID do PC fica com ela — **não vai para este repositório, que é
público**. De longe: AnyDesk → este PC → a Cabine. O Quest precisa estar
ligado e no cabo (ou na Wi-Fi já liberada).

**g) Desligar o Quest pelo computador**: `adb shell reboot -p` (depois de
*Encerrar* a obra na Cabine). Religar é só no botão do capacete.

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
| **6.1** | a 6.0 + (24–25/09): escaneamento **uma vez por aparelho**; **menu da mão** (Atualizar · Sair da experiência · Remapear o espaço); sem "rizomar" — a frase fica sobre a deusa até o fim; chão do cenário 4 mais transparente (segurança); fora da área mapeada a obra esmaece em vez de sumir; halos dos astros sem sombra escura e esfera mais lisa; **tudo responde ao toque** (pedras, planetas, ser de vidro, água, gesto no ar) | é o `index` | `v6.1` |
| **7.2** | **a que está no ar** (25/09): **a deusa que dança é a cópia do ser do céu** — "uma cópia daquela deusa gigante em escala menor dançando". A malha `alien-0` (a mesma do gigante a 60 m), com a pele camuflada dele (matéria 13), **vestida nos ossos da captura por proximidade**: o esqueleto do modelo (automático, do Tripo) não casa com o da captura, então cada vértice se prende aos dois ossos mais próximos no quadro de descanso, com peso pela 4ª potência do inverso da distância. A captura foi reexportada **com rotações** (três eixos por osso → quaternião na base da obra; conferido: 1 mm de erro). Quatro lições que custaram a noite: **as proporções** — o esqueleto tem as da bailarina (quadril a 60 %, ombros no pescoço) e o modelo as dele (quadril a 50 %); presa por proximidade, a coxa pegava a bacia e tudo torcia ("parece que ela está toda torta"). O modelo é deformado na vertical por trechos até os marcos dele (joelho, virilha, quadril, ombro, queixo, topo) caírem nas juntas, e cada região (braço/perna/tronco, por lado) só pega os ossos dela; o esqueleto de descanso tem de vir para **debaixo do modelo** antes de prender (a bailarina andou; sem isso a pele explodia); a **frente se lê pelos quadris**, não pelos ombros (as clavículas Mixamo coincidem); o quadro de descanso é o **mais parecido com a pose de repouso** (em pé, braços pendendo), escolhido pelo conversor. 25 mil vértices por quadro na CPU: 0,6 ms. `raizes.dancaProva()` confere ossos e centro | `index` e `v6.html` | `v7.2` |
| **7.1** | (25/09): **a deusa que dança** (`DEUSA_QUE_DANCA`) — a captura de movimento **PraiaC0094** do `SketchbookGabi` (MetaHuman Animator, Mar de Girassóis), tirada do `.uasset` pelo Unreal 5.8 sem interface: `fontes/exportar_mocap_unreal.py` roda como commandlet (`UnrealEditor-Cmd.exe <projeto> -run=pythonscript -script=…`) **numa cópia do projeto** (`D:\_exportar_mocap_temp`, para não tocar o original) e escreve 21 juntas a 15 fps (65 s); `fontes/mocap_para_obra.py` compacta (mm em int16 base64, quadril recentrado, deslocamento pela metade) em `assets/mocap/deusa-danca.json` (128 KB), que o montador embute (`__MOCAP_DEUSA__`). Na floresta do começo, à frente e à direita (azimute 40°, 2,3 m), flutuando a meio metro do chão, 1,2 m de altura: silhueta de vidro de água (matéria 20) feita a cada quadro de vinte cápsulas, com um coração de luz no peito; acende com a mão, tocada pulsa e soa (`TOCOU-A-DEUSA-QUE-DANCA`). Dos 0:40 aos 0:54, e vai com a floresta. Para trocar a captura: outro `CANDIDATOS` no script do Unreal, ou um BVH pronto (há `IMG_4750` e `WhatsApp_0719` em `Mar de Girassois\mocap-tool`) convertido para o mesmo JSON | `index` e `v6.html` | `v7.1` |
| **7.0** | (25/09): **a versão para celular — a janela mágica** (`CELULAR`, detectado por toque grosso + navegador de celular, nunca no Quest). Sem RM nem mãos, o telefone usa o que tem: a **câmera de trás** faz o passthrough (`<video id="cam">` atrás do canvas, alfa zero), o **giroscópio** move o olhar (zero no primeiro quadro; botão **Centrar**), arrastar gira, e o **toque faz as vezes da mão**: um raio da tela ao mundo pousa a mão no alvo tocado (toque, chamado, sons); segurar o rosa pega e arrastar leva; dois dedos dimensionam; passar o dedo por um planeta bate. Botões de emergência maiores. Neblina de RM, resolução capada (1,25 dpr), lente de 65° na largura. Portão: "Iniciar no celular". **Provado só na bancada emulando um Android** (toque num cogumelo → `TOCOU-UM-COGUMELO`); câmera e giroscópio só num aparelho de verdade — no iPhone o giroscópio pede licença e a tela cheia não existe. Relatos `JANELA-MAGICA`, `GIRO`, `CAMERA-DO-CELULAR` | `index` (o mesmo endereço) | `v7.0` |
| **6.9** | (25/09): **os planetas batidos** — "quando você bate neles eles podem reagir com física e ricochetear nas paredes, menos o rosa". A mão que chega a um planeta a mais de 35 cm/s o empurra na direção da batida (até 4 m/s), com som e pulso; solto, ele voa sem gravidade, com freio de ar leve, e **quica no chão, num teto de 2,55 m e nas paredes de verdade** (contorno do chão lido pelo Quest; sem leitura, caixa de 3,8 m), perdendo um quinto a cada quique, que soa baixinho. Dez segundos depois da última batida volta à órbita. Os três vieram para o alcance do braço (órbita 1,6–1,9 m, altura 1,6–2,0; dispersos 1,8–2,3 m). Relato `BATEU-NO-PLANETA` | `index` e `v6.html` | `v6.9` |
| **6.8** | (25/09): **o horizonte desenhado** (`HORIZONTE_DESENHADO`) — "as montanhas do início ficam transparentes; era para ser um horizonte, pode ser sem assets". No lugar do modelo (a 58 %, sumindo pela base), três cordilheiras feitas em código, em anel a 36, 52 e 70 m, **opacas**: a de longe azul mais clara, a de perto quase preta, cristas recortadas com um fio de luz. A base fica **na linha do horizonte** (altura dos olhos): abaixo dela continua a sala. Anda com o olho; nasce com o mundo (0:16–0:32) e vai com a floresta (3:06–3:18) | `index` e `v6.html` | `v6.8` |
| **6.7** | (25/09): **o planeta rosa com perspectiva certa** — "continua com problema de perspectiva". Os planetas eram desenhados na ordem da lista, com o rosa (gasoso, sem profundidade) primeiro: um planeta **mais longe** desenhado depois passava **por cima** dele. Agora são desenhados de trás para a frente, refeito a cada quadro. E o **miolo denso do rosa grava profundidade** numa segunda passada sem cor (a borda continua macia): seres, buracos, poeira e neblina atrás dele deixam de aparecer por cima. Na mão, não (esconderia o contorno da mão) | `index` e `v6.html` | `v6.7` |
| **6.6** | (25/09): **a cena final em RA** — "está completamente em RV, o que é perigoso". O céu do cenário 4 ia a 45° abaixo do horizonte (cobria o chão de 1,6 a 3 m dos pés e as paredes inteiras); agora é **só no alto** (`ini:0.16, fim:0.42`: transparente abaixo de 14°, cheio a 38° — a faixa meio transparente fica acima da cabeça, e não na altura dos olhos, que era a "mancha cinza" de 13/09): chão e paredes são a sala real. As **deusas cedem do horizonte para baixo** e só são inteiras a 8° acima (as três, em todos os cenários). O **teatro de papel** vira papel de seda no óculos (70 %, e 28 % abaixo da linha dos olhos) e é desenhado no fundo, logo depois das deusas — a frase final não fica mais por trás dele | `index` e `v6.html` | `v6.6` |
| **6.5** | (25/09): **as deusas no fundo** — eram desenhadas depois dos planetas e sem profundidade, e o **planeta rosa** (gasoso, de propósito sem profundidade) e os halos também não gravam: a pintura a 50 m passava por cima do planeta a 2 m. Agora as figuras e os enfeites delas vêm logo depois do céu, antes de tudo o que é perto. **A borboleta desvirada**: a batida passava dois terços do tempo com as asas penduradas abaixo do corpo (lê como virada) — agora golpe rápido para baixo e volta lenta ao V nas costas; e o corpo segue o rumo horizontal com inclinação de no máximo ~30°, em vez da direção do voo (na subida vertical o "cima" perdia a referência) | `index` e `v6.html` | `v6.5` |
| **6.4** | (25/09 — nada visto no óculos ainda): **o céu do começo em camadas, sem imagem** (`CEU_EM_CAMADAS`): nebulosa azul suave gerada ao carregar, poeira azul em 16 mil grãos, 2600 estrelas cintilando e sete rios de luz iridescentes com galhos, na paleta da pintura (coral, dourado, azul-claro, violeta), que se desenham dos 0:20 aos 0:44 — nítidos em qualquer resolução. **Os seres de luz** agora são oito, de 3 a 7 m (além das paredes), e **um de cada vez vem rodear quem visita, curioso**: chega em 7 s, dá uma volta e pouco a 0,95 m na altura do peito, com um som ao chegar, e volta; tocado, foge. Águas-vivas até 5 m | `index` e `v6.html` | `v6.4` |
| **6.3** | (25/09, madrugada, feita com o Quest desligado): **o mar vivo** — cogumelo e plantas gigantes mais longe (anel de 2,05 a 3,4 m) e maiores, normais alisadas, desenhados dos dois lados e com a pele respirando (`bolha`); **cores análogas** por objeto no fundo e nas águas-vivas (`familiaDoMar` no `FS_SOLIDA`: rosa/coral, magenta/violeta, turquesa/azul, lilás/rosa-claro); tudo no mar **acende com a mão** (`maoA`/`maoB`) e **pulsa rosa ao toque, com nota** (gigantes, águas-vivas, seres de luz); as águas-vivas **fogem da mão**. **Seres de luz novos** (matérias 20 e 21, feitos em código em `montarSeresDeLuz`): três ctenóforos com fileiras de arco-íris correndo e sementes de luz, três sinos de sementes com fios acesos; nadam em volta, acima da lâmina, e **escapam quando tocados**. **O ser gigante** (o camuflado do céu) **nada** — deriva de metros, braços ondulando, respiro — e é pintado **numa demão só** (stencil: sem as manchas escuras das dobras; a camada do headset agora pede `stencil: true`). **As deusas vermelha e azul com vida** (`vida` no `FS_FIGU`): manto e cabelo ao vento, respiração, luz subindo pelo corpo | `index` e `v6.html` | `v6.3` |
| **6.2** | (25/09, madrugada): no cenário da deusa a floresta **continua pendurada no teto**, agora **sólida**, com o pé se desfazendo no céu e **folhinhas nas copas**; **os cogumelos voltam** no chão desse cenário; **sem a linha preta em volta do Sol** (a corona passa a ser desenhada antes do corpo); **conforto**: neblina com 4 camadas em RM (era metade da placa de vídeo), foveação fixa 0,75, resolução que cede sozinha (piso 0,75); **menu pela seta da mão + pinça-e-solta**, mais longe e com texto nítido | `index` e `v6.html` | `v6.2` (a marca ficou no primeiro envio da 6.2; as correções da mesma noite vieram logo depois, em `main`) |

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

**Toda publicação marca a anterior** (`publicado-<versão>`); voltar é
`git checkout publicado-…`. O número do commit e da versão de cache no ar
se leem com `git log -1` e no `sw.js` — não se escrevem aqui, envelhecem.

**Regras que a direção de arte deu e que valem sempre:**
- tudo o que for feito localmente vai para o repositório na hora (commit + push), sem esperar pedido;
- cada rodada grande ganha **número de versão novo** e uma marca (`git tag`) — a próxima é a **7.3**;
- **segurança antes de efeito**: em nenhum cenário o céu, as deusas ou o papel podem tapar o chão ou a linha dos olhos (6.6) — quem está de óculos precisa ver onde pisa;
- o padrão de instalação desta seção 1 é conferido em todo PC novo (`fontes/conferir_pc.py`), e o que faltar é **pedido** a ela.

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
**Atenção:** `adb tcpip 5555` reinicia o adb do óculos; se a caixa de
depuração foi aceita sem "Sempre permitir", a autorização cai e volta a
"unauthorized". Por isso, desde 25/09, a Cabine **não** roda o `tcpip` a
cada vez que vê o cabo: só uma vez por inicialização do Quest, e só com a
obra parada.
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
- **Servidor da Cabine com `no-cache`**, nunca `max-age`: com uma hora de
  validade o Quest continuou abrindo a 6.0 com a 6.1 no ar. O portão diz a
  versão no título — conferir antes de avaliar qualquer mudança.
- **Enjoo é quadro perdido.** Medir assim, com a pessoa dentro da obra:
  `adb logcat -d -s VrApi | tail` → `FPS=` (quadros), `App=` (tempo da
  **placa de vídeo** da obra, o limite a 72 Hz é 13,9 ms), `GPU%`/`CPU%`
  (quem é o gargalo), `Stale=` (quadros repetidos — é o que enjoa), `SF=`
  (a escala de resolução em uso), `Fov=` (foveação). Para achar o culpado,
  desligar uma camada por vez pelos botões da página (`bFiguras` = neblina,
  `bPoeira`) com `node fontes/quest_eval.mjs` e ler de novo. Em 25/09 isso
  mostrou em um minuto que **a neblina custava metade da placa** (15 → 8 ms)
  e a poeira nada. Nesta obra o gargalo é a placa de vídeo (GPU 99 %, CPU 15 %).
- A RM leva uns dois segundos para assentar (o Quest lê a sala): quadros
  medidos nesse começo não valem.

## 6. Em aberto

**A primeira coisa da próxima sessão — conferir a 6.2, a 6.3 e a 6.4 no
Quest, com ela dentro** (as três foram feitas sem ver o óculos; a bancada
provou desenho, toque e shaders, mas **passthrough e quadros só o Quest**).
Na 6.4: o céu em camadas no começo (nitidez, o brilho dos rios de luz sobre
a sala, o degradê perto do horizonte) e a visita dos seres de luz no mar
(a distância de 0,95 m é confortável? o som ao chegar):

a. **Os quadros**, cenário a cenário (`VrApi`: `FPS`, `App`, `Stale`), e o
   relato `STENCIL sim`. **O mar rosa ficou mais pesado** na 6.3 (seis seres
   de luz, gigantes dos dois lados, águas-vivas com mão): se cair abaixo de
   72, medir camada a camada como se fez com a neblina e aliviar o que pesar.
b. O mar: gigantes mais longe e maiores ainda "geométricos"? (o contorno é
   do modelo; o que se podia fazer em código foi feito: alisar, dois lados,
   respirar); as cores análogas; o toque e o chamado; as águas-vivas
   fugindo; os seres de luz e a fuga deles.
c. O ser gigante nadando, e **sem as manchas escuras** (no cenário 3, onde o
   céu é pintado; no 2 ele fica invisível de propósito).
d. As deusas vermelha e azul com vida — se ainda parecer pouco, a
   intensidade é o `vida` de cada uma em `FIGURAS` e os números do bloco
   "A VIDA DO CORPO" no `FS_FIGU`.
e. A floresta do teto sólida com folhinhas e os cogumelos no cenário da
   deusa, o Sol sem a linha preta, e o menu pela seta + pinça.

**De antes:**

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
