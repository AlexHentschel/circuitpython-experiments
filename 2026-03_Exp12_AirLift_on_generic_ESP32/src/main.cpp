#include <Arduino.h>
#include <WiFi.h>

#include "secrets.h"

static const char *wlStatusToStr(wl_status_t status) {
  switch (status) {
    case WL_NO_SHIELD:
      return "NO_SHIELD";
    case WL_IDLE_STATUS:
      return "IDLE";
    case WL_NO_SSID_AVAIL:
      return "NO_SSID";
    case WL_SCAN_COMPLETED:
      return "SCAN_DONE";
    case WL_CONNECTED:
      return "CONNECTED";
    case WL_CONNECT_FAILED:
      return "CONNECT_FAILED";
    case WL_CONNECTION_LOST:
      return "CONNECTION_LOST";
    case WL_DISCONNECTED:
      return "DISCONNECTED";
    default:
      return "UNKNOWN";
  }
}

static void printWifiStatus() {
  const wl_status_t st = WiFi.status();
  Serial.printf("WiFi status: %s (%d)\n", wlStatusToStr(st), (int)st);

  if (st == WL_CONNECTED) {
    Serial.printf("  SSID: %s\n", WiFi.SSID().c_str());
    Serial.printf("  RSSI: %ld dBm\n", (long)WiFi.RSSI());
    Serial.printf("  IP:   %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("  GW:   %s\n", WiFi.gatewayIP().toString().c_str());
    Serial.printf("  Mask: %s\n", WiFi.subnetMask().toString().c_str());
    Serial.printf("  DNS:  %s\n", WiFi.dnsIP().toString().c_str());
  }
}

static bool connectToWifi(uint32_t timeoutMs) {
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);

  Serial.printf("Connecting to SSID '%s'...\n", WIFI_SSID);

  if (strlen(WIFI_PASSWORD) == 0) {
    WiFi.begin(WIFI_SSID);
  } else {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  }

  const uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - start) < timeoutMs) {
    delay(250);
    Serial.print('.');
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connected.");
    printWifiStatus();
    return true;
  }

  Serial.println("WiFi connect timed out.");
  printWifiStatus();
  return false;
}

static bool internetCheck() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Internet check skipped (WiFi not connected).");
    return false;
  }

  IPAddress ip;
  const bool dnsOk = WiFi.hostByName("example.com", ip);
  Serial.printf("DNS example.com: %s (%s)\n", dnsOk ? "OK" : "FAIL",
                ip.toString().c_str());
  if (!dnsOk) {
    return false;
  }

  WiFiClient client;
  client.setTimeout(5000);

  Serial.println("HTTP GET http://example.com/ ...");
  if (!client.connect("example.com", 80)) {
    Serial.println("HTTP connect failed.");
    return false;
  }

  client.print(
      "GET / HTTP/1.1\r\n"
      "Host: example.com\r\n"
      "User-Agent: esp32-bringup\r\n"
      "Connection: close\r\n\r\n");

  // Read the status line (e.g. "HTTP/1.1 200 OK")
  const uint32_t start = millis();
  while (!client.available() && (millis() - start) < 5000) {
    delay(10);
  }
  if (!client.available()) {
    Serial.println("HTTP timeout waiting for response.");
    client.stop();
    return false;
  }

  String statusLine = client.readStringUntil('\n');
  statusLine.trim();
  Serial.printf("HTTP status: %s\n", statusLine.c_str());
  client.stop();
  return statusLine.startsWith("HTTP/1.1 200") || statusLine.startsWith("HTTP/1.1 301") ||
         statusLine.startsWith("HTTP/1.1 302");
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println();
  Serial.println("ESP32 WiFi connect + internet check");
  Serial.printf("Chip rev: %u\n", (unsigned)ESP.getChipRevision());

  // Give USB-serial a moment so the first logs are visible.
  delay(250);

  connectToWifi(20000);
  internetCheck();
}

void loop() {
  static uint32_t lastStatusMs = 0;
  static uint32_t lastInternetMs = 0;

  const uint32_t now = millis();

  if (now - lastStatusMs >= 15000) {
    lastStatusMs = now;
    Serial.println();
    Serial.printf("--- Status (uptime %lu ms) ---\n", (unsigned long)now);
    printWifiStatus();
  }

  if (WiFi.status() != WL_CONNECTED) {
    // Try to reconnect occasionally.
    static uint32_t lastReconnectAttemptMs = 0;
    if (now - lastReconnectAttemptMs >= 10000) {
      lastReconnectAttemptMs = now;
      connectToWifi(15000);
    }
  }

  if (now - lastInternetMs >= 60000) {
    lastInternetMs = now;
    Serial.println();
    Serial.printf("--- Internet check (uptime %lu ms) ---\n", (unsigned long)now);
    const bool ok = internetCheck();
    Serial.printf("Internet: %s\n", ok ? "OK" : "FAIL");
  }

  delay(50);
}