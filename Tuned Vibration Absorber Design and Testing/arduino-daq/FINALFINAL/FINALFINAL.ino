#include <Wire.h>

#define TLV493D_ADDR 0x5E

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Wire.setSDA(4);      // GP4
  Wire.setSCL(5);      // GP5
  Wire.begin();

  Serial.println("Scanning I2C...");

  bool found = false;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      found = true;
    }
  }

  if (!found)
    Serial.println("No I2C devices found.");

  Serial.println("Starting TLV493D...");
}

void loop() {

  uint8_t data[6];

  // Read first 6 registers
  Wire.beginTransmission(TLV493D_ADDR);
  Wire.write((uint8_t)0x00);

  if (Wire.endTransmission(false) != 0) {
    Serial.println("Write failed");
    delay(500);
    return;
  }

  if (Wire.requestFrom(TLV493D_ADDR, (uint8_t)6) != 6) {
    Serial.println("Read failed");
    delay(500);
    return;
  }

  for (int i = 0; i < 6; i++)
    data[i] = Wire.read();

  int16_t x = ((int16_t)data[0] << 4) | (data[4] >> 4);
  int16_t y = ((int16_t)data[1] << 4) | (data[4] & 0x0F);
  int16_t z = ((int16_t)data[2] << 4) | (data[5] & 0x0F);

  // Sign extend 12-bit values
  if (x & 0x800) x |= 0xF000;
  if (y & 0x800) y |= 0xF000;
  if (z & 0x800) z |= 0xF000;

  Serial.print("X: ");
  Serial.print(x);
  Serial.print("   Y: ");
  Serial.print(y);
  Serial.print("   Z: ");
  Serial.println(z);

  delay(100);
}