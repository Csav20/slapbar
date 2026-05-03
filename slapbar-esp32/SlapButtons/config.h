// ╔══════════════════════════════════════════════════════════════╗
// ║              SlapMac ESP32 — config.h                       ║
// ║  Configura pines GPIO, LEDs y parámetros de la botonera     ║
// ╚══════════════════════════════════════════════════════════════╝
#pragma once

// ─────────────────────────────────────────────────────────────────
//  PINES DE BOTONES
//  Conecta cada botón entre el GPIO indicado y GND
//  El ESP32 usa pull-up interno: sin resistencias externas
// ─────────────────────────────────────────────────────────────────
#define BTN_SLAP      15   // 👋  Pack SlapMac original
#define BTN_DBZ        2   // 🐉  Pack Dragon Ball Z
#define BTN_CARTOON    4   // 🎪  Pack Cartoon
#define BTN_RETRO     16   // 🕹   Pack Retro
#define BTN_CUSTOM    17   // ⭐  Pack Custom / Tus sonidos
#define BTN_RANDOM     5   // 🎲  Sonido aleatorio de cualquier pack

// ─────────────────────────────────────────────────────────────────
//  LEDs NeoPixel WS2812B (opcional)
//  Pon LED_PIN = -1 si NO usas LEDs
// ─────────────────────────────────────────────────────────────────
#define LED_PIN       18   // Pin de datos del strip NeoPixel
#define NUM_LEDS       6   // Un LED por botón
#define LED_BRIGHTNESS 80  // Brillo 0-255

// ─────────────────────────────────────────────────────────────────
//  SERIAL
// ─────────────────────────────────────────────────────────────────
#define BAUD_RATE  115200

// ─────────────────────────────────────────────────────────────────
//  TIEMPOS
// ─────────────────────────────────────────────────────────────────
#define DEBOUNCE_MS   50   // ms mínimo entre pulsaciones (antirebote)
#define HOLD_MS      800   // ms para activar "hold" (pulsación larga)
#define HEARTBEAT_MS 5000  // ms entre mensajes de latido al Mac

// ─────────────────────────────────────────────────────────────────
//  VERSIÓN
// ─────────────────────────────────────────────────────────────────
#define FW_VERSION  "1.0.0"
#define DEVICE_NAME "SlapMac-ESP32"
