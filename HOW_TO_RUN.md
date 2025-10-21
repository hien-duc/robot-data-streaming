# How to Run the VDA5050 Robot Data Streaming System with a Local MQTT Broker

Based on your question about running the system with a local broker (as shown in Terminal#2-11 logs with MQTT connection errors to localhost:1883), here's a complete guide on how to set up and run the system.

## Understanding the Issue

The error messages you saw in Terminal#2-11 indicate that the robot streamer was trying to connect to a local MQTT broker at `localhost:1883` but couldn't establish a connection. This happens because:

1. No MQTT broker was running on your local machine
2. The broker wasn't properly installed or configured
3. There might be firewall issues blocking the connection

## Solution: Setting Up a Local MQTT Broker

### Step 1: Install Mosquitto MQTT Broker

1. Download Mosquitto for Windows:
   - Visit the official download page: https://mosquitto.org/download/
   - Download the Windows installer (mosquitto-*-install-windows-x64.exe)

2. Install Mosquitto:
   - Run the downloaded installer as Administrator
   - Follow the installation wizard with default settings
   - The installer should automatically add Mosquitto to your system PATH

### Step 2: Start the MQTT Broker

You have several options to start the MQTT broker:

#### Option 1: Using the Provided Batch File (Easiest)
Simply double-click on `start_mosquitto.bat` in your project directory.

#### Option 2: Install as Windows Service
Open Command Prompt as Administrator and run:
```cmd
cd "C:\Program Files\mosquitto"
mosquitto install
mosquitto start
```

#### Option 3: Run Manually
Open Command Prompt and run:
```cmd
mosquitto
```
(Keep this window open while running the robot streamer)

### Step 3: Verify the Broker is Running

Before running the robot streamer, test the MQTT connection:

1. Run the provided test script:
   ```cmd
   python test_mqtt_connection.py
   ```

2. You should see a success message indicating the broker is running correctly.

### Step 4: Run the Robot Streamer

#### Option 1: Using the Provided Batch File (Easiest)
Simply double-click on `run_robot_streamer.bat` in your project directory.

#### Option 2: Command Line
Open a new Command Prompt window and run:
```cmd
python robot_streamer.py
```

### Step 5: Monitor the Messages

#### Option 1: Using the Provided Batch File (Easiest)
Simply double-click on `monitor_topics.bat` in your project directory.

#### Option 2: Command Line
Open another Command Prompt window and run:
```cmd
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

## Troubleshooting Common Issues

### 1. "Error connecting to MQTT broker: [WinError 10061]"
- **Cause**: MQTT broker is not running
- **Solution**: Start Mosquitto broker using one of the methods above

### 2. "Command 'mosquitto' is not recognized"
- **Cause**: Mosquitto is not in your system PATH
- **Solution**: Add Mosquitto installation directory to PATH or use full path to executables

### 3. Messages not appearing in the monitor
- **Cause**: Possible firewall blocking or wrong host/port
- **Solution**: Check firewall settings and verify broker is listening on port 1883

### 4. Dependency Issues
Run the dependency check script to verify all required packages are installed:
```cmd
python check_dependencies.py
```

## Running Multiple Robots

To run multiple robots simultaneously:
```cmd
python multi_robot_demo.py
```

This will start three robots with different identifiers:
- KUKA/KR_1001 (publishing every 2 seconds)
- roboticsInc/AGV_001 (publishing every 3 seconds)
- ABB/IRB_2002 (publishing every 4 seconds)

## Customization Options

You can customize the robot streamer with command-line arguments:
```cmd
python robot_streamer.py --host localhost --port 1883 --manufacturer KUKA --serial KR_1001 --frequency 5.0
```

## Stopping the System

1. To stop the robot streamer: Press Ctrl+C in the terminal
2. To stop the MQTT broker:
   - If running as a service: `mosquitto stop`
   - If running manually: Press Ctrl+C in the terminal

## Summary

To run the system with a local broker:

1. Install Mosquitto MQTT broker
2. Start the broker (using `start_mosquitto.bat` or manually)
3. Run the robot streamer (using `run_robot_streamer.bat` or manually)
4. Monitor messages (using `monitor_topics.bat` or manually)

The system is now ready to stream VDA5050-compliant robot data to your local MQTT broker!