import time
import random
import json
import paho.mqtt.client as mqtt

# ==============================================================================
# MQTT BROKER CONFIGURATION
# ==============================================================================

# "localhost" is a special loopback IP address (127.0.0.1) pointing directly to YOUR OWN computer.
# Use "localhost" when both the publisher script and MQTT broker run on the exact same machine.
# If your MQTT broker is running on a different device (like a Raspberry Pi or cloud server), 
# replace "localhost" with that device's actual IP address (e.g., "192.168.1.50").
BROKER = "localhost"

# PORT: A network port is a specific communication channel used by applications to send/receive data.
# Port 1883 is the default, unencrypted standard network port assigned globally for MQTT messaging.
# (Note: Port 8883 is typically used if you enable encrypted MQTT with SSL/TLS).
PORT = 1883

# TOPIC: The channel/subject name where data is published.
# Subscribers listen specifically to this topic path to receive readings.
TOPIC = "home/smart_meter/readings"

# ==============================================================================
# MQTT CLIENT INITIALIZATION & CONNECTION
# ==============================================================================

# Create an instance of the MQTT client
client = mqtt.Client()

# Connect to the MQTT Broker.
# Parameter 1: Broker address ("localhost")
# Parameter 2: Port number (1883)
# Parameter 3 (60): Keep-Alive timer in seconds. 
# "60" tells the broker to keep the connection open and wait up to 60 seconds. 
# If no messages pass between client and broker within 60 seconds, a ping packet is sent 
# to ensure the client is still alive and prevent the broker from unexpectedly dropping the connection.
client.connect(BROKER, PORT, 60)

print("Smart Meter Emulator Started... Publishing data.")

# ==============================================================================
# MAIN PUBLISHING LOOP
# ==============================================================================

try:
    while True:
        # Simulate realistic smart meter telemetry data using a standard Python dictionary
        data = {
            "device_id": "meter_001",
            "voltage": round(random.uniform(220.0, 240.0), 2),      # Volts (AC Mains Voltage)
            "current": round(random.uniform(1.0, 15.0), 2),        # Amps (Household Current Draw)
            "power_watts": round(random.uniform(200.0, 3500.0), 2), # Watts (Active Power Draw)
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")         # Human-readable formatted time
        }
        
        # JSON CONVERSION:
        # `data` above is a native Python Dictionary object. MQTT cannot transmit Python objects directly over networks.
        # `json.dumps(data)` takes the `data` dictionary and serializes (converts) it into a JSON-formatted STRING (`payload`).
        # This string payload is structured so any subscriber (Python, JavaScript, Node-RED) can easily read it.
        payload = json.dumps(data)
        
        # Publish the JSON string payload over network to the specified topic
        client.publish(TOPIC, payload)
        
        print(f"Published: {payload}")
        
        # Wait for 2 seconds before generating and transmitting the next reading
        time.sleep(2) 

except KeyboardInterrupt:
    # Safely handle Ctrl+C exit in the terminal
    print("\nMeter stopped by user.")
    
    # Gracefully disconnect from the MQTT broker to free up resources
    client.disconnect()
