#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║        SlapMac 3D — Instalador completo                     ║
# ║  Instala dependencias, daemon serial, y copia el firmware   ║
# ╚══════════════════════════════════════════════════════════════╝
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
EXT_DIR="$HOME/.vscode/extensions/slapvscode.slapvscode-0.1.0"
DAEMON_DIR="$HOME/Library/Application Support/SlapDaemon"
DAEMON_PY="$DAEMON_DIR/slap_serial.py"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        SlapMac 3D — Instalador                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── Detectar Python ────────────────────────────────────────────────
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
echo ""

# ── 1. Dependencias Python ─────────────────────────────────────────
echo "[1/6] Instalando dependencias Python..."
$PYTHON -m pip install rumps pynput pyserial --break-system-packages -q 2>/dev/null || \
$PYTHON -m pip install rumps pynput pyserial --user -q 2>/dev/null || \
$PYTHON -m pip install rumps pynput pyserial -q
echo "  ✓ rumps + pynput + pyserial instalados"
echo ""

# ── 2. Extensión VSCode ────────────────────────────────────────────
echo "[2/6] Actualizando extensión VSCode..."
if [ -f "$PROJECT_DIR/software/extension_new.js" ]; then
  cp "$PROJECT_DIR/software/extension_new.js" "$EXT_DIR/extension.js"
  echo "  ✓ extension.js actualizado"
elif [ -f "$PROJECT_DIR/../SlapMac-VSCode/extension_new.js" ]; then
  cp "$PROJECT_DIR/../SlapMac-VSCode/extension_new.js" "$EXT_DIR/extension.js"
  echo "  ✓ extension.js actualizado"
else
  echo "  ⚠ No se encontró extension_new.js (instala SlapMac-VSCode primero)"
fi
echo ""

# ── 3. Copiar sonidos ──────────────────────────────────────────────
echo "[3/6] Configurando carpetas de sonidos..."
for pack in slap dbz cartoon retro custom; do
  mkdir -p "$EXT_DIR/sounds/$pack"
done
# Copiar sonidos del Desktop si existen
if [ -d "$HOME/Desktop/slapmac_sounds_dec" ]; then
  cp -Rn "$HOME/Desktop/slapmac_sounds_dec/"* "$EXT_DIR/sounds/slap/" 2>/dev/null || true
  echo "  ✓ Sonidos SlapMac copiados desde Desktop"
fi
COUNT=$(find "$EXT_DIR/sounds" -name "*.mp3" 2>/dev/null | wc -l | tr -d ' ')
echo "  ✓ $COUNT MP3s encontrados"
echo ""

# ── 4. Instalar daemon serial ──────────────────────────────────────
echo "[4/6] Instalando daemon SlapBar3D..."
mkdir -p "$DAEMON_DIR"
cp "$SCRIPT_DIR/slap_serial.py" "$DAEMON_PY"
chmod +x "$DAEMON_PY"
echo "  ✓ Instalado en: $DAEMON_PY"
echo ""

# ── 5. Matar procesos anteriores ──────────────────────────────────
echo "[5/6] Limpiando procesos anteriores..."
pkill -9 -f slap_menubar  2>/dev/null || true
pkill -9 -f slap_serial   2>/dev/null || true
pkill -9 -f slap_daemon   2>/dev/null || true
launchctl unload ~/Library/LaunchAgents/com.slap.daemon.plist 2>/dev/null || true
rm -f /tmp/slapbar.lock /tmp/slapbar3d.lock
sleep 1
echo "  ✓ Limpio"
echo ""

# ── 6. Lanzar SlapBar3D ────────────────────────────────────────────
echo "[6/6] Lanzando SlapBar3D..."
nohup "$PYTHON" "$DAEMON_PY" > /tmp/slap3d.log 2>&1 &
SLAP_PID=$!
sleep 2

if kill -0 $SLAP_PID 2>/dev/null; then
  echo "  ✓ Corriendo con PID $SLAP_PID"
else
  echo "  ✗ Error — revisa: tail -20 /tmp/slap3d.log"
  tail -20 /tmp/slap3d.log
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  INSTALACIÓN COMPLETA                                        ║"
echo "╟──────────────────────────────────────────────────────────────╢"
echo "║  🐉  Busca el ícono del pack activo en la barra del Mac      ║"
echo "╟──────────────────────────────────────────────────────────────╢"
echo "║  PERMISOS REQUERIDOS (una sola vez):                         ║"
echo "║  Preferencias → Privacidad → Accesibilidad → agregar python3 ║"
echo "╟──────────────────────────────────────────────────────────────╢"
echo "║  FIRMWARE ESP32:                                             ║"
echo "║  Abre firmware/slapbuttons.ino en Arduino IDE               ║"
echo "║  Instala librería: Adafruit NeoPixel (opcional)             ║"
echo "║  Placa: ESP32 Dev Module | Velocidad: 921600                 ║"
echo "╟──────────────────────────────────────────────────────────────╢"
echo "║  Conecta el ESP32 por USB → se detecta automáticamente      ║"
echo "╟──────────────────────────────────────────────────────────────╢"
echo "║  Log en tiempo real:                                         ║"
echo "║  tail -f /tmp/slap3d.log                                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
