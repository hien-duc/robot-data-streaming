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

### Quick Start

For the easiest way to run the system, simply double-click the batch files:
1. `start_mosquitto.bat` - Starts the MQTT broker
2. `run_robot_streamer.bat` - Runs the robot data streamer
3. `monitor_topics.bat` - Monitors the published messages

### Command Line Usage

Run the robot streamer with default settings:
```bash
python robot_streamer.py
```

For detailed step-by-step instructions, see [RUNNING_THE_SYSTEM.md](RUNNING_THE_SYSTEM.md).

If you're seeing connection errors to localhost:1883, see [HOW_TO_RUN.md](HOW_TO_RUN.md) for specific instructions on setting up a local MQTT broker.

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

## Setting up a Local MQTT Broker

For Windows users who want to run a local MQTT broker, here are the steps:

1. Download Mosquitto from the official website: https://mosquitto.org/download/
2. Install Mosquitto by running the Windows installer
3. Add Mosquitto to your system PATH if it wasn't added automatically during installation
4. Start the broker by running `mosquitto` in a command prompt

For testing purposes, you can also run Mosquitto as a Windows service:

1. Open Command Prompt as Administrator
2. Navigate to the Mosquitto installation directory (usually C:\Program Files\mosquitto)
3. Run `mosquitto install` to install the service
4. Run `mosquitto start` to start the service

To manually start the broker, simply run `mosquitto` in a command prompt.

For a complete step-by-step guide, please see [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) which includes detailed instructions for the entire setup process.

For a comprehensive overview of the system architecture and components, see [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md).

For a complete project summary including features, files, and usage instructions, please refer to [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md).

## Testing

To test the system, you can subscribe to the MQTT topics using any MQTT client:

```bash
# Subscribe to all topics for a specific robot
mosquitto_sub -h localhost -t "/vda5050/roboticsInc/AGV_001/#" -v
```

### Testing with Local Broker

Once you have a local Mosquitto broker running:

1. In one terminal, run the robot streamer:
   ```bash
   python robot_streamer.py
   ```

2. In another terminal, subscribe to the VDA5050 topics:
   ```bash
   mosquitto_sub -h localhost -t "/vda5050/#" -v
   ```

You should see the connection, state, and visualization messages being published at the configured frequency.

### Using Batch Files (Windows)

For easier execution on Windows, you can use the provided batch files:

1. Double-click `start_mosquitto.bat` to start the MQTT broker
2. Double-click `run_robot_streamer.bat` to start the robot data streaming
3. Double-click `monitor_topics.bat` to monitor the published messages

Note: You may need to run these as Administrator depending on your system configuration.

### Testing MQTT Connection

You can also test the MQTT connection using the provided test script:

```bash
python test_mqtt_connection.py
```

This script will attempt to connect to a local MQTT broker and publish a test message.

### Checking Dependencies

You can verify that all required dependencies are installed by running:

```bash
python check_dependencies.py
```

This script will check for Python version, required packages, and Mosquitto CLI tools.

### Processing VDA5050 Messages

To see how a fleet management system might process VDA5050 messages, run:

```bash
python process_vda5050_messages.py
```

This script subscribes to all VDA5050 topics and demonstrates how to parse and process the different message types.

## License

This project is licensed under the MIT License.