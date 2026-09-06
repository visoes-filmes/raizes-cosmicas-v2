# -*- coding: utf-8 -*-
"""Reorganiza o roteiro em paineis com botoes, e guarda o que foi decidido."""
import io, os, re
AQUI = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(AQUI, 'roteiro-sala.html')
s = io.open(p, encoding='utf-8').read()


def troca(a, b):
    global s
    assert a in s, 'NAO ACHOU: ' + a[:80]
    s = s.replace(a, b, 1)


# ══════════ 1. as duas correcoes que ela apontou ══════════
troca('''    <tr><th>Vídeo no headset</th>
        <td>O decodificador do Quest aguenta poucos vídeos ao mesmo tempo. As três figuras hoje são <b>imagens paradas</b> justamente por isso. Passar para vídeo exige medir antes.</td>
        <td><span class="selo risco">medir</span></td></tr>''',
'''    <tr><th>Vídeo no headset</th>
        <td><b>Um vídeo por cenário, nunca dois ao mesmo tempo</b> — e os cenários são separados no tempo, então isso vem de graça. O decodificador do Quest aguenta isso sem esforço. O que sobra de risco não é o número: é o <b>instante da troca</b>. Vídeo criado na hora engasga; vídeo já carregado e pausado, só recebendo <i>play</i>, não.</td>
        <td><span class="selo ideia">resolvido no projeto</span></td></tr>''')

troca('''    <tr><th>As figuras são chapas</th>
        <td>Recortes que sempre encaram a pessoa. Funcionam além dos 3 m, onde a falta de paralaxe está correta. <b>Se algo as trouxer para perto, elas se denunciam.</b></td>
        <td><span class="selo risco">projeto</span></td></tr>''',
'''    <tr><th>As figuras são chapas</th>
        <td>Passaram a girar <b>só em torno do próprio eixo vertical</b>. Antes encaravam a câmera inteira: ao olhar para cima elas deitavam junto, e chapa deitada atravessa o chão e corta o que estiver ao lado. Agora se comportam como recorte de teatro em pé — e giram para a <b>posição</b> da pessoa, não para o plano da tela, então quem está de lado vê a figura virada para si. O centro nunca sai do lugar; só a face muda.</td>
        <td><span class="selo ok">corrigido</span></td></tr>''')

# a linha equivalente na tabela de travamento
troca('''    <tr><th>Muitos vídeos ao mesmo tempo</th>
        <td>O decodificador do Quest aguenta poucos. Por isso as figuras hoje são imagens paradas.</td>
        <td><span class="selo risco">medir</span></td></tr>''',
'''    <tr><th>A troca de vídeo</th>
        <td>Nunca há dois tocando: é um por cenário, e os cenários não se sobrepõem. O engasgo mora na <b>troca</b> — criar o elemento na hora custa; tê-lo carregado e pausado, esperando o <i>play</i>, não custa nada.</td>
        <td><span class="selo ideia">ao construir</span></td></tr>''')

# a possibilidade das deusas em video muda de tom
troca('''    <tr><th>As deusas em vídeo</th>
        <td>Hoje são imagens paradas com balanço. Em vídeo, em bumerangue, elas <b>respiram</b> — e o roteiro pede isso. Depende de o decodificador do Quest aguentar.</td>
        <td>~3 h + teste</td></tr>''',
'''    <tr><th>As deusas em vídeo</th>
        <td>Hoje são imagens paradas com balanço. Em vídeo, em bumerangue, elas <b>respiram</b> — e o roteiro pede isso. <b>Um por cenário</b>, carregado antes e só recebendo <i>play</i> na hora.</td>
        <td>~3 h</td></tr>''')

# a suavizacao ja foi feita: sai de possibilidades
troca('''    <tr><th>Suavização no headset</th>
        <td>O navegador do Quest aceita ligar suavização no próprio buffer. É o remédio direto para o serrilhado nas bordas finas.</td>
        <td>~20 min</td></tr>
''', '')


# ══════════ 2. o que fica guardado ══════════
GUARDADO = '''
<h2>Guardado</h2>
<p class="sub">
  Decidido, mas fora do que está construído hoje. Fica aqui para não se
  perder e para não voltar como pergunta.
</p>

<div class="aberto">
  <div class="item"><i>a borboleta</i><p><b>É a 88, e é a única com textura.</b> As outras da animação são outra
    coisa — podem entrar quase invisíveis, como presença e não como figura.
    Por enquanto trabalha-se com <b>uma só</b>.</p></div>
  <div class="item"><i>vídeo</i><p><b>Um por cenário, nunca simultâneo.</b> Os cenários não se sobrepõem no
    tempo, então o decodificador nunca vê dois. O cuidado é carregar antes
    e pausar, não criar na hora.</p></div>
  <div class="item"><i>as figuras</i><p><b>Giro cilíndrico.</b> Giram para a pessoa em torno do eixo vertical, e
    o centro fica onde foi posto. Nunca deitam, nunca passeiam.</p></div>
  <div class="item"><i>o som</i><p><b>A trilha da Crisia por enquanto.</b> Toca em loop, e no build de teste
    entra desligada.</p></div>
</div>
'''
troca('<h2>Erros e melhorias</h2>', GUARDADO + '\n<h2>Erros e melhorias</h2>')


# ══════════ 3. h3 com classe, nao com estilo embutido ══════════
s = re.sub(r'<h3 style="font-family:var\(--serifa\);font-weight:400;font-size:23px;'
           r'color:var\(--leite\);margin:\d+px 0 4px">', '<h3 class="secao">', s)


# ══════════ 4. o corpo vira paineis ══════════
ini = s.index('<div class="folha">') + len('<div class="folha">')
fim = s.rindex('<footer>')
corpo = s[ini:fim]

cab_fim = corpo.index('\n<h2>')
cabecalho = corpo[:cab_fim]
resto = corpo[cab_fim:]

partes = [b for b in re.split(r'\n(?=<h2>)', resto) if b.strip()]
mapa = {}
for b in partes:
    nome = re.match(r'<h2>(.*?)</h2>', b).group(1)
    mapa[nome] = b

bloco_erros = mapa.pop('Erros e melhorias')
fatias = re.split(r'\n(?=<h3 class="secao">)', bloco_erros)
intro_erros = fatias[0]
sub = {}
for f in fatias[1:]:
    nome = re.search(r'<h3 class="secao">\s*(.*?)</h3>', f, re.S).group(1).strip()
    sub[nome] = f

PAINEIS = [
    ('tempos', 'Os tempos', 'o que acontece, minuto a minuto',
     [mapa['Os tempos']]),
    ('regras', 'As regras', 'o que vale nos quatro cenários',
     [mapa['As regras que valem em todos'], mapa['O espaço e a luz'],
      mapa['De onde vem cada peça']]),
    ('decisoes', 'Decisões', 'fechado, aberto e guardado',
     [mapa['Decidido'], mapa['O que ainda está aberto'], mapa['Guardado']]),
    ('erros', 'Erros', 'o que quebrou e o que pode quebrar',
     [intro_erros, sub['Já corrigidos'], sub['O que ainda pode quebrar'],
      sub['Travamento e serrilhado']]),
    ('melhorias', 'Melhorias', 'o que faria a obra melhor',
     [sub['Possibilidades']]),
]

botoes, paineis = [], []
for i, (ident, rotulo, dica, blocos) in enumerate(PAINEIS):
    botoes.append(
        '    <button class="aba" role="tab" aria-selected="{sel}" aria-controls="p-{id}"\n'
        '            id="b-{id}" tabindex="{tab}">\n'
        '      <b>{rot}</b><i>{dica}</i><em class="conta"></em>\n'
        '    </button>'.format(id=ident, rot=rotulo, dica=dica,
                               sel='true' if i == 0 else 'false',
                               tab='0' if i == 0 else '-1'))
    paineis.append(
        '<section class="painel" id="p-{id}" role="tabpanel" aria-labelledby="b-{id}"{oc}>\n'
        '{corpo}\n</section>'.format(id=ident, oc='' if i == 0 else ' hidden',
                                     corpo='\n'.join(blocos).strip()))

FILTRO = '''
  <div class="filtro" id="filtro" hidden>
    <span class="filtro-rot">mostrar</span>
    <button class="fbt" data-f="tudo" aria-pressed="true">tudo</button>
    <button class="fbt" data-f="aberto" aria-pressed="false">só o que falta</button>
    <button class="fbt" data-f="ok" aria-pressed="false">só o resolvido</button>
    <span class="filtro-conta" id="filtro-conta"></span>
  </div>
'''

novo = (cabecalho +
        '\n<div class="corpo">\n'
        '  <nav class="trilho" role="tablist" aria-label="Seções do roteiro">\n' +
        '\n'.join(botoes) + '\n  </nav>\n\n'
        '  <main>\n' + FILTRO + '\n' + '\n\n'.join(paineis) + '\n  </main>\n</div>\n\n')

s = s[:ini] + novo + s[fim:]


# ══════════ 5. o estilo dos paineis ══════════
CSS = '''
  /* ── navegação por painéis ──────────────────────────────────
     O documento é consultado, não lido de ponta a ponta: quem abre
     quer uma coisa. Um painel de cada vez, e a trilha à esquerda
     diz sempre onde se está. */
  .corpo{ display:grid; grid-template-columns:206px 1fr; gap:46px;
          align-items:start; margin-top:38px; }
  .trilho{ position:sticky; top:20px; display:flex; flex-direction:column;
           gap:2px; }
  .aba{ appearance:none; background:none; border:0; text-align:left;
        cursor:pointer; font-family:var(--texto); color:var(--fraca);
        padding:9px 12px 10px; border-left:2px solid var(--linha);
        display:grid; gap:1px; position:relative;
        transition:color .12s, border-color .12s; }
  .aba b{ font-weight:600; font-size:15px; color:var(--tinta); }
  .aba i{ font-style:normal; font-size:12px; line-height:1.35;
          color:var(--fraca); padding-right:16px; }
  .aba:hover{ border-left-color:var(--linha-forte); }
  .aba:hover b{ color:var(--leite); }
  .aba[aria-selected="true"]{ border-left-color:var(--c2); }
  .aba[aria-selected="true"] b{ color:var(--leite); }
  .aba[aria-selected="true"] i{ color:var(--tinta); }
  .conta{ position:absolute; right:11px; top:10px; font-family:var(--mono);
          font-style:normal; font-size:10px; letter-spacing:.06em;
          color:var(--brasa); font-variant-numeric:tabular-nums; }

  .painel > h2:first-child{ margin-top:0; }
  .painel > h3.secao:first-child{ margin-top:0; }
  h3.secao{ font-family:var(--serifa); font-weight:400; font-size:23px;
            color:var(--leite); margin:52px 0 4px; }

  /* ── filtro de estado ───────────────────────────────────────
     A confusão do documento antigo era misturar resolvido com pendente
     na mesma tabela. Aqui isso vira um botão. */
  .filtro{ display:flex; align-items:center; gap:8px; flex-wrap:wrap;
           margin:0 0 26px; padding-bottom:16px;
           border-bottom:1px solid var(--linha); }
  .filtro-rot{ font-family:var(--mono); font-size:10px; letter-spacing:.16em;
               text-transform:uppercase; color:var(--fraca);
               margin-right:2px; }
  .fbt{ appearance:none; cursor:pointer; font-family:var(--texto);
        font-size:13px; padding:4px 11px 5px; border-radius:2px;
        background:none; color:var(--fraca);
        border:1px solid var(--linha-forte);
        transition:color .12s, border-color .12s, background .12s; }
  .fbt:hover{ color:var(--leite); border-color:var(--c2); }
  .fbt[aria-pressed="true"]{ background:var(--c2); border-color:var(--c2);
                             color:var(--fundo); font-weight:600; }
  .filtro-conta{ font-family:var(--mono); font-size:11px; color:var(--fraca);
                 margin-left:auto; font-variant-numeric:tabular-nums; }

  @media (max-width:880px){
    .corpo{ grid-template-columns:1fr; gap:24px; }
    .trilho{ position:sticky; top:0; z-index:5; flex-direction:row;
             gap:0; overflow-x:auto; margin:0 -26px; padding:0 26px;
             background:var(--fundo); border-bottom:1px solid var(--linha); }
    .aba{ border-left:0; border-bottom:2px solid transparent;
          padding:12px 14px; flex:0 0 auto; }
    .aba i, .conta{ display:none; }
    .aba[aria-selected="true"]{ border-bottom-color:var(--c2); }
  }
  @media (prefers-reduced-motion:reduce){
    *{ transition-duration:0.01ms !important; }
  }
'''
troca('</style>', CSS + '</style>')


# ══════════ 6. o comportamento ══════════
JS = '''
<script>
(function(){
  "use strict";
  var abas = [].slice.call(document.querySelectorAll(".aba"));
  var filtro = document.getElementById("filtro");
  var conta = document.getElementById("filtro-conta");

  /* Quantos itens abertos ha em cada painel. Nao e enfeite: e a unica
     pergunta que se faz a um documento de producao — o que falta. */
  abas.forEach(function(b){
    var alvo = document.getElementById(b.getAttribute("aria-controls"));
    var abertos = alvo.querySelectorAll("table.erros .selo:not(.ok)").length;
    if(abertos) b.querySelector(".conta").textContent = abertos;
  });

  var modo = "tudo";

  /* O filtro trabalha so nas tabelas de estado — a partitura dos tempos
     nao tem estado nenhum e nao deve sumir. */
  function aplicar(){
    var painel = document.querySelector(".painel:not([hidden])");
    if(!painel) return;
    var visivel = 0, total = 0;
    [].forEach.call(painel.querySelectorAll("table.erros tbody tr"), function(tr){
      var selo = tr.querySelector(".selo");
      if(!selo) return;
      total++;
      var resolvido = selo.classList.contains("ok");
      var passa = modo === "tudo" || (modo === "ok") === resolvido;
      tr.hidden = !passa;
      if(passa) visivel++;
    });
    // uma tabela que ficou inteira vazia some junto com a moldura dela
    [].forEach.call(painel.querySelectorAll("table.erros"), function(t){
      var vivos = t.querySelectorAll("tbody tr:not([hidden])").length;
      (t.closest(".rolagem") || t).hidden = vivos === 0;
    });
    conta.textContent = modo === "tudo" ? total + " itens"
                                        : visivel + " de " + total;
  }

  function mostrar(id, focar){
    abas.forEach(function(b){
      var sel = b.id === "b-" + id;
      b.setAttribute("aria-selected", sel ? "true" : "false");
      b.tabIndex = sel ? 0 : -1;
      document.getElementById(b.getAttribute("aria-controls")).hidden = !sel;
      if(sel && focar) b.focus();
    });
    filtro.hidden = !document.getElementById("p-" + id).querySelector("table.erros");
    if(location.hash.slice(1) !== id) history.replaceState(null, "", "#" + id);
    window.scrollTo(0, 0);
    aplicar();
  }

  abas.forEach(function(b, i){
    b.addEventListener("click", function(){
      mostrar(b.getAttribute("aria-controls").slice(2), false);
    });
    b.addEventListener("keydown", function(e){
      var d = (e.key === "ArrowDown" || e.key === "ArrowRight") ? 1
            : (e.key === "ArrowUp"   || e.key === "ArrowLeft")  ? -1 : 0;
      if(!d) return;
      e.preventDefault();
      mostrar(abas[(i + d + abas.length) % abas.length]
              .getAttribute("aria-controls").slice(2), true);
    });
  });

  [].forEach.call(document.querySelectorAll(".fbt"), function(b){
    b.addEventListener("click", function(){
      modo = b.dataset.f;
      [].forEach.call(document.querySelectorAll(".fbt"), function(o){
        o.setAttribute("aria-pressed", o === b ? "true" : "false");
      });
      aplicar();
    });
  });

  var inicial = location.hash.slice(1);
  mostrar(document.getElementById("p-" + inicial) ? inicial : "tempos", false);
})();
</script>
'''
s = s.rstrip() + '\n' + JS
io.open(p, 'w', encoding='utf-8').write(s)
print('paineis:', len(PAINEIS), ' tamanho:', len(s) // 1024, 'KB')
