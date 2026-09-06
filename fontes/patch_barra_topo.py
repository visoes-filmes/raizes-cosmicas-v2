# -*- coding: utf-8 -*-
"""A trilha vira barra no topo, grudada, em qualquer largura."""
import io, os, re
AQUI = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(AQUI, 'roteiro-sala.html')
s = io.open(p, encoding='utf-8').read()


def troca(a, b):
    global s
    assert a in s, 'NAO ACHOU: ' + a[:80]
    s = s.replace(a, b, 1)


# ── 1. a trilha sai de dentro do corpo e sobe para o topo da folha ────
m = re.search(r'\n<div class="corpo">\n(  <nav class="trilho".*?</nav>)\n', s, re.S)
assert m, 'nao achou a trilha'
nav = m.group(1)
s = s[:m.start()] + '\n<div class="corpo">\n' + s[m.end():]
troca('<div class="folha">', '<div class="folha">\n' + nav + '\n')


# ── 2. o estilo: barra horizontal, grudada, em qualquer largura ───────
ANTIGO = re.search(r'  /\* ── navegação por painéis ──.*?(?=  /\* ── filtro de estado)', s, re.S)
assert ANTIGO, 'nao achou o css da navegacao'
NOVO = '''  /* ── a barra das seções ─────────────────────────────────────
     O documento é consultado, não lido de ponta a ponta: quem abre já
     quer uma coisa. Por isso os botões são a PRIMEIRA coisa da página,
     antes do título, e ficam grudados no topo enquanto se rola.

     Uma barra horizontal em qualquer largura — não um trilho lateral que
     vira barra só no celular. Este documento é lido num painel estreito
     na maior parte do tempo, e uma coluna de 206 px ali comeria um quinto
     da largura para dizer cinco palavras. */
  .trilho{ position:sticky; top:0; z-index:20; display:flex;
           gap:0; overflow-x:auto; scrollbar-width:none;
           margin:0 -26px; padding:0 26px;
           background:var(--fundo); border-bottom:1px solid var(--linha); }
  .trilho::-webkit-scrollbar{ display:none; }
  .aba{ appearance:none; background:none; border:0; text-align:left;
        cursor:pointer; font-family:var(--texto); font-size:15px;
        font-weight:600; color:var(--fraca); white-space:nowrap;
        flex:0 0 auto; padding:13px 15px 11px;
        border-bottom:2px solid transparent;
        transition:color .12s, border-color .12s; }
  .aba:first-child{ padding-left:0; }
  .aba i{ display:none; }                 /* vira dica no repouso do mouse */
  .aba:hover{ color:var(--leite); }
  .aba[aria-selected="true"]{ color:var(--leite);
                              border-bottom-color:var(--c2); }
  /* O número em aberto anda junto do rótulo, não solto num canto. */
  .conta{ font-style:normal; font-family:var(--mono); font-size:10px;
          color:var(--brasa); margin-left:5px; vertical-align:2px;
          font-variant-numeric:tabular-nums; }

  header{ padding-top:44px; }
  .corpo{ margin-top:30px; }
  .painel > h2:first-child{ margin-top:0; }
  .painel > h3.secao:first-child{ margin-top:0; }
  h3.secao{ font-family:var(--serifa); font-weight:400; font-size:23px;
            color:var(--leite); margin:52px 0 4px; }

'''
s = s[:ANTIGO.start()] + NOVO + s[ANTIGO.end():]

# o filtro gruda logo abaixo da barra
troca('''  .filtro{ display:flex; align-items:center; gap:8px; flex-wrap:wrap;
           margin:0 0 26px; padding-bottom:16px;
           border-bottom:1px solid var(--linha); }''',
'''  .filtro{ display:flex; align-items:center; gap:8px; flex-wrap:wrap;
           margin:0 0 26px; padding-bottom:16px;
           border-bottom:1px solid var(--linha); }
  .filtro-conta{ order:9; }''')

# a regra estreita antiga some: agora é a mesma barra em toda largura
ESTREITO = re.search(r'  @media \(max-width:880px\)\{.*?\n  \}\n', s, re.S)
assert ESTREITO, 'nao achou o media query'
s = s[:ESTREITO.start()] + s[ESTREITO.end():]


# ── 3. a dica volta como repouso do mouse, e a rolagem vai ao conteúdo ─
troca('''  abas.forEach(function(b){
    var alvo = document.getElementById(b.getAttribute("aria-controls"));
    var abertos = alvo.querySelectorAll("table.erros .selo:not(.ok)").length;
    if(abertos) b.querySelector(".conta").textContent = abertos;
  });''',
'''  abas.forEach(function(b){
    var alvo = document.getElementById(b.getAttribute("aria-controls"));
    var abertos = alvo.querySelectorAll("table.erros .selo:not(.ok)").length;
    if(abertos) b.querySelector(".conta").textContent = abertos;
    // a descrição não cabe na barra, mas não se perde: vira dica
    var dica = b.querySelector("i");
    if(dica) b.title = dica.textContent;
  });''')

troca('''    if(location.hash.slice(1) !== id) history.replaceState(null, "", "#" + id);
    window.scrollTo(0, 0);
    aplicar();''',
'''    if(location.hash.slice(1) !== id) history.replaceState(null, "", "#" + id);
    /* Ao trocar de seção, a página sobe até logo abaixo da barra — o
       cabeçalho sai de cena e o conteúdo começa colado no topo. Na
       primeira abertura não sobe nada: aí se quer ver o título. */
    if(!primeira){
      var trilho = document.querySelector(".trilho");
      var corpo = document.querySelector(".corpo");
      window.scrollTo(0, Math.max(0, corpo.offsetTop - trilho.offsetHeight - 12));
    }
    primeira = false;
    aplicar();''')

troca('  var modo = "tudo";', '  var modo = "tudo", primeira = true;')

io.open(p, 'w', encoding='utf-8').write(s)
print('barra no topo, grudada, em qualquer largura')
