# Mede os quadros de uma variante no Quest, cenarios 1 e 3 (24/09):
#   python fontes/estande.py > estande.log   (num terminal a parte; os relatos caem la)
#   bash fontes/medir_quadros.sh v5.html
# Precisa do adb forward 9222 (o DevTools) e da aba da obra aberta no navegador do Quest.
S="$(cd "$(dirname "$0")" && pwd)"; cd "$S/.."; LOG="${ESTANDE_LOG:-estande.log}"
A="fontes/platform-tools/adb.exe${ANDROID_SERIAL:+ -s $ANDROID_SERIAL}"
fps(){ $A logcat -d -s VrApi 2>/dev/null | tail -1 | grep -o -E "FPS=[0-9]+/72|App=[0-9.]+ms" | tr '\n' ' '; }
url="http://localhost:8765/$1"
$A logcat -c 2>/dev/null
node "$S/quest_eval.mjs" "localhost:8765" "location.href='$url'; 'indo'" >/dev/null 2>&1 || { $A shell am start -a android.intent.action.VIEW -d "$url" com.oculus.browser >/dev/null 2>&1; }
sleep 22
id=$(curl -s http://localhost:9222/json | python -c "import json,sys; print([t for t in json.load(sys.stdin) if t['type']=='page' and 'localhost:8765' in t['url']][0]['id'])")
curl -s "http://localhost:9222/json/activate/$id" >/dev/null
node "$S/quest_eval.mjs" "localhost:8765" "document.getElementById('bIniciar').click(); 'clicado'" gesto >/dev/null
sleep 10
echo "== $1  $(grep -o 'CAMADA [^ ]* escala=[^ ]* suavizar=[a-z]*' "$LOG" | tail -1)"
for t in 30 470; do node "$S/quest_eval.mjs" "localhost:8765" "raizes.ir($t); 'ok'" >/dev/null; sleep 9; echo "   t=$t $(node "$S/quest_eval.mjs" "localhost:8765" "raizes.onde().tempo+' cena '+raizes.onde().cena") $(fps)"; done
node "$S/quest_eval.mjs" "localhost:8765" "document.getElementById('bParar').click(); 'parou'" >/dev/null 2>&1
sleep 3
