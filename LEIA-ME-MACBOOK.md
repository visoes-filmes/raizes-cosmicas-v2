# Migrar para o MacBook Pro — 24/09/2026

O Lenovo ficou lento; o computador do estande passa a ser o **MacBook Pro**
(o do Plinio, o mesmo da colmeia). Este arquivo é o que o chat novo, aberto
na pasta do projeto no Mac, lê **primeiro**. Depois, na ordem: `CLAUDE.md`
(regras e a tabela dos interruptores), `LEIA-ME-SEGUIR.md` (estado por
versão, a Cabine), `LEIA-ME-VOLTAR-AO-DESKTOP.md` (o que aconteceu em
24/09, a 6.0 por dentro), `LEIA-ME-UNREAL.md`, `LEIA-ME-ACER.md`.

> **Nada disto foi provado num Mac.** A Cabine foi escrita e testada no
> Windows; a adaptação ao macOS (rede, monitores, navegador, instalador)
> foi feita às cegas em 24/09, pela documentação. O primeiro passo no Mac é
> rodar e ver o que quebra — está tudo isolado atrás de `MAC = sys.platform
> == "darwin"` em `fontes/cabine.py`.
>
> **Rodou na noite de 24/09** — o que passou e o que quebrou está no §8.

---

## 1. Instalar (uma vez)

1. **Homebrew**, se não houver (cole no Terminal):
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. **Trazer o projeto** (o Mac não tem a pasta):
   ```bash
   cd ~/Downloads
   git clone https://github.com/visoes-filmes/raizes-cosmicas-v2.git "Raizes Cosmicas"
   cd "Raizes Cosmicas"
   ```
   São ~300 MB com o histórico e o vídeo; demora. Conta GitHub
   **Crisia-poria** (o Git abre o navegador para o login na primeira vez que
   empurrar).
3. **O instalador**:
   ```bash
   bash fontes/instalar_mac.sh
   ```
   Instala node, adb (`android-platform-tools`), scrcpy e Pillow pelo brew,
   grava a identidade do git e deixa na Mesa o atalho
   **"Raízes Cósmicas - Cabine.command"** (dois cliques: abre o Terminal,
   segura o Mac acordado com `caffeinate` e sobe a Cabine em
   `localhost:8790`). Se o macOS barrar o `.command` na primeira vez:
   botão direito → Abrir.
4. **Google Chrome** (ou Edge) instalado: é ele que a Cabine abre em
   quiosque no projetor. Safari não serve para isso.
5. **Claude Code** aberto na pasta.

Confira: `python3 fontes/verificar.py` → "nada a corrigir";
`python3 fontes/montar_mr.py` monta tudo.

## 2. A rede interna no dia — o que muda no Mac

No Windows a Cabine ligava o hotspot por um botão. **No macOS não há como
ligar o Compartilhamento de Internet por comando** sem senha de
administrador; o botão da Cabine só **abre a janela certa dos Ajustes**
(Geral → Compartilhamento → Compartilhamento de Internet) e mostra se está
ligado (a ponte `bridge100`, ip `192.168.2.1`). Por isso, no Mac, a ordem
de preferência é:

1. **O modem 4G UFI (HiMILink) como roteador.** Ele já é uma Wi-Fi própria
   (painel em `192.168.100.1`). Mac e Quest entram na Wi-Fi dele; não
   precisa de internet no chip para os dois se verem. É o mais simples e o
   que não depende de nada do macOS. **Recomendado.**
2. **O roteador dela** (o do equipamento do FIL): mesma coisa, os dois
   entram nele.
3. **Compartilhamento de Internet do Mac**, configurado uma vez nos
   Ajustes: compartilhar a conexão de "Ethernet/USB" (o modem no cabo) ou
   "iPhone USB" para "Wi-Fi", com nome e senha próprios (a Cabine não
   consegue ler a senha: fica anotada nos Ajustes). Ligado, os aparelhos
   ganham `192.168.2.x`.

Em qualquer dos três, o resto é igual ao Windows: o Quest entra na mesma
rede que o Mac, **uma vez pelo cabo** a Cabine libera o adb pela Wi-Fi
(`adb tcpip 5555` + `connect`), e o túnel `adb reverse` faz
`localhost:8765` dentro do óculos ser o Mac — contexto seguro, botão de RM
sem certificado. Depois o cabo sai.

**Firewall do macOS:** pode perguntar se "python3" aceita conexões de
entrada. Pode negar: o túnel do adb chega pelo próprio Mac (localhost), e a
Cabine escuta só em `127.0.0.1`. Se o Quest não achar a obra, aí sim
permita.

## 3. A Cabine no Mac — o que é igual e o que é diferente

Igual: os cards Quest, Obra, Projeção · tela de tule e Relatos; os botões;
`/eventos`; a `projecao.html`; o roteiro numerado na tela.

Diferente:
- **Rede:** o botão abre os Ajustes em vez de ligar (acima). O nome da
  rede aparece se o macOS o entregar (`com.apple.nat`); senão, está nos
  Ajustes. "Aparelhos na rede" não existe no Mac.
- **Monitores:** o macOS diz tamanho, mas não posição. A Cabine supõe o
  projetor **à direita do monitor principal**. Se nos Ajustes → Monitores o
  projetor estiver em outro lugar, a página em quiosque abre no monitor
  errado: arraste-a para o projetor e aperte **F** (tela cheia).
- **Espelho do óculos:** scrcpy do brew, mesma coisa. Se dois adbs
  brigarem (o do brew e outro), a Cabine já passa `ADB=` o dela.
- **Sem pythonw:** a Cabine roda numa janela do Terminal (o `.command`).
  Fechar o Terminal fecha a Cabine e o servidor da obra. Segundo clique no
  atalho só reabre a página.
- **Meta Quest Link não existe no Mac** — um problema a menos com o cabo.
- **Dormir:** o `.command` já roda com `caffeinate -dims`; o Mac não apaga
  a tela nem dorme enquanto a Cabine estiver de pé.

## 4. O Quest, de novo do zero

A autorização de depuração é **por computador**: no Mac ele vai pedir de
novo. **Aceitar com "Sempre permitir deste computador".** Sem a caixinha, o
`adb tcpip 5555` que a Cabine roda derruba a autorização (foi o que
aconteceu no Lenovo em 24/09 — o dia inteiro em "unauthorized").

Serial: `2G0YC1ZG2307ZW`. Modo de desenvolvedor já está ligado nele.

## 5. O estado da obra (igual ao Lenovo — está tudo no repositório)

| versão | arquivo | o que é |
|---|---|---|
| **5.2** | `v52.html` | sem escaneamento; céu em *fade* com as paredes reais; **chão visível** até o cenário 4; névoa 0,5; escala 0,7 |
| **6.0** | `v6.html` | a 5.2 + **a tela de tule**: o óculos reconhece a tela (plano rotulado tela/janela na Configuração de Espaço, ou dois cantos beliscados via Cabine) e lê o toque; o vídeo "Odara - Cosmos" é **projetado** pela `projecao.html` e ondula a cada toque. **Invisível dentro do óculos** |
| v2, v4, 5.1 | `index.html`, `v4.html`, `v5.html` | as anteriores (a 5.1 foi descartada: chão preto) |

Último commit ao escrever isto: ver `git log -1`. Marcas: `v2.0`, `v4.0`,
`v5.0`, `v5.1`, `v5.2`, `v6.0`. **Nada visto no Quest desde a 5.2.**

A 6.0 por dentro (interruptores `TELA_*`, módulo, shader, ganchos
`raizes.tela.*`, relatos) está no `LEIA-ME-VOLTAR-AO-DESKTOP.md` §5.

## 6. O roteiro do primeiro dia no Mac

1. `bash fontes/instalar_mac.sh` → abrir o atalho da Mesa → a Cabine abre
   em `localhost:8790`. **Anotar o que quebrou** (é a primeira vez num Mac).
2. Quest no cabo → aceitar com "sempre permitir" → a Cabine refaz os túneis
   e libera a Wi-Fi (Quest e Mac na mesma rede antes).
3. Cabine → Abrir no Quest (6.0) → Iniciar em RM. Ler no portão: versão e
   quantos dos 20 programas linkaram.
4. **Ver a 5.2 no capacete**: chão real aparece? céu faz *fade* com as
   paredes?
5. **Cravar a tela**: Configuração de Espaço com a tela marcada como
   "Tela/Janela", ou Cabine → Cravar pelos cantos. "Ver no óculos" só para
   conferir o encaixe; desligar depois.
6. **Tocar o tule** com a `projecao.html` aberta (numa aba mesmo; F = tela
   cheia): a onda nasce onde a mão tocou?
7. Projetor ViewSonic Full HD no Mac (segundo monitor): card de projeção →
   monitor → Projetar; "espelhar" se for retroprojeção. Tule 3 × 2 m em
   16:9: a página deixa barras pretas dos lados. Confirmar as medidas do
   tule.
8. Pendências antigas: relato dela da interatividade (casulo, concha,
   rosa); `sw.js` só guarda o `index`; repositórios v4/v5 próprios;
   licenças (`LEIA-ME-SEGUIR.md` §6).

## 7. Se o Mac não servir como Cabine

Qualquer máquina com Python 3, node e adb serve — a Cabine é um script. O
Windows (desktop "Unreal") continua com tudo pronto, inclusive o hotspot por
botão; o `LEIA-ME-VOLTAR-AO-DESKTOP.md` é o caminho de volta.

## 8. O primeiro dia no Mac — 24/09, à noite

O que foi provado, sem o Quest ainda:

- **O instalador rodou limpo** (Homebrew 7.0.2, macOS 26). node v24.18.0,
  adb e scrcpy 4.1 em `/opt/homebrew/bin`, Python 3.12.6 (o do python.org,
  não o do brew) com Pillow; identidade do git gravada; atalho na Mesa.
  `verificar.py`: 38 shaders, "nada a corrigir". Chrome já estava instalado.
- **A Cabine subiu na primeira tentativa** pelo mesmo comando do atalho
  (`caffeinate -dims python3 fontes/cabine.py`): obra em 8765 (13 MB
  servidos), controle em 8790. A página inteira renderiza, sem erro de
  console. Ela leu o adb e o scrcpy do brew, o hotspot do Mac
  ("MacBook Pro de Plinio", desligado, pelo `com.apple.nat`) e o único
  monitor (Color LCD 1800×1169).
- **A projeção funciona no Mac**: `projecao.html` abre ligada à Cabine
  (preta até o óculos acender), **A** acende o vídeo da Odara, o clique
  gera a onda. `/eventos` responde.
- O Mac estava no **cabo de rede** (192.168.15.42), fora de qualquer Wi-Fi:
  `wifi_do_mac()` devolve `ssid: null` e o ip do `en0` — sem quebrar.

O que quebrou — **o Quest no cabo ficou `unauthorized` sem mostrar a caixa
no capacete**, mesmo aceitando "sempre permitir" (o operador não viu caixa
nenhuma). Do lado do Mac foi tentado, sem efeito: `adb kill-server`, `adb
reconnect`, **chave nova** (`~/.android/adbkey` regenerada — a antiga, de
08/2024, ficou em `~/.android/backup-2026-09-24/`; com chave nova o Quest
*tem* um pedido pendente, então é o óculos que não o exibe). Só há um adb
na máquina (o SideQuest existe em `/Applications`, mas não estava aberto),
e a vigia da Cabine não interfere — ela só roda `adb devices`. Pela Wi-Fi
de casa o Quest (192.168.15.157) responde ao ping, mas a porta 5555 recusa:
o adb de rede está desligado nele, e só um cabo autorizado liga.

O que fica para tentar, nesta ordem:

1. **Reiniciar o óculos com o cabo ligado**, vestir e ficar na tela inicial
   do Horizon (sem app aberto): a caixa costuma vir nos primeiros segundos.
2. Ajustes → Sistema → Desenvolvedor → *Revogar autorizações de depuração
   USB*, e tirar/pôr o cabo. Se a seção não existir, o modo de desenvolvedor
   caiu: religar no app Meta Horizon do celular.
3. **Trazer a chave do Lenovo.** A autorização do Quest é **por chave**, não
   por computador: copiar `%USERPROFILE%\.android\adbkey` (e `.pub`) do
   Lenovo para `~/.android/` no Mac, `adb kill-server`, e o Quest aceita na
   hora — desde que no Lenovo a caixa tenha sido aceita com "sempre
   permitir".

Nota: `system_profiler SPUSBDataType` não listou o Quest quando rodado de
dentro do Claude Code (o `adb` via o aparelho) — não usar isso para
diagnosticar o cabo.

Se algo aqui não bater com o código, **o código manda** — e este arquivo é
que precisa ser corrigido.
