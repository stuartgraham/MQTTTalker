# MQTT Talkerbot
Takes MQTT predefinied messages and outputs predefined mp3 sounds

### Environment variables
Pass the following environment vairables to execution environment
| Settings | Description | Inputs |
| :----: | --- | --- |
| `MQTT_BROKER` | MQTT Broker address | `mqtt.test.local` |
| `MQTT_PORT` | MQTT Broker port | `1883` |
| `MQTT_SUB_TOPIC` | MQTT Topic to subscribe to | `test/messages` |

### triggers.json
Create settings.py from settings.py.example
| Settings | Description | Inputs |
| `TRIGGERS` | Defines thresholds for triggering sounds | `{"person":{"confidence" : 0.95, "mute" : 2}}` |


### Requirements
```sh
pip install -p requirements.txt
apt install < apt-requirement.txt
```

### Execution 
```sh
python3 .\main.py
```
