#!/usr/bin/env python3
"""
button_listener.py  --  PROVIDED EXAMPLE NODE

A minimal ROS 2 node that listens for button-press events coming from the
React GUI. The data flow is:

    React button click
      -> roslibjs (WebSocket)
      -> rosbridge_server (port 9090)
      -> ROS 2 topic /button_press  (message type: std_msgs/String)
      -> THIS node, which logs every message it receives.

For second-year students: a "node" is just a program that talks to other
programs over named channels called "topics". Here we SUBSCRIBE to the
button-press topic, meaning ROS 2 calls our callback whenever a new message
is published to it.
"""

import rclpy
from rclpy.node import Node

# std_msgs/String is the simplest standard message: it carries one text field
# called `data`. The React GUI publishes the same type, which is why both sides
# understand each other.
from std_msgs.msg import String

# Topic names live in ONE shared place (the gui_interface package) so the node
# and the GUI never disagree about spelling. See ros2_ws/src/gui_interface.
from gui_interface.topics import TOPIC_BUTTON_PRESS


class ButtonListener(Node):
    """A ROS 2 node that subscribes to the button-press topic and logs each message."""

    def __init__(self):
        # Give the node a name. This is how it appears in `ros2 node list`.
        super().__init__('button_listener_node')

        # Create the subscription:
        #   - String                -> message type we expect
        #   - TOPIC_BUTTON_PRESS     -> the topic name (shared with the React side)
        #   - self.listener_callback -> function called for every message
        #   - 10                     -> queue size (how many messages to buffer)
        self.subscription = self.create_subscription(
            String,
            TOPIC_BUTTON_PRESS,
            self.listener_callback,
            10,
        )

        # Clear startup logs so students immediately see the node is alive.
        self.get_logger().info('Button listener started')
        self.get_logger().info(f'Waiting for messages on {TOPIC_BUTTON_PRESS}')

    def listener_callback(self, msg):
        """Called automatically whenever a message arrives on the button-press topic."""
        self.get_logger().info(f'Received: "{msg.data}"')


def main(args=None):
    # Boilerplate ROS 2 startup/shutdown pattern.
    rclpy.init(args=args)
    node = ButtonListener()
    try:
        # spin() blocks here and processes incoming messages until Ctrl+C.
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
