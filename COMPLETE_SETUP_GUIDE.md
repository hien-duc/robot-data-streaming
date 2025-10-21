# Complete Setup Guide: VDA5050 Robot Data Streaming with Local MQTT Broker

This guide provides step-by-step instructions for setting up and running the complete VDA5050 robot data streaming system with a local MQTT broker on Windows.

## Prerequisites

1. Windows operating system
2. Python 3.x installed
3. Internet connection for downloading Mosquitto

## Step 1: Project Setup

1. Navigate to your project directory:
   ```
   cd E:\robot-data-streaming
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Step 2: Install Mosquitto MQTT Broker

1. Download Mosquitto for Windows:
   - Visit: https://mosquitto.org/download/
   - Download the Windows installer (mosquitto-*-install-windows-x64.exe)

2. Install Mosquitto:
   - Run the downloaded installer as Administrator
   - Follow the installation wizard with default settings

3. Add Mosquitto to your system PATH (if not done automatically):
   - Open System Properties → Advanced → Environment Variables
   - Edit the PATH variable and add: `C:\Program Files\mosquitto`

## Step 3: Start the MQTT Broker

You have several options to start the MQTT broker:

### Option 1: Using the provided batch file
Double-click on `start_mosquitto.bat` in the project directory.

### Option 2: Install as Windows service
Open Command Prompt as Administrator and run:
```
cd "C:\Program Files\mosquitto"
mosquitto install
mosquitto start
```

### Option 3: Run manually
Open Command Prompt and run:
```
mosquitto -v
```

## Step 4: Test MQTT Broker Connection

Before running the robot streamer, test the MQTT connection:

1. In one terminal, run the test script:
   ```
   python test_mqtt_connection.py
   ```

2. You should see a success message indicating the broker is running correctly.

## Step 5: Run the Robot Streamer

### Single Robot Mode

1. Using the batch file:
   - Double-click `run_robot_streamer.bat`

2. Using command line:
   ```
   python robot_streamer.py
   ```

### Multiple Robot Mode

1. Run the multi-robot demo:
   ```
   python multi_robot_demo.py
   ```

## Step 6: Monitor the Messages

### Using the batch file:
Double-click `monitor_topics.bat` to see all VDA5050 messages.

### Using command line:
```
mosquitto_sub -h localhost -t "/vda5050/#" -v
```

## Expected Output

When everything is working correctly, you should see:

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

## Troubleshooting

### Common Issues and Solutions

1. **"Error connecting to MQTT broker: [WinError 10061]"**
   - Cause: MQTT broker is not running
   - Solution: Start Mosquitto broker using one of the methods above

2. **"Not connected to MQTT broker. Skipping message publish."**
   - Cause: Connection to broker was lost
   - Solution: Check if Mosquitto service is still running

3. **"Command 'mosquitto' is not recognized"**
   - Cause: Mosquitto is not in your system PATH
   - Solution: Add Mosquitto installation directory to PATH or use full path to executables

4. **Messages not appearing in the monitor**
   - Cause: Possible firewall blocking or wrong host/port
   - Solution: Check firewall settings and verify broker is listening on port 1883

### Verifying Mosquitto Installation

To verify Mosquitto is properly installed and in your PATH:

1. Open a new Command Prompt
2. Run:
   ```
   mosquitto --help
   ```

If you see the help output, Mosquitto is correctly installed.

## Customization Options

### Robot Streamer Configuration

You can customize the robot streamer with command-line arguments:

```
python robot_streamer.py --host localhost --port 1883 --manufacturer KUKA --serial KR_1001 --frequency 5.0
```

### Multi-Robot Configuration

Edit `multi_robot_demo.py` to customize the robots:
- Add more robots to the configuration list
- Change manufacturer/serial numbers
- Adjust publish frequencies

## Stopping the System

1. To stop the robot streamer: Press Ctrl+C in the terminal
2. To stop the MQTT broker:
   - If running as a service: `mosquitto stop`
   - If running manually: Press Ctrl+C in the terminal

## Project Structure

```
robot-data-streaming/
├── .venv/                 # Python virtual environment
├── robot_streamer.py      # Main robot streaming implementation
├── multi_robot_demo.py    # Multi-robot demo script
├── test_mqtt_connection.py # MQTT connection test script
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── MQTT_SETUP_GUIDE.md   # Detailed MQTT setup guide
├── COMPLETE_SETUP_GUIDE.md # This file
├── start_mosquitto.bat   # Batch file to start MQTT broker
├── run_robot_streamer.bat # Batch file to run robot streamer
├── monitor_topics.bat    # Batch file to monitor topics
└── .gitignore            # Git ignore file
```

## VDA5050 Compliance

This implementation follows the VDA5050 standard version 2.0.0:
- Proper topic structure: `/vda5050/{manufacturer}/{serialNumber}/{messageType}`
- Correct message formats for connection, state, and visualization messages
- Appropriate header IDs and timestamps
- Standard field names and structures

The system is ready for integration with fleet management systems that support the VDA5050 standard.