import paho.mqtt.client as paho
import time
import os
import json
import subprocess 
import datetime
import logging

# .ENV FILE FOR TESTING
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

# GLOBALS
MQTT_BROKER = os.environ.get('MQTT_BROKER','')
MQTT_PORT = int(os.environ.get('MQTT_PATH', 1883))
MQTT_PUB_TOPIC = os.environ.get('MQTT_PUB_TOPIC','')
MQTT_SUB_TOPIC = os.environ.get('MQTT_SUB_TOPIC','')


with open('triggers.json') as json_file:
    TRIGGERS = json.load(json_file)


def update_mute_timers(category, initialise=False):
    global mute_timers
    try:
        mute_timers
    except NameError:
        mute_timers = {}
    mute_period = TRIGGERS[category]['mute']
    if initialise == True:
        mute_timers.update({category : datetime.datetime.now()-datetime.timedelta(minutes=mute_period)})
    else:
        mute_timers.update({category : datetime.datetime.now()})

def play_alert(category):
    subprocess.Popen(["/usr/bin/mpv", "./sounds/notification.mp3"])
    time.sleep(2)
    subprocess.Popen(["/usr/bin/mpv", "./sounds/" + category + ".mp3"])


# SUB MQTT
def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code "+str(rc))
    client.subscribe(MQTT_SUB_TOPIC)

def on_message(client, userdata, msg):
    logging.info("Recieved : {}".format(str(msg.payload))) 
    message = msg.payload.decode('utf-8')
    logging.debug("message : {}".format(str(message))) 
    message = json.loads(message)
    category = message['category']
    logging.debug("json_category : {}".format(str(category))) 
    confidence = message['confidence']
    logging.debug("json_confidence : {}".format(str(confidence)))
    action_message(category, confidence)

def action_message(category, confidence):
    for i in TRIGGERS:
        if category == i:
            temp_category = i
            break
        temp_category = 'unknown'
    category = temp_category
    logging.debug("category : {}".format(category))
    now = datetime.datetime.now()
    trigger_mute = TRIGGERS[category]['mute']
    logging.debug("trigger_mute : {}".format(str(trigger_mute))) 
    trigger_confidence = TRIGGERS[category]['confidence']
    logging.debug("trigger_confidence : {}".format(str(trigger_confidence)))
    trigger_overnight = bool(TRIGGERS[category]['overnight'])
    logging.debug("trigger_overnight : {}".format(str(trigger_confidence)))
    # Break if the overnight mode
    if trigger_overnight == False:
        now_time = now.time()
        if now_time >= datetime.time(21,00) or now_time <= datetime.time(9,00):
            logging.info("Category : {} detected, however in mute period because of overnight mode".format(category))
            return
    # Send if high confidence on match
    if confidence > trigger_confidence:
        delta = now - datetime.timedelta(minutes=trigger_mute)
        logging.debug("delta : {}".format(str(delta)))
        mute_timer = mute_timers[category]
        logging.debug("mute_timer : {}".format(str(mute_timer)))
        if mute_timer < delta:
            logging.info("Category : {} detected, playing alert".format(category))
            play_alert(category)
            update_mute_timers(category)
        else:
            logging.info("Category : {} detected, however in mute period".format(category))

# PUB MQTT
def on_publish(client,userdata,result,rc):  
    print("Connected with result code "+str(rc))

def push_mqtt_message(message):
    client1 = paho.Client("mqtt-talker")
    client1.on_publish = on_publish
    client1.connect(MQTT_BROKER, MQTT_PORT)
    client1.publish(MQTT_PUB_TOPIC, str(message))

def main():
    for i in TRIGGERS:
        update_mute_timers(i, initialise=True)

    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info("STARTING MQTT Talker")
    client = paho.Client("mqtt-talkerbot")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Main Exectution
main()
