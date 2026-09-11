import threading
import json
import paho.mqtt.client as mqtt
from flask import Flask, render_template, jsonify

# ==============================================================================
# FLASK WEB APPLICATION INITIALIZATION
# ==============================================================================

# Create the Flask application instance.
# Flask serves HTML pages and API endpoints to web browsers.
app = Flask(__name__)

# GLOBAL STATE STORE:
# This dictionary holds the most recent smart meter reading received from MQTT.
# It acts as an in-memory buffer shared between the MQTT background thread and the Flask web endpoints.
latest_reading = {
    "device_id": "Waiting for meter...",
    "voltage": 0.0,
    "current": 0.0,
    "power_watts": 0.0,
    "timestamp": "N/A"
}

# ==============================================================================
# MQTT BROKER CONFIGURATION
# ==============================================================================

# "localhost" tells the client that the MQTT broker is running on the local machine.
BROKER = "localhost"

# Port 1883 is the standard default port for unencrypted MQTT network traffic.
PORT = 1883

# The MQTT topic path we subscribe to for smart meter telemetry messages.
TOPIC = "home/smart_meter/readings"

# ==============================================================================
# MQTT CALLBACK FUNCTION (DATA RECEIVING & CONVERSION)
# ==============================================================================

def on_message(client, userdata, msg):
    """
    Callback function that automatically executes whenever a new MQTT message arrives on the subscribed topic.
    """
    global latest_reading
    try:
        # WHERE DATA IS RECEIVED & CONVERTED:
        # 1. RECEIVING DATA: `msg.payload` contains the raw byte data transmitted over the network by the publisher.
        # 2. BYTES TO STRING: `.decode("utf-8")` converts the raw network bytes into a human-readable JSON formatted String.
        # 3. STRING TO PYTHON DICTIONARY: `json.loads(...)` parses that JSON String and converts it back into a native Python Dictionary object.
        data = json.loads(msg.payload.decode("utf-8"))
        
        # Update the global buffer so web clients get the newest values instantly
        latest_reading = data
        
    except Exception as e:
        print("Error parsing MQTT message:", e)

# ==============================================================================
# MQTT BACKGROUND WORKER (THREADING)
# ==============================================================================

def start_mqtt():
    """
    Initializes and runs the MQTT client loop continuously.
    """
    client = mqtt.Client()
    
    # Register the callback function so the client knows what to do when a message arrives
    client.on_message = on_message
    
    # Connect to the broker (Keep-Alive set to 60 seconds)
    client.connect(BROKER, PORT, 60)
    
    # Tell the broker we want to listen for messages published on this specific topic
    client.subscribe(TOPIC)
    
    # `client.loop_forever()` starts an infinite blocking loop to handle networking, 
    # reconnects, and message callbacks. Because it blocks execution, we must run it inside a thread.
    client.loop_forever()

# THREADING EXPLANATION:
# Running `start_mqtt()` directly would block Flask from ever starting its web server.
# `threading.Thread(...)` creates a separate background thread so MQTT can be listening 
# and Flask web hosting can run simultaneously side-by-side.
# `daemon=True` ensures the thread automatically terminates when you stop the main Python program (Ctrl+C).
mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
mqtt_thread.start()

# ==============================================================================
# FLASK WEB ROUTES (HTTP ENDPOINTS)
# ==============================================================================

@app.route('/')
def index():
    """
    Serves the main web dashboard page.
    Flask looks for 'index.html' inside the '/templates' folder.
    """
    return render_template('index.html')

@app.route('/data')
def get_data():
    """
    API Endpoint called periodically by JavaScript inside index.html.
    `jsonify(latest_reading)` serializes our Python dictionary into a JSON HTTP response 
    so the browser can render live updates without refreshing the whole web page.
    """
    return jsonify(latest_reading)

# ==============================================================================
# APPLICATION ENTRY POINT & HOSTING PORTS
# ==============================================================================

if __name__ == '__main__':
    # HOSTING PORTS & BINDING EXPLANATION:
    # `host='0.0.0.0'`: Tells Flask to listen on ALL available network interfaces on this machine.
    # By default, Flask uses '127.0.0.1' (localhost only). Changing it to '0.0.0.0' makes the dashboard 
    # accessible to any external device (phones, PCs, tablets) connected on the exact same Wi-Fi/LAN network.
    # `port=5000`: The HTTP web server port. Users visit `http://<YOUR_IP_ADDRESS>:5000` in their browser.
    # `debug=False`: Ensures background threads aren't duplicated by Flask's auto-reloader during development.
    app.run(host='0.0.0.0', port=5000, debug=False)
