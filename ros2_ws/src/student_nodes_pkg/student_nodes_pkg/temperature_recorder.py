#!/usr/bin/env python3
"""Record fake temperature readings to CSV when commanded by the React GUI."""

import csv
from datetime import datetime, timezone
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

from gui_interface.topics import (
    TOPIC_RECORDER_COMMAND,
    TOPIC_RECORDER_STATUS,
    TOPIC_SENSOR_TEMPERATURE,
)


class TemperatureRecorder(Node):
    """A command-controlled CSV recorder for /sensor/temperature."""

    def __init__(self):
        super().__init__('temperature_recorder_node')

        self.declare_parameter('csv_path', 'data/temperature_readings.csv')
        configured_path = str(self.get_parameter('csv_path').value)
        self.csv_path = Path(configured_path).expanduser().resolve()
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        self.is_recording = False
        self.recorded_count = 0

        self.temperature_subscription = self.create_subscription(
            Float32,
            TOPIC_SENSOR_TEMPERATURE,
            self.record_temperature,
            10,
        )
        self.command_subscription = self.create_subscription(
            String,
            TOPIC_RECORDER_COMMAND,
            self.handle_command,
            10,
        )
        self.status_publisher = self.create_publisher(
            String,
            TOPIC_RECORDER_STATUS,
            10,
        )

        self.ensure_csv_header()
        self.status_timer = self.create_timer(2.0, self.publish_current_status)

        self.get_logger().info('Temperature recorder started (idle)')
        self.get_logger().info(f'CSV output: {self.csv_path}')
        self.get_logger().info(f'Waiting for commands on {TOPIC_RECORDER_COMMAND}')

    def ensure_csv_header(self):
        """Create the file and header if it is new or empty."""
        if self.csv_path.exists() and self.csv_path.stat().st_size > 0:
            return

        with self.csv_path.open('w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['timestamp_utc', 'temperature_celsius'])

    def handle_command(self, message):
        """Handle start, stop, and reset commands sent from the browser."""
        command = message.data.strip().lower()

        if command == 'start':
            self.is_recording = True
            self.get_logger().info('CSV recording started')
        elif command == 'stop':
            self.is_recording = False
            self.get_logger().info(
                f'CSV recording stopped after {self.recorded_count} readings'
            )
        elif command == 'reset':
            was_recording = self.is_recording
            self.recorded_count = 0
            with self.csv_path.open('w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['timestamp_utc', 'temperature_celsius'])
            self.is_recording = was_recording
            self.get_logger().info('CSV recording file reset')
        else:
            self.get_logger().warning(f'Ignoring unknown recorder command: {message.data}')
            return

        self.publish_current_status()

    def record_temperature(self, message):
        """Append a timestamped sensor reading while recording is active."""
        if not self.is_recording:
            return

        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
        with self.csv_path.open('a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([timestamp, f'{message.data:.2f}'])

        self.recorded_count += 1

    def publish_current_status(self):
        """Publish periodic state so a newly opened GUI receives it quickly."""
        state = 'recording' if self.is_recording else 'idle'
        status = String()
        status.data = f'{state}:{self.recorded_count}'
        self.status_publisher.publish(status)


def main(args=None):
    rclpy.init(args=args)
    node = TemperatureRecorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
