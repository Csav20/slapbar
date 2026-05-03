#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║     SlapBar — Pack Latino 🌎                                 ║
# ║     Descarga sonidos típicos chilenos y latinos              ║
# ║     desde myinstants.com                                     ║
# ╚══════════════════════════════════════════════════════════════╝

DEST="$HOME/.vscode/extensions/slapvscode.slapvscode-0.1.0/sounds/latino"
mkdir -p "$DEST"

echo "🌎 Descargando sonidos latinos / chilenos..."
echo "   Destino: $DEST"
echo ""

BASE="https://www.myinstants.com/media/sounds"

declare -a SOUNDS=(
  "1500-es-hora-y-media.mp3|1500-hora-media"
  "yapo-apure-que-tamo-atrasao.mp3|yapo-apure"
  "los-chilenos.mp3|los-chilenos"
  "chao-conchetumare_Fhy0J3u.mp3|chao-ctm"
  "manana-no-hay-clases.mp3|manana-no-hay-clases"
  "que-penca.mp3|que-penca"
  "mira-esa-wea.mp3|mira-esa-wea"
  "callao.mp3|callao-culiao"
  "vamos-a-ver.mp3|vamos-a-ver"
  "no-teni-permiso-pa-salil.mp3|no-teni-permiso"
  "alo-kike-alo-kike-musica-tito.mp3|alo-kike"
  "ando-curao.mp3|ando-curao"
  "fuera-depresion.mp3|fuera-depresion"
  "le-pegoooo.mp3|le-pegoooo"
  "guatona-ballena.mp3|guatona-ballena"
  "soy-joaquin-lavin-tu-mama-medijo.mp3|lavin-tu-mama"
  "atento-atento-central-cambio.mp3|atento-central-cambio"
  "pipa-pipa-pipa-no-no-no-corto.mp3|pipa-no-no-no"
  "suspencion-permanente.mp3|suspension-permanente"
  "conchetumare-ayyyy.mp3|conchetumare-ayy"
  "popin-se-equivoco-lo-hizo-mal-penca.mp3|popin-penca"
  "y-me-le-ocurrio-otra-idea.mp3|me-ocurrio-otra-idea"
  "sapa-marite.mp3|sapa-marite"
  "cuanto-cobra-la-maraca_IaP5lhc.mp3|cuanto-cobra-maraca"
  "yo-te-amo-te-quiero.mp3|yo-te-amo"
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
  echo "✓ SlapBar reiniciado — selecciona el pack 🌎 Latino en el menú"
fi
