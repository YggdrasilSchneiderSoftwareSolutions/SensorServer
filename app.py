from flask import Flask, render_template
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

MQTT_SERVER = "127.0.0.1"
MQTT_TOPIC = "home/bme680"

# Dictionary containing mapping between {room : list of data}
sensor_data_map = {
    "Wohnzimmer": [],
    "Schlafzimmer": [],
    "Kinderzimmer": [],
    "Büro": [],
    "Bad": []
}

# Object for holding measurement data
class BME680_Data:
    def __init__(self, room, temperature, humidity, pressure, gas, iaq, co2_ppm, voc, iaq_accuracy, stab_status):
        self.room = room
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.gas = gas
        self.iaq = iaq
        self.co2_ppm = co2_ppm
        self.voc = voc
        self.iaq_accuracy = iaq_accuracy
        self.stab_status = stab_status
        self.iaq_text = self.get_indoor_air_quality_text()
        self.co2_text = self.get_co2_quality_level_text()
    
    # Define air quality. Reference: https://forum.iot-usergroup.de/t/indoor-air-quality-index/416/2
    def get_indoor_air_quality_text(self):
        if self.iaq >= 301:
            iaq_text = "Gefährlich"    
        elif 201 <= self.iaq <= 300:
            iaq_text = "Sehr ungesund"
        elif 176 <= self.iaq <= 200:
            iaq_text = "Ungesund"
        elif 151 <= self.iaq <= 175:
            iaq_text = "Schlecht"
        elif 51 <= self.iaq <= 150:
            iaq_text = "Mittelmäßig"
        elif 0 <= self.iaq <= 50:
            iaq_text = "Gut"
        else:
            iaq_text = ""
        
        return iaq_text

    # Define CO2 level. Reference: https://www.cik-solutions.com/anwendungen/co2-im-innenraum/
    def get_co2_quality_level_text(self):
        if self.co2_ppm <= 800:
            co2_level_text = "Hoch"
        elif 800 > self.co2_ppm <= 1000:
            co2_level_text = "Mittel"
        elif 1000 > self.co2_ppm <= 1400:
            co2_level_text = "Mäßig"
        else:
            co2_level_text = "Niedrig"

        return co2_level_text
        

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # more callbacks, etc
    # example: '{"room":"Wohnzimmer","temperature":"23.5","pressure":"945.6","humidity":"43.5","iaq":"34","co2":"200"}'
    payload = msg.payload
    json_data = json.loads(payload)
    
    sensor_data_map[json_data['room']].append(
        BME680_Data(
            json_data['room'], 
            json_data['temperature'], 
            json_data['humidity'], 
            json_data['pressure'], 
            json_data['gas'], 
            json_data['iaq'],
            json_data['co2_ppm'], 
            json_data['voc'], 
            json_data['iaq_accuracy'],
            json_data['stab_status']
        )
    )


@app.route('/')
def index():
    version = '1.0'
    return render_template('index.html', version=version)

@app.route('/data/<room>')
def get_data(room):
    #return json.dumps(sensor_data_map) TODO
    return json.dumps('{"room":"Wohnzimmer","temperature":"23.5","humidity":"43.5","iaq":"34","co2_ppm":"200"}')


if __name__ == '__main__':
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    print('Starting MQTT')
    #mqtt_client.connect(MQTT_SERVER, 1883, 60)

    # Non-blocking MQTT server
    #mqtt_client.loop_start()
        
    # Start Webserver (blocking) - stopped via CTRL + C
    app.run(debug=True, host='0.0.0.0')

    #mqtt_client.loop_stop()
    print('MQTT stopped - exit program')
    exit(0)
        
