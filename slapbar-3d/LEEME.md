# SlapMac 3D 🐉👋 — Botonera física con ESP32

Convierte los packs de sonido de SlapBar en **botones físicos imprimibles en 3D**,
controlados por un ESP32 conectado al Mac por USB.

---

## ¿Qué hace?

Al presionar un botón físico en la botonera:
1. El ESP32 detecta la pulsación y envía un mensaje JSON al Mac por USB.
2. El daemon Python (`slap_serial.py`) lo recibe, cambia el pack activo y reproduce un sonido.
3. El ícono en la barra de menú se actualiza automáticamente.

El ESP32 también actúa como **detector de latido** — si se desconecta, SlapBar 3D lo detecta y sigue funcionando con teclado.

---

## Contenido del proyecto

```
SlapMac-3D/
├── firmware/
│   ├── slapbuttons.ino    ← Firmware ESP32 (Arduino IDE)
│   └── config.h           ← Pines GPIO y parámetros
├── software/
│   ├── slap_serial.py     ← Daemon Python (SlapBar3D con serial)
│   └── instalar_3d.sh     ← Instalador completo
├── 3d_models/
│   ├── enclosure.scad     ← Caja paramétrica (OpenSCAD)
│   └── botones.scad       ← Tapas de botones con logos
├── wiring/
│   └── conexiones.md      ← Diagrama de cableado y BOM
└── LEEME.md               ← Este archivo
```

---

## Paso a paso completo

### PARTE 1 — Hardware

#### 1.1 Componentes necesarios
Ver la lista completa en `wiring/conexiones.md`. Lo esencial:
- ESP32 DevKit v1 (~$6)
- 6 botones pulsadores de 22mm (~$1-2 c/u)
- Cable USB para el ESP32
- Filamento PLA para la caja y los botones

#### 1.2 Cableado
Cada botón se conecta entre su GPIO y GND (**sin resistencias**, el ESP32 usa pull-up interno):

| Botón | GPIO | Pack |
|-------|------|------|
| 1 | 15 | 👋 SLAP |
| 2 | 2 | 🐉 DBZ |
| 3 | 4 | 🎪 CARTOON |
| 4 | 16 | 🕹 RETRO |
| 5 | 17 | ⭐ CUSTOM |
| 6 | 5 | 🎲 RANDOM |

Ver diagrama detallado en `wiring/conexiones.md`.

#### 1.3 Impresión 3D con FreeCAD

Los modelos 3D son **macros Python de FreeCAD** (`.FCMacro`). Se ejecutan dentro de FreeCAD y generan los sólidos paramétricos listos para exportar a STEP o STL.

**Programa requerido:** [FreeCAD 0.21+](https://www.freecad.org) (gratuito, macOS/Windows/Linux)

---

**Caja (`enclosure.FCMacro`):**

1. Abre FreeCAD
2. `Macro → Macros...` → botón **Ejecutar** (o `Execute`)
3. Navega a `SlapMac-3D/3d_models/enclosure.FCMacro` → **Ejecutar**
4. Verás la caja base + tapa en vista 3D
5. Para ajustar dimensiones: edita las variables al inicio del macro (BOX_W, BTN_D, etc.)
6. Exportar: `File → Export` → elige **STEP** (para slicer) o **STL Mesh**

Genera dos piezas:
- **Caja base** — con postes para tornillos M3, ranura USB y plataforma ESP32
- **Tapa superior** — con los 6 huecos de 22mm para los botones

---

**Tapas de botones (`botones.FCMacro`):**

1. `Macro → Macros...` → selecciona `botones.FCMacro` → **Ejecutar**
2. Genera los 6 capuchones en fila (DBZ, SLAP, CARTOON, RETRO, CUSTOM, RANDOM)
3. Cada capuchón tiene texto en relieve en la cara superior
4. Exportar cada uno: selecciona el objeto → `File → Export → STL`

---

**Configuración de impresión recomendada:**

| Pieza | Material | Capa | Relleno | Soporte |
|-------|----------|------|---------|---------|
| Caja base | PLA/PETG | 0.2mm | 20% | No |
| Tapa | PLA/PETG | 0.2mm | 15% | No |
| Capuchones | PLA (2 colores) | 0.15mm | 100% | No |

**Truco multicolor en capuchones:** Programa una pausa en la capa donde empieza el texto (~2mm de altura), cambia el filamento, y reanuda — el texto queda en un color diferente al cuerpo.

**Ajustar diámetro del botón:** Si tus botones son de 16mm o 19mm en lugar de 22mm, cambia `BTN_D` en `enclosure.FCMacro` y `CAP_OD/CAP_ID` en `botones.FCMacro`.

---

### PARTE 2 — Firmware ESP32

#### 2.1 Instalar Arduino IDE
1. Descarga [Arduino IDE 2](https://www.arduino.cc/en/software)
2. `File → Preferences → Additional board manager URLs`:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. `Tools → Board → Boards Manager` → busca "esp32" → instala "esp32 by Espressif"

#### 2.2 Librería NeoPixel (opcional, si usas LEDs)
`Tools → Manage Libraries` → busca "Adafruit NeoPixel" → instala

#### 2.3 Cargar el firmware
1. Abre `firmware/slapbuttons.ino` en Arduino IDE
2. Edita `config.h` si cambiaste los pines
3. Conecta el ESP32 por USB
4. `Tools → Board → ESP32 Dev Module`
5. `Tools → Port → /dev/cu.usbserial-...` (el que aparezca)
6. `Sketch → Upload` (Ctrl+U)
7. Abre `Tools → Serial Monitor` a 115200 baud — verás:
   ```json
   {"event":"ready","fw":"1.0.0","buttons":6,"hello":"SlapMac 3D"}
   ```

---

### PARTE 3 — Software (Mac)

#### 3.1 Instalar SlapBar3D
```bash
bash ~/Desktop/SlapMac-3D/software/instalar_3d.sh
```

Esto instala `rumps`, `pynput` y **`pyserial`**, copia el daemon y lo lanza.

#### 3.2 Dar permiso de Accesibilidad
`Sistema → Privacidad y Seguridad → Accesibilidad → +` → agrega `/opt/homebrew/bin/python3`

#### 3.3 Recargar VSCode
`Cmd+Shift+P → Developer: Reload Window`

#### 3.4 Verificar que el ESP32 fue detectado
En la barra de menú verás el ícono del pack. Al hacer clic:
```
⚡  ESP32: /dev/cu.usbserial-XXXX ✓
```

#### 3.5 Ver log en tiempo real
```bash
tail -f /tmp/slap3d.log
```

---

## Uso de la botonera

| Acción | Resultado |
|--------|-----------|
| **Presionar botón** | Cambia el pack y reproduce un sonido |
| **Mantener 0.8s** | Toggle ON/OFF de SlapBar |
| **Botón RANDOM** | Sonido aleatorio de cualquier pack |
| **Ícono menú → Pack** | También puedes cambiar por software |

---

## Solución de problemas

**ESP32 no detectado:**
```bash
ls /dev/cu.*    # ver puertos disponibles
# o en el menú: ⚡ Botonera ESP32 → Buscar ESP32 ahora
```

**No sube el firmware:**
- Mantén pulsado el botón **BOOT** del ESP32 mientras presionas Upload
- Prueba velocidad 115200 en lugar de 921600

**Botón no responde:**
- Verifica el GPIO en `config.h`
- Prueba el Serial Monitor — al presionar debe aparecer el JSON
- Verifica que un cable conecte el botón a GND

**Icono duplicado en barra de menú:**
```bash
pkill -9 -f slap_serial; rm -f /tmp/slapbar3d.lock; sleep 1
nohup /opt/homebrew/bin/python3 "$HOME/Library/Application Support/SlapDaemon/slap_serial.py" > /tmp/slap3d.log 2>&1 &
```

---

## Personalización

### Agregar más packs
1. Crea carpeta en `~/.vscode/extensions/slapvscode.slapvscode-0.1.0/sounds/mi_pack/`
2. Pon los MP3s ahí
3. Asigna un botón extra en `config.h` y `slapbuttons.ino`
4. SlapBar3D los detecta automáticamente

### Cambiar el tamaño de la caja
Edita las variables al inicio de `enclosure.scad`:
```
BOX_W = 200;   // Ancho
BOX_H = 110;   // Alto  
BOX_D = 40;    // Profundidad
```

### Logos SVG en los botones
1. Exporta tu logo como SVG desde Inkscape (objeto seleccionado → Export)
2. En `botones.scad`, reemplaza `text_relief()` por:
   ```
   translate([0,0,CAP_H])
     linear_extrude(0.8)
       import("tu_logo.svg", center=true);
   ```

---

## Requisitos

- macOS 12 o superior
- Python 3 con Homebrew (`/opt/homebrew/bin/python3`)
- Arduino IDE 2.x
- ESP32 DevKit v1 o compatible
- OpenSCAD (para editar/exportar modelos 3D)
- Impresora 3D (cualquier FDM: Bambu, Prusa, Ender, etc.)
