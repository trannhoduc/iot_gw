# IoT Gateway (6loWPAN + MESH Wifi)

This is the first project in my bachelor's years. 

### Purposes
A multiple IoT gateway where integrate 6LowPAN and mesh Wifi in a single device. The other devices which are running 6LoWPAN or mesh Wifi can connect to this gateway and send their information. 
Additionally, the data from sensors will be showed real-time on device's monitor.

### What is included in this project 

- 🛳️ ESP8266 module
  * server.ino - The server : Receive data and publish it to CloudMQTT
  * dht11_node.ino, light_node.ino - The sensor nodes collect data and send to others in mesh network (of course include server)
- 📊 LCD function
  * interface.py - This file I designed by using PyQt5 Designer
  * lcd_display.py - Run this file to display in 3.5 inch LCD Raspberry Pi
- 🎯 The main function, where connect 6LoWPAN, mesh wifi and the other functions.

