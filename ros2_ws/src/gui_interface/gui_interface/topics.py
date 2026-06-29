"""
topics.py  --  the single source of truth for topic names.

Every ROS 2 node in this workspace imports its topic names from here instead
of typing the raw string (e.g. '/button_press') in many files. If you ever
rename a topic, change it ONCE in this file and all Python nodes follow.

    from gui_interface.topics import TOPIC_BUTTON_PRESS

IMPORTANT - how this reaches the React GUI:
    rosbridge_server automatically exposes EVERY ROS 2 topic to the browser.
    So any topic you define and publish to here is instantly visible to the
    React GUI (via roslibjs) with no extra wiring. The only catch is that the
    JavaScript side cannot import this Python file, so when you add a topic
    here you must copy the SAME string into the React code (and into TOPICS.md
    so everyone can see the full list).

Convention for second-year students:
    - Topic names start with '/'.
    - Use lower_snake_case.
    - Keep the constant name (UPPER_SNAKE_CASE) close to the topic name.
"""

# ---------------------------------------------------------------------------
# Topics used by the provided example (button_listener_pkg + the React GUI).
# ---------------------------------------------------------------------------

# React button click -> this topic -> button_listener node.
# Message type: std_msgs/String
TOPIC_BUTTON_PRESS = '/button_press'


# ---------------------------------------------------------------------------
# Add YOUR topics below. Example (uncomment and adapt):
#
#   # A node publishes robot status text; the GUI subscribes to show it.
#   # Message type: std_msgs/String
#   TOPIC_ROBOT_STATUS = '/robot_status'
#
# After adding one here, remember to:
#   1. document it in ros2_ws/src/TOPICS.md
#   2. use the SAME string in the React GUI (web_gui/src/App.jsx)
# ---------------------------------------------------------------------------
