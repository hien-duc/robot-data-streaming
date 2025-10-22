
import json
import time
import paho.mqtt.client as mqtt
import argparse
from datetime import datetime, timezone

class VDA5050RobotStreamer:
    def __init__(self, host, port, manufacturer, serial_number, frequency=3):
        self.host = host
        self.port = port
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.frequency = frequency
        self.header_id = 0
        
        # Robot state variables
        self.battery_level = 100.0
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.driving = False
        self.operating_mode = "AUTOMATIC"
        
        # MQTT client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        
        # VDA5050 topic structure
        self.base_topic = f"/vda5050/{self.manufacturer}/{self.serial_number}"
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker at {self.host}:{self.port}")
            self.connected = True
            # Publish initial connection message
            self.publish_connection_message("ONLINE")
        else:
            print(f"Failed to connect to MQTT broker with error code: {rc}")
            self.connected = False
            
    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT broker")
        self.connected = False
        
    def connect(self):
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            
    def disconnect(self):
        self.publish_connection_message("OFFLINE")
        self.client.loop_stop()
        self.client.disconnect()
        
    def get_next_header_id(self):
        self.header_id += 1
        return self.header_id
        
    def get_timestamp(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
    def publish_connection_message(self, state):
        """Publish VDA5050 connection message"""
        if not self.connected:
            print("Not connected to MQTT broker. Skipping connection message publish.")
            return
            
        topic = f"{self.base_topic}/connection"
        payload = {
            "headerId": self.get_next_header_id(),
            "timestamp": self.get_timestamp(),
            "version": "2.0.0",
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            "connectionState": state
        }
        
        self.client.publish(topic, json.dumps(payload))
        print(f"Published connection message to {topic}")
        
    def publish_state_message(self):
        """Publish VDA5050 state message"""
        if not self.connected:
            print("Not connected to MQTT broker. Skipping state message publish.")
            return
            
        topic = f"{self.base_topic}/state"
        payload = {
            "headerId": self.get_next_header_id(),
            "timestamp": self.get_timestamp(),
            "version": "2.0.0",
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            "driving": self.driving,
            "operatingMode": self.operating_mode,
            "batteryState": {
                "batteryCharge": self.battery_level
            },
            "position": {
                "x": self.x,
                "y": self.y,
                "theta": self.theta
            },
            "errors": [],
            "information": []
        }
        
        self.client.publish(topic, json.dumps(payload))
        print(f"Published state message to {topic}")
        
    def publish_visualization_message(self):
        """Publish VDA5050 visualization message"""
        if not self.connected:
            print("Not connected to MQTT broker. Skipping visualization message publish.")
            return
            
        topic = f"{self.base_topic}/visualization"
        payload = {
            "headerId": self.get_next_header_id(),
            "timestamp": self.get_timestamp(),
            "version": "2.0.0",
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            "visualizationData": {
                "path": [
                    {"x": self.x, "y": self.y},
                    {"x": self.x + 1, "y": self.y + 1}
                ]
            }
        }
        
        self.client.publish(topic, json.dumps(payload))
        print(f"Published visualization message to {topic}")
        
    def simulate_robot_movement(self):
        """Simulate robot movement and state changes"""
        # Simple simulation - move in a square pattern
        self.x = (self.x + 0.5) % 20
        self.y = (self.y + 0.3) % 15
        self.theta = (self.theta + 5) % 360
        self.battery_level = max(0, self.battery_level - 0.1)
        
        # Randomly change driving state
        import random
        self.driving = random.choice([True, False])
        
    def run(self):
        """Main streaming loop"""
        print(f"Starting VDA5050 Robot Streamer for {self.manufacturer}/{self.serial_number}")
        print(f"Publishing data every {self.frequency} seconds")
        print(f"Attempting to connect to MQTT broker at {self.host}:{self.port}")
        
        try:
            while True:
                self.simulate_robot_movement()
                self.publish_state_message()
                self.publish_visualization_message()
                time.sleep(self.frequency)
        except KeyboardInterrupt:
            print("\nStopping robot streamer...")
            self.disconnect()


def main():
    parser = argparse.ArgumentParser(description="VDA5050 Robot Data Streaming via MQTT")
    parser.add_argument("--host", default="localhost", help="MQTT broker host (default: localhost)")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port (default: 1883)")
    parser.add_argument("--manufacturer", default="roboticsInc", help="Robot manufacturer (default: roboticsInc)")
    parser.add_argument("--serial", default="AGV_001", help="Robot serial number (default: AGV_001)")
    parser.add_argument("--frequency", type=float, default=3.0, help="Publish frequency in seconds (default: 3.0)")
    
    args = parser.parse_args()
    
    # Create and start the robot streamer
    streamer = VDA5050RobotStreamer(
        host=args.host,
        port=args.port,
        manufacturer=args.manufacturer,
        serial_number=args.serial,
        frequency=args.frequency
    )
    
    streamer.connect()
    
    try:
        streamer.run()
    except KeyboardInterrupt:
        streamer.disconnect()


if __name__ == "__main__":
    main()