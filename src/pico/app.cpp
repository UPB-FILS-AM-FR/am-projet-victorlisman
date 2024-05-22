#include <WiFi.h>
#include <WiFiMulti.h>
#include <Wire.h>
#include <SPI.h>
#include <ArduinoHttpClient.h>
#include <OV7670.h>

#ifndef STASSID
#define STASSID "ak"
#define STAPSK "aa"
#endif

const char* ssid = STASSID;
const char* password = STAPSK;

const char* host = "172.23.201.66";  
const uint16_t port = 5000;           

WiFiMulti multi;

OV7670 camera;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  SPI.begin();

  camera.init();
  camera.setResolution(Resolution::QVGA_320x240);
  camera.setColorSpace(ColorSpace::YUV422);

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  multi.addAP(ssid, password);

  if (multi.run() != WL_CONNECTED) {
    Serial.println("Unable to connect to network, rebooting in 10 seconds...");
    delay(10000);
    rp2040.reboot();
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  Serial.println("Capturing image...");

  camera.startCapture();
  while (!camera.captureDone()) {
  }

  const size_t imageSize = camera.getImageSize();
  uint8_t* imageData = camera.getImageBuffer();

  Serial.print("Image captured, size: ");
  Serial.println(imageSize);

  Serial.print("Connecting to ");
  Serial.print(host);
  Serial.print(':');
  Serial.println(port);

  WiFiClient wifiClient;
  HttpClient client = HttpClient(wifiClient, host, port);

  String head = "--randomBoundary\r\nContent-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
  String tail = "\r\n--randomBoundary--\r\n";

  int contentLength = head.length() + imageSize + tail.length();

  client.beginRequest();
  client.post("/predict");
  client.sendHeader("Content-Type", "multipart/form-data; boundary=randomBoundary");
  client.sendHeader("Content-Length", contentLength);
  client.beginBody();
  client.print(head);
  client.write(imageData, imageSize);
  client.print(tail);
  client.endRequest();

  while (client.available() == 0) {
    delay(100);
  }

  Serial.println("Receiving from remote server");
  while (client.available()) {
    char ch = static_cast<char>(client.read());
    Serial.print(ch);
  }

  client.stop();

  delay(300000);
}
