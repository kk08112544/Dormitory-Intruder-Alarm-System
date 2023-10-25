#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "Kookoo_2.4G";
const char* password = "2511251125";
const char* mqtt_server = "broker.mqtt-dashboard.com";
const char* mqtt_topic = "motion_sensor";
const int pirPin = D2; // GPIO2
const char* flask_api_endpoint = "http://your-flask-api-endpoint";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];

void setup_wifi() {
  delay(10);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Handle MQTT messages, if needed
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT... ");
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe(mqtt_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retry in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  pinMode(pirPin, INPUT);
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  int motionState = digitalRead(pirPin);
  if (motionState == HIGH) {
    String message = "Motion Detected at " + String(millis()) + " ms";
    client.publish(mqtt_topic, message.c_str());
    
    // Send data to Flask API
    HTTPClient http;
    http.begin(flask_api_endpoint);
    int httpCode = http.POST(message);
    http.end();
    Serial.println("Data sent to Flask API");

    delay(1000); // To avoid multiple readings for the same event
  }

  // Rest of your loop code
}
