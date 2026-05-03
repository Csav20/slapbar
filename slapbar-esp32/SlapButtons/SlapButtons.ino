/*
 * ╔══════════════════════════════════════════════════════════════╗
 * ║           SlapMac ESP32 — Firmware Botonera                 ║
 * ╟──────────────────────────────────────────────────────────────╢
 * ║  Detecta pulsaciones físicas y envía JSON por USB-Serial    ║
 * ║  al Mac para que SlapBar cambie de pack y reproduzca sonido ║
 * ╟──────────────────────────────────────────────────────────────╢
 * ║  PROTOCOLO SERIAL (115200 baud):                            ║
 * ║                                                              ║
 * ║  ESP32 → Mac (eventos):                                     ║
 * ║    {"event":"ready","fw":"1.0.0","buttons":6}               ║
 * ║    {"event":"press","pack":"dbz","button":1}                ║
 * ║    {"event":"hold","pack":"dbz","button":1}                 ║
 * ║    {"event":"heartbeat","pack":"dbz","enabled":true}        ║
 * ║                                                              ║
 * ║  Mac → ESP32 (comandos):                                    ║
 * ║    {"cmd":"enable"}   ← activa los LEDs/feedback            ║
 * ║    {"cmd":"disable"}  ← desactiva LEDs/feedback             ║
 * ╟──────────────────────────────────────────────────────────────╢
 * ║  PLACA: ESP32 Dev Module (ESP32-WROOM-32 / DevKit v1)       ║
 * ║  ARDUINO IDE: Board Manager → esp32 by Espressif Systems    ║
 * ║  LIBRERÍA LEDS (opcional): Adafruit NeoPixel                ║
 * ╚══════════════════════════════════════════════════════════════╝
 */

#include "config.h"
#include <Arduino.h>

// ─────────────────────────────────────────────────────────────────
//  NEOPIXEL (se compila solo si LED_PIN >= 0)
// ─────────────────────────────────────────────────────────────────
#if LED_PIN >= 0
  #include <Adafruit_NeoPixel.h>
  Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

  // Colores RGB por pack  {R, G, B}
  const uint8_t PACK_COLORS[6][3] = {
    {255, 165,   0},   // 0 SLAP    — Naranja
    {255, 200,   0},   // 1 DBZ     — Dorado Super Saiyan
    {  0, 200, 255},   // 2 CARTOON — Cian
    {150,   0, 255},   // 3 RETRO   — Violeta
    {  0, 200,  80},   // 4 CUSTOM  — Verde
    {220, 220, 220},   // 5 RANDOM  — Blanco
  };

  void ledSetActive(int activeIdx) {
    for (int i = 0; i < NUM_LEDS; i++) {
      if (i == activeIdx) {
        strip.setPixelColor(i, strip.Color(
          PACK_COLORS[i][0], PACK_COLORS[i][1], PACK_COLORS[i][2]));
      } else {
        // Resto apagados o muy tenues
        strip.setPixelColor(i, strip.Color(
          PACK_COLORS[i][0] / 10,
          PACK_COLORS[i][1] / 10,
          PACK_COLORS[i][2] / 10));
      }
    }
    strip.show();
  }

  void ledFlash(int idx, int times = 2) {
    for (int t = 0; t < times; t++) {
      strip.setPixelColor(idx, strip.Color(255, 255, 255));
      strip.show();
      delay(70);
      strip.setPixelColor(idx, strip.Color(0, 0, 0));
      strip.show();
      delay(70);
    }
  }

  void ledStartup() {
    // Animación de inicio: recorre todos los LEDs
    for (int i = 0; i < NUM_LEDS; i++) {
      strip.setPixelColor(i, strip.Color(
        PACK_COLORS[i][0], PACK_COLORS[i][1], PACK_COLORS[i][2]));
      strip.show();
      delay(100);
    }
    delay(300);
    for (int i = 0; i < NUM_LEDS; i++) strip.setPixelColor(i, 0);
    strip.show();
    delay(200);
  }
#else
  // Stubs vacíos cuando no hay LEDs
  void ledSetActive(int i) {}
  void ledFlash(int i, int t = 2) {}
  void ledStartup() {}
#endif

// ─────────────────────────────────────────────────────────────────
//  DEFINICIÓN DE BOTONES
// ─────────────────────────────────────────────────────────────────
struct Button {
  uint8_t     pin;
  const char* pack;    // nombre del pack (debe coincidir con SlapBar)
  const char* emoji;   // solo para el mensaje de bienvenida
  bool        lastState;
  bool        currState;
  unsigned long pressedAt;
  bool        holdFired;
};

Button buttons[] = {
  { BTN_SLAP,    "slap",    "👋", HIGH, HIGH, 0, false },
  { BTN_DBZ,     "dbz",     "🐉", HIGH, HIGH, 0, false },
  { BTN_CARTOON, "cartoon", "🎪", HIGH, HIGH, 0, false },
  { BTN_RETRO,   "retro",   "🕹", HIGH, HIGH, 0, false },
  { BTN_CUSTOM,  "custom",  "⭐", HIGH, HIGH, 0, false },
  { BTN_RANDOM,  "random",  "🎲", HIGH, HIGH, 0, false },
};
const uint8_t NUM_BUTTONS = sizeof(buttons) / sizeof(buttons[0]);

// ─────────────────────────────────────────────────────────────────
//  ESTADO GLOBAL
// ─────────────────────────────────────────────────────────────────
int           activePack      = 0;
bool          slapEnabled     = true;
unsigned long lastHeartbeat   = 0;

// ─────────────────────────────────────────────────────────────────
//  ENVIAR JSON POR SERIAL
// ─────────────────────────────────────────────────────────────────
void sendEvent(const char* event, int btnIdx) {
  Serial.print(F("{\"event\":\""));
  Serial.print(event);
  Serial.print(F("\",\"pack\":\""));
  Serial.print(buttons[btnIdx].pack);
  Serial.print(F("\",\"button\":"));
  Serial.print(btnIdx);
  Serial.print(F(",\"fw\":\""));
  Serial.print(FW_VERSION);
  Serial.println(F("\"}"));
}

void sendHeartbeat() {
  unsigned long now = millis();
  if (now - lastHeartbeat < HEARTBEAT_MS) return;
  lastHeartbeat = now;

  Serial.print(F("{\"event\":\"heartbeat\",\"pack\":\""));
  Serial.print(buttons[activePack].pack);
  Serial.print(F("\",\"enabled\":"));
  Serial.print(slapEnabled ? F("true") : F("false"));
  Serial.println(F("}"));
}

// ─────────────────────────────────────────────────────────────────
//  PROCESAR COMANDOS DEL MAC → ESP32
// ─────────────────────────────────────────────────────────────────
void handleCommand(const String& cmd) {
  if (cmd.indexOf("\"enable\"") >= 0) {
    slapEnabled = true;
    ledSetActive(activePack);
  } else if (cmd.indexOf("\"disable\"") >= 0) {
    slapEnabled = false;
    #if LED_PIN >= 0
      strip.clear(); strip.show();
    #endif
  }
}

// ─────────────────────────────────────────────────────────────────
//  SETUP
// ─────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(BAUD_RATE);
  delay(500);

  // Configurar pines de botones con pull-up interno
  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(buttons[i].pin, INPUT_PULLUP);
  }

  // LEDs
  #if LED_PIN >= 0
    strip.begin();
    strip.setBrightness(LED_BRIGHTNESS);
    strip.show();
    ledStartup();
    ledSetActive(activePack);
  #endif

  // Mensaje de bienvenida
  Serial.println();
  Serial.print(F("{\"event\":\"ready\""));
  Serial.print(F(",\"device\":\""));
  Serial.print(DEVICE_NAME);
  Serial.print(F("\",\"fw\":\""));
  Serial.print(FW_VERSION);
  Serial.print(F("\",\"buttons\":"));
  Serial.print(NUM_BUTTONS);
  Serial.print(F(",\"packs\":["));
  for (int i = 0; i < NUM_BUTTONS; i++) {
    Serial.print(F("\""));
    Serial.print(buttons[i].pack);
    Serial.print(F("\""));
    if (i < NUM_BUTTONS - 1) Serial.print(F(","));
  }
  Serial.println(F("]}"));
}

// ─────────────────────────────────────────────────────────────────
//  LOOP
// ─────────────────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();

  // ── Leer botones ──────────────────────────────────────────────
  for (int i = 0; i < NUM_BUTTONS; i++) {
    buttons[i].currState = digitalRead(buttons[i].pin);

    // Flanco de bajada → botón presionado
    if (buttons[i].lastState == HIGH && buttons[i].currState == LOW) {
      buttons[i].pressedAt = now;
      buttons[i].holdFired = false;
    }

    // Pulsación larga → evento "hold"
    if (buttons[i].currState == LOW
        && !buttons[i].holdFired
        && (now - buttons[i].pressedAt) >= HOLD_MS) {
      buttons[i].holdFired = true;
      sendEvent("hold", i);
      ledFlash(i, 3);
      ledSetActive(activePack);
    }

    // Flanco de subida → botón suelto → evento "press"
    if (buttons[i].lastState == LOW && buttons[i].currState == HIGH) {
      unsigned long duration = now - buttons[i].pressedAt;
      if (duration >= DEBOUNCE_MS && !buttons[i].holdFired) {
        sendEvent("press", i);
        activePack = i;
        ledFlash(i, 1);
        ledSetActive(activePack);
      }
    }

    buttons[i].lastState = buttons[i].currState;
  }

  // ── Recibir comandos del Mac ──────────────────────────────────
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() > 0) handleCommand(cmd);
  }

  // ── Heartbeat ────────────────────────────────────────────────
  sendHeartbeat();

  delay(5);
}
