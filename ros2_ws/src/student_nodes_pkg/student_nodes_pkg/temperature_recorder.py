#!/usr/bin/env python3
"""Record temperature and simulated vehicle telemetry to a single CSV file."""

import csv
from datetime import datetime, timezone
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

from gui_interface.topics import (
    TOPIC_RECORDER_COMMAND,
    TOPIC_RECORDER_STATUS,
    TOPIC_SDC_BATTERY,
    TOPIC_SDC_EVENTS,
    TOPIC_SDC_SPEED,
    TOPIC_SDC_STATUS,
    TOPIC_SDC_STEERING,
    TOPIC_SENSOR_TEMPERATURE,
)


class TemperatureRecorder(Node):
    """Command-controlled snapshot recorder for every dashboard telemetry value."""

    CSV_HEADER = [
        'timestamp',
        'temperature',
        'speed',
        'steering',
        'battery',
        'vehicle_status',
    ]

    def __init__(self):
        super().__init__('temperature_recorder_node')

        self.declare_parameter('csv_path', 'data/temperature_readings.csv')
        configured_path = str(self.get_parameter('csv_path').value)
        self.csv_path = Path(configured_path).expanduser().resolve()
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        self.is_recording = False
        self.recorded_count = 0
        self.csv_file = None
        self.csv_writer = None

        self.latest_temperature = None
        self.latest_speed = None
        self.latest_steering = None
        self.latest_battery = None
        self.latest_vehicle_status = None

        self.temperature_subscription = self.create_subscription(
            Float32,
            TOPIC_SENSOR_TEMPERATURE,
            self.update_temperature,
            10,
        )
        self.speed_subscription = self.create_subscription(
            Float32,
            TOPIC_SDC_SPEED,
            self.update_speed,
            10,
        )
        self.steering_subscription = self.create_subscription(
            Float32,
            TOPIC_SDC_STEERING,
            self.update_steering,
            10,
        )
        self.battery_subscription = self.create_subscription(
            Float32,
            TOPIC_SDC_BATTERY,
            self.update_battery,
            10,
        )
        self.vehicle_status_subscription = self.create_subscription(
            String,
            TOPIC_SDC_STATUS,
            self.update_vehicle_status,
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
        self.event_publisher = self.create_publisher(String, TOPIC_SDC_EVENTS, 10)

        self.ensure_csv_header()
        self.record_timer = self.create_timer(0.25, self.record_snapshot)
        self.status_timer = self.create_timer(2.0, self.publish_current_status)

        self.get_logger().info('Telemetry recorder started (idle)')
        self.get_logger().info(f'CSV output: {self.csv_path}')
        self.get_logger().info(f'Waiting for commands on {TOPIC_RECORDER_COMMAND}')

    def ensure_csv_header(self):
        if self.csv_path.exists() and self.csv_path.stat().st_size > 0:
            return

        with self.csv_path.open('w', newline='', encoding='utf-8') as csv_file:
            csv.writer(csv_file).writerow(self.CSV_HEADER)

    def open_csv_for_append(self):
        if self.csv_file is not None:
            return

        self.ensure_csv_header()
        self.csv_file = self.csv_path.open('a', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)

    def close_csv(self):
        if self.csv_file is None:
            return

        csv_file = self.csv_file
        self.csv_file = None
        self.csv_writer = None
        try:
            csv_file.flush()
        except OSError as error:
            self.get_logger().error(f'Could not flush telemetry CSV: {error}')
        try:
            csv_file.close()
        except OSError as error:
            self.get_logger().error(f'Could not close telemetry CSV: {error}')

    def publish_event(self, text):
        message = String()
        message.data = text
        self.event_publisher.publish(message)
        self.get_logger().info(text)

    def update_temperature(self, message):
        self.latest_temperature = float(message.data)

    def update_speed(self, message):
        self.latest_speed = float(message.data)

    def update_steering(self, message):
        self.latest_steering = float(message.data)

    def update_battery(self, message):
        self.latest_battery = float(message.data)

    def update_vehicle_status(self, message):
        self.latest_vehicle_status = message.data.strip() or None

    def handle_command(self, message):
        command = message.data.strip().lower()

        if command == 'start':
            if not self.is_recording:
                try:
                    self.open_csv_for_append()
                except OSError as error:
                    self.get_logger().error(f'Could not open telemetry CSV: {error}')
                    self.publish_event('Recording could not be started')
                    self.publish_current_status()
                    return
                self.is_recording = True
                self.publish_event('Recording started')
        elif command == 'stop':
            if self.is_recording:
                self.is_recording = False
                self.close_csv()
                self.publish_event('Recording stopped')
        elif command == 'reset':
            was_recording = self.is_recording
            self.close_csv()
            self.recorded_count = 0
            try:
                with self.csv_path.open('w', newline='', encoding='utf-8') as csv_file:
                    csv.writer(csv_file).writerow(self.CSV_HEADER)
                if was_recording:
                    self.open_csv_for_append()
            except OSError as error:
                self.is_recording = False
                self.get_logger().error(f'Could not reset telemetry CSV: {error}')
                self.publish_event('CSV reset failed')
                self.publish_current_status()
                return
            self.publish_event('CSV reset')
        else:
            self.get_logger().warning(
                f'Ignoring unknown recorder command: {message.data}'
            )
            return

        self.publish_current_status()

    @staticmethod
    def csv_value(value):
        return '' if value is None else value

    def record_snapshot(self):
        if not self.is_recording:
            return

        try:
            self.open_csv_for_append()
            timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
            self.csv_writer.writerow(
                [
                    timestamp,
                    self.csv_value(self.latest_temperature),
                    self.csv_value(self.latest_speed),
                    self.csv_value(self.latest_steering),
                    self.csv_value(self.latest_battery),
                    self.csv_value(self.latest_vehicle_status),
                ]
            )
            self.csv_file.flush()
            self.recorded_count += 1
        except OSError as error:
            self.is_recording = False
            self.close_csv()
            self.get_logger().error(f'Could not write telemetry CSV: {error}')
            self.publish_event('Recording stopped because the CSV could not be written')
            self.publish_current_status()

    def publish_current_status(self):
        state = 'recording' if self.is_recording else 'idle'
        status = String()
        status.data = f'{state}:{self.recorded_count}'
        self.status_publisher.publish(status)

    def destroy_node(self):
        self.close_csv()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = TemperatureRecorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Telemetry recorder stopped by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
