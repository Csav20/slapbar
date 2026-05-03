#!/bin/bash
# descargar_dbz.sh — Descarga sonidos Dragon Ball Z desde myinstants.com
# Los guarda en la carpeta correcta para SlapBar

DEST="$HOME/.vscode/extensions/slapvscode.slapvscode-0.1.0/sounds/dbz"
mkdir -p "$DEST"

echo "🐉 Descargando sonidos Dragon Ball Z..."
echo "   Destino: $DEST"
echo ""

BASE="https://www.myinstants.com/media/sounds"

declare -a SOUNDS=(
  "dbz-teleport.mp3|teleport"
  "dragon-ball-z-heavy-punch.mp3|heavy-punch"
  "kamehameha-wave-sound-effect.mp3|kamehameha"
  "gohan-kamehameha.mp3|kamehameha-gohan"
  "vegeta-final-flash.mp3|final-flash"
  "vegeta_2.mp3|vegeta-scream"
  "im-very-angry-goku.mp3|goku-angry"
  "goku-yelling-drip.mp3|goku-yelling"
  "ya-basta-freezer-meme-plantilla-clip-goku-gritando.mp3|ya-basta-freezer"
  "fsdfsdfsdfsd.mp3|dbz-battle"
  "dragon-ball-z-grabbing-sound.mp3|grabbing"
  "dragon-ball-z-body-falling-down-sound.mp3|body-falling"
  "surprised-dbz-sound-effect.mp3|surprised"
  "kaio-ken-times-10.mp3|kaioken-x10"
  "dragon-ball-super-broly-gogeta-goes-into-battle.mp3|gogeta"
  "dragon-ball-flying-nimbus-notification-sound.mp3|nimbus"
  "cha-la.mp3|cha-la-head-cha-la"
  "tfs-krillin-scream-1.mp3|krillin-scream"
  "dragon-ball-punch.mp3|punch"
  "all-dragon-ball-eyecatch-intermission.mp3|intermission-z"
  "all-dragon-ball-eyecatch-intermission_zqSpgBO.mp3|intermission-db"
  "stereo-sayan-3d-lezbeepic-remix-hd-audiotrimmer_qvUxYEt.mp3|super-saiyan-3"
  "shunsuke-kikuchi-m-1525-the-tragic-battle-dragon-ball-z-mp3cut.mp3|tragic-battle"
  "dbza-vegeta-you-ruined-it-and-im-leaving.mp3|vegeta-im-leaving"
  "en-ese-momento-cell-sintio-el-verdadero-terror-v-descarga.mp3|cell-terror"
  "por-fin-apareciste-malnacido-picoro.mp3|piccolo-malnacido"
  "07-sayonara-senshi-tachi-mp3cut.mp3|sayonara"
)

OK=0
FAIL=0

for entry in "${SOUNDS[@]}"; do
  FILE="${entry%%|*}"
  NAME="${entry##*|}"
  URL="$BASE/$FILE"
  OUT="$DEST/${NAME}.mp3"

  printf "  %-40s → " "$NAME"
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

# Reiniciar SlapBar para que detecte los nuevos sonidos
if pgrep -f slap_menubar > /dev/null 2>&1; then
  echo "Reiniciando SlapBar..."
  pkill -f slap_menubar 2>/dev/null || true
  rm -f /tmp/slapbar.lock
  sleep 1
  nohup /opt/homebrew/bin/python3 \
    "$HOME/Library/Application Support/SlapDaemon/slap_menubar.py" \
    > /tmp/slap.log 2>&1 &
  echo "✓ SlapBar reiniciado — selecciona el pack 🐉 DBZ en el menú"
fi
