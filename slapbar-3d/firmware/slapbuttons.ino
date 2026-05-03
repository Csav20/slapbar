/*
 * ╔══════════════════════════════════════════════════════════════╗
 * ║           SlapMac 3D — Firmware ESP32                       ║
 * ║  Botonera física con packs de sonido para SlapBar           ║
 * ╟──────────────────────────────────────────────────────────────╢
 * ║  Al presionar un botón → envía JSON por Serial al Mac       ║
 * ║  {"event":"press","pack":"dbz","button":1}                  ║
 * ║  {"event":"hold","pack":"dbz","button":1}                   ║
 * ╟──────────────────────────────────────────────────────────────╢
 * ║  Placa recomendada: ESP32 DevKit v1 / ESP32-WROOM-32        ║
 * ║  En Arduino IDE:                                            ║
 * ║    Board → "ESP32 Dev Module"                               ║
 * ║    Upload Speed → 921600                                    ║
 * ║    Flash Freq → 80MHz                                       ║
 * ╚══════════════════════════════════════════════════════════════╝
 */

#include "config.h"
#include <Arduino.h>

// ── Opcional: NeoPixel ─────────────────────────────────────────
#if LED_PIN >= 0
  #include <Adafruit_NeoPixel.h>
  Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);
  uint8_t COLORS[6][3] = {
    COLOR_SLAP,
    COLOR_DBZ,
    COLOR_CARTOON,
    COLOR_RETRO,
    COLOR_CUSTOM,
    COLOR_RANDOM
  };
#endif

// ── Definición de botones ──────────────────────────────────────
struct Button {
  uint8_t     pin;
  const char* pack;    // nombre del pack (debe coincidir con SlapBar)
  const char* label;   // emoji / etiqueta
  int         ledIdx;  // índice LED (-1 = sin LED)
  bool        lastState;
  bool        currState;
  unsigned long pressedAt;
  bool        holdFired;
};

Button buttons[] = {
  { BTN_SLAP,    "slap",    "👋",  0, HIGH, HIGH, 0, false },
  { BTN_DBZ,     "dbz",     "🐉",  1, HIGH, HIGH, 0, false },
  { BTN_CARTOON, "cartoon", "🎪",  2, HIGH, HIGH, 0, false },
  { BTN_RETRO,   "retro",   "🕹",  3, HIGH, HIGH, 0, false },
  { BTN_CUSTOM,  "custom",  "⭐",  4, HIGH, HIGH, 0, false },
  { BTN_RANDOM,  "random",  "🎲",  5, HIGH, HIGH, 0, false },
};

const uint8_t NUM_BUTTONS = sizeof(buttons) / sizeof(buttons[0]);

// ── Estado global ──────────────────────────────────────────────
int   activePack  = 0;   // Índice del pack activo actualmente
bool  slapEnabled = true; // Refleja el estado ON/OFF de SlapBar

// ── Helpers LED ────────────────────────────────────────────────
#if LED_PIN >= 0
void setLedPack(int packIdx) {
  for (int i = 0; i < NUM_LEDS; i++) {
    if (i == packIdx) {
      strip.setPixelColor(i, strip.Color(COLORS[i][0], COLORS[i][1], COLORS[i][2]));
    } else {
      // Apagar el resto o poner tenue
      strip.setPixelColor(i, strip.Color(
        COLORS[i][0] / 8,
        COLORS[i][1] / 8,
        COLORS[i][2] / 8
      ));
    }
  }
  strip.show();
}

void flashLed(int ledIdx, uint8_t r, uint8_t g, uint8_t b, int times = 2) {
  for (int t = 0; t < times; t++) {
    strip.setPixelColor(ledIdx, strip.Color(r, g, b));
    strip.show();
    delay(80);
    strip.setPixelColor(ledIdx, strip.Color(0, 0, 0));
    strip.show();
    delay(80);
  }
  // Restaurar estado activo
  setLedPack(activePack);
}
#endif

// ── Enviar evento JSON por Serial ──────────────────────────────
void sendEvent(const char* event, int btnIdx) {
  Serial.print("{\"event\":\"");
  Serial.print(event);
  Serial.print("\",\"pack\":\"");
  Serial.print(buttons[btnIdx].pack);
  Serial.print("\",\"button\":");
  Serial.print(btnIdx);
  Serial.print(",\"label\":\"");
  Serial.print(buttons[btnIdx].label);
  Serial.print("\",\"fw\":\"");
  Serial.print(FW_VERSION);
  Serial.println("\"}");
}

// ── Enviar heartbeat (cada 5s) para que el Mac sepa que el ESP32 está vivo ──
unsigned long lastHeartbeat = 0;

void sendHeartbeat() {
  unsigned long now = millis();
  if (now - lastHeartbeat >= 5000) {
    lastHeartbeat = now;
    Serial.print("{\"event\":\"heartbeat\",\"pack\":\"");
    Serial.print(buttons[activePack].pack);
    Serial.print("\",\"enabled\":");
    Serial.print(slapEnabled ? "true" : "false");
    Serial.println("}");
  }
}

// ── Setup ──────────────────────────────────────────────────────
void setup() {
  Serial.begin(BAUD_RATE);
  delay(500);

  // Configurar pines de botones con pull-up interno
  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(buttons[i].pin, INPUT_PULLUP);
    buttons[i].lastState = HIGH;
  }

#if LED_PIN >= 0
  strip.begin();
  strip.setBrightness(80);  // 0-255
  strip.show();
  // Animación de inicio: recorre todos los LEDs
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, strip.Color(COLORS[i][0], COLORS[i][1], COLORS[i][2]));
    strip.show();
    delay(120);
  }
  delay(300);
  setLedPack(activePack);
#endif

  // Anunciar presencia al Mac
  Serial.print("{\"event\":\"ready\",\"fw\":\"");
  Serial.print(FW_VERSION);
  Serial.print("\",\"buttons\":");
  Serial.print(NUM_BUTTONS);
  Serial.println(",\"hello\":\"SlapMac 3D\"}");
}

// ── Loop ───────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();

  for (int i = 0; i < NUM_BUTTONS; i++) {
    buttons[i].currState = digitalRead(buttons[i].pin);

    // Flanco de bajada → botón presionado
    if (buttons[i].lastState == HIGH && buttons[i].currState == LOW) {
      buttons[i].pressedAt = now;
      buttons[i].holdFired = false;
    }

    // Mantenido → hold
    if (buttons[i].currState == LOW &&
        !buttons[i].holdFired &&
        (now - buttons[i].pressedAt) >= HOLD_MS) {
      buttons[i].holdFired = true;
      sendEvent("hold", i);
#if LED_PIN >= 0
      flashLed(i, 255, 255, 255, 3);
#endif
    }

    // Flanco de subida → botón suelto (dispara "press" si no fue hold)
    if (buttons[i].lastState == LOW && buttons[i].currState == HIGH) {
      if ((now - buttons[i].pressedAt) >= DEBOUNCE_MS && !buttons[i].holdFired) {
        sendEvent("press", i);
        activePack = i;  // Actualiza pack activo localmente
#if LED_PIN >= 0
        flashLed(i, COLORS[i][0], COLORS[i][1], COLORS[i][2], 1);
        setLedPack(activePack);
#endif
      }
    }

    buttons[i].lastState = buttons[i].currState;
  }

  // Escuchar comandos desde el Mac (ej: cambio de pack por software)
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.startsWith("{")) {
      // Comando JSON simple → {"cmd":"enable"} o {"cmd":"disable"}
      if (cmd.indexOf("\"enable\"") >= 0) {
        slapEnabled = true;
      } else if (cmd.indexOf("\"disable\"") >= 0) {
        slapEnabled = false;
      }
    }
  }

  sendHeartbeat();
  delay(10);  // pequeño delay para estabilidad
}
