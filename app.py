from flask import Flask, render_template
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

MQTT_SERVER = "127.0.0.1"
MQTT_PATH = "sensor_channel"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # more callbacks, etc
    # example: '{"temperature":"23.5","pressure":"945.6","humidity":"43.5","iaq":"34","co2":"200"}'
    payload = msg.payload
    json_data = json.loads(payload)


@app.route('/')
def index():
    version = '1.0'
    return render_template('index.html', version=version)


if __name__ == '__main__':
    try:
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        print('Starting MQTT')
        mqtt_client.connect(MQTT_SERVER, 1883, 60)

        # Non-blocking MQTT server
        mqtt_client.loop_start()
        
        # Start Webserver
        app.run(debug=True, host='0.0.0.0')

    except KeyboardInterrupt:
        print('Shutdown program')
    except (SystemError, OSError) as e:
        print('Fatal error: ', e)
    finally:
        mqtt_client.loop_stop()
        print('MQTT stopped - exit program')
        exit(0)
        
