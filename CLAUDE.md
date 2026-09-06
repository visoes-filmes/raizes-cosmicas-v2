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

**Antes do push, troque a versão do cache** em `sw.js`:

```js
const VERSAO = 'raizes-cosmicas-AAAA-MM-DD';
```

A estratégia é cache primeiro, rede como reserva — o nome do cache **é** o
número da versão. Sem trocar essa string, o headset continua servindo o
cache antigo e a obra nova nunca chega lá. É essa a causa real do "abri e
parece a versão de antes".

Depois:

```bash
git add -A && git commit -m "o que mudou" && git push
```

GitHub Pages serve a pasta como está. Sem build, sem Actions — Actions foi
tentado e falhou (token padrão é só de leitura), removido de propósito.

Conta: **Crisia-poria**, owner da organização `visoes-filmes`.

---

## O andaime de ateliê

A barra de baixo é ferramenta de trabalho, não parte da peça: cada faixa é
um momento, com a largura da duração real e a cor do cenário. **Clicar salta
para aquele ponto** — sem isso não há como trabalhar num cenário que só
acontece aos 6:30. As marcas laranja são as três janelas de interação.

**Tecla `H`** esconde e mostra tudo.

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
