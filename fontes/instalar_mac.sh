#!/bin/bash
# Prepara o MacBook para ser o computador do estande (a Cabine) -- 24/09.
#
#   bash fontes/instalar_mac.sh
#
# O que faz, e por que:
#   - Homebrew: e de onde vem o resto (se nao houver, manda instalar e para);
#   - node: o verificador confere cada <script> com node --check, e o
#     quest_eval.mjs fala com o navegador do Quest pelo DevTools;
#   - android-platform-tools: o adb -- o tunel pelo cabo e pela Wi-Fi;
#   - scrcpy: o espelho do Quest na tela (e a saida "espelho do oculos");
#   - Pillow: o montador mexe nas imagens;
#   - a identidade do git nesta pasta;
#   - o atalho "Raizes Cosmicas - Cabine.command" na Mesa: abre o Terminal,
#     segura o Mac acordado (caffeinate) e sobe a Cabine.
# Tudo pode rodar de novo: o que ja existe e pulado.
set -e
cd "$(dirname "$0")/.."
PASTA="$(pwd)"

if ! command -v brew >/dev/null 2>&1; then
  echo "Falta o Homebrew. Instale primeiro (cole no Terminal):"
  echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  echo "e rode este script de novo."
  exit 1
fi

echo "== node"
brew list --formula 2>/dev/null | grep -qx node || brew install node

echo "== adb (android-platform-tools)"
command -v adb >/dev/null 2>&1 || brew install --cask android-platform-tools

echo "== scrcpy"
command -v scrcpy >/dev/null 2>&1 || brew install scrcpy

echo "== python3 + Pillow"
command -v python3 >/dev/null 2>&1 || brew install python
python3 -c "import PIL" 2>/dev/null || python3 -m pip install --user --break-system-packages Pillow 2>/dev/null || python3 -m pip install --user Pillow

echo "== tinytuya (a lampada da sala, pela Wi-Fi)"
python3 -c "import tinytuya" 2>/dev/null || python3 -m pip install --user --break-system-packages tinytuya 2>/dev/null || python3 -m pip install --user tinytuya

echo "== git: quem publica"
git config user.name "Crisia-poria"
git config user.email "admcrisia@gmail.com"

echo "== atalho na Mesa"
ATALHO="$HOME/Desktop/Raízes Cósmicas - Cabine.command"
cat > "$ATALHO" <<EOF
#!/bin/bash
# A Cabine do estande (Raizes Cosmicas). Fecha com Ctrl+C ou pelo botao "Fechar a cabine".
export PATH="/opt/homebrew/bin:/usr/local/bin:\$PATH"
cd "$PASTA"
# caffeinate: o Mac nao dorme nem apaga a tela enquanto a Cabine estiver de pe
exec caffeinate -dims python3 fontes/cabine.py
EOF
chmod +x "$ATALHO"

echo "== conferindo a maquina"
python3 fontes/verificar.py
echo
echo "Pronto. Na Mesa: 'Raízes Cósmicas - Cabine.command' (dois cliques)."
echo "Se o macOS reclamar do .command na primeira vez: botao direito > Abrir."
echo "adb: $(command -v adb || echo 'NAO ACHADO')   scrcpy: $(command -v scrcpy || echo 'NAO ACHADO')   node: $(node --version 2>/dev/null || echo 'NAO ACHADO')"
