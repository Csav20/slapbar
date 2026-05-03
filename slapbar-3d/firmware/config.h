// ╔══════════════════════════════════════════════════════════════╗
// ║              SlapMac 3D — config.h                          ║
// ║  Asigna pines GPIO del ESP32 a cada botón de pack           ║
// ╚══════════════════════════════════════════════════════════════╝
#pragma once

// ── Pines de botones (INPUT_PULLUP — conectar a GND al presionar) ──
#define BTN_SLAP     15   // 👋  Pack SlapMac original
#define BTN_DBZ      2    // 🐉  Pack Dragon Ball Z
#define BTN_CARTOON  4    // 🎪  Pack Cartoon
#define BTN_RETRO    16   // 🕹   Pack Retro
#define BTN_CUSTOM   17   // ⭐  Pack Custom
#define BTN_RANDOM   5    // 🎲  Sonido aleatorio de cualquier pack

// ── Pines LED RGB (opcional — WS2812B NeoPixel o LED simple) ──
// Deja en -1 si no usas LEDs
#define LED_PIN      18   // Pin de datos para tira NeoPixel (1 LED por botón)
#define NUM_LEDS     6    // Un LED por botón

// ── Colores por pack (RGB para NeoPixel) ──
// formato: {R, G, B}
#define COLOR_SLAP    {255, 165,   0}   // Naranja
#define COLOR_DBZ     {255, 140,   0}   // Dorado / Super Saiyan
#define COLOR_CARTOON {  0, 200, 255}   // Cian
#define COLOR_RETRO   {150,   0, 255}   // Violeta
#define COLOR_CUSTOM  {255, 215,   0}   // Amarillo estrella
#define COLOR_RANDOM  {255, 255, 255}   // Blanco

// ── Serial ──
#define BAUD_RATE    115200

// ── Debounce ──
#define DEBOUNCE_MS  50     // Tiempo mínimo entre pulsaciones (ms)
#define HOLD_MS      800    // Mantener pulsado para "hold" (ms)

// ── Versión de firmware ──
#define FW_VERSION   "1.0.0"
