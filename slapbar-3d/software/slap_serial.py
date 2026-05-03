#!/usr/bin/env python3
"""
SlapBar 3D — Versión con botonera física ESP32
Extiende SlapBar para escuchar el ESP32 por USB/Serial y cambiar
de pack / reproducir sonido al presionar un botón físico.
"""
import os, sys, random, subprocess, threading, time, fcntl, json, glob
from pathlib import Path

# ── Instancia única ────────────────────────────────────────────────
LOCK_FILE = "/tmp/slapbar3d.lock"
_lock_fh = open(LOCK_FILE, "w")
try:
    fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    _lock_fh.write(str(os.getpid()))
    _lock_fh.flush()
except IOError:
    print("[SlapBar3D] Ya hay una instancia corriendo. Saliendo.")
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
ensure("pyserial")

import rumps
from pynput import keyboard
import serial
import serial.tools.list_ports

# ── Rutas de sonidos ──────────────────────────────────────────────
SOUNDS_BASE = Path.home() / ".vscode/extensions/slapvscode.slapvscode-0.1.0/sounds"

PACK_ICONS = {
    "slap":    "👋",
    "dbz":     "🐉",
    "cartoon": "🎪",
    "retro":   "🕹",
    "custom":  "⭐",
}

def pack_icon(name):
    return PACK_ICONS.get(name.lower(), "🎵")

def get_packs():
    if not SOUNDS_BASE.exists():
        return []
    return [d.name for d in sorted(SOUNDS_BASE.iterdir())
            if d.is_dir() and any(
                f.suffix.lower() in {'.mp3', '.wav', '.aiff'}
                for f in d.iterdir())]

def get_sounds(pack):
    d = SOUNDS_BASE / pack
    if not d.exists():
        return []
    return [f for f in d.iterdir() if f.suffix.lower() in {'.mp3', '.wav', '.aiff'}]

# ── Estado global ─────────────────────────────────────────────────
enabled   = True
cur_pack  = (get_packs() or ['slap'])[0]
volume    = 0.8
last_t    = 0.0
COOLDOWN  = 0.1
cur_proc  = None
esp_port  = None   # Puerto serial del ESP32
esp_conn  = None   # Objeto serial.Serial

# ── Reproducción ──────────────────────────────────────────────────
def play(pack_override=None):
    global last_t, cur_proc
    if not enabled:
        return
    now = time.monotonic()
    if now - last_t < COOLDOWN:
        return
    last_t = now
    pack = pack_override or cur_pack
    sounds = get_sounds(pack)
    if not sounds:
        return
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
            print(f"[SlapBar3D] {e}")
    threading.Thread(target=_go, daemon=True).start()

# ── Auto-detectar ESP32 ───────────────────────────────────────────
def find_esp32_port():
    """Busca automáticamente el puerto del ESP32 (CH340, CP2102, FTDI)."""
    known_ids = [
        "10c4:ea60",   # CP2102 (Silicon Labs)
        "1a86:7523",   # CH340
        "0403:6001",   # FTDI FT232
        "0403:6015",   # FTDI FT231
        "239a:",       # Adafruit
        "2341:",       # Arduino
    ]
    for port in serial.tools.list_ports.comports():
        hwid = port.hwid.lower()
        desc = port.description.lower()
        for kid in known_ids:
            if kid in hwid:
                return port.device
        if "esp" in desc or "silabs" in desc or "ch340" in desc or "uart" in desc:
            return port.device
    # Último recurso: primer /dev/cu.usbserial* o /dev/ttyUSB*
    for pattern in ["/dev/cu.usbserial*", "/dev/cu.SLAB*", "/dev/ttyUSB*", "/dev/ttyACM*"]:
        found = glob.glob(pattern)
        if found:
            return found[0]
    return None

# ── Hilo lector de Serial ─────────────────────────────────────────
_app_ref = None

def serial_reader():
    global cur_pack, esp_conn, esp_port
    BAUD = 115200
    RETRY_WAIT = 5  # segundos entre reintentos

    while True:
        # Buscar puerto
        port = find_esp32_port()
        if not port:
            print("[SlapBar3D] ESP32 no detectado — reintentando en 5s...")
            time.sleep(RETRY_WAIT)
            continue

        print(f"[SlapBar3D] Conectando a ESP32 en {port}...")
        try:
            conn = serial.Serial(port, BAUD, timeout=1)
            esp_port = port
            esp_conn = conn
            if _app_ref:
                _app_ref.update_esp_status(True, port)
            print(f"[SlapBar3D] ✓ ESP32 conectado en {port}")

            last_heartbeat = time.time()
            while True:
                line = conn.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    # Comprobar timeout de heartbeat (15s)
                    if time.time() - last_heartbeat > 15:
                        print("[SlapBar3D] Heartbeat perdido — reconectando...")
                        break
                    continue

                # Parsear JSON del ESP32
                try:
                    data = json.loads(line)
                    event = data.get("event", "")
                    pack  = data.get("pack", "")

                    if event == "heartbeat":
                        last_heartbeat = time.time()

                    elif event == "ready":
                        print(f"[SlapBar3D] ESP32 FW {data.get('fw','?')} listo — {data.get('buttons','?')} botones")
                        last_heartbeat = time.time()
                        if _app_ref:
                            _app_ref.update_esp_status(True, port)

                    elif event == "press":
                        print(f"[SlapBar3D] Botón: {data.get('label','?')} → {pack}")
                        if pack == "random":
                            packs = get_packs()
                            if packs:
                                pack = random.choice(packs)
                        if pack in get_packs():
                            cur_pack = pack
                            if _app_ref:
                                _app_ref._sync()
                        global last_t
                        last_t = 0  # Forzar reproducción inmediata
                        play()

                    elif event == "hold":
                        # Hold = toggle ON/OFF global
                        print(f"[SlapBar3D] Hold detectado — toggle ON/OFF")
                        if _app_ref:
                            _app_ref.toggle(None)

                except json.JSONDecodeError:
                    print(f"[SlapBar3D] Serial raw: {line}")

        except serial.SerialException as e:
            print(f"[SlapBar3D] Error serial: {e}")
            esp_conn = None
            esp_port = None
            if _app_ref:
                _app_ref.update_esp_status(False, None)
            time.sleep(RETRY_WAIT)

# ── Listener global de teclado ────────────────────────────────────
trigger_space = True
trigger_enter = True

def on_press_smart(key):
    try:
        if _app_ref is None:
            return
        if key == keyboard.Key.enter and _app_ref.trigger_enter:
            play()
        elif key == keyboard.Key.space and _app_ref.trigger_space:
            play()
    except Exception:
        pass

# ── App barra de menú ─────────────────────────────────────────────
class SlapBar3D(rumps.App):
    def __init__(self):
        super().__init__("SlapBar3D", title=self._title(), quit_button="Salir")
        self.trigger_enter = True
        self.trigger_space = True

        # Toggle ON/OFF
        self.btn_toggle = rumps.MenuItem("", callback=self.toggle)
        self._update_toggle()

        # Estado ESP32
        self.btn_esp = rumps.MenuItem("⚡  ESP32: buscando...", callback=None)

        # Pack items
        self.pack_items = {}
        for p in get_packs():
            item = rumps.MenuItem(self._pack_label(p), callback=self.set_pack)
            self.pack_items[p] = item
        pack_menu = rumps.MenuItem("🎵  Pack de sonidos")
        for item in self.pack_items.values():
            pack_menu[item.title] = item

        open_folder = rumps.MenuItem("📂  Abrir carpeta de sonidos",
                                     callback=self.open_sounds_folder)

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

        # Teclas
        trigger_menu = rumps.MenuItem("⌨️  Teclas (teclado)")
        self.btn_enter = rumps.MenuItem("✓   Enter", callback=self.toggle_enter)
        self.btn_space = rumps.MenuItem("✓   Space", callback=self.toggle_space)
        trigger_menu["enter"] = self.btn_enter
        trigger_menu["space"] = self.btn_space

        # Botonera ESP32
        esp_menu = rumps.MenuItem("⚡  Botonera ESP32")
        btn_scan = rumps.MenuItem("🔍  Buscar ESP32 ahora", callback=self.scan_esp)
        btn_ports = rumps.MenuItem("📡  Puertos detectados", callback=self.show_ports)
        esp_menu["scan"]  = btn_scan
        esp_menu["ports"] = btn_ports

        btn_test = rumps.MenuItem("▶  Probar sonido", callback=self.test)
        self.btn_info = rumps.MenuItem(self._info())
        self.btn_info.set_callback(None)

        self.menu = [
            self.btn_toggle,
            None,
            self.btn_esp,
            None,
            pack_menu,
            open_folder,
            None,
            vol_menu,
            trigger_menu,
            None,
            esp_menu,
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
        n     = len(get_sounds(cur_pack))
        esp   = f"⚡{esp_port}" if esp_port else "sin ESP32"
        return f"   {n} sonidos · {cur_pack} · {int(volume*100)}% · {esp}"

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

    def update_esp_status(self, connected, port):
        if connected:
            self.btn_esp.title = f"⚡  ESP32: {port} ✓"
        else:
            self.btn_esp.title = "⚡  ESP32: desconectado"
        self._sync()

    # ── callbacks ─────────────────────────────────────────────────
    def toggle(self, _):
        global enabled
        enabled = not enabled
        self._sync()

    def set_pack(self, sender):
        global cur_pack
        raw = sender.title.replace("✓  ", "").replace("    ", "").strip()
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

    def scan_esp(self, _):
        port = find_esp32_port()
        if port:
            self.btn_esp.title = f"⚡  ESP32: encontrado en {port}"
        else:
            self.btn_esp.title = "⚡  ESP32: no detectado — revisa USB"

    def show_ports(self, _):
        ports = [f"{p.device}: {p.description}" for p in serial.tools.list_ports.comports()]
        msg = "\n".join(ports) if ports else "Ningún puerto serial detectado"
        rumps.alert("Puertos disponibles", msg)

    def test(self, _):
        global last_t
        last_t = 0
        play()
        self.btn_info.title = self._info()


# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import atexit
    atexit.register(lambda: os.path.exists(LOCK_FILE) and os.remove(LOCK_FILE))

    # Crear carpetas de packs
    for pack_name in ["slap", "dbz", "cartoon", "retro", "custom"]:
        (SOUNDS_BASE / pack_name).mkdir(parents=True, exist_ok=True)

    packs = get_packs()
    print(f"[SlapBar3D] Packs: {packs} | Pack activo: {cur_pack} | Sonidos: {len(get_sounds(cur_pack))}")
    print(f"[SlapBar3D] Carpeta de sonidos: {SOUNDS_BASE}")

    app = SlapBar3D()
    _app_ref = app

    # Hilo de lectura serial (ESP32)
    serial_thread = threading.Thread(target=serial_reader, daemon=True)
    serial_thread.start()

    # Listener global de teclado
    smart_lst = keyboard.Listener(on_press=on_press_smart)
    smart_lst.daemon = True
    smart_lst.start()

    app.run()
