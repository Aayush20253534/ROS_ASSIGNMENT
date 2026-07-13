#!/usr/bin/env python3
"""Authoritative ROS 2 simulation for the self-driving-car dashboard."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

from gui_interface.topics import (
    TOPIC_SDC_BATTERY,
    TOPIC_SDC_COMMAND,
    TOPIC_SDC_EVENTS,
    TOPIC_SDC_SPEED,
    TOPIC_SDC_STATUS,
    TOPIC_SDC_STEERING,
)


class SimulatedVehicle(Node):
    """Process GUI commands and publish smooth, bounded vehicle telemetry."""

    STATE_IDLE = 'IDLE'
    STATE_RUNNING = 'RUNNING'
    STATE_STOPPED = 'STOPPED'
    STATE_EMERGENCY_STOP = 'EMERGENCY_STOP'

    MAX_SPEED = 80.0
    MIN_STEERING = -30.0
    MAX_STEERING = 30.0

    UPDATE_RATE_HZ = 10.0
    ACCELERATION_RATE = 6.0
    BRAKING_RATE = 12.0
    EMERGENCY_BRAKING_RATE = 35.0
    STEERING_RATE = 45.0

    def __init__(self):
        super().__init__('simulated_vehicle_node')

        self.state = self.STATE_IDLE
        self.speed = 0.0
        self.target_speed = 0.0
        self.steering = 0.0
        self.target_steering = 0.0
        self.battery = 100.0
        self.stop_requested = False
        self.battery_empty_event_sent = False

        self.command_subscription = self.create_subscription(
            String,
            TOPIC_SDC_COMMAND,
            self.handle_command,
            10,
        )
        self.status_publisher = self.create_publisher(String, TOPIC_SDC_STATUS, 10)
        self.speed_publisher = self.create_publisher(Float32, TOPIC_SDC_SPEED, 10)
        self.steering_publisher = self.create_publisher(
            Float32,
            TOPIC_SDC_STEERING,
            10,
        )
        self.battery_publisher = self.create_publisher(Float32, TOPIC_SDC_BATTERY, 10)
        self.event_publisher = self.create_publisher(String, TOPIC_SDC_EVENTS, 10)

        self.timer_period = 1.0 / self.UPDATE_RATE_HZ
        self.update_timer = self.create_timer(self.timer_period, self.update_vehicle)

        self.get_logger().info('Simulated vehicle started')
        self.get_logger().info(f'Waiting for commands on {TOPIC_SDC_COMMAND}')
        self.publish_status()
        self.publish_telemetry()
        self.publish_event('Vehicle simulator ready')

    @staticmethod
    def clamp(value, minimum, maximum):
        return max(minimum, min(maximum, value))

    @staticmethod
    def move_toward(current, target, maximum_step):
        if current < target:
            return min(current + maximum_step, target)
        if current > target:
            return max(current - maximum_step, target)
        return current

    def publish_event(self, text):
        message = String()
        message.data = text
        self.event_publisher.publish(message)
        self.get_logger().info(text)

    def publish_status(self):
        message = String()
        message.data = self.state
        self.status_publisher.publish(message)

    def publish_float(self, publisher, value):
        message = Float32()
        message.data = float(value)
        publisher.publish(message)

    def publish_telemetry(self):
        self.publish_status()
        self.publish_float(self.speed_publisher, self.speed)
        self.publish_float(self.steering_publisher, self.steering)
        self.publish_float(self.battery_publisher, self.battery)

    def reject_command(self, reason):
        self.publish_event(f'Command rejected: {reason}')

    def handle_command(self, message):
        command = message.data.strip().upper()
        self.get_logger().info(f'Received command: {command or "<empty>"}')

        handlers = {
            'START_VEHICLE': self.start_vehicle,
            'STOP_VEHICLE': self.stop_vehicle,
            'ACCELERATE': self.accelerate,
            'BRAKE': self.brake,
            'STEER_LEFT': self.steer_left,
            'STEER_RIGHT': self.steer_right,
            'CENTER_STEERING': self.center_steering,
            'EMERGENCY_STOP': self.emergency_stop,
            'RESET_VEHICLE': self.reset_vehicle,
        }

        handler = handlers.get(command)
        if handler is None:
            self.publish_event(f'Unknown vehicle command: {command or "<empty>"}')
            return

        if self.state == self.STATE_EMERGENCY_STOP and command != 'RESET_VEHICLE':
            self.reject_command('reset the vehicle after an emergency stop')
            return

        handler()
        self.publish_status()

    def start_vehicle(self):
        if self.state not in (self.STATE_IDLE, self.STATE_STOPPED):
            self.reject_command('vehicle is already running')
            return
        if self.battery <= 0.0:
            self.reject_command('battery is empty')
            return

        self.state = self.STATE_RUNNING
        self.stop_requested = False
        self.publish_event('Vehicle started')

    def stop_vehicle(self):
        if self.state != self.STATE_RUNNING:
            self.reject_command('vehicle is not running')
            return

        self.target_speed = 0.0
        self.target_steering = 0.0
        self.stop_requested = True
        if self.speed <= 0.01:
            self.finish_stop()
        else:
            self.publish_event('Vehicle stopping')

    def accelerate(self):
        if self.state != self.STATE_RUNNING or self.stop_requested:
            self.reject_command('vehicle is not ready to accelerate')
            return
        if self.battery <= 0.0:
            self.reject_command('battery is empty')
            return

        self.target_speed = self.clamp(
            self.target_speed + 10.0,
            0.0,
            self.MAX_SPEED,
        )
        self.publish_event(f'Accelerating toward {self.target_speed:.0f} km/h')

    def brake(self):
        if self.state != self.STATE_RUNNING or self.stop_requested:
            self.reject_command('vehicle is not running normally')
            return

        self.target_speed = self.clamp(self.target_speed - 10.0, 0.0, self.MAX_SPEED)
        self.publish_event(f'Braking toward {self.target_speed:.0f} km/h')

    def steer_left(self):
        if self.state != self.STATE_RUNNING or self.stop_requested:
            self.reject_command('vehicle is not running normally')
            return

        self.target_steering = self.clamp(
            self.target_steering - 10.0,
            self.MIN_STEERING,
            self.MAX_STEERING,
        )
        self.publish_event('Steering left')

    def steer_right(self):
        if self.state != self.STATE_RUNNING or self.stop_requested:
            self.reject_command('vehicle is not running normally')
            return

        self.target_steering = self.clamp(
            self.target_steering + 10.0,
            self.MIN_STEERING,
            self.MAX_STEERING,
        )
        self.publish_event('Steering right')

    def center_steering(self):
        if self.state != self.STATE_RUNNING or self.stop_requested:
            self.reject_command('vehicle is not running normally')
            return

        self.target_steering = 0.0
        self.publish_event('Steering centered')

    def emergency_stop(self):
        self.state = self.STATE_EMERGENCY_STOP
        self.target_speed = 0.0
        self.target_steering = 0.0
        self.stop_requested = False
        self.publish_event('Emergency stop activated')

    def reset_vehicle(self):
        self.state = self.STATE_IDLE
        self.speed = 0.0
        self.target_speed = 0.0
        self.steering = 0.0
        self.target_steering = 0.0
        self.stop_requested = False
        self.battery_empty_event_sent = self.battery <= 0.0
        self.publish_event('Vehicle reset')

    def finish_stop(self):
        self.speed = 0.0
        self.target_speed = 0.0
        self.state = self.STATE_STOPPED
        self.stop_requested = False
        self.publish_event('Vehicle stopped')
        self.publish_status()

    def update_speed(self):
        if self.state == self.STATE_EMERGENCY_STOP:
            rate = self.EMERGENCY_BRAKING_RATE
        elif self.target_speed > self.speed:
            rate = self.ACCELERATION_RATE
        else:
            rate = self.BRAKING_RATE

        self.speed = self.move_toward(
            self.speed,
            self.target_speed,
            rate * self.timer_period,
        )
        self.speed = self.clamp(self.speed, 0.0, self.MAX_SPEED)

    def update_steering(self):
        self.steering = self.move_toward(
            self.steering,
            self.target_steering,
            self.STEERING_RATE * self.timer_period,
        )
        self.steering = self.clamp(
            self.steering,
            self.MIN_STEERING,
            self.MAX_STEERING,
        )

    def update_battery(self):
        if self.state != self.STATE_RUNNING or self.battery <= 0.0:
            return

        speed_factor = self.speed / self.MAX_SPEED
        drain_per_second = 0.005 + (0.005 * speed_factor)
        self.battery = self.clamp(
            self.battery - (drain_per_second * self.timer_period),
            0.0,
            100.0,
        )

        if self.battery <= 0.0 and not self.battery_empty_event_sent:
            self.battery_empty_event_sent = True
            self.target_speed = 0.0
            self.target_steering = 0.0
            self.stop_requested = True
            self.publish_event('Battery empty; vehicle stopping')

    def update_vehicle(self):
        self.update_battery()
        self.update_speed()
        self.update_steering()

        if self.stop_requested and self.speed <= 0.01:
            self.finish_stop()

        self.publish_telemetry()


def main(args=None):
    rclpy.init(args=args)
    node = SimulatedVehicle()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Simulated vehicle stopped by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
