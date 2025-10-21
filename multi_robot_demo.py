#!/usr/bin/env python3
"""
Multi-Robot Demo for VDA5050 Robot Data Streaming via MQTT

This script demonstrates how to run multiple VDA5050 robot streamers simultaneously
with different identifiers.
"""

import threading
import time
from robot_streamer import VDA5050RobotStreamer


def run_robot(robot_config):
    """Run a single robot streamer in a separate thread"""
    streamer = VDA5050RobotStreamer(
        host=robot_config['host'],
        port=robot_config['port'],
        manufacturer=robot_config['manufacturer'],
        serial_number=robot_config['serial_number'],
        frequency=robot_config['frequency']
    )
    
    streamer.connect()
    
    try:
        streamer.run()
    except KeyboardInterrupt:
        streamer.disconnect()


def main():
    # Configuration for multiple robots
    robots = [
        {
            'host': 'localhost',
            'port': 1883,
            'manufacturer': 'roboticsInc',
            'serial_number': 'AGV_001',
            'frequency': 3.0
        },
        {
            'host': 'localhost',
            'port': 1883,
            'manufacturer': 'KUKA',
            'serial_number': 'KR_1001',
            'frequency': 5.0
        },
        {
            'host': 'localhost',
            'port': 1883,
            'manufacturer': 'Yaskawa',
            'serial_number': 'MOTOMAN_01',
            'frequency': 7.0
        }
    ]
    
    # Create and start a thread for each robot
    threads = []
    for i, robot_config in enumerate(robots):
        print(f"Starting robot {i+1}: {robot_config['manufacturer']}/{robot_config['serial_number']}")
        thread = threading.Thread(target=run_robot, args=(robot_config,))
        thread.daemon = True  # Dies when main thread dies
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Small delay between starting each robot
    
    print(f"Started {len(threads)} robot streamers. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all robot streamers...")
        # In a real implementation, you would have a way to signal threads to stop
        # For now, we'll just exit and let the daemon threads die


if __name__ == "__main__":
    main()