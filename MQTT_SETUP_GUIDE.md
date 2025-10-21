# Setting up Local MQTT Broker and Running Robot Data Streaming

This guide will help you install a local MQTT broker (Mosquitto) on Windows and run the VDA5050 robot data streaming system.

## Step 1: Install Mosquitto MQTT Broker

1. Download Mosquitto for Windows:
   - Visit the official download page: https://mosquitto.org/download/
   - Download the Windows installer (mosquitto-*-install-windows-x64.exe)

2. Install Mosquitto:
   - Run the downloaded installer as Administrator
   - Follow the installation wizard with default settings
   - The default installation path is usually: `C:\Program Files\mosquitto`

## Step 2: Configure Mosquitto (Optional)

The default configuration should work for testing purposes. However, if you want to customize it:

1. Navigate to the Mosquitto installation directory (typically `C:\Program Files\mosquitto`)
2. Open `mosquitto.conf` in a text editor
3. Common configurations:
   - Change the listening port: `listener 1883`
   - Allow anonymous connections: `allow_anonymous true` (default)
   - Set up authentication if needed

## Step 3: Start Mosquitto Service

You can start Mosquitto in two ways:

### Option A: As a Windows Service (Recommended)
1. Open Command Prompt as Administrator
2. Navigate to Mosquitto directory:
   ```
   cd "C:\Program Files\mosquitto"
   ```
3. Install the service:
   ```
   mosquitto install
   ```
4. Start the service:
   ```
   mosquitto start
   ```

### Option B: Run Manually
1. Open Command Prompt
2. Navigate to Mosquitto directory:
   ```
   cd "C:\Program Files\mosquitto"
   ```
3. Run Mosquitto broker:
   ```
   mosquitto -v
   ```
   The `-v` flag enables verbose output which is helpful for debugging.

## Step 4: Test the MQTT Broker

To verify that Mosquitto is running correctly:

1. Open a new Command Prompt window
2. Subscribe to a test topic:
   ```
   mosquitto_sub -h localhost -t test/topic
   ```

3. Open another Command Prompt window
4. Publish a test message:
   ```
   mosquitto_pub -h localhost -t test/topic -m "Hello MQTT"
   ```

If everything is working, you should see "Hello MQTT" appear in the subscriber window.

## Step 5: Run the Robot Data Streaming System

With Mosquitto running, you can now run the robot data streaming system:

1. Open a new terminal in the project directory (`E:\robot-data-streaming`)
2. Activate the virtual environment:
   ```
   .venv\Scripts\activate
   ```

3. Run the robot streamer:
   ```
   python robot_streamer.py
   ```

The system will connect to your local MQTT broker and start publishing VDA5050 messages.

## Step 6: Monitor the Messages

To see the VDA5050 messages being published by the robot streamer:

1. Open a new Command Prompt window
2. Subscribe to the robot topics:
   ```
   mosquitto_sub -h localhost -t "/vda5050/#" -v
   ```

This will show all messages published to topics under the `/vda5050/` hierarchy.

## Running Multiple Robots

To run multiple robots simultaneously:

1. Open a new terminal in the project directory
2. Activate the virtual environment:
   ```
   .venv\Scripts\activate
   ```

3. Run the multi-robot demo:
   ```
   python multi_robot_demo.py
   ```

This will start three robots with different identifiers, all publishing to your local MQTT broker.

## Troubleshooting

1. If you get connection errors:
   - Make sure Mosquitto is running
   - Check that the port (default 1883) is not blocked by firewall
   - Verify that localhost resolves correctly

2. If you see "Not connected to MQTT broker" messages:
   - Check that Mosquitto service is started
   - Try connecting with mosquitto_sub/mosquitto_pub to verify the broker is working

3. If you have authentication enabled in Mosquitto:
   - Modify robot_streamer.py to include username/password authentication
   - Or disable authentication in mosquitto.conf for testing