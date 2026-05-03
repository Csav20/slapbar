#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║           SlapBar — Instalador                  ║
# ║  Sonidos SlapMac al presionar Enter y Space en todo el Mac  ║
# ╚══════════════════════════════════════════════════════════════╝
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXT_DIR="$HOME/.vscode/extensions/slapvscode.slapvscode-0.1.0"
DAEMON_DIR="$HOME/Library/Application Support/SlapDaemon"
DAEMON_PY="$DAEMON_DIR/slapbar.py"
SOUNDS_DEST="$EXT_DIR/sounds/slap"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           SlapBar — Instalador                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── Detectar Python con pip ────────────────────────────────────────
find_python() {
  for py in /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3 python3; do
    if command -v "$py" &>/dev/null && "$py" -m pip --version &>/dev/null 2>&1; then
      echo "$py"; return
    fi
  done
  echo "python3"
}
PYTHON="$(find_python)"
echo "  Python: $PYTHON ($($PYTHON --version 2>&1))"

# ── 1. Dependencias Python ─────────────────────────────────────────
echo ""
echo "[1/5] Instalando dependencias (rumps + pynput)..."
$PYTHON -m pip install rumps pynput --break-system-packages -q 2>/dev/null || \
$PYTHON -m pip install rumps pynput --user -q 2>/dev/null || \
$PYTHON -m pip install rumps pynput -q
echo "  ✓ OK"

# ── 2. Extensión VSCode ────────────────────────────────────────────
echo ""
echo "[2/5] Instalando extensión VSCode..."
mkdir -p "$SOUNDS_DEST"

# Copiar extension.js
cp "$SCRIPT_DIR/extension_new.js" "$EXT_DIR/extension.js"

# Copiar sonidos si están en la carpeta del paquete
if [ -d "$SCRIPT_DIR/sounds" ]; then
  cp -R "$SCRIPT_DIR/sounds/"* "$EXT_DIR/sounds/" 2>/dev/null || true
  COUNT=$(find "$EXT_DIR/sounds" -name "*.mp3" | wc -l | tr -d ' ')
  echo "  ✓ $COUNT MP3s instalados"
else
  echo "  ⚠ Coloca tus MP3s en: $SOUNDS_DEST"
fi

# ── 3. Instalar daemon ─────────────────────────────────────────────
echo ""
echo "[3/5] Instalando app de barra de menú..."
mkdir -p "$DAEMON_DIR"
cp "$SCRIPT_DIR/slapbar.py" "$DAEMON_PY"
chmod +x "$DAEMON_PY"
echo "  ✓ Instalado en $DAEMON_PY"

# ── 4. Matar instancias anteriores ────────────────────────────────
echo ""
echo "[4/5] Limpiando procesos anteriores..."
pkill -9 -f slap_menubar 2>/dev/null || true
pkill -9 -f slap_daemon  2>/dev/null || true
launchctl unload ~/Library/LaunchAgents/com.slap.daemon.plist 2>/dev/null || true
rm -f /tmp/slap_menubar.lock
sleep 1
echo "  ✓ Limpio"

# ── 5. Lanzar ─────────────────────────────────────────────────────
echo ""
echo "[5/5] Lanzando SlapMac..."
nohup "$PYTHON" "$DAEMON_PY" > /tmp/slap.log 2>&1 &
SLAP_PID=$!
sleep 2

if kill -0 $SLAP_PID 2>/dev/null; then
  echo "  ✓ Corriendo con PID $SLAP_PID"
else
  echo "  ✗ Error al iniciar — revisa: tail -20 /tmp/slap.log"
  tail -20 /tmp/slap.log
fi

# ── Resultado ──────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  INSTALACIÓN COMPLETA                                        ║"
echo "╟──────────────────────────────────────────────────────────────╢"
echo "║  👋  Busca el icono en la barra superior del Mac             ║"
echo "╟──────────────────────────────────────────────────────────────╢"
echo "║  PERMISO REQUERIDO (una sola vez):                           ║"
echo "║  Preferencias del Sistema → Privacidad y Seguridad           ║"
echo "║  → Accesibilidad → agregar python3                           ║"
echo "╟──────────────────────────────────────────────────────────────╢"
echo "║  En VSCode: Cmd+Shift+P → Developer: Reload Window           ║"
echo "╟──────────────────────────────────────────────────────────────╢"
echo "║  Inicio automático:                                          ║"
echo "║  Preferencias → General → Elementos de inicio de sesión      ║"
echo "║  → agregar $DAEMON_PY    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
