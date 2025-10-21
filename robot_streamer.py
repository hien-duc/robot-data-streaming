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
        
        # Order state variables - with sample data
        self.order_id = "order_12345"
        self.order_update_id = 1
        self.last_node_id = "node_10"
        self.last_node_sequence_id = 10
        
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
        """Publish VDA5050 factsheet message - fully compliant with factsheet.schema
        
        Factsheet provides basic information about the AGV type series including
        capabilities, specifications, protocol limits, and supported features.
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
                "seriesDescription": "High-capacity autonomous mobile robot for warehouse operations",
                "agvKinematic": "DIFF",
                "agvClass": "CARRIER",
                "maxLoadMass": 1500.0,
                "localizationTypes": ["NATURAL", "REFLECTOR"],
                "navigationTypes": ["AUTONOMOUS", "VIRTUAL_LINE_GUIDED"]
            },
            "physicalParameters": {
                "speedMin": 0.1,
                "speedMax": 2.0,
                "accelerationMax": 0.8,
                "decelerationMax": 1.2,
                "heightMin": 0.3,
                "heightMax": 2.1,
                "width": 0.9,
                "length": 1.5
            },
            "protocolLimits": {
                "maxStringLens": {
                    "msgLen": 65536,
                    "topicSerialLen": 50,
                    "topicElemLen": 30,
                    "idLen": 100,
                    "idNumericalOnly": False,
                    "enumLen": 50,
                    "loadIdLen": 100
                },
                "maxArrayLens": {
                    "order.nodes": 100,
                    "order.edges": 100,
                    "node.actions": 20,
                    "edge.actions": 20,
                    "actions.actionsParameters": 10,
                    "instantActions": 5,
                    "trajectory.knotVector": 200,
                    "trajectory.controlPoints": 200,
                    "state.nodeStates": 50,
                    "state.edgeStates": 50,
                    "state.loads": 5,
                    "state.actionStates": 20,
                    "state.errors": 10,
                    "state.information": 10,
                    "error.errorReferences": 5,
                    "information.infoReferences": 5
                },
                "timing": {
                    "minOrderInterval": 1.0,
                    "minStateInterval": 0.5,
                    "defaultStateInterval": 1.0,
                    "visualizationInterval": 0.2
                }
            },
            "protocolFeatures": {
                "optionalParameters": [
                    {
                        "parameter": "order.nodes.nodePosition.allowedDeviationXY",
                        "support": "SUPPORTED",
                        "description": "AGV supports deviation tolerance in X and Y directions"
                    },
                    {
                        "parameter": "order.nodes.nodePosition.allowedDeviationTheta",
                        "support": "SUPPORTED",
                        "description": "AGV supports angular deviation tolerance"
                    },
                    {
                        "parameter": "state.agvPosition.localizationScore",
                        "support": "SUPPORTED",
                        "description": "AGV can provide localization confidence score"
                    },
                    {
                        "parameter": "state.velocity",
                        "support": "SUPPORTED",
                        "description": "AGV reports current velocity"
                    }
                ],
                "agvActions": [
                    {
                        "actionType": "pick",
                        "actionDescription": "Pick up a load at the current position",
                        "actionScopes": ["NODE"],
                        "actionParameters": [
                            {
                                "key": "stationType",
                                "valueDataType": "STRING",
                                "description": "Type of pickup station",
                                "isOptional": True
                            },
                            {
                                "key": "lhd",
                                "valueDataType": "STRING",
                                "description": "Load handling device to use",
                                "isOptional": False
                            }
                        ],
                        "resultDescription": "Returns load ID if detected",
                        "blockingTypes": ["HARD"]
                    },
                    {
                        "actionType": "drop",
                        "actionDescription": "Drop load at the current position",
                        "actionScopes": ["NODE"],
                        "actionParameters": [
                            {
                                "key": "stationType",
                                "valueDataType": "STRING",
                                "description": "Type of drop station",
                                "isOptional": True
                            },
                            {
                                "key": "lhd",
                                "valueDataType": "STRING",
                                "description": "Load handling device to use",
                                "isOptional": False
                            }
                        ],
                        "resultDescription": "Confirmation of successful drop",
                        "blockingTypes": ["HARD"]
                    },
                    {
                        "actionType": "wait",
                        "actionDescription": "Wait for specified duration",
                        "actionScopes": ["NODE", "EDGE"],
                        "actionParameters": [
                            {
                                "key": "duration",
                                "valueDataType": "FLOAT",
                                "description": "Wait duration in seconds",
                                "isOptional": False
                            }
                        ],
                        "resultDescription": "Wait completed",
                        "blockingTypes": ["SOFT", "HARD"]
                    },
                    {
                        "actionType": "startCharging",
                        "actionDescription": "Start battery charging",
                        "actionScopes": ["NODE"],
                        "actionParameters": [],
                        "resultDescription": "Charging started",
                        "blockingTypes": ["HARD"]
                    },
                    {
                        "actionType": "stopCharging",
                        "actionDescription": "Stop battery charging",
                        "actionScopes": ["NODE"],
                        "actionParameters": [],
                        "resultDescription": "Charging stopped",
                        "blockingTypes": ["HARD"]
                    },
                    {
                        "actionType": "pause",
                        "actionDescription": "Pause current order execution",
                        "actionScopes": ["INSTANT"],
                        "actionParameters": [],
                        "resultDescription": "AGV paused",
                        "blockingTypes": ["NONE"]
                    },
                    {
                        "actionType": "resume",
                        "actionDescription": "Resume paused order execution",
                        "actionScopes": ["INSTANT"],
                        "actionParameters": [],
                        "resultDescription": "AGV resumed",
                        "blockingTypes": ["NONE"]
                    }
                ]
            },
            "agvGeometry": {
                "wheelDefinitions": [
                    {
                        "type": "DRIVE",
                        "isActiveDriven": True,
                        "isActiveSteered": False,
                        "position": {
                            "x": 0.4,
                            "y": 0.3,
                            "theta": 0.0
                        },
                        "diameter": 0.25,
                        "width": 0.08
                    },
                    {
                        "type": "DRIVE",
                        "isActiveDriven": True,
                        "isActiveSteered": False,
                        "position": {
                            "x": 0.4,
                            "y": -0.3,
                            "theta": 0.0
                        },
                        "diameter": 0.25,
                        "width": 0.08
                    },
                    {
                        "type": "CASTER",
                        "isActiveDriven": False,
                        "isActiveSteered": False,
                        "position": {
                            "x": -0.4,
                            "y": 0.3
                        },
                        "diameter": 0.15,
                        "width": 0.05,
                        "centerDisplacement": 0.05
                    },
                    {
                        "type": "CASTER",
                        "isActiveDriven": False,
                        "isActiveSteered": False,
                        "position": {
                            "x": -0.4,
                            "y": -0.3
                        },
                        "diameter": 0.15,
                        "width": 0.05,
                        "centerDisplacement": 0.05
                    }
                ],
                "envelopes2d": [
                    {
                        "set": "agvEnvelope",
                        "description": "AGV footprint envelope",
                        "polygonPoints": [
                            {"x": 0.75, "y": 0.45},
                            {"x": 0.75, "y": -0.45},
                            {"x": -0.75, "y": -0.45},
                            {"x": -0.75, "y": 0.45}
                        ]
                    },
                    {
                        "set": "loadEnvelope",
                        "description": "AGV envelope with maximum load",
                        "polygonPoints": [
                            {"x": 1.35, "y": 0.6},
                            {"x": 1.35, "y": -0.6},
                            {"x": -0.75, "y": -0.6},
                            {"x": -0.75, "y": 0.6}
                        ]
                    }
                ]
            },
            "loadSpecification": {
                "loadPositions": ["front", "back"],
                "loadSets": [
                    {
                        "setName": "DEFAULT",
                        "loadType": "EPAL",
                        "loadPositions": ["front"],
                        "boundingBoxReference": {
                            "x": 0.6,
                            "y": 0.0,
                            "z": 0.1,
                            "theta": 0.0
                        },
                        "loadDimensions": {
                            "length": 1.2,
                            "width": 0.8,
                            "height": 1.5
                        },
                        "maxWeight": 1000.0,
                        "minLoadhandlingHeight": 0.05,
                        "maxLoadhandlingHeight": 0.3,
                        "minLoadhandlingDepth": 0.0,
                        "maxLoadhandlingDepth": 0.2,
                        "minLoadhandlingTilt": -0.1,
                        "maxLoadhandlingTilt": 0.1,
                        "agvSpeedLimit": 1.5,
                        "agvAccelerationLimit": 0.6,
                        "agvDecelerationLimit": 0.9,
                        "pickTime": 8.5,
                        "dropTime": 6.0,
                        "description": "Standard EUR pallet handling"
                    },
                    {
                        "setName": "HEAVY",
                        "loadType": "CUSTOM_HEAVY",
                        "loadPositions": ["front"],
                        "boundingBoxReference": {
                            "x": 0.6,
                            "y": 0.0,
                            "z": 0.1,
                            "theta": 0.0
                        },
                        "loadDimensions": {
                            "length": 1.0,
                            "width": 1.0,
                            "height": 1.0
                        },
                        "maxWeight": 1500.0,
                        "minLoadhandlingHeight": 0.05,
                        "maxLoadhandlingHeight": 0.25,
                        "agvSpeedLimit": 1.0,
                        "agvAccelerationLimit": 0.4,
                        "agvDecelerationLimit": 0.7,
                        "pickTime": 12.0,
                        "dropTime": 10.0,
                        "description": "Heavy custom load handling with reduced speed"
                    }
                ]
            },
            "vehicleConfig": {
                "versions": [
                    {
                        "key": "softwareVersion",
                        "value": "v3.2.1"
                    },
                    {
                        "key": "firmwareVersion",
                        "value": "v2.0.5"
                    },
                    {
                        "key": "hardwareVersion",
                        "value": "HW-Rev-C"
                    },
                    {
                        "key": "controllerVersion",
                        "value": "v1.8.3"
                    }
                ],
                "network": {
                    "localIpAddress": "192.168.1.100",
                    "netmask": "255.255.255.0",
                    "defaultGateway": "192.168.1.1",
                    "dnsServers": ["8.8.8.8", "8.8.4.4"],
                    "ntpServers": ["time.google.com", "pool.ntp.org"]
                }
            }
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
            "maps": [
                {
                    "mapId": "warehouse_map_01",
                    "mapVersion": "v2.3.1",
                    "mapDescription": "Main warehouse floor with updated layout",
                    "mapStatus": "ENABLED"
                },
                {
                    "mapId": "warehouse_map_02",
                    "mapVersion": "v1.0.0",
                    "mapDescription": "Secondary warehouse area",
                    "mapStatus": "DISABLED"
                }
            ],
            "orderId": self.order_id,
            "orderUpdateId": self.order_update_id,
            "zoneSetId": "zone_set_production_A",
            "lastNodeId": self.last_node_id,
            "lastNodeSequenceId": self.last_node_sequence_id,
            "driving": self.driving,
            "paused": False,
            "newBaseRequest": False,
            "distanceSinceLastNode": 2.45,
            "operatingMode": self.operating_mode,
            "nodeStates": [
                {
                    "nodeId": "node_11",
                    "sequenceId": 11,
                    "nodeDescription": "Pickup station A",
                    "released": True,
                    "nodePosition": {
                        "x": 10.5,
                        "y": 8.3,
                        "theta": 1.57,
                        "mapId": self.map_id
                    }
                },
                {
                    "nodeId": "node_12",
                    "sequenceId": 12,
                    "nodeDescription": "Waypoint B",
                    "released": False,
                    "nodePosition": {
                        "x": 15.2,
                        "y": 12.1,
                        "theta": 0.0,
                        "mapId": self.map_id
                    }
                }
            ],
            "edgeStates": [
                {
                    "edgeId": "edge_11_12",
                    "sequenceId": 11,
                    "edgeDescription": "Straight path from node 11 to 12",
                    "released": True,
                    "trajectory": {
                        "degree": 1,
                        "knotVector": [0.0, 0.0, 1.0, 1.0],
                        "controlPoints": [
                            {"x": 10.5, "y": 8.3, "weight": 1.0},
                            {"x": 15.2, "y": 12.1, "weight": 1.0}
                        ]
                    }
                }
            ],
            "agvPosition": {
                "x": self.x,
                "y": self.y,
                "theta": self.theta,
                "mapId": self.map_id,
                "mapDescription": "Main warehouse floor level 1",
                "positionInitialized": self.position_initialized,
                "localizationScore": 0.95,
                "deviationRange": 0.15
            },
            "velocity": {
                "vx": 0.5 if self.driving else 0.0,
                "vy": 0.0,
                "omega": 0.1 if self.driving else 0.0
            },
            "loads": [
                {
                    "loadId": "PALLET_7894",
                    "loadType": "EPAL",
                    "loadPosition": "front",
                    "boundingBoxReference": {
                        "x": 0.6,
                        "y": 0.0,
                        "z": 0.1,
                        "theta": 0.0
                    },
                    "loadDimensions": {
                        "length": 1.2,
                        "width": 0.8,
                        "height": 1.5
                    },
                    "weight": 450.5
                }
            ] if self.driving else [],
            "actionStates": [
                {
                    "actionId": "pick_action_001",
                    "actionType": "pick",
                    "actionDescription": "Pick load at station A",
                    "actionStatus": "RUNNING",
                    "resultDescription": "Load detected, gripper engaged"
                },
                {
                    "actionId": "wait_action_002",
                    "actionType": "wait",
                    "actionDescription": "Wait for 5 seconds",
                    "actionStatus": "WAITING",
                    "resultDescription": ""
                }
            ],
            "batteryState": {
                "batteryCharge": self.battery_level,
                "batteryVoltage": 48.5,
                "batteryHealth": 92,
                "charging": self.charging,
                "reach": 12500.0
            },
            "errors": [
                {
                    "errorType": "batteryLow",
                    "errorLevel": "WARNING",
                    "errorDescription": "Battery charge below 20%, consider recharging soon",
                    "errorHint": "Navigate to charging station when current order is completed",
                    "errorReferences": [
                        {
                            "referenceKey": "batteryCharge",
                            "referenceValue": str(self.battery_level)
                        }
                    ]
                }
            ] if self.battery_level < 20 else [],
            "information": [
                {
                    "infoType": "currentTask",
                    "infoLevel": "INFO",
                    "infoDescription": "Executing material transport from warehouse to production line",
                    "infoReferences": [
                        {
                            "referenceKey": "orderId",
                            "referenceValue": self.order_id
                        },
                        {
                            "referenceKey": "orderUpdateId",
                            "referenceValue": str(self.order_update_id)
                        }
                    ]
                }
            ],
            "safetyState": {
                "eStop": "NONE",
                "fieldViolation": False
            }
        }
        
        self.client.publish(topic, json.dumps(payload))
        print(f"Published state message to {topic}")
        
    def publish_visualization_message(self):
        """Publish VDA5050 visualization message - fully compliant with visualization.schema"""
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
            "agvPosition": {
                "x": self.x,
                "y": self.y,
                "theta": self.theta,
                "mapId": self.map_id,
                "positionInitialized": self.position_initialized,
                "localizationScore": 0.95,
                "deviationRange": 0.15
            },
            "velocity": {
                "vx": 0.5 if self.driving else 0.0,
                "vy": 0.0,
                "omega": 0.1 if self.driving else 0.0
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