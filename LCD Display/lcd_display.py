
from PyQt5 import QtCore, QtGui, QtWidgets
from random import seed, randint
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from interface import Ui_DataDisplay  # importing our generated file
from mysql.connector import Error
from threading import Thread 
from socketserver import ThreadingMixIn 
from datetime import datetime

import paho.mqtt.client as mqtt
import mysql.connector
import socket
import sys
import paho.mqtt.client as mqtt
from time import strftime
import json

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8888        # Port to listen on (non-privileged ports are > 1023)

seed(1)

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttc, obj, msg):
	mySQLconnection = mysql.connector.connect(host='localhost',
											database='sls_db', 
											user='root', 
											password='Son100480')
	cursor = mySQLconnection.cursor(prepared=True)
	# print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload.decode()))
	print(str(msg.payload.decode()))

	# application.ui.label_25.setText(str(msg.payload.decode()))
	time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	python_dict = json.loads(msg.payload.decode())
	if python_dict["topic"] == "dht11":
		application.ui.label_25.setText(python_dict["temperature"])
		application.ui.label_24.setText(python_dict["humidity"])
		application.ui.label_13.setText("ID: " + str(python_dict["nodeID"]) + " - " + strftime("%H:%M:%S"))
		temp = python_dict["temperature"]
		humi = python_dict["humidity"]

		sql_select_Query = "INSERT INTO esp8266(Temperature, Humidity, Last_updated) VALUES (%s,%s,%s)"
		insert_tuple = (python_dict["temperature"], python_dict["humidity"], time)

	else:
		application.ui.label_22.setText(python_dict["light"])
		application.ui.label_17.setText("ID: " + str(python_dict["nodeID"]) + " - " + strftime("%H:%M:%S")) 
		sql_select_Query = "INSERT INTO esp8266(Light, Last_updated) VALUES (%s,%s)"
		insert_tuple = (python_dict["light"], time)

	result  = cursor.execute(sql_select_Query, insert_tuple)
	mySQLconnection.commit()
	# result  = cursor.execute(sql_select_Query, insert_tuple)
	# connection.commit()

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

class mywindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(mywindow, self).__init__()
		self.ui = Ui_DataDisplay()
		self.ui.setupUi(self)
		self.ui.pushButton.clicked.connect(self.close)

	def update_label(self):
		# self.ui.textBrowser.setText(str(update))
		mySQLconnection = mysql.connector.connect(host='localhost',
                             database='sls_db',
                             user='root',
                             password='Son100480')
		sql_select_Query = "INSERT INTO esp8266(Temperature, Humidity) VALUES('Jack','dfdf')"
		cursor = mySQLconnection .cursor()
		cursor.execute(sql_select_Query)
		#records = cursor.fetchall()
		# for row in records:
		# 	self.ui.textBrowser_2.setText(str(row[1]))		
		# self.update = update.label_update(self)

class ServerThread(Thread):
	def __init__(self,window): 
		Thread.__init__(self) 
		self.window=application

	def run(self): 
     
		tcpServer.listen(4) 
		# conn, addr = tcpServer.accept() 

		while True:
			print("Multithreaded Python server : Waiting for connections from TCP clients...") 
			global conn
			(conn, (ip,port)) = tcpServer.accept() 
			newthread = ClientThread(ip,port,application) 
			newthread.start() 
			threads.append(newthread)
		for t in threads:
			t.join()  


class ClientThread(Thread, QObject): 

	trigger = pyqtSignal()
	def __init__(self,ip,port,window): 
		Thread.__init__(self) 
		self.window=application
		self.ip = ip 
		self.port = port 
		print("\t[+] New server socket thread started for " + ip + ":" + str(port)) 
	
	def run(self):
		while True :   
			#(conn, (self.ip,self.port)) = serverThread.tcpServer.accept() 
			global conn
			data = conn.recv(2048) 
			element = data.split()
			if not data: 
				break
			print(data)
			application.ui.label_18.setText(str(element[3].decode()))
			application.ui.label_21.setText(str(element[1].decode()))
			application.ui.label_19.setText(str(element[2].decode()))
			application.ui.label_20.setText(str(element[4].decode()))

			application.ui.label_12.setText("IPv6: " + str(element[0].decode()))
			application.ui.label_16.setText("Last update: " + strftime("%H:%M:%S"))

			msg = "temperature: " + str(element[3].decode()) + " ºC, light: " + str(element[4].decode()) + " lux, humidity: " + str(element[2].decode()) + " RH, pressure: " + str(element[1].decode()) + "hPa"

			mqttc.publish("6loWPAN", str(msg))

		print("Client disconnect")

		# close socket server
		serverThread=ServerThread(application)
		serverThread.start()

        # while True : 
            
        #     #(conn, (self.ip,self.port)) = serverThread.tcpServer.accept() 
        #     global conn
        #     data = conn.recv(2048) 
        #     # window.chat.append(data.decode("utf-8"))
        #     print(data)


if __name__ == '__main__':
	app = QtWidgets.QApplication([])
	application = mywindow()

	application.showFullScreen()

	TCP_IP = '127.0.0.1' 
	TCP_PORT = 8888 
	BUFFER_SIZE = 20  
	tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
	tcpServer.bind((TCP_IP, TCP_PORT)) 
	threads = []     
	    
	serverThread=ServerThread(application)
	serverThread.start()

	mqttc = mqtt.Client()
	mqttc.on_message = on_message
	mqttc.on_connect = on_connect
	mqttc.on_publish = on_publish
	mqttc.on_subscribe = on_subscribe
	# Uncomment to enable debug messages
	# mqttc.on_log = on_log
	mqttc.username_pw_set("fuwcgyvb", "B--K38UfxXE2")
	mqttc.connect("m16.cloudmqtt.com", 15843, 60)
	mqttc.subscribe("painlessMesh/from", 0)

	mqttc.loop_start()

	
	# application.exec_()  
	sys.exit(app.exec_())
	


