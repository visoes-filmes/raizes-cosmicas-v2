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

## Testar no aparelho

```bash
python fontes/servir.py 8766        # CERT=<pasta> para HTTPS na rede
```

Um servidor por pedido, sem cache. O de prateleira (`http.server`) atende uma
conexão por vez, e com 7 MB num arquivo só o Quest desiste no meio — aparece
como "carrega as imagens e nada acontece".

**A obra relata o que acontece dentro do headset** pedindo `/_relato/…` ao
servidor: cada passo sai no log com `>>`. Dentro do capacete não há console,
e a depuração remota do Quest cai com facilidade. É bilhete jogado pela
janela, e funciona quando o resto não.

> **Produção é só `visoes-filmes.github.io`.** Qualquer outro endereço é
> teste. A regra já foi `localhost` e furou no primeiro teste pela rede: a
> obra se achou publicada, guardou cache e calou os relatos.

---

## Os interruptores

| onde | o quê |
|---|---|
| `ANDAIME` em `mr.template.html` | `false` é a obra; `true` devolve régua, medidores e a tecla H |
| `window.raizes.ir(seg)` / `.cena(n)` | salta cenários — **só quando servida de localhost**, não existe na obra publicada |
| `node fontes/luz-segue-cena.mjs` | a lâmpada da sala segue o cenário, pelo estúdio do v1 |

---

## O que morde sem dar erro

Nada aqui aparece no console. Ou a página morre inteira, ou a coisa
simplesmente não aparece.

- **Crase em comentário de shader** fecha o template literal e quebra o
  arquivo, com o erro aparecendo longe dali. Já aconteceu cinco vezes.
- **`${` dentro de shader** — o JavaScript tenta interpolar.
- **Precisão de uniforme diferente entre vértice e fragmento**: o programa
  não linka, e não linkar não gera erro — o desenho só não acontece.
- **Atributo vaza entre programas.** Chame `soltarAtributos()` depois de
  todo `useProgram`.
- **Alocar memória por quadro** vira engasgo periódico do coletor de lixo.
  Use o `mvpBuf` que já existe.
- **Contar tempo em quadros** supõe 60 fps. Use `passo()`.
- **Mipmap em imagem com alfa** deixa halo escuro. As figuras carregam sem
  mipmap de propósito.
- **Repetição vertical em céu**: zênite e nadir não são vizinhos. Céus usam
  `CLAMP_TO_EDGE` no vertical.
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

## Se algo não bater

**O código manda**, e a documentação é que precisa ser corrigida.
