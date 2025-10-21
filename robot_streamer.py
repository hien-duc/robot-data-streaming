#!/usr/bin/env python3
"""
VDA5050 Robot Data Streaming via MQTT

This script simulates an Autonomous Mobile Robot (AMR) or Automated Guided Vehicle (AGV)
that streams operational data using the MQTT protocol in compliance with the VDA5050 standard.
"""

import json
import time
import paho.mqtt.client as mqtt
import argparse
import uuid
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
        self.charging = False
        self.map_id = "warehouse_map_01"
        self.position_initialized = True
        
        # Order state variables - required fields
        self.order_id = ""
        self.order_update_id = 0
        self.last_node_id = ""
        self.last_node_sequence_id = 0
        
        # MQTT client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        
        # VDA5050 topic structure
        self.base_topic = f"/vda5050/{self.manufacturer}/{self.serial_number}"
        
        # Configure last will message (CONNECTIONBROKEN state)
        self._setup_last_will()
        
    def _setup_last_will(self):
        """Configure MQTT last will message for CONNECTIONBROKEN state"""
        topic = f"{self.base_topic}/connection"
        # Note: header_id will be 0 for last will since it's set before connection
        last_will_payload = {
            "headerId": 0,
            "timestamp": self.get_timestamp(),
            "version": "2.0.0",
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            "connectionState": "CONNECTIONBROKEN"
        }
        self.client.will_set(topic, json.dumps(last_will_payload), qos=1, retain=True)
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker at {self.host}:{self.port}")
            self.connected = True
            # Publish initial connection message
            self.publish_connection_message("ONLINE")
            # Publish factsheet once on connection
            self.publish_factsheet_message()
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
        """Generate ISO8601 timestamp with milliseconds (e.g., 1991-03-11T11:40:03.12Z)"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
    def publish_connection_message(self, state):
        """Publish VDA5050 connection message with retain flag
        
        ONLINE: Published when AGV connects to broker
        OFFLINE: Published when AGV disconnects in orderly fashion
        CONNECTIONBROKEN: Sent via last will if connection drops unexpectedly
        """
        topic = f"{self.base_topic}/connection"
        payload = {
            "headerId": self.get_next_header_id(),
            "timestamp": self.get_timestamp(),
            "version": "2.0.0",
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            "connectionState": state
        }
        
        # Connection messages must be sent with retain flag per VDA5050 spec
        self.client.publish(topic, json.dumps(payload), qos=1, retain=True)
        print(f"Published connection message to {topic}: {state}")
        
    def publish_factsheet_message(self):
        """Publish VDA5050 factsheet message - only required fields per factsheet.schema
        
        Factsheet provides basic information about the AGV type series.
        This is typically published once when the AGV connects.
        """
        topic = f"{self.base_topic}/factsheet"
        payload = {
            "headerId": self.get_next_header_id(),
            "timestamp": self.get_timestamp(),
            "version": "2.0.0",
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            "typeSpecification": {
                "seriesName": "AGV-Pro 3000",
                "agvKinematic": "DIFF",
                "agvClass": "CARRIER",
                "maxLoadMass": 1500.0,
                "localizationTypes": ["NATURAL"],
                "navigationTypes": ["AUTONOMOUS"]
            },
            "physicalParameters": {
                "speedMin": 0.1,
                "speedMax": 2.0,
                "accelerationMax": 0.8,
                "decelerationMax": 1.2,
                "heightMax": 2.1,
                "width": 0.9,
                "length": 1.5
            },
            "protocolLimits": {
                "maxStringLens": {},
                "maxArrayLens": {},
                "timing": {
                    "minOrderInterval": 1.0,
                    "minStateInterval": 0.5
                }
            },
            "protocolFeatures": {
                "optionalParameters": [],
                "agvActions": [
                    {
                        "actionType": "pick",
                        "actionScopes": ["NODE"]
                    },
                    {
                        "actionType": "drop",
                        "actionScopes": ["NODE"]
                    },
                    {
                        "actionType": "wait",
                        "actionScopes": ["NODE"]
                    }
                ]
            },
            "agvGeometry": {},
            "loadSpecification": {}
        }
        
        self.client.publish(topic, json.dumps(payload), qos=1, retain=True)
        print(f"Published factsheet message to {topic}")
        
    def publish_state_message(self):
        """Publish VDA5050 state message - fully compliant with state.schema"""
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
            "orderId": self.order_id,
            "orderUpdateId": self.order_update_id,
            "lastNodeId": self.last_node_id,
            "lastNodeSequenceId": self.last_node_sequence_id,
            "nodeStates": [],
            "edgeStates": [],
            "driving": self.driving,
            "operatingMode": self.operating_mode,
            "actionStates": [],
            "batteryState": {
                "batteryCharge": self.battery_level,
                "charging": self.charging
            },
            "errors": [],
            "safetyState": {
                "eStop": "NONE",
                "fieldViolation": False
            }
        }
        
        self.client.publish(topic, json.dumps(payload))
        print(f"Published state message to {topic}")
        
    def publish_visualization_message(self):
        """Publish VDA5050 visualization message - all fields are optional per schema"""
        if not self.connected:
            print("Not connected to MQTT broker. Skipping visualization message publish.")
            return
            
        topic = f"{self.base_topic}/visualization"
        # Note: visualization.schema has NO required fields - all are optional
        # Sending minimal useful data: just position
        payload = {
            "headerId": self.get_next_header_id(),
            "timestamp": self.get_timestamp(),
            "version": "2.0.0",
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            "agvPosition": {
                "x": self.x,
                "y": self.y,
                "theta": self.theta,
                "mapId": self.map_id,
                "positionInitialized": self.position_initialized
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