import paho.mqtt.client as mqtt
import json
import requests
import io
import os

import OneM2MProtoc as module

from requests.api import head
import ANPRnoRestart as ANPR

# GLOBAL VARIABLES
ACP_NAME = "MYACP"
AE_NAME = "LicensePlateRecog"
DATA_CONTAINER = "DATA_license"
COMMAND_CONTAINER = "COMMAND"
CSE_URL = "127.0.0.1:7579"
CSE_NAME = "Mobius"
CSE_RELEASE = 3

DOWNLOADED_IMAGE_PATH = "./DownloadedImage"


# Function for creating the LicensePlateRecog AE with all its containers
def registerAE(ae, acp, cntDescription, description, cntData, cntCommand, commandSub, dataSub):
    
    module.createAE(ae)
    module.createACP(ae, acp)
    module.createCNT(ae, cntDescription)
    module.createCI(ae, cntDescription, description)
    module.createCNT(ae, cntData)
    module.createCNT(ae, cntCommand)
    module.createSUB(commandSub, ae, cntCommand)
    module.createSUB(dataSub, ae, cntData)



#/////////////////DO NOT USE, JUST FOR DEVELOPING/////////////////////

# def requestCSE (url, ty, body, callback, originator ):

#     Headers = {
#       "Content-Type": "application/json;ty={}".format(ty),
#       "X-M2M-Origin": originator,
#       "X-M2M-RVI": "{}".format(CSE_RELEASE),
#       "X-M2M-RI": "req0",
#       'Connection': "close"
#     }

#     r = requests.post('http://{}/{}{}'.format(CSE_URL, CSE_NAME, url), headers=Headers, data=json.dumps(body))
#     callback(r)

# def createCI(ae, cnt, ciContent, callback):
#     requestCSE("/{}/{}".format(ae, cnt), 4, {"m2m:cin": {'con': ciContent}}, callback, 'C{}'.format(ae))

#//////////////////////////////////////////////////////////////////




# Creates AE entity and containers inside
registerAE(AE_NAME, ACP_NAME, "DESCRIPTOR", "This is a neuronal network for number-plate recognition", DATA_CONTAINER, COMMAND_CONTAINER, "Command", "License")

# Executes a null recognition to load all the drivers
ANPR.runDetection(export=False)


# Function to execute when connected to MQTT
def on_connect(client, userdata, flags, rc):

    # Make shure that its connected (should return code 0)
    print("Connected with result code "+str(rc))

    # Subscribe to the corresponding topic
    client.subscribe("/oneM2M/req/Mobius2/Command/json")



# The callback to handle an incoming message over MQTT
def on_message(client, userdata, msg):

    # Processes the message and converts it into a json format
    message = msg.payload
    jsonP = json.loads(message)

    # Looks for the "con" property which contains the URL to the image
    try:
        con = jsonP["pc"]["m2m:sgn"]["nev"]["rep"]["m2m:cin"]["con"]
        if con:
            print(con)
            response = requests.get(con)
            if not os.path.isdir(DOWNLOADED_IMAGE_PATH):
                os.mkdir(DOWNLOADED_IMAGE_PATH)
            file = open("{}/image.jpg".format(DOWNLOADED_IMAGE_PATH), "wb")
            file.write(response.content)
            file.close()
            numberPlate = ANPR.runDetection("{}/image.jpg".format(DOWNLOADED_IMAGE_PATH), export=False)
            if numberPlate != False:
                print(numberPlate[0])
                module.createCI(AE_NAME, DATA_CONTAINER, numberPlate[0])
            else:
                module.createCI(AE_NAME, DATA_CONTAINER, "none")

        else:
            print("No data received")

    # If there's no URL or an error ocurred during the detection or download, skip        
    except:
        print("Error ocurred or con not existant")


# MQTT initialization
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()