# Raízes Cósmicas v2 — regras da casa

Obra de realidade mista para Meta Quest 3, em WebXR. Dez minutos, quatro
cenários, 3 × 3 m caminháveis. FIL 2026. HTML único, sem build, sem npm.

O mapa completo está em `LEIA-ME-ACER.md` — **leia-o antes de mexer no
código de verdade.** Este arquivo tem só o que não pode ser esquecido nem
por um minuto.

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

**Testar no aparelho é pelo cabo:**

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

Fora do arquivo:

| onde | o quê |
|---|---|
| `window.raizes.ir(seg)` / `.cena(n)` | salta no tempo — existe em **qualquer endereço que não seja o publicado**, e não na obra publicada |
| `node fontes/luz-segue-cena.mjs` | a lâmpada da sala segue o cenário, pelo estúdio do v1 |

---

## O vocabulário da casa, que não é o do código

O código chama de **nuvem** o que é nuvem de pontos — `plantarNuvem`,
`decodificarNuvem`, `CENAS[n].nuvem`. **A direção de arte chama de outra
coisa**, e ler o pedido com o dicionário do código já produziu o mesmo
defeito três vezes seguidas.

| ela diz | quer dizer | como se faz |
|---|---|---|
| **nuvem** | fluido e macio, sem grão — como o céu cósmico | ruído no shader, volume |
| **poeira** | grão, e é o único lugar onde partícula é o certo | `progPo` |
| um bicho, um corpo, um planeta | **superfície**, o mais curva possível | `plantarMalha` + `progSolida` |

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
  > tinham achado.
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
