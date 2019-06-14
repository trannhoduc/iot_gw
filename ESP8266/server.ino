//************************************************************
// this is a simple example that uses the painlessMesh library to
// connect to a another network and relay messages from a MQTT broker to the nodes of the mesh network.
// To send a message to a mesh node, you can publish it to "painlessMesh/to/12345678" where 12345678 equals the nodeId.
// To broadcast a message to all nodes in the mesh you can publish it to "painlessMesh/to/broadcast".
// When you publish "getNodes" to "painlessMesh/to/gateway" you receive the mesh topology as JSON
// Every message from the mesh which is send to the gateway node will be published to "painlessMesh/from/12345678" where 12345678 
// is the nodeId from which the packet was send.
//************************************************************

#include <Arduino.h>
#include <painlessMesh.h>
#include <PubSubClient.h>
#include <WiFiClient.h>

#define   MESH_PREFIX     "nho"
#define   MESH_PASSWORD   "22trannho"
#define   MESH_PORT       5555

#define   STATION_SSID     "NHO "
#define   STATION_PASSWORD "ahihi123"

#define HOSTNAME "MQTT_Bridge"

const char* mqtt_server = "m16.cloudmqtt.com";
const char* mqtt_username = "fuwcgyvb";
const char* mqtt_password = "B--K38UfxXE2";
const char* clientID = "NHO";

size_t exeNodeID = 0;

// Prototypes
void receivedCallback( const uint32_t &from, const String &msg );
void mqttCallback(char* topic, byte* payload, unsigned int length);

IPAddress getlocalIP();

IPAddress myIP(0,0,0,0);
//IPAddress mqttBroker("m2m.eclipse.org");

painlessMesh  mesh;
WiFiClient wifiClient;
PubSubClient mqttClient(mqtt_server, 15843, mqttCallback, wifiClient);

void setup() {
  Serial.begin(115200);

  mesh.setDebugMsgTypes( ERROR | STARTUP | CONNECTION );  // set before init() so that you can see startup messages

  // Channel set to 6. Make sure to use the same channel for your mesh and for you other
  // network (STATION_SSID)
  mesh.init( MESH_PREFIX, MESH_PASSWORD, MESH_PORT, WIFI_AP_STA, 6 );
  mesh.onReceive(&receivedCallback);

  mesh.stationManual(STATION_SSID, STATION_PASSWORD);
  mesh.setHostname(HOSTNAME);

  WiFi.begin(STATION_SSID, STATION_PASSWORD);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to the WiFi network");

  mqttClient.setServer(mqtt_server, 15843);
  mqttClient.setCallback(mqttCallback);

  if (mqttClient.connect(clientID, mqtt_username, mqtt_password)) {
    Serial.println("Connected to MQTT Broker!");
  }
  else {
    Serial.println("Connection to MQTT Broker failed...");
  }

  while (!mqttClient.connected()) {
    Serial.println("Connecting to MQTT...");
    if (mqttClient.connect("ESP8266Client", mqtt_username, mqtt_password ))
    {
      Serial.println("connected");  
    } 
    else 
    { 
      Serial.print("failed with state ");
      Serial.print(mqttClient.state());
      delay(2000); 
    }
  }
  mqttClient.subscribe("command");
}

void loop() {
  mesh.update();
  mqttClient.loop();

  if(myIP != getlocalIP()){
    myIP = getlocalIP();
    Serial.println("My IP is " + myIP.toString());

    if (mqttClient.connect("painlessMeshClient")) {
      mqttClient.publish("painlessMesh/from/gateway","Ready!");
      mqttClient.subscribe("command");
    } 
  }
}

void receivedCallback( const uint32_t &from, const String &msg ) {
  Serial.printf("bridge: Received from %u msg=%s\n",  from, msg.c_str());
  String topic = "painlessMesh/from";
//  String topic = "painlessMesh/from/" + String(from);
  mqttClient.publish(topic.c_str(), msg.c_str());
}

void mqttCallback(char* topic, uint8_t* payload, unsigned int length) {

  String cmd ="";
  
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    //Serial.print((char)payload[i]);
    cmd += (char)payload[i];
  }  
  Serial.println(cmd);

  //send to every node to implements commands
  DynamicJsonDocument jsonBuffer(1024);
  //JsonObject root = jsonBuffer.parseObject(cmd);
  deserializeJson(jsonBuffer, cmd);
  if (jsonBuffer.containsKey("topic"))
  {
      if (String("exeNode").equals(jsonBuffer["topic"].as<String>()))
      {
          exeNodeID = jsonBuffer["nodeId"];
          mesh.sendSingle(exeNodeID, cmd);  //send to specific Node with execute command
          Serial.println("Send to every node, done!");
          Serial.println(exeNodeID);
      }
  }

  
  char* cleanPayload = (char*)malloc(length+1);
  payload[length] = '\0';
  memcpy(cleanPayload, payload, length+1);
  String msg = String(cleanPayload);
  free(cleanPayload);

  String targetStr = String(topic).substring(16);

  if(targetStr == "gateway")
  {
        if(msg == "getNodes")
        {
              auto nodes = mesh.getNodeList(true);
              String str;
              for (auto &&id : nodes)
                str += String(id) + String(" ");
              mqttClient.publish("painlessMesh/from/gateway", str.c_str());
        }
  }
  else if(targetStr == "broadcast") 
  {
        mesh.sendBroadcast(msg);
  }
  else
  {
        uint32_t target = strtoul(targetStr.c_str(), NULL, 10);
        if(mesh.isConnected(target))
        {
          mesh.sendSingle(target, msg);
          Serial.println(msg);
        }
        else
        {
          mqttClient.publish("painlessMesh/from/gateway", "Client not connected!");
        }
   }
}
//end mqttCallback

IPAddress getlocalIP() {
  return IPAddress(mesh.getStationIP());
}
