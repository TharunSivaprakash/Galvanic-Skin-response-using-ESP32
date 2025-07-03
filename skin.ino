const int GSR_PIN = A0;           // NodeMCU analog input
const int NUM_READINGS = 3;       // Number of samples per cycle

void setup() {
  Serial.begin(115200);           // Baud rate matching Flask
  delay(1000);                    // Allow time for Serial to stabilize
}

void loop() {
  long sum = 0;

  for (int i = 0; i < NUM_READINGS; i++) {
    sum += analogRead(GSR_PIN);   // Read 10-bit ADC (0–1023)
    delay(10);
  }

  int sensorValue = sum / NUM_READINGS;

  Serial.println(sensorValue);    // Send averaged value over Serial

  delay(200 - (NUM_READINGS * 10)); // Maintain ~200ms interval
}
