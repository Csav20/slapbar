# SlapMac ESP32 🐉 — Firmware para la botonera física

Este proyecto contiene **únicamente el firmware** para grabar en la placa ESP32.
El ESP32 se conecta al Mac por USB y envía eventos JSON cuando presionas un botón físico.

---

## Contenido

```
SlapMac-ESP32/
├── SlapButtons/
│   ├── SlapButtons.ino   ← Sketch principal de Arduino
│   └── config.h          ← Pines GPIO y parámetros
├── platformio.ini        ← Configuración para PlatformIO (VSCode)
└── LEEME.md              ← Este archivo
```

---

## OPCIÓN A — Arduino IDE (recomendada para principiantes)

### Paso 1 — Instalar Arduino IDE 2
Descarga desde: https://www.arduino.cc/en/software

### Paso 2 — Agregar soporte para ESP32
1. Abre Arduino IDE
2. `File → Preferences` (o `Arduino IDE → Settings` en Mac)
3. En **"Additional boards manager URLs"** pega:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. `Tools → Board → Boards Manager`
5. Busca **"esp32"** → instala **"esp32 by Espressif Systems"** (versión 2.x o 3.x)

### Paso 3 — Instalar librería NeoPixel (solo si usas LEDs)
1. `Tools → Manage Libraries`
2. Busca **"Adafruit NeoPixel"**
3. Instala la versión más reciente

### Paso 4 — Abrir el proyecto
1. `File → Open`
2. Navega a `SlapMac-ESP32/SlapButtons/`
3. Selecciona `SlapButtons.ino`

### Paso 5 — Configurar pines (opcional)
Abre `config.h` y ajusta los pines GPIO si tu cableado es diferente:
```c
#define BTN_DBZ    2    // cambia el número por tu GPIO
#define LED_PIN   -1    // pon -1 si NO usas LEDs NeoPixel
```

### Paso 6 — Conectar el ESP32
1. Conecta el ESP32 al Mac con cable USB
2. `Tools → Board → ESP32 Arduino → ESP32 Dev Module`
3. `Tools → Port` → selecciona el puerto que aparezca (ej: `/dev/cu.usbserial-XXXX`)

> **Si no aparece ningún puerto:** instala el driver CH340 (placas chinas) o CP2102 (Silicon Labs).
> - CH340: https://www.wch-ic.com/downloads/CH34XSER_MAC_ZIP.html
> - CP2102: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

### Paso 7 — Grabar el firmware
1. Presiona el botón **→ Upload** (flecha derecha) en Arduino IDE
2. Si falla: mantén presionado **BOOT** en el ESP32 mientras hace Upload, suéltalo cuando empiece a subir
3. Espera hasta ver: `Done uploading`

### Paso 8 — Verificar
1. `Tools → Serial Monitor`
2. Configura la velocidad a **115200 baud**
3. Deberías ver:
   ```json
   {"event":"ready","device":"SlapMac-ESP32","fw":"1.0.0","buttons":6,"packs":["slap","dbz","cartoon","retro","custom","random"]}
   ```
4. Al presionar un botón físico verás:
   ```json
   {"event":"press","pack":"dbz","button":1,"fw":"1.0.0"}
   ```

---

## OPCIÓN B — PlatformIO en VSCode (para desarrolladores)

### Paso 1 — Instalar PlatformIO
1. En VSCode: Extensions (`Cmd+Shift+X`)
2. Busca **"PlatformIO IDE"** → instalar
3. Reinicia VSCode

### Paso 2 — Abrir el proyecto
1. `File → Open Folder`
2. Selecciona la carpeta `SlapMac-ESP32/`
3. PlatformIO detecta automáticamente el `platformio.ini`

### Paso 3 — Grabar
- Barra inferior → botón **→** (Upload)
- O `Ctrl+Alt+U`

### Paso 4 — Monitor serial
- Barra inferior → botón **🔌** (Monitor)
- O `Ctrl+Alt+S`

---

## Cableado de los botones

Cada botón se conecta entre su GPIO y GND. **Sin resistencias** — el ESP32 usa pull-up interno.

```
  GPIO_PIN ───────────── [Botón] ───── GND
```

| Botón | GPIO | Pack     | Color sugerido LED |
|-------|------|----------|--------------------|
| 1     | 15   | 👋 SLAP   | Naranja |
| 2     | 2    | 🐉 DBZ    | Dorado  |
| 3     | 4    | 🎪 CARTOON| Cian    |
| 4     | 16   | 🕹 RETRO  | Violeta |
| 5     | 17   | ⭐ CUSTOM | Verde   |
| 6     | 5    | 🎲 RANDOM | Blanco  |

**NeoPixel (opcional):**
```
  ESP32 GPIO18 ── DIN del strip
  ESP32 5V     ── VCC del strip
  ESP32 GND    ── GND del strip
```

---

## Pulsación larga (HOLD)

Mantener cualquier botón **más de 0.8 segundos** envía:
```json
{"event":"hold","pack":"dbz","button":1}
```
SlapBar 3D interpreta esto como toggle ON/OFF de los sonidos.

---

## Solución de problemas

**No sube el firmware:**
- Mantén **BOOT** pulsado al iniciar el upload
- Prueba con velocidad 115200 en lugar de 921600
- Verifica que el cable sea de datos (no solo de carga)

**No aparece el puerto serial:**
- Instala el driver CH340 o CP2102 según tu placa
- Prueba otro cable USB

**Los botones no responden:**
- Verifica en el Serial Monitor que los pines GPIO coincidan con `config.h`
- Comprueba que el botón conecta el GPIO a GND (no a 3.3V)

**LEDs no encienden:**
- Verifica que `LED_PIN` en `config.h` apunte al pin de datos del strip
- Confirma que el strip tenga 5V en VCC (no 3.3V)
- Si no usas LEDs, pon `#define LED_PIN -1`

---

## Protocolo JSON

El ESP32 envía estos mensajes al Mac por serial:

| Mensaje | Cuándo |
|---------|--------|
| `{"event":"ready",...}` | Al encender o reiniciar |
| `{"event":"press","pack":"dbz","button":1}` | Al soltar un botón |
| `{"event":"hold","pack":"dbz","button":1}` | Al mantener >0.8s |
| `{"event":"heartbeat","pack":"dbz","enabled":true}` | Cada 5 segundos |

El Mac puede enviar al ESP32:

| Comando | Efecto |
|---------|--------|
| `{"cmd":"enable"}` | Activa feedback LED |
| `{"cmd":"disable"}` | Apaga LEDs |
