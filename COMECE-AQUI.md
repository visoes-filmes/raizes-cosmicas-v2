# Comece aqui

**Raízes Cósmicas v2** — obra em realidade mista para Meta Quest 3.
Visões Filmes · FIL 2026 · pasta preparada em 06/09/2026.

---

## Só quero ver a obra

**Duplo clique no `index.html`.** Abre no navegador, aparece o portão, botão
**Iniciar na tela**. Não precisa instalar nada, não precisa de internet.

## Quero ver no Quest 3

No navegador do headset, digite:

```
visoes-filmes.github.io/raizes-cosmicas-v2/
```

Espere as **17 imagens** carregarem (o botão fica cinza até lá) e toque em
**Iniciar em RM**.

> Se abrir e parecer a versão antiga, puxe a página para baixo para
> recarregar. O navegador guarda a anterior com bastante teimosia.

---

## Quero mexer no código

Instale duas coisas:

```
Python 3          (python.org)
pip install Pillow
```

E depois, **de dentro desta pasta**:

```
python fontes/verificar.py
python fontes/montar_mr.py
```

O primeiro procura erros; o segundo refaz o `index.html`.

> ⚠️ **Nunca edite o `index.html` direto.** Ele é gerado. Toda edição vai em
> `fontes/mr.template.html`. Editar o index funciona até a próxima
> montagem, que apaga tudo.

---

## Quero publicar

**Esta pasta, sozinha, não publica.** Ela veio de um ZIP, e um ZIP não tem
histórico de versões — é uma fotografia, não uma linha de trabalho.

Para publicar, instale o **Git** e traga o repositório de verdade:

```
git clone https://github.com/visoes-filmes/raizes-cosmicas-v2.git
```

Login: conta **Crisia-poria**, que já é owner da organização.

**Se você já mexeu nesta pasta antes de clonar**, não perdeu nada. Faça
assim:

1. clone o repositório numa pasta nova
2. copie por cima dele o seu `fontes/mr.template.html` editado
3. copie também qualquer imagem nova que tenha posto em `assets/`
4. rode os dois comandos de montagem
5. **troque a data em `const VERSAO` dentro do `sw.js`** — sem isso o
   headset serve o cache antigo e a obra nova não chega lá
6. e então:

```
git add -A
git commit -m "o que mudou"
git push
```

Um ou dois minutos depois está no ar.

> Daí em diante, **trabalhe sempre na pasta clonada** e esqueça esta. Duas
> cópias vivas do mesmo projeto é como se perde trabalho.

---

## O que tem aqui

```
index.html        A obra. Um arquivo só, com as imagens e o som dentro.
roteiro.html      O roteiro de sala — abra no navegador, tem abas.
LEIA-ME-ACER.md   O MANUAL COMPLETO. Leia este quando for mexer de verdade.
COMECE-AQUI.md    Este arquivo.

assets/           As imagens e o som de origem
  ceus/           os 3 céus (floresta, cósmico, rosa)
  figuras/        as 4 figuras da Odara
  peles/          as 6 do Midjourney, uma por planeta
  texturas/       raiz, mármore, água, papel
  audio/          a trilha

fontes/           O código
  mr.template.html    É AQUI QUE SE EDITA
  montar_mr.py        gera o index.html
  verificar.py        procura erros antes
  planetas/           as 6 do Midjourney em resolução cheia
```

---

## As três coisas que não podem ser esquecidas

**1. No headset, nunca use `gl.blendFunc` cru.** Use `sobrepor()` ou
`somarLuz()`. A mistura comum eleva o alfa ao quadrado, e como o quadro do
headset começa com alfa zero, **tudo o que não for quase opaco some**. Foi
isso que fez o primeiro teste no Quest não mostrar nada — e no computador o
defeito é invisível.

**2. Crase em comentário de shader quebra o arquivo inteiro**, com o erro
aparecendo longe dali. Já aconteceu cinco vezes. O `verificar.py` pega.

**3. O passthrough é outro ambiente, não uma janela para o mesmo.** Nada
visto no computador prova coisa alguma sobre o headset.

O resto está no **`LEIA-ME-ACER.md`**: a partitura dos dez minutos, os
quatro cenários com seus parâmetros, as unidades de textura, os dez
programas de shader, as doze armadilhas do projeto, o orçamento de quadros
e o que ainda falta.
