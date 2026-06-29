#!/usr/bin/env python3
"""
example_publisher.py  --  STARTER TEMPLATE FOR YOUR OWN NODE

This node PUBLISHES a short text message once per second. The data flow is the
reverse of the button example:

    THIS node publishes to a topic
      -> rosbridge_server (port 9090)
      -> roslibjs (WebSocket)
      -> React GUI, which can subscribe and display the message.

KEY IDEA: rosbridge automatically exposes EVERY ROS 2 topic to the browser.
So whatever topic you publish here is immediately available to the React GUI
with no extra setup on the ROS side -- the GUI just needs to subscribe to the
same topic name and message type.

HOW TO MAKE YOUR OWN NODE FROM THIS FILE:
    1. Copy this file, e.g. to my_node.py, and rename the class + node name.
    2. Add your topic name to ros2_ws/src/gui_interface/gui_interface/topics.py
       and import it here (see TOPIC_ROBOT_STATUS below as the pattern).
    3. Register the node in setup.py under console_scripts.
    4. Document the topic in ros2_ws/src/TOPICS.md and mirror the name in the
       React GUI (web_gui/src/App.jsx).
    5. Rebuild:  colcon build   (run inside ros2_ws/)
"""

import rclpy
from rclpy.node import Node

# std_msgs/String carries a single text field called `data`.
from std_msgs.msg import String


# We publish to a brand-new topic. It is defined here directly to keep the
# example self-contained, but the RECOMMENDED pattern is to add it to
# gui_interface/topics.py and import it, exactly like button_listener does:
#
#     from gui_interface.topics import TOPIC_ROBOT_STATUS
#
# For now we use a local constant so this example runs without editing the
# shared file first.
TOPIC_ROBOT_STATUS = '/robot_status'


class ExamplePublisher(Node):
    """Publishes an incrementing status message to /robot_status once per second."""

    def __init__(self):
        super().__init__('example_publisher_node')

        # create_publisher(message_type, topic_name, queue_size)
        self.publisher = self.create_publisher(String, TOPIC_ROBOT_STATUS, 10)

        # Fire timer_callback() every 1.0 seconds.
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.count = 0

        self.get_logger().info('Example publisher started')
        self.get_logger().info(f'Publishing to {TOPIC_ROBOT_STATUS} once per second')

    def timer_callback(self):
        """Build a message and publish it. The GUI can subscribe to see it."""
        self.count += 1
        msg = String()
        msg.data = f'Hello from ROS 2. Tick = {self.count}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Published: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = ExamplePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
