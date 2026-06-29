# Topics Reference

This file is the **single human-readable list of every topic** in the
workspace. Whenever you create a new topic in a node, add a row here so other
students (and the React GUI author) know it exists.

> Why this matters: `rosbridge_server` automatically exposes **every** ROS 2
> topic to the browser. So any topic listed below is reachable from the React
> GUI just by subscribing/publishing to the same name + message type. There is
> no extra wiring — this table *is* the contract between ROS 2 and the GUI.

## How a topic flows

```
React GUI  <--roslibjs/WebSocket-->  rosbridge_server (:9090)  <-->  ROS 2 topics  <-->  your nodes
```

- **GUI -> ROS:** the GUI publishes, a node subscribes (e.g. the button example).
- **ROS -> GUI:** a node publishes, the GUI subscribes (e.g. the publisher example).

## Current topics

| Topic | Message type | Published by | Subscribed by | Notes |
|-------|--------------|--------------|---------------|-------|
| `/button_press` | `std_msgs/String` | React GUI (`web_gui/src/App.jsx`) | `button_listener` (`button_listener_pkg`) | Sent on every button click. |
| `/robot_status` | `std_msgs/String` | `example_publisher` (`student_nodes_pkg`) | React GUI (optional) | Demo: a node publishing up to the GUI once per second. |

## Adding a new topic — checklist

1. **Define the name once** in
   `ros2_ws/src/gui_interface/gui_interface/topics.py`
   (e.g. `TOPIC_MY_THING = '/my_thing'`).
2. **Import and use it** in your node:
   `from gui_interface.topics import TOPIC_MY_THING`.
3. **Add a row** to the table above (topic, message type, who publishes/subscribes).
4. **Mirror the string** in the React GUI (`web_gui/src/App.jsx`) — JavaScript
   cannot import the Python file, so the name must be copied there too.
5. **Rebuild**: run `colcon build` inside `ros2_ws/`.
