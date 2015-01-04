
#!/usr/bin/python 

import os
import glob
import time
import datetime
import RPi.GPIO as GPIO
import socket
import thread

###########################################
##    Produce log file
###########################################

oldFileName = ""
logFile = open("/home/pi/myrep/tmp", 'a+')
logLock = thread.allocate_lock()
def recordDataInLog(string):
    global oldFileName, logFile, logLock
    logLock.acquire
    fileName = datetime.datetime.now().strftime("%d-%m-%y")+"_log.thr"
    if fileName != oldFileName:
        logFile.close()
        logFile = open('/home/pi/myrep/'+fileName, 'a+')
    logFile.write(datetime.datetime.now().strftime("%H:%M:%S")+" - "+string+"\n")
    logLock.release
    print(datetime.datetime.now().strftime("%H:%M:%S")+" - "+string+"\n")

###########################################
##    Communication with other devices
###########################################
isExit = False
isExitLock = thread.allocate_lock()
roomTempFileLock = thread.allocate_lock()
roomTempFileName = "/var/www/roomTempFile.thr"
def handleComm():
    global isExit, isExitLock, roomTempFileLock, roomTempFileName
    recordDataInLog("starting handle the communication")
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('', 8089))
    serversocket.listen(5) # become a server socket, maximum 5 connections
    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(64)
        if len(buf) > 0:
            if buf == 'exit':
                isExitLock.acquire()
                isExit = True
                isExitLock.release()
                recordDataInLog("Exit")
            tokens = buf.split('_')
            if len(tokens) == 2:
                if tokens[0] == 'roomTemp':
                    roomTempFileLock.acquire
                    roomTempFile = open(roomTempFileName,'w')
                    roomTempFile.write('roomTemp ' + tokens[1]) 
                    roomTempFile.close()
                    roomTempFileLock.release
                    recordDataInLog("Write to roomTempFile: roomTemp "+tokens[1])
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
RELAY = 23
BLUE_LED = 12
WHITE_LED = 11
BUTTON = 3
blueValue = 0
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RELAY, GPIO.OUT)
GPIO.setup(BLUE_LED, GPIO.OUT)
GPIO.setup(WHITE_LED, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN)

GPIO.output(BLUE_LED, 1)
GPIO.output(WHITE_LED, 0)
GPIO.output(RELAY, 0)
 
def blinkBlueLed():
    global blueValue, BLUE_LED
    blueValue = 1 - blueValue
    GPIO.output(BLUE_LED, blueValue)

#################################
##   Main
#################################
recordDataInLog("Booting - Up")
commThread = thread.start_new_thread(handleComm, ())

recordDataInLog("Starting the control")
relayValue = 0
while True:

    isExitLock.acquire()
    if isExit == True:
        break
    isExitLock.release()
    
    blinkBlueLed();
    waterTemp = read_temp()
    roomTempFileLock.acquire
    roomTempFile = open(roomTempFileName,'r')
    lines = roomTempFile.readlines()
    roomTempFile.close()
    roomTempFileLock.release
    roomTemp = float(lines[0].split()[1])

    desiredWaterTemp = -5.55555*roomTemp + 178.88 # (16,90) -> liear (25,40)
    if desiredWaterTemp > 90:
       desiredWaterTemp = 90
    
    instantData = datetime.datetime.now().strftime("%d-%m-%y")+"  "+datetime.datetime.now().strftime("%H:%M:%S")+" roomTemp "+repr(roomTemp)+" waterTemp "+repr(waterTemp)+" desiredWaterTemp "+repr(desiredWaterTemp)

    DT = 3.0     

    if (waterTemp < desiredWaterTemp - DT) and (relayValue == 0):
        relayValue = 1
        recordDataInLog("OPEN RELAY Temp: "+" roomTemp "+repr(roomTemp)+" waterTemp "+repr(waterTemp)+" desiredWaterTemp "+repr(desiredWaterTemp))
         
    if (waterTemp > desiredWaterTemp + DT) and (relayValue == 1):
        relayValue = 0
        recordDataInLog("Close RELAY Temp: "+" roomTemp "+repr(roomTemp)+" waterTemp "+repr(waterTemp)+" desiredWaterTemp "+repr(desiredWaterTemp))

    GPIO.output(RELAY, relayValue)

    instantData = instantData +" relayValue "+ repr(relayValue)
    instantDataFile = open('/var/www/instantDataFile.thr','w')
    instantDataFile.write(instantData) 
    instantDataFile.close()
    print(instantData)
       

GPIO.cleanup()
