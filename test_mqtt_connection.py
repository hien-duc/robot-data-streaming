#!/usr/bin/env python3
"""
Simple MQTT Connection Test Script

This script tests connectivity to an MQTT broker to verify that it's running correctly.
"""

import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to MQTT broker!")
        print("Publishing test message...")
        client.publish("test/connection", "Hello from MQTT test script!")
    else:
        print(f"Failed to connect to MQTT broker with error code: {rc}")
        
def on_publish(client, userdata, mid):
    print("Test message published successfully!")
    print("Test completed. You can now run the robot streamer.")
    client.disconnect()

def main():
    print("Testing MQTT broker connection...")
    print("Make sure your MQTT broker is running on localhost:1883")
    print()
    
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    try:
        # Connect to broker
        client.connect("localhost", 1883, 60)
        client.loop_start()
        
        # Wait for a moment to complete the test
        time.sleep(2)
        client.loop_stop()
        
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        print("Please make sure:")
        print("1. Mosquitto is installed")
        print("2. Mosquitto service is running")
        print("3. No firewall is blocking port 1883")

if __name__ == "__main__":
    main()