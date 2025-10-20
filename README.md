# VDA5050 Robot Data Streaming via MQTT

This project simulates an Autonomous Mobile Robot (AMR) or Automated Guided Vehicle (AGV) that streams operational data using the MQTT protocol in compliance with the VDA5050 standard.

## Features

- Publishes VDA5050-compliant JSON messages to an MQTT broker
- Supports all three VDA5050 message types:
  - Connection messages
  - State messages
  - Visualization messages
- Configurable MQTT connection parameters
- Adjustable publish frequency
- Support for multiple robots with different identifiers
- Realistic robot simulation (position, battery level, etc.)

## Prerequisites

- Python 3.x
- An MQTT broker (e.g., Mosquitto, HiveMQ)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/hien-duc/robot-data-streaming.git
   cd robot-data-streaming
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the robot streamer with default settings:
```bash
python robot_streamer.py
```

### Command Line Arguments

- `--host`: MQTT broker host (default: localhost)
- `--port`: MQTT broker port (default: 1883)
- `--manufacturer`: Robot manufacturer (default: roboticsInc)
- `--serial`: Robot serial number (default: AGV_001)
- `--frequency`: Publish frequency in seconds (default: 3.0)

### Example Usage

```bash
# Connect to a remote MQTT broker
python robot_streamer.py --host test.mosquitto.org --port 1883

# Customize robot identifier
python robot_streamer.py --manufacturer KUKA --serial KR_1001

# Adjust publish frequency to 5 seconds
python robot_streamer.py --frequency 5.0
```

### Running Multiple Robots

To run multiple robots simultaneously, use the provided multi-robot demo:
```bash
python multi_robot_demo.py
```

This will start three robots with different identifiers and publish frequencies.

## VDA5050 Message Format

The system publishes messages to the following MQTT topics:
- `/vda5050/{manufacturer}/{serialNumber}/connection`
- `/vda5050/{manufacturer}/{serialNumber}/state`
- `/vda5050/{manufacturer}/{serialNumber}/visualization`

### Example Messages

Connection:
```json
{
  "headerId": 1,
  "timestamp": "2025-10-20T08:00:00Z",
  "version": "2.0.0",
  "manufacturer": "roboticsInc",
  "serialNumber": "AGV_001",
  "connectionState": "ONLINE"
}
```

State:
```json
{
  "headerId": 2,
  "timestamp": "2025-10-20T08:01:00Z",
  "version": "2.0.0",
  "manufacturer": "roboticsInc",
  "serialNumber": "AGV_001",
  "driving": true,
  "operatingMode": "AUTOMATIC",
  "batteryState": { "batteryCharge": 87.5 },
  "position": { "x": 12.3, "y": 8.5, "theta": 45.0 },
  "errors": [],
  "information": []
}
```

Visualization:
```json
{
  "headerId": 3,
  "timestamp": "2025-10-20T08:02:00Z",
  "version": "2.0.0",
  "manufacturer": "roboticsInc",
  "serialNumber": "AGV_001",
  "visualizationData": {
    "path": [
      { "x": 10, "y": 5 },
      { "x": 12, "y": 8 }
    ]
  }
}
```

## Testing

To test the system, you can subscribe to the MQTT topics using any MQTT client:

```bash
# Subscribe to all topics for a specific robot
mosquitto_sub -h localhost -t "/vda5050/roboticsInc/AGV_001/#" -v
```

## License

This project is licensed under the MIT License.