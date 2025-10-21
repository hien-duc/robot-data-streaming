#!/usr/bin/env python3
"""
VDA5050 Message Processor

This script demonstrates how to subscribe to and process VDA5050 messages from the robot streamer.
It shows how a fleet management system might consume these messages.
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

class VDA5050MessageProcessor:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.message_count = 0
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Successfully connected to MQTT broker!")
            print("Subscribing to VDA5050 topics...")
            # Subscribe to all VDA5050 topics
            self.client.subscribe("/vda5050/#")
            print("Subscription successful. Waiting for messages...")
            print("-" * 50)
        else:
            print(f"Failed to connect to MQTT broker with error code: {rc}")
            
    def on_message(self, client, userdata, msg):
        self.message_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Parse the JSON message
            payload = json.loads(msg.payload.decode())
            
            # Extract message type from topic
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 4:
                message_type = topic_parts[3]
            else:
                message_type = "unknown"
                
            # Extract robot identifier
            if len(topic_parts) >= 3:
                manufacturer = topic_parts[1]
                serial_number = topic_parts[2]
                robot_id = f"{manufacturer}/{serial_number}"
            else:
                robot_id = "unknown"
                
            # Process based on message type
            print(f"[{timestamp}] Message #{self.message_count}")
            print(f"  Topic: {msg.topic}")
            print(f"  Robot: {robot_id}")
            print(f"  Type: {message_type}")
            
            if message_type == "connection":
                self.process_connection_message(payload)
            elif message_type == "state":
                self.process_state_message(payload)
            elif message_type == "visualization":
                self.process_visualization_message(payload)
            else:
                print(f"  Content: {json.dumps(payload, indent=2)}")
                
            print("-" * 50)
            
        except json.JSONDecodeError:
            print(f"[{timestamp}] Received non-JSON message on {msg.topic}")
            print(f"  Content: {msg.payload.decode()}")
            print("-" * 50)
        except Exception as e:
            print(f"[{timestamp}] Error processing message: {e}")
            print("-" * 50)
            
    def process_connection_message(self, payload):
        """Process a VDA5050 connection message"""
        header_id = payload.get("headerId", "N/A")
        timestamp = payload.get("timestamp", "N/A")
        version = payload.get("version", "N/A")
        connection_state = payload.get("connectionState", "N/A")
        
        print(f"  Header ID: {header_id}")
        print(f"  Timestamp: {timestamp}")
        print(f"  Version: {version}")
        print(f"  Connection State: {connection_state}")
        
    def process_state_message(self, payload):
        """Process a VDA5050 state message"""
        header_id = payload.get("headerId", "N/A")
        timestamp = payload.get("timestamp", "N/A")
        version = payload.get("version", "N/A")
        driving = payload.get("driving", False)
        operating_mode = payload.get("operatingMode", "N/A")
        
        # Battery state
        battery_state = payload.get("batteryState", {})
        battery_charge = battery_state.get("batteryCharge", "N/A")
        
        # Position
        position = payload.get("position", {})
        x = position.get("x", "N/A")
        y = position.get("y", "N/A")
        theta = position.get("theta", "N/A")
        
        print(f"  Header ID: {header_id}")
        print(f"  Timestamp: {timestamp}")
        print(f"  Version: {version}")
        print(f"  Driving: {driving}")
        print(f"  Operating Mode: {operating_mode}")
        print(f"  Battery Charge: {battery_charge}%")
        print(f"  Position: x={x}, y={y}, theta={theta}")
        
    def process_visualization_message(self, payload):
        """Process a VDA5050 visualization message"""
        header_id = payload.get("headerId", "N/A")
        timestamp = payload.get("timestamp", "N/A")
        version = payload.get("version", "N/A")
        
        # Visualization data
        viz_data = payload.get("visualizationData", {})
        path = viz_data.get("path", [])
        
        print(f"  Header ID: {header_id}")
        print(f"  Timestamp: {timestamp}")
        print(f"  Version: {version}")
        print(f"  Path Points: {len(path)}")
        if path:
            print("  Sample Path Points:")
            # Show first few points
            for i, point in enumerate(path[:3]):
                x = point.get("x", "N/A")
                y = point.get("y", "N/A")
                print(f"    {i+1}. x={x}, y={y}")
            if len(path) > 3:
                print(f"    ... and {len(path) - 3} more points")
                
    def start(self, host="localhost", port=1883):
        """Start the message processor"""
        print("Starting VDA5050 Message Processor...")
        print(f"Connecting to MQTT broker at {host}:{port}")
        
        try:
            self.client.connect(host, port, 60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\nStopping message processor...")
            self.client.disconnect()
            print(f"Processed {self.message_count} messages")
        except Exception as e:
            print(f"Error: {e}")

def main():
    print("VDA5050 Message Processor")
    print("=" * 50)
    print("This script demonstrates how to subscribe to and process VDA5050 messages.")
    print("Make sure the robot streamer is running and connected to the same MQTT broker.")
    print()
    
    # Create and start the processor
    processor = VDA5050MessageProcessor()
    processor.start()

if __name__ == "__main__":
    main()