// ======================================================
//        ESP32-C3 SuperMini Leakage Detection System
// ======================================================

// ================== Thinger.io ==================
#include <ThingerESP32.h>

#define USERNAME "jwoejrj"
#define DEVICE_ID "leak_detector"
#define DEVICE_CREDENTIAL "leak_detector"

// ================== WiFi ==================
#include <WiFi.h>

#define SSID "vivo T3 5g"
#define SSID_PASSWORD "mdg123456"

// ================== LCD ==================
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

// ================== DHT ==================
#include <DHT.h>

#define DHTPIN 6
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// ================== GPS ==================
#include <TinyGPS++.h>
#include <HardwareSerial.h>

TinyGPSPlus gps;
HardwareSerial gpsSerial(1);

// ================== Objects ==================
ThingerESP32 thing(USERNAME, DEVICE_ID, DEVICE_CREDENTIAL);

// ================== Pin Definitions ==================

// Flow Sensors
#define FLOW1 2
#define FLOW2 3
#define FLOW3 4
#define FLOW4 5

// MQ6 Analog Pin
#define GAS_SENSOR 1

// Outputs
#define BUZZER 18
#define MOTOR_RELAY 10

#define GREEN_LED 19
#define RED_LED 0

// GPS Pins
#define GPS_RX 20
#define GPS_TX 21

// ================== Variables ==================

float latitude = 0.0;
float longitude = 0.0;

bool gpsSentOnce = false;
unsigned long lastGpsPush = 0;

// Flow Variables
volatile byte pulseCount1 = 0;
volatile byte pulseCount2 = 0;
volatile byte pulseCount3 = 0;
volatile byte pulseCount4 = 0;

float flow1 = 0;
float flow2 = 0;
float flow3 = 0;
float flow4 = 0;

float calibrationFactor = 6.0;

unsigned long prevMillis = 0;

// Leak Logic
unsigned long systemStartTime = 0;

bool leakageCheckReady = false;
bool leakTimerRunning = false;
bool leakageConfirmed = false;

unsigned long leakTimerStart = 0;

// ================== Interrupt Functions ==================

void IRAM_ATTR count1() {
  pulseCount1++;
}

void IRAM_ATTR count2() {
  pulseCount2++;
}

void IRAM_ATTR count3() {
  pulseCount3++;
}

void IRAM_ATTR count4() {
  pulseCount4++;
}

// ======================================================
//                        SETUP
// ======================================================

void setup() {

  Serial.begin(115200);

  // LCD
  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("System Starting");

  delay(2000);

  // DHT
  dht.begin();

  // Flow Sensors
  pinMode(FLOW1, INPUT_PULLUP);
  pinMode(FLOW2, INPUT_PULLUP);
  pinMode(FLOW3, INPUT_PULLUP);
  pinMode(FLOW4, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(FLOW1), count1, FALLING);
  attachInterrupt(digitalPinToInterrupt(FLOW2), count2, FALLING);
  attachInterrupt(digitalPinToInterrupt(FLOW3), count3, FALLING);
  attachInterrupt(digitalPinToInterrupt(FLOW4), count4, FALLING);

  // Outputs
  pinMode(BUZZER, OUTPUT);
  pinMode(MOTOR_RELAY, OUTPUT);

  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  pinMode(GAS_SENSOR, INPUT);

  // Initial State
  digitalWrite(BUZZER, LOW);

  digitalWrite(MOTOR_RELAY, HIGH);

  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED, LOW);

  // GPS UART
  gpsSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);

  // WiFi
  thing.add_wifi(SSID, SSID_PASSWORD);

  // ================== Thinger Resources ==================

  thing["flow1"] >> [](pson &out) {
    out = flow1;
  };

  thing["flow2"] >> [](pson &out) {
    out = flow2;
  };

  thing["flow3"] >> [](pson &out) {
    out = flow3;
  };

  thing["flow4"] >> [](pson &out) {
    out = flow4;
  };

  thing["temperature"] >> [](pson &out) {
    out = dht.readTemperature();
  };

  thing["humidity"] >> [](pson &out) {
    out = dht.readHumidity();
  };

  thing["gas"] >> [](pson &out) {
    out = map(analogRead(GAS_SENSOR), 0, 4095, 0, 100);
  };

  thing["location"] >> [](pson &out) {

    out["latitude"] = latitude;
    out["longitude"] = longitude;
  };

  systemStartTime = millis();
}

// ======================================================
//                         LOOP
// ======================================================

void loop() {

  thing.handle();

  readGPS();

  updateFlow();

  checkLeaks();

  streamData();
}

// ======================================================
//                      GPS FUNCTION
// ======================================================

void readGPS() {

  while (gpsSerial.available()) {

    gps.encode(gpsSerial.read());
  }

  if (gps.location.isValid()) {

    latitude = gps.location.lat();
    longitude = gps.location.lng();

    if (!gpsSentOnce || millis() - lastGpsPush > 60000) {

      thing.stream("location");

      gpsSentOnce = true;

      lastGpsPush = millis();

      Serial.println("GPS Location Sent");
    }
  }
}

// ======================================================
//                   FLOW CALCULATION
// ======================================================

void updateFlow() {

  unsigned long currentMillis = millis();

  if (currentMillis - prevMillis >= 1000) {

    noInterrupts();

    flow1 = (1000.0 / (currentMillis - prevMillis)) * pulseCount1 / calibrationFactor;

    flow2 = (1000.0 / (currentMillis - prevMillis)) * pulseCount2 / calibrationFactor;

    flow3 = (1000.0 / (currentMillis - prevMillis)) * pulseCount3 / calibrationFactor;

    flow4 = (1000.0 / (currentMillis - prevMillis)) * pulseCount4 / calibrationFactor;

    pulseCount1 = 0;
    pulseCount2 = 0;
    pulseCount3 = 0;
    pulseCount4 = 0;

    prevMillis = currentMillis;

    interrupts();

    Serial.printf(
      "F1: %.2f | F2: %.2f | F3: %.2f | F4: %.2f\n",
      flow1,
      flow2,
      flow3,
      flow4
    );
  }
}

// ======================================================
//                   LEAK DETECTION
// ======================================================

void checkLeaks() {

  // Delay Leak Detection at Startup
  if (!leakageCheckReady && millis() - systemStartTime >= 10000) {

    leakageCheckReady = true;

    Serial.println("Leak Detection Active");
  }

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  int gas = map(analogRead(GAS_SENSOR), 0, 4095, 0, 100);

  bool leak1 = false;
  bool leak2 = false;

  bool gasLeak = gas > 30;

  if (leakageCheckReady) {

    leak1 = (flow1 > flow2 && flow1 > 1);

    leak2 = (flow3 > flow4 && flow3 > 1);
  }

  // ================== Fluid Leakage ==================

  if ((leak1 || leak2) && !leakageConfirmed) {

    if (!leakTimerRunning) {

      leakTimerRunning = true;

      leakTimerStart = millis();

    } else if (millis() - leakTimerStart >= 5000) {

      leakageConfirmed = true;

      digitalWrite(MOTOR_RELAY, LOW);

      digitalWrite(BUZZER, HIGH);

      digitalWrite(GREEN_LED, LOW);
      digitalWrite(RED_LED, HIGH);

      lcd.clear();

      lcd.setCursor(0, 0);
      lcd.print("Leak Detected");

      lcd.setCursor(0, 1);
      lcd.print("Motor OFF");

      Serial.println("Fluid Leakage Detected");
    }

  } else if (!leak1 && !leak2) {

    leakTimerRunning = false;

    leakTimerStart = 0;
  }

  // ================== Gas Leakage ==================

  if (gasLeak) {

    digitalWrite(BUZZER, HIGH);

    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, HIGH);

    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Gas Leak Alert");

    lcd.setCursor(0, 1);
    lcd.print("Be Careful");

    Serial.println("Gas Leakage Detected");
  }

  // ================== Normal Condition ==================

  if (!leakageConfirmed && !gasLeak) {

    digitalWrite(MOTOR_RELAY, HIGH);

    digitalWrite(BUZZER, LOW);

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);

    static unsigned long lastDisplay = 0;

    if (millis() - lastDisplay > 5000) {

      lcd.clear();

      lcd.setCursor(0, 0);
      lcd.print("System Normal");

      lcd.setCursor(0, 1);

      lcd.print("T:");
      lcd.print((int)temp);

      lcd.print("C ");

      lcd.print((int)hum);

      lcd.print("%");

      lastDisplay = millis();
    }
  }
}

// ======================================================
//                 STREAM DATA FUNCTION
// ======================================================

void streamData() {

  static unsigned long lastStream = 0;

  if (millis() - lastStream >= 5000) {

    thing.stream("temperature");

    thing.stream("humidity");

    thing.stream("gas");

    thing.stream("flow1");
    thing.stream("flow2");
    thing.stream("flow3");
    thing.stream("flow4");

    lastStream = millis();
  }
}
