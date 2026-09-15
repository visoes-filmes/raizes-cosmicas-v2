# -*- coding: utf-8 -*-
"""O banco de provas dos shaders.

    python fontes/provar_shaders.py        # escreve _prova.html
    abrir http://localhost:<porta>/_prova.html na bancada e ler a pagina

O verificar.py e estatico e nao compila GLSL: hoje (14/09) um 'else'
orfao no FS_SOLIDA e um uniforme com precisao diferente entre o VS_AGUA e
um fragmento novo passaram por ele, e a obra abriu sem nenhuma superficie
-- sem erro em lugar nenhum alem do console. Este script tira todos os
shaders do template e todos os pares programa(VS, FS), e monta uma pagina
que os compila e linka num contexto WebGL de verdade, listando o log de
cada um que falhar. E o que a nota do CLAUDE.md pede: "extrair os dois
shaders do template para arquivos, servi-los, e compila-los num contexto
WebGL separado lendo o log".

E andaime de bancada: _prova.html esta no .gitignore.
"""
import io
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fonte = io.open(os.path.join(RAIZ, "fontes", "mr.template.html"), encoding="utf-8").read()

shaders = {m.group(1): m.group(2)
           for m in re.finditer(r"const ((?:VS|FS)_\w+) = `([\s\S]*?)`;", fonte)}
pares = re.findall(r"programa\((VS_\w+),\s*(FS_\w+)\)", fonte)
faltam = [n for p in pares for n in p if n not in shaders]
assert not faltam, "shader sem fonte: %s" % faltam

pagina = """<!doctype html><meta charset="utf-8"><title>prova dos shaders</title>
<pre id="saida">compilando...</pre>
<script>
const SH = %s, PARES = %s;
const gl = document.createElement('canvas').getContext('webgl');
const linhas = [];
function compila(tipo, nome){
  const sh = gl.createShader(tipo); gl.shaderSource(sh, SH[nome]); gl.compileShader(sh);
  if(!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) linhas.push('COMPILA ' + nome + ': ' + gl.getShaderInfoLog(sh));
  return sh;
}
for(const [vs, fs] of PARES){
  const a = compila(gl.VERTEX_SHADER, vs), b = compila(gl.FRAGMENT_SHADER, fs);
  const pr = gl.createProgram(); gl.attachShader(pr, a); gl.attachShader(pr, b); gl.linkProgram(pr);
  if(!gl.getProgramParameter(pr, gl.LINK_STATUS)) linhas.push('LINKA ' + vs + ' + ' + fs + ': ' + gl.getProgramInfoLog(pr));
}
document.getElementById('saida').textContent = linhas.length ? linhas.join('\\n') : 'todos os ' + PARES.length + ' programas compilam e linkam';
window.__prova = linhas;
</script>"""
io.open(os.path.join(RAIZ, "_prova.html"), "w", encoding="utf-8").write(
    pagina % (json.dumps(shaders), json.dumps(pares)))
print("_prova.html: %d shaders, %d programas" % (len(shaders), len(pares)))
