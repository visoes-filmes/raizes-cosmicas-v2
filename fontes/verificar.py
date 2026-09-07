# -*- coding: utf-8 -*-
"""
Confere o template antes de montar.

Os erros desta obra sao sempre os mesmos, e todos so se manifestam ao
CARREGAR a pagina — quando ja custaram uma viagem ao navegador:

  1. crase perdida num comentario, que fecha o template literal do
     JavaScript no meio e quebra o arquivo inteiro;
  2. nome declarado duas vezes no escopo do modulo, que mata a pagina com
     "already been declared" antes de qualquer coisa rodar;
  3. bloco que roda ao carregar usando um const declarado mais abaixo —
     o console diz apenas "Cannot access before initialization";
  4. constante usada num shader e declarada noutro: o GLSL nao herda nada
     entre shaders, cada um e um programa fechado;
  5. chaves desequilibradas dentro de um shader;
  6. uniforme declarado e nunca buscado, que nao quebra nada e por isso
     passa despercebido.

Rodar isto custa um segundo. Cada um destes ja aconteceu aqui.
"""
import io
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
alvo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'mr.template.html')
fonte = io.open(alvo, encoding='utf-8').read()

problemas = []
BLOCO = re.compile(r"const (\w+) = `([\s\S]*?)`;")
blocos = {m.group(1): m.group(2) for m in BLOCO.finditer(fonte)}
restante = BLOCO.sub("", fonte)

# ── 1. crases fora de shader ─────────────────────────────────────────
soltas = [ln.strip()[:88] for ln in restante.splitlines() if "`" in ln]
if soltas:
    problemas.append("CRASE fora de shader (fecha o template literal no meio):")
    problemas += ["    " + c for c in soltas]

# ── 2. interpolacao dentro de shader ─────────────────────────────────
for nome, corpo in blocos.items():
    if "${" in corpo:
        problemas.append("INTERPOLACAO dentro do shader " + nome)

# ── 3. chaves desequilibradas por shader ─────────────────────────────
for nome, corpo in blocos.items():
    d = corpo.count("{") - corpo.count("}")
    if d:
        problemas.append("CHAVES desequilibradas em " + nome + ": " + str(d))

# corpo do script, sem os shaders
i = restante.find("<script>")
codigo = restante[i:] if i >= 0 else restante
linhas = codigo.splitlines()

# ── 4. colisao de nome no escopo do modulo ───────────────────────────
# so o que esta na coluna zero: dentro de funcao a indentacao existe, e
# nomes iguais em funcoes diferentes nao colidem
topo = {}
for k, ln in enumerate(linhas):
    m = re.match(r'(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)', ln)
    if m:
        topo.setdefault(m.group(1), []).append(k + 1)
    m2 = re.match(r'(?:const|let|var)\s+(.+)', ln)
    if m2 and '=' in m2.group(1):
        for parte in m2.group(1).split(','):
            n = parte.split('=')[0].strip()
            if re.fullmatch(r'[A-Za-z_$][\w$]*', n or ''):
                if (k + 1) not in topo.get(n, []):
                    topo.setdefault(n, []).append(k + 1)
for n, L in sorted(topo.items()):
    if len(set(L)) > 1:
        problemas.append("NOME REPETIDO no modulo: " + n +
                         " (linhas " + str(sorted(set(L))) + ")")

# ── 5. usado antes de existir (zona morta temporal) ──────────────────
declaracao = {}
for k, ln in enumerate(linhas):
    m = re.match(r'(?:const|let)\s+([A-Za-z_$][\w$]*)', ln)
    if m:
        declaracao.setdefault(m.group(1), k + 1)

dentro = False
ini_iife = 0
prof = 0
corpo_iife = []
# O arquivo inteiro esta dentro de uma funcao imediata. Essa e o
# involucro, nao um bloco a analisar: ignoro a primeira que aparecer,
# senao o detector conclui que tudo roda na primeira linha.
primeira = True
ABRE = re.compile(r'\(function\s*\(\s*\)\s*\{')
for k, ln in enumerate(linhas):
    if not dentro and ABRE.match(ln):
        if primeira:
            primeira = False
            continue
        dentro = True
        ini_iife = k + 1
        prof = ln.count("{") - ln.count("}")
        corpo_iife = []
        continue
    if dentro:
        prof += ln.count("{") - ln.count("}")
        corpo_iife.append(ln)
        if prof <= 0:
            texto = chr(10).join(corpo_iife)
            for nome, onde in declaracao.items():
                if onde > ini_iife and re.search(r'\b' + re.escape(nome) + r'\b', texto):
                    problemas.append(
                        "USADO ANTES DE EXISTIR: " + nome +
                        " e usado no bloco da linha " + str(ini_iife) +
                        ", declarado so na " + str(onde))
            dentro = False

# ── 6. constante usada e nao declarada dentro do shader ──────────────
NATIVAS = set(['GL_ES', 'GL_FRAGMENT_PRECISION_HIGH'])
COMENT_LINHA = re.compile('//[^' + chr(10) + ']*')
for nome, c in blocos.items():
    limpo = COMENT_LINHA.sub('', c)
    limpo = re.sub(r'/\*[\s\S]*?\*/', '', limpo)
    declaradas = set(re.findall(r'const\s+\w+\s+([A-Z][A-Z0-9_]*)', limpo))
    usadas = set(re.findall(r'\b([A-Z][A-Z0-9_]+)\b', limpo))
    for u in sorted(usadas - declaradas - NATIVAS):
        problemas.append("CONSTANTE nao declarada no shader " + nome + ": " + u)

# ── 6b. precisao de uniforme diferente entre os dois estagios ──────
# No shader de vertice float e highp por padrao; no de fragmento a precisao
# e a declarada no topo. Um uniforme com o mesmo nome nos dois precisa da
# mesma precisao, senao o programa NAO LINKA — e nao linkar nao aparece
# como erro de shader: o desenho simplesmente nao acontece.
def precisoes(corpo, padrao):
    fora = {}
    for m in re.finditer(r"uniform\s+(?:(highp|mediump|lowp)\s+)?(\w+)\s+([^;]+);", corpo):
        qual, tipo, nomes = m.group(1), m.group(2), m.group(3)
        if tipo.startswith("sampler"):
            continue
        for n in nomes.split(","):
            n = n.strip().split("[")[0]
            if n:
                fora[n] = qual or padrao
    return fora

for nome in list(blocos):
    if not nome.startswith("VS_"):
        continue
    par = "FS_" + nome[3:]
    if par not in blocos:
        continue
    mp = re.search(r"precision\s+(highp|mediump|lowp)\s+float", blocos[par])
    padrao_fs = mp.group(1) if mp else "mediump"
    pv = precisoes(blocos[nome], "highp")
    pf = precisoes(blocos[par], padrao_fs)
    for n in set(pv) & set(pf):
        if pv[n] != pf[n]:
            problemas.append(
                "PRECISAO DIFERENTE do uniforme " + n + ": " + pv[n] +
                " em " + nome + ", " + pf[n] + " em " + par +
                " — o programa nao vai linkar")

# ── 7. uniformes declarados e nunca buscados ─────────────────────────
# o codigo usa atalhos como "const uS = n=>gl.getUniformLocation(prog,n)"
buscados = set(re.findall(r"getUniformLocation\(\w+,\s*'(\w+)'\)", codigo))
for at in re.findall(r"const\s+(\w+)\s*=\s*n\s*=>\s*gl\.getUniformLocation", codigo):
    buscados |= set(re.findall(at + r"\('(\w+)'\)", codigo))
for nome, c in blocos.items():
    for decl in re.findall(r"uniform\s+(?:highp|mediump|lowp)?\s*\w+\s+([^;]+);", c):
        for u in decl.split(','):
            u = u.strip().split('[')[0]
            if u and u not in buscados:
                problemas.append("UNIFORME nunca buscado: " + u + " (em " + nome + ")")

def _semComentario(txt):
    """O codigo do shader sem prosa: so o que a placa le."""
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", " ", txt)
    return txt


# -- 8. o CONTRARIO: usado no shader e nunca declarado ----------------
#
# Esta escapou duas vezes num dia so, e as duas custaram caro: o shader da
# agua ficou horas sem compilar porque "furacao" e "agitacao" foram
# declarados no JavaScript e esquecidos no GLSL. O cenario 3 inteiro ficou
# sem agua e ninguem viu, porque o unico sinal e uma linha no console -- e
# dentro do capacete nao ha console.
#
# A verificacao 7 olhava so um lado: uniforme declarado que ninguem busca.
# Ela nao dizia nada sobre o lado que QUEBRA a obra.
#
# A conta e simples: tudo o que o JavaScript busca de um programa precisa
# existir no shader dele. Como um programa e um par vertice/fragmento,
# procura-se nos dois.
for _vs, _fs in re.findall(r"programa\((VS_\w+),\s*(FS_\w+)\)", codigo):
    _m = re.search(r"const\s+(\w+)\s*=\s*programa\(" + _vs + r"\s*,", codigo)
    if not _m:
        continue
    _prog = _m.group(1)
    _fonte = blocos.get(_vs, "") + "\n" + blocos.get(_fs, "")
    _pedidos = set(re.findall(
        r"getUniformLocation\(" + _prog + r"\s*,\s*'(\w+)'\)", codigo))
    for _at in re.findall(
            r"const\s+(\w+)\s*=\s*n\s*=>\s*gl\.getUniformLocation\("
            + _prog + r"\s*,", codigo):
        _pedidos |= set(re.findall(_at + r"\('(\w+)'\)", codigo))
    for _u in sorted(_pedidos):
        if not re.search(r"\buniform\b[^;]*\b" + re.escape(_u) + r"\b", _fonte):
            problemas.append(
                "UNIFORME BUSCADO E NUNCA DECLARADO: " + _u + " (programa "
                + _prog + ") -- o shader nao compila, e isso nao aparece na tela")
        else:
            # E POR ESTAGIO, e nao pelo par. Um uniforme declarado no
            # vertice e USADO no fragmento nao compila: em GLSL cada estagio
            # tem as suas declaracoes, e o que se ve num e invisivel no
            # outro. Este caso passou pela verificacao acima justamente
            # porque ela olhava os dois shaders somados -- e custou mais uma
            # rodada de "por que nada desenha".
            for _est in (_vs, _fs):
                # SEM OS COMENTARIOS. Este arquivo comenta em portugues, e
                # palavras como "centro", "raio" e "pele" aparecem em prosa o
                # tempo todo -- a primeira versao desta verificacao acusou
                # nove defeitos que eram todos frases explicando o codigo.
                _corpo = _semComentario(blocos.get(_est, ""))
                _usa = re.search(r"\b" + re.escape(_u) + r"\b", _corpo)
                _decl = re.search(
                    r"\buniform\b[^;]*\b" + re.escape(_u) + r"\b", _corpo)
                if _usa and not _decl:
                    problemas.append(
                        "UNIFORME USADO SEM DECLARAR EM " + _est + ": " + _u
                        + " -- esta declarado no outro estagio, e GLSL nao"
                        + " compartilha declaracao entre eles")



print("shaders: " + str(len(blocos)) + "   linhas: " + str(len(fonte.splitlines())))
if problemas:
    print(chr(10).join(problemas))
    raise SystemExit(chr(10) + str(len(problemas)) +
                     " problema(s). Corrija antes de montar.")
print("nada a corrigir")
