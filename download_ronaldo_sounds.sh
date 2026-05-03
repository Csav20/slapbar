#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║     SlapBar — Pack Ronaldo ⚽                                 ║
# ║     Descarga sonidos de Cristiano Ronaldo                    ║
# ║     desde myinstants.com                                     ║
# ╚══════════════════════════════════════════════════════════════╝

DEST="$HOME/.vscode/extensions/slapvscode.slapvscode-0.1.0/sounds/ronaldo"
mkdir -p "$DEST"

echo "⚽ Descargando sonidos de Ronaldo / CR7..."
echo "   Destino: $DEST"
echo ""

BASE="https://www.myinstants.com/media/sounds"

declare -a SOUNDS=(
  "cr_suuu.mp3|cr7-siuu"
  "ronaldo-siuuuu.mp3|ronaldo-siuuuu"
  "ronaldo-siuu.mp3|ronaldo-siuu"
  "ronaldo-suiiiii.mp3|ronaldo-suiiiii"
  "ronaldo-suiiiiiiiiiiiii.mp3|ronaldo-suiii-largo"
  "suuuuuuuuuuuuu.mp3|suuuuu"
  "siiii-ronaldo.mp3|siiii-ronaldo"
  "sii.mp3|grito-siii"
  "ronaldos-siuu-in-good-quality.mp3|siuu-quality"
  "urlo-del-sium-cristiano-ronaldo.mp3|urlo-sium"
  "ishowspeed-ronaldo-sui.mp3|ishowspeed-sui"
  "cristiano-ronaldo-buenas-noches.mp3|buenas-noches"
  "cristiano-ronaldo-forza-juve.mp3|forza-juve"
  "cristiano-ronaldo-scream-in-celebration-of-ballon-dor-2014.mp3|ballon-dor-grito"
  "ronaldo.mp3|ronaldo"
  "tiaspecto.mp3|ti-aspecto"
  "bom-dia-do-cr7.mp3|bom-dia-cr7"
  "chanpions-league.mp3|champions-league"
  "mundial-ronaldinho-soccer-64.mp3|ronaldinho-64"
  "siuuuuuuuu.mp3|siuuuuuu"
)

OK=0
FAIL=0

for entry in "${SOUNDS[@]}"; do
  FILE="${entry%%|*}"
  NAME="${entry##*|}"
  URL="$BASE/$FILE"
  OUT="$DEST/${NAME}.mp3"

  printf "  %-35s → " "$NAME"
  if curl -s -L --max-time 15 -o "$OUT" "$URL" && [ -s "$OUT" ]; then
    SIZE=$(du -h "$OUT" | cut -f1)
    echo "✓ $SIZE"
    OK=$((OK+1))
  else
    echo "✗ (falló)"
    rm -f "$OUT"
    FAIL=$((FAIL+1))
  fi
done

echo ""
echo "══════════════════════════════════════"
echo "  ✓ Descargados: $OK"
echo "  ✗ Fallidos:    $FAIL"
echo "  Carpeta: $DEST"
echo "══════════════════════════════════════"
echo ""

# Reiniciar SlapBar si está corriendo
if pgrep -f slapbar > /dev/null 2>&1; then
  echo "Reiniciando SlapBar..."
  pkill -f slapbar 2>/dev/null || true
  rm -f /tmp/slapbar.lock
  sleep 1
  nohup /opt/homebrew/bin/python3 \
    "$HOME/Library/Application Support/SlapDaemon/slapbar.py" \
    > /tmp/slap.log 2>&1 &
  echo "✓ SlapBar reiniciado — selecciona el pack ⚽ Ronaldo en el menú"
fi
