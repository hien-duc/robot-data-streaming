# Running the VDA5050 Robot Data Streaming System

This document provides clear, step-by-step instructions for running the complete VDA5050 robot data streaming system on Windows.

## Quick Start (Recommended for Beginners)

If you're new to the system, follow these steps to get started quickly:

1. **Install Mosquitto MQTT Broker**
   - Download from: https://mosquitto.org/download/
   - Run the Windows installer as Administrator
   - Follow the installation wizard with default settings

2. **Start the MQTT Broker**
   - Double-click `start_mosquitto.bat` in the project folder
   - You should see a terminal window with Mosquitto running

3. **Run the Robot Streamer**
   - Double-click `run_robot_streamer.bat` in the project folder
   - You should see connection messages and periodic status updates

4. **Monitor the Messages**
   - Double-click `monitor_topics.bat` in the project folder
   - You should see the VDA5050 messages being published

## Detailed Setup Instructions

### Prerequisites

Before running the system, ensure you have:

1. Windows operating system
2. Python 3.6 or higher installed
3. Internet connection for initial setup

### Step 1: Environment Setup

1. Open Command Prompt and navigate to the project directory:
   ```
   cd E:\robot-data-streaming
   ```

2. Create a Python virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```
   .venv\Scripts\activate
   ```

4. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Step 2: MQTT Broker Installation

1. Download Mosquitto for Windows:
   - Visit: https://mosquitto.org/download/
   - Download the Windows installer

2. Install Mosquitto:
   - Run the installer as Administrator
   - Follow the installation wizard (default settings are fine)

3. Add Mosquitto to your system PATH (usually done automatically):
   - The installer typically adds Mosquitto to your PATH
   - If not, manually add `C:\Program Files\mosquitto` to your PATH

### Step 3: Starting the System

#### Option 1: Using Batch Files (Easiest)

1. Start the MQTT broker:
   - Double-click `start_mosquitto.bat`
   - Keep this window open

2. Run the robot streamer:
   - Double-click `run_robot_streamer.bat`
   - You should see connection messages

3. Monitor the messages:
   - Double-click `monitor_topics.bat`
   - You should see the published messages

#### Option 2: Manual Execution

1. Start the MQTT broker:
   ```
   mosquitto
   ```
   (Keep this terminal open)

2. In a new terminal, run the robot streamer:
   ```
   python robot_streamer.py
   ```

3. In another terminal, monitor the messages:
   ```
   mosquitto_sub -h localhost -t "/vda5050/#" -v
   ```

### Step 4: Verification

When the system is running correctly, you should see:

1. In the robot streamer terminal:
   ```
   Starting VDA5050 Robot Streamer for roboticsInc/AGV_001
   Publishing data every 3.0 seconds
   Attempting to connect to MQTT broker at localhost:1883
   Connected to MQTT broker at localhost:1883
   Published connection message to /vda5050/roboticsInc/AGV_001/connection
   Published state message to /vda5050/roboticsInc/AGV_001/state
   Published visualization message to /vda5050/roboticsInc/AGV_001/visualization
   ```

2. In the monitoring terminal:
   ```
   /vda5050/roboticsInc/AGV_001/connection {"headerId": 1, "timestamp": "2023-05-15T10:30:45Z", ...}
   /vda5050/roboticsInc/AGV_001/state {"headerId": 2, "timestamp": "2023-05-15T10:30:48Z", ...}
   /vda5050/roboticsInc/AGV_001/visualization {"headerId": 3, "timestamp": "2023-05-15T10:30:48Z", ...}
   ```

## Running Multiple Robots

To run multiple robots simultaneously:

1. Make sure the MQTT broker is running
2. Execute the multi-robot demo:
   ```
   python multi_robot_demo.py
   ```
   
This will start three robots with different identifiers:
- KUKA/KR_1001 (publishing every 2 seconds)
- roboticsInc/AGV_001 (publishing every 3 seconds)
- ABB/IRB_2002 (publishing every 4 seconds)

## Customization Options

### Robot Streamer Parameters

You can customize the robot streamer with these command-line arguments:

```
python robot_streamer.py --host [host] --port [port] --manufacturer [manufacturer] --serial [serial] --frequency [seconds]
```

Examples:
```bash
# Connect to a different MQTT broker
python robot_streamer.py --host test.mosquitto.org --port 1883

# Customize robot identifier
python robot_streamer.py --manufacturer ABB --serial IRB_2002

# Change publish frequency to 5 seconds
python robot_streamer.py --frequency 5.0
```

### Multi-Robot Configuration

Edit `multi_robot_demo.py` to customize the robots:
- Add more robots to the configuration list
- Change manufacturer/serial numbers
- Adjust publish frequencies

## Troubleshooting

### Common Issues and Solutions

1. **"Error connecting to MQTT broker: [WinError 10061]"**
   - Cause: MQTT broker is not running
   - Solution: Start Mosquitto broker using one of the methods above

2. **"Command 'mosquitto' is not recognized"**
   - Cause: Mosquitto is not in your system PATH
   - Solution: Add Mosquitto installation directory to PATH or use full path to executables

3. **Messages not appearing in the monitor**
   - Cause: Possible firewall blocking or wrong host/port
   - Solution: Check firewall settings and verify broker is listening on port 1883

### Verifying Installation

Run the dependency check script:
```
python check_dependencies.py
```

This will verify that all required components are properly installed.

## Stopping the System

1. To stop the robot streamer: Press Ctrl+C in the terminal
2. To stop the MQTT broker:
   - If running as a service: `mosquitto stop`
   - If running manually: Press Ctrl+C in the terminal

## System Components Overview

The system includes these key components:

1. **robot_streamer.py** - Main robot streaming implementation
2. **multi_robot_demo.py** - Multi-robot demo script
3. **start_mosquitto.bat** - Batch file to start MQTT broker
4. **run_robot_streamer.bat** - Batch file to run robot streamer
5. **monitor_topics.bat** - Batch file to monitor topics
6. **test_mqtt_connection.py** - MQTT connection test script
7. **check_dependencies.py** - Dependency verification script
8. **process_vda5050_messages.py** - VDA5050 message processor demo

## VDA5050 Compliance

This implementation follows the VDA5050 standard version 2.0.0:
- Proper topic structure: `/vda5050/{manufacturer}/{serialNumber}/{messageType}`
- Correct message formats for connection, state, and visualization messages
- Appropriate header IDs and timestamps
- Standard field names and structures

The system is ready for integration with fleet management systems that support the VDA5050 standard.