#include <FastLED.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ==========================================
// 🎛️ GLOBAL DEVICE SETTINGS & CALIBRATION
// ==========================================
#define TEMP_MIN 35.0f   // Deep Blue (Cold)
#define TEMP_MAX 60.0f   // Pure Red (Hot)

// 🔌 PROBE PIN ASSIGNMENTS (Adjust for your final wiring)
#define PROBE_1_PIN 2    // Maps to Row 0
#define PROBE_2_PIN 12    // Maps to Row 5
#define PROBE_3_PIN 4    // Maps to Row 10
#define PROBE_4_PIN 3   // Maps to Row 15

// 🔘 TOGGLE SWITCH ASSIGNMENTS
#define BTN_MODE   11     // Switch between Physical and Virtual Modes
#define BTN_STEP   8     // Virtual: Advance Cursor
#define BTN_ADD    10    // Virtual: Stamp source
#define BTN_IGNITE 9    // Virtual: Start/Stop Simulation

// --- HARDWARE & GRID DEFINITIONS ---
#define LED_PIN     7       
#define NUM_LEDS    128     
#define BRIGHTNESS  140     
#define COLOR_ORDER GRB     
#define LED_TYPE    WS2812B 

#define COLS 8
#define ROWS 16

CRGB leds[NUM_LEDS];

// --- ONEWIRE SENSOR SETUP ---
OneWire ow1(PROBE_1_PIN); DallasTemperature sensor1(&ow1);
OneWire ow2(PROBE_2_PIN); DallasTemperature sensor2(&ow2);
OneWire ow3(PROBE_3_PIN); DallasTemperature sensor3(&ow3);
OneWire ow4(PROBE_4_PIN); DallasTemperature sensor4(&ow4);

unsigned long lastTemperatureRequest = 0;
const int tempRequestDelay = 750; 
float targetT1 = 0.0f, targetT2 = 0.0f, targetT3 = 0.0f, targetT4 = 0.0f; 

// --- PHYSICS PARAMETERS & OPTIMIZATIONS ---
#define ALPHA 0.19f          
#define HEAT_LOSS 0.0f       // Zero sink. Heat reaches all edges.
#define STEPS_PER_FRAME 5    // Balanced for 16MHz CPU lag-free execution

const float C_CENTER = 1.0f - (4.0f * ALPHA) - HEAT_LOSS; 

float T[ROWS][COLS];
float T_new[ROWS][COLS];

// --- SYSTEM STATES ---
enum SystemState { BOOT_ANIM, PHYSICAL_SIM, VIRTUAL_SETUP, VIRTUAL_SIM };
SystemState currentState = BOOT_ANIM;

// --- VIRTUAL MULTI-SOURCE STATE ---
#define MAX_SOURCES 10
int srcX[MAX_SOURCES];
int srcY[MAX_SOURCES];
int numSources = 0;

int setupSubState = 0; // 0: Scan X, 1: Scan Y, 2: Locked
int cursorX = 0;
int cursorY = 0;

unsigned long lastScanMoveTime = 0;
#define SCAN_SPEED 300
unsigned long lastFrameTime = 0;

// --- SWITCH TRACKING ---
bool lastMode = HIGH, lastStep = HIGH, lastAdd = HIGH, lastIgnite = HIGH;
unsigned long lastDebounceTime = 0;

// ==========================================
// CORE GRAPHICS & MAPPING
// ==========================================

uint16_t xyToIndex(uint8_t col, uint8_t row) {
  uint8_t panel = row / 8;       
  uint8_t localRow = row % 8;    
  return (panel * 64) + (localRow * 8) + col; 
}

uint8_t mapFloat(float x, float in_min, float in_max) {
  return (uint8_t)((x - in_min) * 255.0f / (in_max - in_min));
}

// 🔥 REVISED COLOR PALETTE (Capped at Pure Red)
CRGB getThermalColor(float temp) {
  if (temp > 1.0f) temp = 1.0f;
  if (temp < 0.0f) temp = 0.0f;
  
  if (temp < 0.20f) return blend(CRGB(0, 0, 255), CRGB(0, 255, 255), mapFloat(temp, 0.0f, 0.20f));     // Blue -> Cyan
  if (temp < 0.40f) return blend(CRGB(0, 255, 255), CRGB(0, 255, 0), mapFloat(temp, 0.20f, 0.40f));    // Cyan -> Green
  if (temp < 0.60f) return blend(CRGB(0, 255, 0), CRGB(255, 255, 0), mapFloat(temp, 0.40f, 0.60f));    // Green -> Yellow
  if (temp < 0.85f) return blend(CRGB(255, 255, 0), CRGB(255, 100, 0), mapFloat(temp, 0.60f, 0.85f));  // Yellow -> Orange
  return blend(CRGB(255, 100, 0), CRGB(255, 0, 0), mapFloat(temp, 0.85f, 1.0f));                       // Orange -> PURE RED
}

float normalizeTemp(float rawTemp) {
  if (rawTemp <= -50.0f) return -1.0f; 
  if (rawTemp <= TEMP_MIN) return 0.0f;
  if (rawTemp >= TEMP_MAX) return 1.0f;
  return (rawTemp - TEMP_MIN) / (TEMP_MAX - TEMP_MIN); 
}

// ==========================================
// MATHEMATICAL SOLVER
// ==========================================

void injectPhysicalHeat() {
  if(targetT1 >= 0.0f) { T[0][2]=targetT1; T[0][3]=targetT1; T[0][4]=targetT1; T[0][5]=targetT1; }
  if(targetT2 >= 0.0f) { T[5][2]=targetT2; T[5][3]=targetT2; T[5][4]=targetT2; T[5][5]=targetT2; }
  if(targetT3 >= 0.0f) { T[10][2]=targetT3; T[10][3]=targetT3; T[10][4]=targetT3; T[10][5]=targetT3; }
  if(targetT4 >= 0.0f) { T[15][2]=targetT4; T[15][3]=targetT4; T[15][4]=targetT4; T[15][5]=targetT4; }
}

void injectVirtualHeat() {
  for(int s=0; s<numSources; s++) {
    T[srcY[s]][srcX[s]] = 1.0f;
  }
}

void runPhysicsStep() {
  for (int r = 0; r < ROWS; r++) {
    for (int c = 0; c < COLS; c++) {
      float t_center = T[r][c];
      
      float t_up    = (r > 0) ? T[r-1][c] : t_center;      
      float t_down  = (r < ROWS-1) ? T[r+1][c] : t_center; 
      float t_left  = (c > 0) ? T[r][c-1] : t_center;      
      float t_right = (c < COLS-1) ? T[r][c+1] : t_center; 

      T_new[r][c] = (t_center * C_CENTER) + ((t_left + t_right + t_up + t_down) * ALPHA);
    }
  }
  memcpy(T, T_new, sizeof(T));
}

void renderGrid() {
  for (int r = 0; r < ROWS; r++) {
    for (int c = 0; c < COLS; c++) {
      leds[xyToIndex(c, r)] = getThermalColor(T[r][c]);
    }
  }
  FastLED.show();
}

// ==========================================
// ARDUINO MAIN
// ==========================================

void setup() {
  Serial.begin(9600);
  Serial.println(F("========================================="));
  Serial.println(F(" THERMOVIZ FINAL EXHIBITION BUILD READY  "));
  Serial.println(F("========================================="));
  
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);

  pinMode(BTN_MODE, INPUT_PULLUP);
  pinMode(BTN_STEP, INPUT_PULLUP);
  pinMode(BTN_ADD, INPUT_PULLUP);
  pinMode(BTN_IGNITE, INPUT_PULLUP);

  lastMode = digitalRead(BTN_MODE);
  lastStep = digitalRead(BTN_STEP);
  lastAdd = digitalRead(BTN_ADD);
  lastIgnite = digitalRead(BTN_IGNITE);

  sensor1.begin(); sensor1.setWaitForConversion(false);
  sensor2.begin(); sensor2.setWaitForConversion(false);
  sensor3.begin(); sensor3.setWaitForConversion(false);
  sensor4.begin(); sensor4.setWaitForConversion(false);
  
  sensor1.requestTemperatures(); sensor2.requestTemperatures();
  sensor3.requestTemperatures(); sensor4.requestTemperatures();
  lastTemperatureRequest = millis();

  memset(T, 0, sizeof(T));
  memset(T_new, 0, sizeof(T_new));
}

void loop() {
  handleSwitches();

  switch(currentState) {
    case BOOT_ANIM:
      runEpicBootAnimation();
      break;

    case PHYSICAL_SIM:
      if (millis() - lastTemperatureRequest >= tempRequestDelay) {
        targetT1 = normalizeTemp(sensor1.getTempCByIndex(0));
        targetT2 = normalizeTemp(sensor2.getTempCByIndex(0));
        targetT3 = normalizeTemp(sensor3.getTempCByIndex(0));
        targetT4 = normalizeTemp(sensor4.getTempCByIndex(0));

        sensor1.requestTemperatures(); sensor2.requestTemperatures();
        sensor3.requestTemperatures(); sensor4.requestTemperatures();
        lastTemperatureRequest = millis();
      }

      if (millis() - lastFrameTime > 50) {
        for(int i=0; i<STEPS_PER_FRAME; i++) {
          injectPhysicalHeat();
          runPhysicsStep();
        }
        injectPhysicalHeat(); 
        renderGrid();
        lastFrameTime = millis();
      }
      break;

    case VIRTUAL_SETUP:
      runAutoScanLogic();
      renderSetupUI();
      break;

    case VIRTUAL_SIM:
      if (millis() - lastFrameTime > 50) {
        for(int i=0; i<STEPS_PER_FRAME; i++) {
          injectVirtualHeat();
          runPhysicsStep();
        }
        injectVirtualHeat(); 
        renderGrid();
        lastFrameTime = millis();
      }
      break;
  }
}

// ==========================================
// CINEMATIC ANIMATIONS & TRANSITIONS
// ==========================================

void runEpicBootAnimation() {
  Serial.println(F("[ACTION] Executing Thermodynamic Collision Boot..."));
  FastLED.clear(); FastLED.show(); delay(500);

  // 1. Rush to center with gradient trails
  for (int i = 0; i <= 7; i++) {
    // Dim the trails
    for(int j=0; j<NUM_LEDS; j++) leds[j].nscale8(180); 
    
    // Draw leading red edges
    for(int c=0; c<COLS; c++) {
      leds[xyToIndex(c, i)] = CRGB(255, 0, 0);          // Top moving down
      leds[xyToIndex(c, 15 - i)] = CRGB(255, 0, 0);     // Bottom moving up
    }
    FastLED.show(); delay(60);
  }

  // 2. Impact Flash
  for(int j=0; j<NUM_LEDS; j++) leds[j] = CRGB::White;
  FastLED.show(); delay(50);

  // 3. Mathematical Gradient Bloom
  memset(T, 0, sizeof(T));
  T[7][3]=1.0f; T[7][4]=1.0f; T[8][3]=1.0f; T[8][4]=1.0f; // Seed center
  
  for(int i=0; i<30; i++) {
    runPhysicsStep();
    renderGrid();
    delay(20);
  }

  // Fade out to black to start
  for(int fade=0; fade<20; fade++) {
    for(int j=0; j<NUM_LEDS; j++) leds[j].nscale8(200);
    FastLED.show(); delay(20);
  }

  memset(T, 0, sizeof(T));
  currentState = PHYSICAL_SIM; 
}

void transitionToPhysical() {
  Serial.println(F("[ACTION] Transitioning to Physical Sensing..."));
  // "Thermal Scanner" Wipe Down
  for (int r = 0; r < ROWS; r++) {
    for(int j=0; j<NUM_LEDS; j++) leds[j] = CRGB(0, 0, 40); // Deep blue background
    for (int c = 0; c < COLS; c++) leds[xyToIndex(c, r)] = CRGB(0, 255, 255); // Cyan scanner line
    FastLED.show(); delay(30);
  }
  memset(T, 0, sizeof(T));
}

void transitionToVirtual() {
  Serial.println(F("[ACTION] Transitioning to Virtual Sandbox..."));
  FastLED.clear();
  
  // "Targeting Grid" Activation
  // Draw corners
  for(int c=0; c<COLS; c++) { leds[xyToIndex(c,0)] = CRGB::Green; leds[xyToIndex(c,15)] = CRGB::Green; }
  for(int r=0; r<ROWS; r++) { leds[xyToIndex(0,r)] = CRGB::Green; leds[xyToIndex(7,r)] = CRGB::Green; }
  FastLED.show(); delay(200);

  // Draw crosshairs meeting
  for(int c=0; c<4; c++) {
    leds[xyToIndex(c, 7)] = CRGB::Cyan; leds[xyToIndex(7-c, 7)] = CRGB::Cyan;
    leds[xyToIndex(c, 8)] = CRGB::Cyan; leds[xyToIndex(7-c, 8)] = CRGB::Cyan;
    FastLED.show(); delay(40);
  }
  delay(300);
  FastLED.clear(); FastLED.show();
  memset(T, 0, sizeof(T));
}

// ==========================================
// VIRTUAL UI LOGIC
// ==========================================

void runAutoScanLogic() {
  if (millis() - lastScanMoveTime > SCAN_SPEED) {
    if (setupSubState == 0) cursorX = (cursorX + 1) % COLS;
    else if (setupSubState == 1) cursorY = (cursorY + 1) % ROWS;
    lastScanMoveTime = millis();
  }
}

void renderSetupUI() {
  memset(T, 0, sizeof(T));
  for(int i=0; i<numSources; i++) T[srcY[i]][srcX[i]] = 0.8f; 
  if (setupSubState == 0) for(int r=0; r<ROWS; r++) T[r][cursorX] = 0.15f; 
  else if (setupSubState == 1) for(int c=0; c<COLS; c++) T[cursorY][c] = 0.15f; 
  if (setupSubState == 2 || (millis() % 400 < 200)) T[cursorY][cursorX] = 1.0f; 
  renderGrid();
}

// ==========================================
// HARDWARE TOGGLE SWITCH LOGIC 
// ==========================================

void handleSwitches() {
  if (millis() - lastDebounceTime < 50) return; 

  bool curMode = digitalRead(BTN_MODE);
  bool curStep = digitalRead(BTN_STEP);
  bool curAdd = digitalRead(BTN_ADD);
  bool curIgnite = digitalRead(BTN_IGNITE);

  // --- BUTTON 1: MODE TOGGLE ---
  if (curMode != lastMode) {
    lastMode = curMode; lastDebounceTime = millis();
    
    if (currentState == PHYSICAL_SIM) {
      transitionToVirtual();
      currentState = VIRTUAL_SETUP;
      cursorX = 0; cursorY = 0; setupSubState = 0; numSources = 0;
    } else {
      transitionToPhysical();
      currentState = PHYSICAL_SIM;
    }
  }

  if (currentState == VIRTUAL_SETUP || currentState == VIRTUAL_SIM) {
    // --- BUTTON 2: STEP CURSOR ---
    if (curStep != lastStep) {
      lastStep = curStep; lastDebounceTime = millis();
      if (currentState == VIRTUAL_SETUP) {
        setupSubState++;
        if (setupSubState > 2) { setupSubState = 0; cursorX = 0; cursorY = 0; }
        Serial.println(F("[UI] Cursor Advanced"));
      }
    }
    
    // --- BUTTON 3: ADD SOURCE ---
    if (curAdd != lastAdd) {
      lastAdd = curAdd; lastDebounceTime = millis();
      if (currentState == VIRTUAL_SETUP && setupSubState == 2 && numSources < MAX_SOURCES) {
        srcX[numSources] = cursorX; srcY[numSources] = cursorY; numSources++;
        setupSubState = 0; cursorX = 0; cursorY = 0; 
        Serial.print(F("[UI] Source Stamped. Total: ")); Serial.println(numSources);
      }
    }
    
    // --- BUTTON 4: IGNITE/STOP ---
    if (curIgnite != lastIgnite) {
      lastIgnite = curIgnite; lastDebounceTime = millis();
      if (currentState == VIRTUAL_SETUP) {
        if (setupSubState == 2 && numSources < MAX_SOURCES) { srcX[numSources]=cursorX; srcY[numSources]=cursorY; numSources++; }
        if (numSources > 0) { currentState = VIRTUAL_SIM; memset(T, 0, sizeof(T)); Serial.println(F("[UI] IGNITION")); }
      } 
      else if (currentState == VIRTUAL_SIM) {
        currentState = VIRTUAL_SETUP;
        numSources = 0; setupSubState = 0; cursorX = 0; cursorY = 0;
        memset(T, 0, sizeof(T)); Serial.println(F("[UI] STOPPED"));
      }
    }
  }
}