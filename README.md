# IoT Gateway (6loWPAN + MESH Wifi)
Feature
*
*
*

About this repository
## ESP8266
* server.ino - The server : Receive data and publish it to CloudMQTT
* dht11_node.ino, light_node.ino - The sensor nodes collect data and send to others in mesh network (of course include server)

## LCD Display
* interface.py - This file I designed by using PyQt5 Designer
* lcd_display.py - Run this file to display in 3.5 inch LCD Raspberry Pi

Final is the main.c file !

