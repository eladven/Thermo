
#!/usr/bin/python 

import os
import glob
import time
import datetime
import RPi.GPIO as GPIO
import socket
import threading

DT = 3.0

RELAY = 23
BLUE_LED = 12
WHITE_LED = 11
BUTTON = 3

###########################################
##    Produce log file
###########################################

oldFileName = ""
logFile = open("tmp", 'a+')

def recordDataInLog(string):
    global oldFileName, logFile 
    fileName = datetime.datetime.now().strftime("%d-%m-%y")+"_log.thr"
    if fileName != oldFileName:
        logFile.close()
        logFile = open(fileName, 'a+')
    logFile.write(datetime.datetime.now().strftime("%H:%H:%S")+" - "+string+"\n")
    print(datetime.datetime.now().strftime("%H:%H:%S")+" - "+string+"\n")

###########################################
##    Communication with other devices
###########################################

def handleComm():
    recordDataInLog("starting handle the communication")
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('', 8089))
    serversocket.listen(5) # become a server socket, maximum 5 connections
    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(64)
        if len(buf) > 0:
            print buf
        serversocket.close

###########################################
##   Reading the thermo
###########################################

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
recordDataInLog("Waiting for thermometer communication...")

while len(glob.glob(base_dir + '28*')) < 1:
    time.sleep(0.001)
    print('.'),
recordDataInLog("Found!")
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.05)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

##########################################
##  GPIO 
##########################################

GPIO.setmode(GPIO.BOARD)
GPIO.setup(RELAY, GPIO.OUT)
GPIO.setup(BLUE_LED, GPIO.OUT)
GPIO.setup(WHITE_LED, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN)

GPIO.output(BLUE_LED, 1)
GPIO.output(WHITE_LED, 0)
GPIO.output(RELAY, 0)

#################################
##   Main
#################################
recordDataInLog("Booting - Up")

blueValue = 0;
counter = 0;

commThread = threading.Thread(target=handleComm, args=())
commThread.start()

recordDataInLog("Starting the control")
while True:
    counter += 1
    if counter == 10:
        counter = 0;
        blueValue = 1 - blueValue
        GPIO.output(BLUE_LED, blueValue)

        with open ('desire.thr', 'r') as desirefile:
            desiredTemp = float(desirefile.read().split()[0])
            desirefile.close
        if read_temp() < desiredTemp - DT :
            GPIO.output(RELAY, 1)
            recordDataInLog("OPEN RELAY Temp: "+repr(read_temp())+" desired temp: "+repr(desiredTemp))
        if read_temp() > desiredTemp + DT :
            GPIO.output(RELAY, 0)
            recordDataInLog("CLOSE RELAY Temp: "+repr(read_temp())+" desired temp: "+repr(desiredTemp))
            
   
       

GPIO.cleanup()
