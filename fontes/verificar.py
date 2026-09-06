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

# ── 7. uniformes declarados e nunca buscados ─────────────────────────
# o codigo usa atalhos como "const uS = n=>gl.getUniformLocation(prog,n)"
buscados = set(re.findall(r"getUniformLocation\(\w+,\s*'(\w+)'\)", codigo))
for at in re.findall(r"const\s+(\w+)\s*=\s*n\s*=>\s*gl\.getUniformLocation", codigo):
    buscados |= set(re.findall(at + r"\('(\w+)'\)", codigo))
for nome, c in blocos.items():
    for decl in re.findall(r"uniform\s+\w+\s+([^;]+);", c):
        for u in decl.split(','):
            u = u.strip().split('[')[0]
            if u and u not in buscados:
                problemas.append("UNIFORME nunca buscado: " + u + " (em " + nome + ")")

print("shaders: " + str(len(blocos)) + "   linhas: " + str(len(fonte.splitlines())))
if problemas:
    print(chr(10).join(problemas))
    raise SystemExit(chr(10) + str(len(problemas)) +
                     " problema(s). Corrija antes de montar.")
print("nada a corrigir")
