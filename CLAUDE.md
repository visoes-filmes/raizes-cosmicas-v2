# Raízes Cósmicas v2 — regras da casa

Obra de realidade mista para Meta Quest 3, em WebXR. Dez minutos, quatro
cenários, 3 × 3 m caminháveis. FIL 2026. HTML único, sem build, sem npm.

Migrando para o MacBook Pro em 24/09: **`LEIA-ME-MACBOOK.md`** primeiro
(e `LEIA-ME-VOLTAR-AO-DESKTOP.md` para o que aconteceu nesse dia).
Para seguir em outra máquina: **`LEIA-ME-SEGUIR.md`** (o que instalar, o
estado, como se trabalha). O mapa completo está em `LEIA-ME-ACER.md` — **leia-o antes de mexer no
código de verdade.** Este arquivo tem só o que não pode ser esquecido nem
por um minuto.

> **No começo de toda sessão, num computador que ainda não foi conferido:**
> rode `python fontes/conferir_pc.py` e **peça à pessoa**, uma a uma, as
> peças que ele apontar como faltando e que só ela pode fazer (administrador,
> senha, aceitar a depuração no capacete marcando "Sempre permitir",
> desligar o Meta Quest Link, a senha de acesso não supervisionado do
> AnyDesk). O resto, instale você. O padrão completo — programas, Quest,
> Cabine, espelho de um olho só, projeção e janela de teste, atalho como
> app, acesso de longe — está no `LEIA-ME-SEGUIR.md`, seção 1. Pedido dela
> em 25/09: "pra garantir que tudo isso vai ser lembrado e requisitado".

---

## As três regras invioláveis

**1. Nunca edite `index.html`.** Ele é gerado. Toda edição vai em
`fontes/mr.template.html`. Editar o index funciona até a próxima montagem,
que apaga tudo.

**2. Nunca use `gl.blendFunc` cru.** Use `sobrepor()` ou `somarLuz()`. A
mistura comum eleva o alfa ao quadrado, e como o quadro do headset começa
com alfa zero, tudo que não for quase opaco **some**. No computador o
defeito é invisível.

**3. Sempre verificar antes de montar:**

```bash
python fontes/verificar.py
python fontes/montar_mr.py
```

O verificador só reclama do que já quebrou esta obra alguma vez. Se ele
apontar algo, conserte antes de montar.

---

## Publicar

```bash
python fontes/publicar.py "o que mudou"
```

Um comando só, e ele faz na ordem: verifica, **marca o que está no ar**,
monta, commita, empurra. Se o verificador reclamar, para antes de publicar
qualquer coisa.

**Toda publicação guarda a anterior.** Antes de empurrar, o commit que está
no ar ganha uma marca com o nome da versão de cache dele —
`publicado-2026-09-07ci`. Voltar é `git checkout publicado-2026-09-07ci`. O
nome é a versão e não a data porque é a versão que o headset pede: quando
alguém disser "no aparelho está a de ontem e quebrou", o nome está escrito na
tela do relato.

À mão eram três comandos decorados e o backup era o quarto — o que se
esquece.

**A versão do cache se troca sozinha.** O montador gira o `VERSAO` do
`sw.js` a cada montagem (data + letra). Ela existe porque o service worker
serve cache primeiro e o nome do cache *é* a versão: sem trocá-la, o headset
continua servindo a obra antiga e a nova nunca chega lá. Era feito à mão, e
à mão significa esquecer — já se perdeu uma tarde olhando um defeito que
estava corrigido havia meia hora.

GitHub Pages serve a pasta como está. Sem build, sem Actions — Actions foi
tentado e falhou (token padrão é só de leitura), removido de propósito.

Conta: **Crisia-poria**, owner da organização `visoes-filmes`.

---

## O andaime de ateliê — fora da obra

Régua, medidores, interruptores e o botão que os chamava **não existem para
quem visita**: nem escondidos, nem a uma tecla de distância. Isto é um
ambiente, não um editor.

Para trabalhar, troque `ANDAIME = false` para `true` em
`fontes/mr.template.html` e monte de novo: volta a régua (clicar salta para
qualquer ponto — sem ela não há como alcançar um cenário que só acontece aos
6:30), os medidores e a tecla `H`.

Ficam sempre, porque são de quem opera a sala e não de quem edita: os **dois
de emergência** — reiniciar (leva a obra ao zero sem fechar a RM) e encerrar.
Eles só aparecem **depois** que a obra começa, e vivem na página, não dentro
do headset.

## O que o Quest faz e ninguém espera

**A regra que custou uma noite inteira: em WebXR, nunca `await` em nada de
que a obra não precise para existir.** Três promessas penduraram no Quest
num único dia — `dom-overlay`, o pedido de permissão, e
`updateTargetFrameRate`. Elas não resolvem, não falham, e **`try` não pega
promessa que nunca volta**. A terceira travou a obra com a sessão já aberta:
tela preta, mãos aparecendo por cima, e nenhum erro em lugar nenhum.

**Nenhum DOM existe dentro do headset.** O navegador do Quest não suporta
`dom-overlay` em `immersive-ar` — e pendura em vez de recusar. O que precisar
ser tocado dentro da obra tem que ser **desenhado na cena**.

**Nada em `requiredFeatures`.** Exigir significa "se não puder dar, não abra
nada". Tudo é opcional; o que vier, vem. Medido no aparelho, o Quest concede:
`viewer, plane-detection, webxr, hit-test, anchors, local, local-floor,
hand-tracking` — e 72 Hz.

**O chão pode faltar.** `local-floor` só existe quando o Quest mapeou o
espaço. Sem ele, cai-se em `local` deslocado pela altura dos olhos: a obra
abre torta em vez de não abrir.

**A permissão é humana e não tem pressa.** O Quest mostra a caixa dentro do
capacete e a promessa espera. Qualquer prazo curto aí não é prudência, é
sabotagem — e o pedido pendurado ainda envenena todos os seguintes, porque o
aparelho só admite uma sessão por vez.

**A entrada em RM não é condição para a obra existir.** Recusada, ela corre
na tela com o motivo escrito no portão.

---

## No estande — e no aparelho

**No estande a obra não depende de rede.** Ela é carregada **uma vez** do
endereço publicado, e a partir daí mora no aparelho:

1. no Quest, com rede, abrir `visoes-filmes.github.io/raizes-cosmicas-v2/`
2. deixar carregar até o portão aparecer — é aí que o guardião termina de
   guardar
3. vale instalar como app: o manifesto já está pronto, e origem instalada
   tem prioridade maior contra despejo
4. desligar a rede. Reiniciar quantas vezes quiser

**Carregue o headset por último**, depois de tudo publicado: o nome do cache
*é* a versão, e um headset carregado antes continua servindo a de antes —
ótimo durante o evento, e um problema se você quiser a nova.

Duas coisas fazem isso ser verdade, e as duas foram consertadas em 08/09:

- **a obra pede armazenamento durável** (`navigator.storage.persist`). Sem o
  pedido, o navegador pode apagar o cache por conta própria quando o espaço
  aperta — e esse modo de falhar só aparece no dia, no estande, com fila;
- **o cache guarda UMA cópia.** Havia `./` e `./index.html`: mesmo corpo de
  oito megabytes, duas entradas. Quem cobre o `./` agora é o desvio de
  navegação no `sw.js` — qualquer navegação no escopo é respondida pela
  única cópia. É isso que faz a obra abrir com o aparelho sem rede: a
  navegação nunca chega a consultar a rede, então não importa que o DNS não
  resolva.

**No dia, o computador do estande roda a Cabine** (24/09):

```bash
python fontes/cabine.py       # obra em 8765 (modo estande) + página de controle em localhost:8790
```

Rede interna (o hotspot deste Windows), Quest (cabo → *Liberar Wi-Fi* →
sem cabo), abrir a obra no capacete, *Iniciar em RM* daqui, relatos, cena,
quadros e bateria — tudo em botões. No Lenovo há um atalho na área de
trabalho. Detalhes no `LEIA-ME-SEGUIR.md`, seção 4.

**Testar no aparelho à mão é pelo cabo:**

```bash
python fontes/estande.py
```

`adb reverse` abre um túnel ao contrário: dentro do headset o endereço é
`http://localhost:8765`. E é o **localhost** que resolve o problema difícil
— WebXR só existe em contexto seguro, https pede certificado, mas localhost
já é seguro por definição. O botão de entrar em RM aparece direto, sem
certificado, sem aviso, sem ninguém aceitar nada dentro do capacete. Pela
Wi-Fi o endereço passa a ser um IP, IP não é contexto seguro, e sem
certificado o botão **não existe**.

O `adb` não vem com nada: baixe o `platform-tools` e largue a pasta em
`fontes/`. O script diz o caminho exato se não achar. E no headset, uma vez:
modo de desenvolvedor ligado.

Nesse modo o cache fica **ligado**: oito megabytes num arquivo só, e sem
cache cada abertura espera o download outra vez.

**Só para testar na tela:**

```bash
python fontes/servir.py 8766        # CERT=<pasta> para HTTPS na rede
```

Um servidor por pedido, sem cache. O de prateleira (`http.server`) atende uma
conexão por vez, e com 8 MB num arquivo só o Quest desiste no meio — aparece
como "carrega as imagens e nada acontece".

**Ele também recebe fotos.** Um `POST /_foto/<nome>` grava o corpo em
`_fotos/`. A obra tira o quadro de dentro do WebGL e manda para cá, e o
quadro vira arquivo — serve para mostrar como algo ficou sem depender de
captura de tela. É o mesmo bilhete-pela-janela dos relatos, com imagem em
vez de texto. Andaime de ateliê: produção é GitHub Pages, que serve arquivo
parado e não recebe nada.

**A obra relata o que acontece dentro do headset** pedindo `/_relato/…` ao
servidor: cada passo sai no log com `>>`. Dentro do capacete não há console,
e a depuração remota do Quest cai com facilidade. É bilhete jogado pela
janela, e funciona quando o resto não.

> **Produção é só `visoes-filmes.github.io`.** Qualquer outro endereço é
> teste. A regra já foi `localhost` e furou no primeiro teste pela rede: a
> obra se achou publicada, guardou cache e calou os relatos.

---

## Os interruptores

Todos no alto de `fontes/mr.template.html`, e todos pedem montar de novo.

| interruptor | hoje | o quê |
|---|---|---|
| `ANDAIME` | `false` | `true` devolve régua, medidores e a tecla H |
| `MATA_SOLIDA` | `true` | a floresta como superfície; `false` volta à nuvem de pontos |
| `POEIRA_NA_FLORESTA` | `true` | a poeira cósmica no cenário 1 |
| `PEDRAS_NO_CHAO` | `true` | as onze pedras — **separado de propósito**: foram pedidas depois de o chão ser limpo, e apagá-las junto com a grama seria desfazer o pedido novo com o interruptor do velho |
| `COGUMELOS_NO_CHAO` | `true` | os treze cogumelos |
| `SER_NO_CEU` | `true` | o ser camuflado no céu — **separado pelo mesmo motivo**: estava atrás do interruptor do chão, e por isso ninguém nunca o viu |
| `OBJETOS_NO_CHAO` | `false` | grama, folhas, trevo e soja como nuvem de pontos |
| `ARVORE_MAE` | `1` | 1 é a de sempre; 2 é a árvore da vida, com a raiz como espelho da copa |
| `PAPEL_NO_CENARIO` | `true` | o teatro de papel do cenário 4: as ondas do quadro de 186 s cortadas em cinco camadas com os portais vazados (`fontes/teatro_de_papel.py`) — os planos com borda rasgada saíram em 13/09 |
| `CONTORNO_PROFUNDIDADE` | `false` | o fio de luz em volta de qualquer corpo que entre na visão, pelo mapa de profundidade do Quest (`depth-sensing`). **Desligado em 20/09**: o Quest 3 entrega o mapa como texture-array, o WebGL 1 não tem isso e o contexto inteiro caía no primeiro quadro em RM. Só religar com WebGL 2 ou `cpu-optimized`, provado no aparelho |
| `CONTORNO_MAOS` | `true` | o contorno das mãos pelas juntas rastreadas — só quando o mapa de profundidade não vem |
| `ESPACO_ESCANEADO` | `false` | **o v4**: a obra lê os planos do aparelho e se planta no espaço de verdade — o que é pequeno pousa na superfície que estiver embaixo (chão, mesa, banco) e as árvores procuram chão livre, sem móvel embaixo. O montador escreve `v4.html` com ele ligado; a obra de sempre não muda. Sem espaço configurado no Quest não vem plano nenhum, e o v4 é idêntico ao v2. **A 6.0 sai com ele ligado** (24/09, à noite: "é importante para reconhecer os espaços e objetos"), e desde então, em RM, **seis segundos sem plano nenhum abrem a Configuração de Espaço do Quest** por cima da sessão (`initiateRoomCapture`, uma vez por sessão, sem `await`) — e na 6.0 também **doze segundos com sala lida e nenhum plano rotulado como tela**, para marcarem a tela de projeção; pela Cabine, `raizes.escanear()` |
| `PAREDES_RACHADAS` | `false` | **a 5.0** (pede `ESPACO_ESCANEADO`): as paredes lidas viram tampa — alfa zero (a câmera) escrevendo profundidade — com rachaduras e buracos descartados por onde a outra realidade aparece, e um fio de luz na borda. Abrem cenário a cenário (`aberturaDasParedes`) e no papel quase somem. O teto não recebe tampa: é o único espaço 100 % VR. Sem paredes lidas, nada muda |
| `NEBLINA_FATOR` | `1.0` | multiplica a neblina de todos os cenários; a 5.0 sai com 0,5 ("diminua a névoa para ficar mais limpo") |
| `TELA_DE_TULE` | `false` | **a 6.0** (o montador liga em `v6.html`, sobre a 5.2): a obra acha a tela de tule real (o plano vertical que a Configuração de Espaço do Quest rotula como tela/janela/quadro, ou dois cantos beliscados pelo operador via Cabine), estica nela o vídeo `assets/video/odara-cosmos.mp4` e cada toque da mão vira onda. As ondas são soma de anéis no shader (`FS_TELA`), sem simulação em textura, de propósito: a página `projecao.html` faz a mesma conta a partir dos relatos `TOCOU-A-TELA` e joga a mesma água no projetor. **O vídeo não é embutido** (70 MB): mora em `assets/video/` e é servido ao lado |
| — | — | **O que está no ar (`index.html`) é a 8.9** (26/09 — da 6.2 à 8.9 ainda não foram vistas no Quest; **a 8.9**: o epílogo de 12 s depois da frase (`fecho` só aqui, `estrelasFim`, `nomeFim` com `texTitulo` + Visões Filmes; a obra para aos 10:26 na sala real), as faces da asa da borboleta desfeitas (azul na normal +y), e `TAMPAR_A_TELA` (a tela lida vira janela para o céu — **desligado** na 8.9b: lia como retângulo preto; a tela de tule sem vídeo agora é transparente, só com as ondas do toque); **a 8.8**: as três deusas pintadas em código ao carregar (`FIGURAS_EM_CODIGO`, `pinturaEmCodigo`, `gerarDeusaGalactica/Vermelha/Integra`; o montador deixa os JPEG de fora, 11,1 → 9,0 MB; **sem mipmap**: 1280 de altura não é potência de dois e a textura sairia preta), **as deusas híbridas (26/09, à tarde)**: em código o corpo virava mancha ("as deusas sumiram"), então `FIGURAS_EM_CODIGO = false` devolve as pinturas e `FIGURAS_HIBRIDAS` mistura — **o corpo é a pintura** (a elipse `nucleo` de cada uma) e **em volta a simulação da 8.8** (`FIGS_SIM`, na **unidade de textura 8**: 0 a 7 têm dono; com menos de 9 unidades fica a pintura inteira), com o quadro recuando a véu (`misturaSim` = véu, força; a vermelha 0,42/0,72 e com o manto e o barco pintados); o custo ao carregar sai no relato `DEUSAS-HIBRIDAS` (0,8 s no Mac); **o rosa não gruda** (26/09): só o pinça pega (pousar não pega mais), abrir a mão solta sempre, 1 s sem poder repegar, encostar sem pinça empurra a casca como bolha, e 15 s de pinça seguido soltam sozinhos (rastreio que prende o aperto); sem o buraco negro (`BURACOS_NEGROS`), sem pedras debaixo d'água, tamanduá de uma cor só com padronagem e destravado, estrelas do chão a partir de 1,5 m, e o espelho alinhado com o QR do site e a animação quando a captura acaba; **a 8.7**: o mar visto de dentro — `NIVEL_AGUA` 2,35 m (acima da cabeça), `NIVEL_COISAS` 0,80 para o que se toca, azul dos sólidos por distância com o olho dentro (`dentroDagua` no FS_SOLIDA), véu do mergulho mais leve; **a 8.6**: os planetas orbitam mais baixo (1,28–1,55 m) e mais perto (1,4–1,65 m) com sobe-e-desce de 30 cm (`ondeEsta`, fase B e C); **estrelas no chão** do cosmos (`montarEstrelasDoChao`, 420 pontos no `progPo`, com os planetas); **a 8.5**: as ondas do fim são meio-discos cheios com a base dissolvendo (matéria 25, `hA`), 6 a 12 por fileira; as plantas grandes do mar a 3,4–5,0 m; o céu do planeta rosa com `ini` 0,10 / `fim` 0,52; **as músicas de cada cenário** (`TRILHAS_DA_CENA`: `assets/audio/trilha-2-planetas.mp3` = Raízes Mar B nos planetas, `trilha-3-mar.mp3` = Raízes Cosmos A no mar, cross-fade de 10 s, o laço cede; **não embutidas** — servidas ao lado e listadas no `sw.js`); e o crescimento sem fitas ao chão (`kFrente` no VS_SOLIDA); **a 8.4** (a lista da manhã de 26/09): a vitrine só com estrelas (`ligarVitrine` aos 0:04) e o crescimento de volta (`iniciarObra` zera `crescimento` — a vitrine deixava a floresta feita); as deusas com `satura`, `manchas` e `juntas` (FS_FIGU: a vermelha 35 % maior e a 0,72 de saturação, manchas de aquarela no escuro do quadro, mãos e rosto girando em volta de si); o céu do planeta rosa mais alto (`alto` nas `CENAS`) com estrelas miúdas piscando; o mar a 0,58/0,86 com iridescência leve; a saída do mar pela água subindo (`nivelExtra` + 2,6 m dos 8:20 aos 8:46, presenças até 9:00, `lamina` enquanto houver água); **os corais vivos** (`CORAIS_VIVOS`, matéria 27, opacos e bioluminescentes, tocáveis, azulam só 10 %); o cenário final mais longe (íntegra a 52 m, `FILAS` ×1,3, papel ×1,3 e 15 % menor); e as galáxias do céu final girando (`giraAng`, `GALAXIAS_ST`, seis centros em coordenadas da textura); **o espaço de cada corpo** (8.3, `separarOsCorpos`/`afastar`/`TUFOS_CHAO`; bancada `raizes.espaco()`, `raizes.dentro()`): nada entra em nada — cogumelos em duas faixas (perto 1,3–1,7 m, meio 1,9–2,6 m) e os tufos de folhas, agora **todos no chão** ao pé das árvores, se espalham antes de nascer, com 1 m livre em volta de quem começa e 30 cm das paredes lidas; quem anda (tartaruga, tamanduá, coruja, abelha, vagalumes, seres de luz, planetas soltos) sai de tronco/chapéu/pedra/tufo a cada quadro — galhos e copas não contam, e o poleiro de destino é porta; plantas nas paredes até nove, menores; **o céu desce mais** (`ini/fim` nas `CENAS`; −0,42 com paredes); **o tamanduá de olhos de caracol** (8.2, dentro de `VIDA_NA_FLORESTA`, matéria 26, `montarTamandua`/`andarTamandua`): anda até um cogumelo pela lateral (lado fixo por cogumelo, contornando quem está no centro), ergue o focinho e lambe o chapéu três vezes — o cogumelo muda de cor (`cogPolenEm`) e há um estalinho —, depois escolhe outro a mais de 1,9 m; tocado, recolhe as hastes dos olhos como caracol, para e segue; **os céus em código** (8.1, `CEU_EM_CODIGO` no template e `CEUS_EM_CODIGO` no `montar_mr.py`): o cósmico e o rosa são gerados ao carregar (`gerarCeuCosmico`, `gerarCeuRosa`, `ceuEmCodigo` com carimbos gaussianos a 2048×1024) e as quatro pinturas saíram do arquivo (13,1 → 11,1 MB; `TEX_TOTAL` 18 → 14); **o cenário 4** sem as árvores do teto (`ARVORES_NO_TETO`) e sem cogumelos (`COGUMELOS_NO_FIM`), com os **arcos d'água** (`ARCOS_NO_FIM`, `montarArcos`, matéria 25): seis fileiras de semicírculos de 6 a 31 m, azul-turquesa com borda de ouro e pontos, convergindo para a deusa, boiando, véu abaixo da linha dos olhos; **a gigante viva** (8.0): o ser do céu passou a usar a mesma pele por proximidade e a mesma captura da dançarina (`vestirCorpo`, `GIG`, `andarAGigante`), a um quinto da velocidade, 55× (topo a ~65 m), virando devagar para onde a pessoa está e com a cabeça inclinada para olhá-la; `bAlien` fica só de reserva se a captura faltar; **a vitrine** (7.9): atrás do portão a obra fica viva, parada aos 0:40 do roteiro com a câmera olhando para cima entre as árvores e girando devagar — `ligarVitrine`, `vitrine`; o portão virou vinheta translúcida; **a obra voltou a durar dez minutos** na 7.8 (durou seis da 7.3 à 7.7) — a partitura sempre foi escrita em 600 s de roteiro, ver `DURACAO_REAL`; a 7.0 abre também no celular, como janela mágica (`CELULAR`, `iniciarCelular`, `maoDoCelular`) — o mesmo arquivo, o mesmo endereço; os planetas 1 a 3 têm física quando batidos (`SOLTOS`, `baterNosPlanetas`, `andarPlanetasSoltos`), o rosa não; **os planetas são desenhados de trás para a frente** e o miolo do rosa grava profundidade — translúcido fora de ordem passa por cima do que está na frente; **as deusas e o teatro de papel são desenhados logo depois do céu**, antes de tudo o que é perto — não os mova para depois: o planeta rosa não grava profundidade e ficaria por baixo delas, e a frase final ficava por trás do papel. **Nenhum cenário é mais "céu inteiro"**: desde a 6.6 o cenário 4 também tem o céu só no alto — o chão e a linha dos olhos são sempre a sala real, por segurança; ver `LEIA-ME-SEGUIR.md` §6; o corpo da 6.x desde 24/09 à noite): o montador escreve o index com o corpo da 6.x e o prefixo de cache de sempre; `v6.html` é o mesmo corpo com cache próprio, para a Cabine. O número da versão está em `montar_mr.py` (título, portão) e nos rótulos de `cabine.html` — trocar os dois a cada rodada |
| `TELA_VISIVEL` | `true` | o vídeo e a água **dentro do óculos**. O `v6.html` sai com `false` — "o vídeo não precisa aparecer dentro do óculos, ele já vai ser visto na realidade; a tela tem que ser reconhecida para, ao tocar, o vídeo reagir como água" (24/09). Invisível, o Quest nem baixa o vídeo: reconhece a tela, lê o toque, e a água é do projetor. `raizes.tela.ver(true)` pela Cabine liga só para conferir o encaixe |
| `TELA_LARGURA` / `TELA_ALTURA` | `3.0` / `2.0` | metros, quando a tela é cravada pelos cantos ou ditada; o escaneamento traz a medida real |
| `TELA_QUANDO` | `'cosmos'` | quando a tela acende: `'cosmos'` (3:06 a 6:32), `'papel'` (8:40 em diante) ou `'sempre'`; a Cabine força acesa/apagada por cima |
| `TELA_VIDEO` | `./assets/video/odara-cosmos.mp4` | o desenho da Odara (1920×1080, 24 fps, 4 min, sem som, em loop) |
| `DURACAO_REAL` | `600` | **dez minutos de novo** (7.8, "agora tem mais elementos para ver"; foi 360 da 7.3 à 7.7). A partitura continua em 600 s **de roteiro** — `DURACAO`, os `MOMENTOS`, todo `rampa(a, b, t)` — e o relógio do roteiro anda `RITMO = DURACAO / DURACAO_REAL` por segundo real. Não reescreva instantes: mude só este número. O que lê `relogio`/`dt` (ondas, seres, física dos planetas) é tempo real e não acelera; `TRAVESSIA` e os 14 s da frase são reais. `raizes.onde()` traz `tempo` (roteiro) e `real` |
| `ESCALA_DESENHO` | `1.0` | fração da resolução nativa do olho em que a obra é desenhada (`framebufferScaleFactor`). **Medido no Quest em 24/09:** 1,0 → floresta 35, planeta rosa 17 quadros; 0,8 → 46/23; **0,7 → 54/26, e com as paredes tampando o que está atrás, 58/47**. A 5.0 sai com 0,7 |
| `SUAVIZAR_RM` | `true` | o multisample 4× da camada do headset. Medido: desligar **não** muda os quadros (32/17) — fica ligado |
| `FOVEACAO` | `0.75` | foveação fixa da camada do headset (`fixedFoveation`): a borda de cada olho com menos pixels. 1,0 borrava o que se vê de canto ("qualidade baixa", 25/09) |
| `ESCALA_VIVA_MIN` | `0.82` | a resolução que cede: por cima da `ESCALA_DESENHO`, cada olho encolhe um degrau (`requestViewportScale`) quando os quadros caem abaixo do alvo por um segundo, e cresce de volta depois de seis segundos com folga; ignora os 5 s da partida. Relato `RESOLUCAO` |
| `VIDA_NA_FLORESTA` | `true` | **a vida miúda do cenário 1** (7.4, 25/09 à noite — "trazer mais vida, está monótono", cor complementar, público criança): 84 **vagalumes** âmbar (`VAGAS`, ciclo de 56 s: espalhados → enxame em volta da pessoa, piscando em onda → revoada em linha → espalhados; tocado, acende, foge e soa), a **abelha** que vai de planta em planta e poliniza (o cogumelo muda de cor pela metade), 72 **formiguinhas** coral em fila pelas trilhas (`TRILHAS`: a mãe pelo lado visto, as onze árvores — `TRONCOS` registrado ao gerar —, e cada cogumelo do chão à beira do chapéu; um terço carrega migalha turquesa), e 18 **folhas padronadas** (matéria 22; oito padrões: quatro das folhas pintadas + quatro ancestrais — zigue-zague, losangos, espirais, fileiras de pontos — fluorescentes, dormem a 35 % e acendem com a mão/pessoa perto, e ondulam com a mão via `ondulaMao`). Pontos pelo `progVida` (24º programa), simulação em `andarVida`. Junto: **cogumelo muda de cor ao toque** (`cogToque[13]`, a fase do vértice = índice + fração), **tremor do toque** na superfície e **respiração com a mão perto** (VS_SOLIDA, `maoA/maoB` agora enviados na mata), **veias da mãe onde a mão passa** + **faixas ancestrais em ocre** (`maeXZ`), pulso do toque 0,15 → 0,42 e 1,9 s; som: mestre 0,35 → 0,5, sino 0,075 → 0,13, e a **trilha abaixa pela metade** quando algo soa (`abaixarTrilha`, `seguirTrilha`) |
| — | — | **A coruja-helicóptero** (7.5, dentro de `VIDA_NA_FLORESTA`): "uma coruja com olhos grandes, pode ter apenas um olho, e em vez de asas voasse como um helicóptero". Ovo de penas roxas de 40 cm com um olho âmbar só que pisca e cuja pupila segue a pessoa, bico, orelhas, pés, rotor de quatro pás e rotor de cauda; malha feita em `montarCoruja` e transformada na CPU a cada quadro (`andarCoruja`: yaw/pitch/roll, o VS_SOLIDA não gira), matéria 23 (a parte na fase: 0 penas, 1 íris com o raio na fração, 2 pás, 3 pupila, 4 bico, 5 disco; **as partes inteiras vão com +0,02** — um varying em 2,0 exato chega ao fragmento como 1,9999 e floor() dá a íris nas pás). Poleiros: o vão da mãe (anel 4 da linha de centro) e o alto de três cogumelos. Ciclo: pousada → decola na vertical → patrulha a sala a 2,1–2,4 m inclinando o nariz e pendendo nas curvas → visita (paira a 1,2 m da cara, olhando, 8 s) → volta ao poleiro seguinte. Tocada: pisca, pia (`piarDaCoruja`, duas notas graves) e sobe. É alvo de chamado (`'coruja'`, sussurro de perto) |
| `DEUSA_QUE_DANCA` | `true` | **a cópia do ser do céu dançando** (7.2), na floresta do começo: a malha `alien-0` com a pele camuflada, vestida por proximidade nos ossos da captura de movimento, ≈1,75 m, a 3,8 m à frente-direita, com os pés no chão, dançando de ida e volta (7.3: "longe, mais alta, com os pés no chão"; "quando terminar, de trás pra frente"). Os dados vêm de `assets/mocap/deusa-danca.json` (exportado do Unreal por `fontes/exportar_mocap_unreal.py` + `fontes/mocap_para_obra.py`); sem o arquivo, ela não existe. Posição e altura em `DANCA_AZ/DIST/PE/ALTURA` |
| — | — | **As mãos falam a língua de cada cenário** (7.7, 25/09: "cada cenário de uma forma diferente... no dos planetas algo mais suave, as linhas das deusas saindo das mãos"): a mão emite pelo movimento — Floresta: esporos turquesa/âmbar que sobem e apagam; Cosmos: um fio por mão (o rastro de 1,5 s, três passadas com desvio mínimo, `progRastro`, ouro pálido dos fios da deusa, bem fraco); Mar: bolhas de ar só com a mão embaixo da lâmina, estouram na superfície; Papel: pó de estrelas que cintila e sobe para o teto. `andarEfeitoDasMaos`/`desenharEfeitoDasMaos`, um tanque de 240 pontos no `progVida`. **A tartaruga** (7.7): casco em cúpula de escamas em tijolo com costura turquesa e miolo ocre (matéria 24), cabeça que balança, patas alternadas, cauda; anda a 8 cm/s pelo chão real escolhendo pontos a até 1,8 m (longe da mãe), para de vez em quando; tocada, recolhe cabeça e patas por 3 s, o casco pulsa e soa grave (`montarTartaruga`/`andarTartaruga`). **A árvore cresce inteiriça**: o alfa dos troncos e da folhagem fecha nos primeiros 30 % de `vivo` ("consegue ver a geometria por dentro"). **A plantaruga** (7.7, "uma mistura de planta com tartaruga, nas cores das folhas"): casco de escamas em tijolo, cada uma com um padrão das folhas no verde delas e costura turquesa, três folhas e um cogumelinho brotando do casco (matéria 24, partes 0 a 5). **A mãe a dois passos à direita de quem começa** (`ARVORE_BASE = [1.45, 0, -1.05]`, o casulo e a dançarina acompanharam; `acharLugarDaMae` só afasta até meio passo): "o ambiente tem que se distribuir a partir de onde a pessoa começa". **Plantas pontuais nas paredes lidas** (`plantarNasParedes`, `TUFOS_DE_PAREDE`, até quatro, uma por parede, na altura da mão; os cogumelos já pousam na mesa pelo v4) e a vida se rearruma depois do escaneamento (`montarTrilhasDaVida`, `montarPoleiros`). **As faixas da mãe** ficam sempre a um quarto, ocre; perto, cheias e rosa. **O menu da mão**: pinça segurada **5 s**, apontando para a frente (`apontandoParaFrente`: nem chão nem teto, mão acima da cintura), sem pegar nada; fechar leva 1 s ou o botão **Voltar**. **Qualidade** ("ruído, pixelizado, saturação alta"): a escala de desenho do index sobe de 0,7 para **0,8** e `ESCALA_VIVA_MIN` de 0,75 para 0,82 (o piso efetivo vai de 0,52 para 0,66 do nativo); a aquarela perde contraste (1,62 → 1,45) e saturação (1,26 → 1,05); o papel 14 % menos saturado |
| `MONTANHAS` | `false` | **sem montanhas** (7.6, 25/09: "estão num horizonte, e esse horizonte, quando vai para a realidade aumentada, não faz sentido; melhor tirar"). `false` apaga as duas versões (o horizonte desenhado e o modelo); `true` volta ao que `HORIZONTE_DESENHADO` escolher |
| `HORIZONTE_DESENHADO` | `true` | **o horizonte do cenário 1 feito em código** (6.8): três cordilheiras opacas em anel (36, 52, 70 m), a base na linha dos olhos — no lugar do modelo de montanhas a 58 %, que lia como vulto translúcido. `false` volta o modelo |
| `CEU_EM_CAMADAS` | `true` | **o céu do cenário 1 feito em código** (6.4, 25/09: "a resolução do céu no início não está boa… ou não usar imagem, só camadas de estrelas e assets"). A pintura dos filamentos (`ceu-mata`, 2048 × 1024) cobria o céu com um disco de 1024 px — 4,5 px por grau acima da cabeça, contra ~12 que a obra desenha e 25 da lente. Agora: nebulosa azul suave gerada ao carregar (`gerarNebulosa`, `CEUS[4]`, a mesma estereográfica — o ser camuflado a veste), poeira azul em 16 mil grãos, 2600 estrelas, e sete rios de luz iridescentes (`progFila`) que se desenham dos 0:20 aos 0:44. `false` volta a pintura. Para uma pintura ficar nítida no céu, ela precisaria ser **quadrada, 4096 × 4096** (o formato 2:1 perde metade) |
| `NEBLINA_CAMADAS_RM` / `NEBLINA_DENSA_RM` | `4` / `1.45` | a neblina marmorizada em RM: quatro das sete camadas, mais densas. **Medido no Quest em 25/09: a neblina era metade da placa de vídeo** (15 → 8 ms por quadro só desligando ela). Na tela do computador, as sete |

Fora do arquivo:

| onde | o quê |
|---|---|
| `window.raizes.ir(seg)` / `.cena(n)` | salta no tempo — existe em **qualquer endereço que não seja o publicado**, e não na obra publicada. Só o `.onde()` (leitura) existe em todo lugar: é dele que a lâmpada lê o cenário |
| `node fontes/luz-segue-cena.mjs` | a lâmpada da sala segue o cenário, pelo estúdio do v1 (cores e receita no `LEIA-ME-ACER.md`, "A lâmpada da sala") |

---

## O vocabulário da casa, que não é o do código

O código chama de **nuvem** o que é nuvem de pontos — `plantarNuvem`,
`decodificarNuvem`, `CENAS[n].nuvem`. **A direção de arte chama de outra
coisa**, e ler o pedido com o dicionário do código já produziu o mesmo
defeito três vezes seguidas.

| ela diz | quer dizer | como se faz |
|---|---|---|
| **neblina marmorizada**, ou *fog* | os maços com a marmorização assada por dentro e o leitoso por massa. **Não tem ponto nenhum.** No código chamava-se `nuvem` até 09/09, e era essa a confusão | `neblina` na partitura, `progFig` |
| **nuvem** | fluido e macio, sem grão — como o céu cósmico | ruído no shader, volume |
| **poeira** | grão, e é o único lugar onde partícula é o certo | `progPo` |
| um bicho, um corpo, um planeta | **superfície**, o mais curva possível | `plantarMalha` + `progSolida` |

> A palavra **nuvem** era o pior caso: no código ela quer dizer nuvem de
> *pontos* (`plantarNuvem`), e na partitura queria dizer a *neblina*, que
> não tem ponto nenhum. Duas coisas opostas com o mesmo nome. Renomeada em
> 09/09 para `neblina`.

**Partícula só quando ela pedir a palavra.** Nada é nuvem de pontos por
padrão: a floresta já fez essa travessia com `MATA_SOLIDA`, e o que sobrou
em pontos é dívida, não escolha.

E **antes de apagar o que ela já pediu uma vez, pergunte.** "Retirar as
partículas excessivas" foi corrigido no minuto seguinte para "não é pra
apagar os seres, é pra não fazer como partículas".

---

## O que morde sem dar erro

Nada aqui aparece no console. Ou a página morre inteira, ou a coisa
simplesmente não aparece.

- **Crase em comentário de shader** fecha o template literal e quebra o
  arquivo, com o erro aparecendo longe dali. Já aconteceu cinco vezes.
- **`${` dentro de shader** — o JavaScript tenta interpolar.
- **Precisão de uniforme diferente entre vértice e fragmento**: o programa
  não linka, e não linkar não gera erro — o desenho só não acontece.

  > **Como pegar isso em um minuto.** O `verificar.py` não consegue: ele é
  > estático e não compila GLSL. O que pega é um banco de provas — extrair
  > os dois shaders do template para arquivos, servi-los, e compilá-los num
  > contexto WebGL separado lendo o log:
  >
  >     const sh = gl.createShader(gl.FRAGMENT_SHADER);
  >     gl.shaderSource(sh, FS); gl.compileShader(sh);
  >     gl.getShaderInfoLog(sh)     // diz a linha e o identificador
  >
  > Em 08/09 ele respondeu em uma linha o que três hipóteses erradas não
  > tinham achado. Desde 14/09 é um comando: `python fontes/provar_shaders.py`
  > escreve `_prova.html`; aberta num navegador, ela compila e linka todos os
  > programas e lista o log dos que falharem.
  >
  > E **dentro do capacete**, desde 20/09, o portão diz embaixo da versão
  > quantos dos dezoito programas linkaram *naquele aparelho* — e o nome
  > dos que não. "Várias mudanças não estão lá" com o portão dizendo
  > 18/18 é cache velho; com menos de 18 é o aparelho, e aí é o cabo.
- **Atributo vaza entre programas.** Chame `soltarAtributos()` depois de
  todo `useProgram`.
- **Alocar memória por quadro** vira engasgo periódico do coletor de lixo.
  Use o `mvpBuf` que já existe.
- **Contar tempo em quadros** supõe 60 fps. Use `passo()`.
- **Mipmap em imagem com alfa** deixa halo escuro. As figuras carregam sem
  mipmap de propósito.
- **Repetição em céu**: os céus usam `CLAMP_TO_EDGE` nos dois eixos. Desde
  08/09 a pintura não é mais espalhada em volta da cúpula — é projetada
  inteira por **estereográfica**, que cobre o céu sem distorcer forma (só
  escala) e não tem emenda, porque não há volta. Repetir ali agora seria
  erro, e não escolha.
- **Função de shader declarada antes dos uniformes que ela usa.** Custou uma
  rodada em 08/09: o `coracao()` foi posto antes do bloco de uniformes, o
  fragmento não compilou, e a floresta inteira sumiu sem erro nenhum. Em
  GLSL a ordem do arquivo é a ordem de visibilidade — e uniforme não é
  içado como função de JavaScript.
- **Apagar um trecho por fatia entre duas âncoras** leva junto o que estava
  no meio. Já aconteceu duas vezes: com o `montarCogumelos` e com o
  `let bCrisalida = null`. `node --check` passa — não é sintaxe, é
  referência que sumiu — e a obra morre inteira ao carregar.
- **Trocar uma unidade de textura** troca a imagem de um objeto pela de
  outro, silenciosamente. Tabela no `LEIA-ME-ACER.md`, seção 8.
- **Um uniforme com valor "neutro" que não é neutro na conta.** `lamina` nascia em
  99 para dizer "não há água", mas no shader `1 - smoothstep(lamina-0.25, lamina, y)`
  99 quer dizer "tudo está embaixo d'água": de 3ce6a39 (setembro) até a 7.4 a floresta,
  o cosmos e o papel inteiros levavam o azul do fundo do mar a 92 %, e ninguém viu
  porque a obra é azul mesmo. Foi o "cenário quase monocromático" de 25/09. Hoje o
  shader ignora a lâmina acima de 50 m. Quando um efeito "desligado" ainda mexe na
  cor, desconfie do valor-sentinela.

---

## A regra de ouro do teste

**O passthrough é outro ambiente, não uma janela para o mesmo.**
Nada visto no computador prova coisa alguma sobre o headset.

Alvo de quadros: **72**, pedido explicitamente ao aparelho. Cair de quadros
não causa enjoo aqui (o timewarp cobre, e a câmera nunca se move sozinha) —
o risco real é o rastreamento perder a sala no escuro.

---

## Licenças

`CREDITOS.md` tem a lista. Dois resolvidos: a **borboleta** (CC BY 4.0, de
Artistic_side no Sketchfab — crédito obrigatório) e o **cogumelo** (CC0). O
resto é pendência declarada — os dezoito `magnific_*`, a crisálida, o ser e
a mão cósmica, todos de origem desconhecida, e **três deles estão na obra**.

A lição do v1 vale para todos: a árvore-mãe também era modelo baixado com
licença por resolver, e ao virar procedural *"a pendência desapareceu junto
com o megabyte e meio de malha"*.

---

## Se algo não bater

**O código manda**, e a documentação é que precisa ser corrigida.
