# SlapBar 🎵

**SlapBar** es una app de barra de menú para macOS que reproduce sonidos al presionar **Enter** o **Space** en cualquier aplicación — incluyendo VSCode.

Soporta múltiples packs: 👋 SlapMac · 🐉 DBZ · 🌎 Latino · 🎪 Cartoon · 🕹 Retro · ⭐ Custom

> 🎮 ¿Quieres una botonera física? Mira [`slapbar-3d/`](./slapbar-3d/) y [`slapbar-esp32/`](./slapbar-esp32/)

---

## ☕ Apoya el proyecto

Si te gusta SlapBar y quieres que siga creciendo, puedes invitarme un café:

[![Donar con PayPal](https://img.shields.io/badge/Donar-PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?business=csav20%40gmail.com&currency_code=USD)

---

## Características

- 🔊 Sonidos globales en todo el Mac al presionar **Enter** y/o **Space**
- 🎵 Múltiples **packs de sonidos** seleccionables desde la barra de menú
- 🐉 Pack **Dragon Ball Z** — 27 sonidos (Kamehameha, Vegeta, Goku, Cha-La...)
- 🌎 Pack **Latino** — 25 frases y sonidos típicos chilenos y latinos
- 🔈 Control de **volumen** (30% a 200%)
- ⌨️ Toggle individual para **Enter** y **Space**
- 🔇 Toggle ON/OFF desde la barra de menú
- 💻 Integración con **VSCode**
- 🎮 Soporte para **botonera física ESP32** (ver `slapbar-3d/`)

---

## Instalación rápida

### Requisitos
- macOS 12+
- Python 3 Homebrew: `/opt/homebrew/bin/python3`
- VSCode (opcional)

### 1 — Clonar
```bash
git clone https://github.com/TU_USUARIO/slapbar.git
cd slapbar
```

### 2 — Instalar
```bash
bash install.sh
```

### 3 — Permiso de Accesibilidad *(obligatorio para sonido global)*
```
Preferencias del Sistema → Privacidad y Seguridad → Accesibilidad
→ Agregar /opt/homebrew/bin/python3
```

### 4 — Descargar packs de sonidos

**Pack DBZ 🐉**
```bash
bash download_dbz_sounds.sh
```

**Pack Latino 🌎**
```bash
bash download_latino_sounds.sh
```

---

## Estructura del repositorio

```
slapbar/
├── slapbar.py                  ← App principal (barra de menú macOS)
├── extension.js                ← Extensión VSCode
├── install.sh                  ← Instalador
├── download_dbz_sounds.sh      ← Descarga 27 sonidos DBZ
├── download_latino_sounds.sh   ← Descarga 25 sonidos Latinos 🌎
├── sounds/
│   ├── slap/                   ← Tus MP3s de SlapMac
│   ├── dbz/                    ← Dragon Ball Z
│   ├── latino/                 ← Frases chilenas y latinas
│   ├── cartoon/
│   ├── retro/
│   └── custom/
│
├── slapbar-3d/                 ← Botonera física impresa en 3D
│   ├── firmware/               ← Firmware ESP32 (Arduino)
│   ├── software/               ← Daemon Python con serial
│   ├── 3d_models/              ← STL + FreeCAD macros
│   └── wiring/                 ← Diagrama de cableado
│
├── slapbar-esp32/              ← Proyecto ESP32 standalone
│   ├── SlapButtons/
│   │   ├── SlapButtons.ino
│   │   └── config.h
│   └── platformio.ini
│
└── .github/
    └── ISSUE_TEMPLATE/
```

---

## Pack Latino 🌎

25 frases y sonidos típicos chilenos y latinos:

| Sonido | Descripción |
|--------|-------------|
| `1500-hora-media` | "Son las 1500, es hora y media" |
| `yapo-apure` | "Yapo apure que tamo atrasao" |
| `que-penca` | "¡Qué penca!" |
| `mira-esa-wea` | "Mira esa wea" |
| `vamos-a-ver` | "¡Vamos a ver!" |
| `ando-curao` | "Ando curao" |
| `alo-kike` | "Aló Kike" |
| `callao-culiao` | "Queate callao malo culiao y juega noma" |
| `no-teni-permiso` | "No teni permiso pa salil" |
| `manana-no-hay-clases` | "Mañana no hay clases" |
| `fuera-depresion` | "¡Fuera depresión!" |
| `los-chilenos` | "Los chilenos" |
| `suspension-permanente` | "Suspención permanente" |
| `chao-ctm` | "Chao..." |
| `le-pegoooo` | "Le pegoooo" |
| y 10 más... | |

---

## Uso del ícono en la barra

| Acción | Resultado |
|--------|-----------|
| **Enter** o **Space** | Reproduce sonido del pack activo |
| 🔊 Sonidos: ON/OFF | Activa / desactiva todo |
| 🎵 Pack de sonidos | Cambia de pack |
| 🔈 Volumen | 30% – 200% |
| ▶ Probar sonido | Reproduce ahora |
| 📂 Abrir carpeta | Abre sounds/ en Finder |

---

## Botonera física 🎮

¿Quieres botones físicos reales con logos en relieve?

- **`slapbar-3d/`** — Caja imprimible en 3D, capuchones con logos (STL incluidos), daemon con soporte serial para ESP32
- **`slapbar-esp32/`** — Firmware listo para grabar en ESP32 vía Arduino IDE o PlatformIO

Ver [`slapbar-3d/LEEME.md`](./slapbar-3d/LEEME.md) para instrucciones completas.

---

## Solución de problemas

**No aparece el ícono:**
```bash
pkill -9 -f slapbar; rm -f /tmp/slapbar.lock; sleep 1
nohup /opt/homebrew/bin/python3 "$HOME/Library/Application Support/SlapDaemon/slapbar.py" \
  > /tmp/slap.log 2>&1 &
```

**Ver log en tiempo real:**
```bash
tail -f /tmp/slap.log
```

**Sin sonido global:** Verifica el permiso de Accesibilidad.

---

## Dependencias

| Librería | Uso |
|----------|-----|
| [rumps](https://github.com/jaredks/rumps) | App barra de menú macOS |
| [pynput](https://github.com/moses-palmer/pynput) | Listener global de teclado |
| [pyserial](https://github.com/pyserial/pyserial) | Comunicación con ESP32 (slapbar-3d) |

---

## Licencia

MIT License — libre para uso personal y modificación.

---

## ☕ Apoya el proyecto

[![Donar con PayPal](https://img.shields.io/badge/Donar-PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?business=csav20%40gmail.com&currency_code=USD)

Los sonidos de Dragon Ball Z son propiedad de Toei Animation.  
Los sonidos de myinstants.com pertenecen a sus respectivos autores.
