#!/usr/bin/env python3
"""
SlapBar — Reproductor de sonidos en la barra de menú del Mac
Packs: SlapMac · DBZ · Cartoon · Retro · Custom
Trigger: Enter y Space globalmente
"""
import os, sys, random, subprocess, threading, time, fcntl
from pathlib import Path

# ── Instancia única ────────────────────────────────────────────────
LOCK_FILE = "/tmp/slapbar.lock"
_lock_fh = open(LOCK_FILE, "w")
try:
    fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    _lock_fh.write(str(os.getpid()))
    _lock_fh.flush()
except IOError:
    print("[SlapBar] Ya hay una instancia corriendo. Saliendo.")
    sys.exit(0)

def ensure(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg,
                        "--break-system-packages", "-q"], capture_output=True)
        subprocess.run([sys.executable, "-m", "pip", "install", pkg,
                        "--user", "-q"], capture_output=True)

ensure("rumps")
ensure("pynput")

import rumps
from pynput import keyboard

# ── Rutas de sonidos ──────────────────────────────────────────────
SOUNDS_BASE = Path.home() / ".vscode/extensions/slapvscode.slapvscode-0.1.0/sounds"

# Íconos por pack
PACK_ICONS = {
    "slap":    "👋",
    "dbz":     "🐉",
    "dragon":  "🐉",
    "cartoon": "🎪",
    "retro":   "🕹",
    "custom":  "⭐",
    "latino":  "🌎",
    "ronaldo": "⚽",
}

def pack_icon(name):
    return PACK_ICONS.get(name.lower(), "🎵")

def get_packs():
    if not SOUNDS_BASE.exists():
        return []
    packs = []
    for d in sorted(SOUNDS_BASE.iterdir()):
        if d.is_dir() and any(
            f.suffix.lower() in {'.mp3', '.wav', '.aiff'}
            for f in d.iterdir()
        ):
            packs.append(d.name)
    return packs or []

def get_sounds(pack):
    d = SOUNDS_BASE / pack
    if not d.exists():
        return []
    return [f for f in d.iterdir() if f.suffix.lower() in {'.mp3', '.wav', '.aiff'}]

# ── Estado global ─────────────────────────────────────────────────
enabled  = True
cur_pack = (get_packs() or ['slap'])[0]
volume   = 0.8
last_t   = 0.0
COOLDOWN = 0.1
cur_proc = None

def play():
    global last_t, cur_proc
    if not enabled: return
    now = time.monotonic()
    if now - last_t < COOLDOWN: return
    last_t = now
    sounds = get_sounds(cur_pack)
    if not sounds: return
    f = random.choice(sounds)
    def _go():
        global cur_proc
        try:
            if cur_proc and cur_proc.poll() is None:
                cur_proc.terminate()
            cur_proc = subprocess.Popen(
                ["afplay", "-v", str(volume), str(f)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[SlapBar] {e}")
    threading.Thread(target=_go, daemon=True).start()

# ── Listener global de teclado (se inicia después de crear la app) ─

# ── App barra de menú ─────────────────────────────────────────────
class SlapBar(rumps.App):
    def __init__(self):
        super().__init__("SlapBar", title=self._title(), quit_button="Salir de SlapBar")

        # Toggle ON/OFF
        self.btn_toggle = rumps.MenuItem("", callback=self.toggle)
        self._update_toggle()

        # Pack items — creados UNA sola vez
        self.pack_items = {}
        for p in get_packs():
            item = rumps.MenuItem(self._pack_label(p), callback=self.set_pack)
            self.pack_items[p] = item

        pack_menu = rumps.MenuItem("🎵  Pack de sonidos")
        for item in self.pack_items.values():
            pack_menu[item.title] = item

        # Separador + opción para abrir carpeta de sonidos
        open_folder = rumps.MenuItem("📂  Abrir carpeta de sonidos", callback=self.open_sounds_folder)

        # Volumen
        self.vol_steps = [
            (0.3,  "🔈  Bajo   30%"),
            (0.5,  "🔉  Medio  50%"),
            (0.8,  "🔊  Alto   80%"),
            (1.2,  "📢  Muy alto 120%"),
            (2.0,  "💥  Máximo  200%"),
        ]
        self.vol_items = {}
        vol_menu = rumps.MenuItem("🔈  Volumen")
        for v, label in self.vol_steps:
            item = rumps.MenuItem(self._vol_label(v, label), callback=self.set_vol)
            item._v = v
            self.vol_items[label] = item
            vol_menu[label] = item

        # Teclas trigger
        self.trigger_space = True
        self.trigger_enter = True
        trigger_menu = rumps.MenuItem("⌨️  Teclas")
        self.btn_enter = rumps.MenuItem("✓   Enter", callback=self.toggle_enter)
        self.btn_space = rumps.MenuItem("✓   Space", callback=self.toggle_space)
        trigger_menu["enter"] = self.btn_enter
        trigger_menu["space"] = self.btn_space

        # Probar
        btn_test = rumps.MenuItem("▶  Probar sonido ahora", callback=self.test)

        # Info
        self.btn_info = rumps.MenuItem(self._info())
        self.btn_info.set_callback(None)

        # Menú — construido UNA sola vez
        self.menu = [
            self.btn_toggle,
            None,
            pack_menu,
            open_folder,
            None,
            vol_menu,
            trigger_menu,
            None,
            btn_test,
            None,
            self.btn_info,
        ]

    # ── helpers ───────────────────────────────────────────────────
    def _title(self):
        ico = pack_icon(cur_pack)
        n   = len(get_sounds(cur_pack))
        return f"{ico} {n}" if enabled else "🔇"

    def _pack_label(self, p):
        ico  = pack_icon(p)
        mark = "✓  " if p == cur_pack else "    "
        return f"{mark}{ico} {p.upper() if p.lower() in ('dbz',) else p.capitalize()}"

    def _vol_label(self, v, label):
        return ("✓  " if abs(v - volume) < 0.05 else "    ") + label

    def _info(self):
        n = len(get_sounds(cur_pack))
        return f"   {n} sonidos · {cur_pack} · Vol {int(volume*100)}%"

    def _update_toggle(self):
        self.btn_toggle.title = "🔊  Sonidos: ON" if enabled else "🔇  Sonidos: OFF"

    def _sync(self):
        self.title = self._title()
        self._update_toggle()
        for p, item in self.pack_items.items():
            item.title = self._pack_label(p)
        for v, label in self.vol_steps:
            self.vol_items[label].title = self._vol_label(v, label)
        self.btn_info.title = self._info()

    # ── callbacks ─────────────────────────────────────────────────
    def toggle(self, _):
        global enabled
        enabled = not enabled
        self._sync()

    def set_pack(self, sender):
        global cur_pack
        raw = sender.title.replace("✓  ", "").replace("    ", "").strip()
        # Quitar el emoji del principio
        for p in self.pack_items:
            label_clean = f"{pack_icon(p)} {p.upper() if p.lower()=='dbz' else p.capitalize()}"
            if raw == label_clean or p.lower() == raw.lower():
                cur_pack = p
                break
        self._sync()
        global last_t
        last_t = 0
        play()

    def set_vol(self, sender):
        global volume
        volume = sender._v
        self._sync()

    def toggle_enter(self, _):
        self.trigger_enter = not self.trigger_enter
        self.btn_enter.title = ("✓   " if self.trigger_enter else "      ") + "Enter"

    def toggle_space(self, _):
        self.trigger_space = not self.trigger_space
        self.btn_space.title = ("✓   " if self.trigger_space else "      ") + "Space"

    def open_sounds_folder(self, _):
        subprocess.Popen(["open", str(SOUNDS_BASE)])

    def test(self, _):
        global last_t
        last_t = 0
        play()
        self.btn_info.title = self._info()


# ── Callback único del listener ───────────────────────────────────
_app_ref = None

def on_press_smart(key):
    try:
        if _app_ref is None: return
        if key == keyboard.Key.enter and _app_ref.trigger_enter:
            play()
        elif key == keyboard.Key.space and _app_ref.trigger_space:
            play()
    except Exception:
        pass


if __name__ == "__main__":
    import atexit
    atexit.register(lambda: os.path.exists(LOCK_FILE) and os.remove(LOCK_FILE))

    # Crear carpetas de packs si no existen (incluye DBZ)
    for pack_name in ["slap", "dbz", "cartoon", "retro", "custom"]:
        (SOUNDS_BASE / pack_name).mkdir(parents=True, exist_ok=True)

    packs = get_packs()
    print(f"[SlapBar] Packs: {packs} | Pack activo: {cur_pack} | Sonidos: {len(get_sounds(cur_pack))}")
    print(f"[SlapBar] Carpeta de sonidos: {SOUNDS_BASE}")

    app = SlapBar()
    _app_ref = app

    # Reiniciar listener con la función inteligente
    smart_lst = keyboard.Listener(on_press=on_press_smart)
    smart_lst.daemon = True
    smart_lst.start()

    app.run()
