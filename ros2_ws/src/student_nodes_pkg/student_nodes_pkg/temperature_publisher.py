#!/usr/bin/env python3
"""Publish a realistic-looking fake temperature value four times per second."""

import math
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

from gui_interface.topics import TOPIC_SENSOR_TEMPERATURE


class TemperaturePublisher(Node):
    """Small sensor simulator used by the React subscription example."""

    def __init__(self):
        super().__init__('temperature_publisher_node')

        self.declare_parameter('publish_rate_hz', 4.0)
        publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        if publish_rate_hz <= 0:
            self.get_logger().warning('publish_rate_hz must be positive; using 4 Hz')
            publish_rate_hz = 4.0

        self.publisher = self.create_publisher(
            Float32,
            TOPIC_SENSOR_TEMPERATURE,
            10,
        )
        self.started_at = self.get_clock().now()
        self.timer = self.create_timer(1.0 / publish_rate_hz, self.publish_reading)

        self.get_logger().info('Fake temperature publisher started')
        self.get_logger().info(
            f'Publishing {TOPIC_SENSOR_TEMPERATURE} at {publish_rate_hz:g} Hz'
        )

    def publish_reading(self):
        """Generate a smooth value plus a little noise and publish it."""
        elapsed = (self.get_clock().now() - self.started_at).nanoseconds / 1e9
        temperature = 22.0 + (2.5 * math.sin(elapsed / 6.0))
        temperature += random.uniform(-0.15, 0.15)

        message = Float32()
        message.data = float(round(temperature, 2))
        self.publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = TemperaturePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
