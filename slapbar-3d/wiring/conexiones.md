# Diagrama de Cableado — SlapMac 3D

## ESP32 DevKit v1 — Pinout de la botonera

```
                    ┌─────────────────────────────┐
                    │        ESP32 DevKit v1       │
                    │                              │
  BTN_SLAP   ──────┤ GPIO15         GPIO18 ├────── NeoPixel DATA
  BTN_DBZ    ──────┤ GPIO2                  │
  BTN_CARTOON──────┤ GPIO4          3.3V   ├────── NeoPixel VCC (si <4 LEDs)
  BTN_RETRO  ──────┤ GPIO16           GND  ├────── GND común
  BTN_CUSTOM ──────┤ GPIO17                │
  BTN_RANDOM ──────┤ GPIO5                 │
                    │             USB ════════════> Mac (Serial + 5V)
                    └─────────────────────────────┘
```

## Esquema de un botón (se repite ×6)

```
  GPIO_PIN ──────────────────┬──── [Botón momentáneo] ──── GND
                             │
                      (Pull-up interno del ESP32 — INPUT_PULLUP)
                      Normal = HIGH · Presionado = LOW
```

> **No necesitas resistencias externas** — el ESP32 tiene pull-ups internos activados con `INPUT_PULLUP`.

---

## LEDs opcionales — NeoPixel WS2812B (1 LED por botón)

```
  5V  ──── VCC del strip NeoPixel
  GND ──── GND del strip
  GPIO18 ── DIN (datos) del primer LED

  Orden de LEDs:    LED0=SLAP · LED1=DBZ · LED2=CARTOON
                    LED3=RETRO · LED4=CUSTOM · LED5=RANDOM
```

Si usas LEDs individuales simples (no NeoPixel):
- Un LED + resistencia de 220Ω desde cada GPIO a GND
- Actualiza `LED_PIN -1` en `config.h` y maneja los pines manualmente

---

## Lista de componentes (BOM)

| # | Componente | Especificación | Cantidad | Precio aprox. |
|---|-----------|----------------|----------|---------------|
| 1 | ESP32 DevKit v1 | WROOM-32, 38 pines | 1 | $5-8 USD |
| 2 | Botones pulsadores | 22mm, momentáneo, con LED | 6 | $1-2 c/u |
| 3 | Tira NeoPixel | WS2812B, 6 LEDs | 1 segmento | $3-5 USD |
| 4 | Cable dupont | Macho-hembra 20cm | 20 | $2-3 USD |
| 5 | Cable USB | Micro-USB o USB-C (según ESP32) | 1 | $2-4 USD |
| 6 | PLA / PETG | 2 colores (caja + logos) | ~150g | $3-5 USD |
| 7 | Tornillos M3×8 | Cabeza plana | 4 | $1 USD |
| 8 | Insertos de calor M3 | Para tapa roscada | 4 | $2 USD |
| 9 | Pies antideslizantes | Auto-adhesivos, 10mm | 4 | $1 USD |

**Total estimado: $20-35 USD**

---

## Conexión rápida (colores sugeridos)

| Cable | Desde | Hasta | Color |
|-------|-------|-------|-------|
| GND común | ESP32 GND | Rail GND breadboard/PCB | Negro |
| SLAP | GPIO15 | Botón 1 terminal A | Naranja |
| DBZ | GPIO2 | Botón 2 terminal A | Amarillo |
| CARTOON | GPIO4 | Botón 3 terminal A | Azul |
| RETRO | GPIO16 | Botón 4 terminal A | Violeta |
| CUSTOM | GPIO17 | Botón 5 terminal A | Verde |
| RANDOM | GPIO5 | Botón 6 terminal A | Blanco |
| Botones B | Todos los terminal B | Rail GND | Negro |
| NeoPixel | GPIO18 | DIN | Verde |

---

## Configuración de pines en botones con LED integrado

Los botones de 22mm con LED generalmente tienen 4 terminales:
```
  [COM] [NO]   ← Terminales del interruptor (NO = Normally Open)
  [+]   [-]   ← Terminales del LED interno
```
- COM → GND
- NO → GPIO del ESP32  
- LED+ → 3.3V (o GPIO para control por software)
- LED- → GND (con resistencia de 100Ω)
