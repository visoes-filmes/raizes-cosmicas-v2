# -*- coding: utf-8 -*-
"""
Confere o template antes de montar.

Os erros que aparecem nesta obra sao sempre os mesmos, e todos so se
manifestam ao CARREGAR a pagina — quando ja custou uma viagem ao navegador:

  1. crase perdida num comentario, que fecha o template literal do
     JavaScript no meio e quebra o arquivo inteiro;
  2. nome declarado duas vezes no escopo do modulo, que mata a pagina com
     "already been declared" antes de qualquer coisa rodar;
  3. chaves desequilibradas dentro de um shader;
  4. uniforme declarado no shader e nunca buscado no JavaScript, ou o
     contrario — o que nao quebra nada, e por isso passa despercebido.

Rodar isto custa um segundo.
"""
import io, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
alvo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'mr.template.html')
s = io.open(alvo, encoding='utf-8').read()

problemas = []
BLOCO = re.compile(r"const (\w+) = `([\s\S]*?)`;")
blocos = {m.group(1): m.group(2) for m in BLOCO.finditer(s)}
restante = BLOCO.sub("", s)

# ── 1. crases fora de shader ─────────────────────────────────────────
soltas = [ln.strip()[:88] for ln in restante.splitlines() if "`" in ln]
if soltas:
    problemas.append("CRASE fora de shader (fecha o template literal no meio):")
    problemas += ["    " + c for c in soltas]

# ── 2. interpolacao dentro de shader ─────────────────────────────────
for nome, corpo in blocos.items():
    if "${" in corpo:
        problemas.append(f"INTERPOLACAO dentro do shader {nome}: o JavaScript "
                         f"vai tentar avaliar isso.")

# ── 3. chaves desequilibradas por shader ─────────────────────────────
for nome, corpo in blocos.items():
    d = corpo.count("{") - corpo.count("}")
    if d:
        problemas.append(f"CHAVES desequilibradas em {nome}: {d:+d}")

# ── 4. colisao de nome no escopo do modulo ───────────────────────────
i = restante.find("<script>")
corpo = restante[i:] if i >= 0 else restante
linhas = corpo.splitlines()
# so o que esta na coluna zero do corpo do script: dentro de funcao a
# indentacao existe, e nomes iguais em funcoes diferentes nao colidem
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
        problemas.append(f"NOME REPETIDO no escopo do modulo: {n} "
                         f"(linhas {sorted(set(L))})")

# ── 5. uniformes declarados e nunca buscados ─────────────────────────
# O codigo nao chama getUniformLocation direto: usa atalhos como
# "const uS = n=>gl.getUniformLocation(progSala,n)". Entao procuro os dois:
# a chamada literal e qualquer atalho declarado assim.
buscados = set(re.findall(r"getUniformLocation\(\w+,\s*'(\w+)'\)", corpo))
atalhos = re.findall(r"const\s+(\w+)\s*=\s*n\s*=>\s*gl\.getUniformLocation", corpo)
for at in atalhos:
    buscados |= set(re.findall(at + r"\('(\w+)'\)", corpo))
for nome, c in blocos.items():
    for decl in re.findall(r"uniform\s+\w+\s+([^;]+);", c):
        for u in decl.split(','):
            u = u.strip().split('[')[0]
            if u and u not in buscados:
                problemas.append(f"UNIFORME nunca buscado: {u} (em {nome})")

# ── 6. marcadores ────────────────────────────────────────────────────
for marca in re.findall(r"__[A-Z_]+__", s):
    pass  # os marcadores sao esperados aqui; o montador confere depois

print(f"shaders: {len(blocos)}   linhas: {len(s.splitlines())}")
if problemas:
    print("\n".join(problemas))
    raise SystemExit(f"\n{len(problemas)} problema(s). Corrija antes de montar.")
print("nada a corrigir")
