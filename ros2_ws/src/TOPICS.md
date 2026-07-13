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
| `/sensor/temperature` | `std_msgs/Float32` | `temperature_publisher` (`student_nodes_pkg`) | React GUI and `temperature_recorder` | Fake Celsius reading published at 4 Hz. |
| `/recorder/command` | `std_msgs/String` | React GUI | `temperature_recorder` | Commands: `start`, `stop`, or `reset`. |
| `/recorder/status` | `std_msgs/String` | `temperature_recorder` | React GUI | State and row count in `state:count` format. |
| `/sdc/command` | `std_msgs/String` | React GUI | `simulated_vehicle` | Exact vehicle command strings listed below. |
| `/sdc/status` | `std_msgs/String` | `simulated_vehicle` | React GUI and `temperature_recorder` | Authoritative state: `IDLE`, `RUNNING`, `STOPPED`, or `EMERGENCY_STOP`. |
| `/sdc/speed` | `std_msgs/Float32` | `simulated_vehicle` | React GUI and `temperature_recorder` | Smooth simulated speed from 0–80 km/h. |
| `/sdc/steering` | `std_msgs/Float32` | `simulated_vehicle` | React GUI and `temperature_recorder` | Smooth steering angle from -30° to +30°. |
| `/sdc/battery` | `std_msgs/Float32` | `simulated_vehicle` | React GUI and `temperature_recorder` | Battery percentage from 0–100%. |
| `/sdc/events` | `std_msgs/String` | `simulated_vehicle` and `temperature_recorder` | React GUI | Human-readable state, control, and recorder events. |

## Vehicle commands

Publish one of these exact strings to `/sdc/command`:

| Command | Effect |
|---------|--------|
| `START_VEHICLE` | Move from `IDLE` or `STOPPED` to `RUNNING`. |
| `STOP_VEHICLE` | Smoothly stop, center steering, then publish `STOPPED`. |
| `ACCELERATE` | Raise the target speed by 10 km/h, up to 80 km/h. |
| `BRAKE` | Lower the target speed by 10 km/h. |
| `STEER_LEFT` | Lower the target steering angle by 10°, down to -30°. |
| `STEER_RIGHT` | Raise the target steering angle by 10°, up to +30°. |
| `CENTER_STEERING` | Smoothly return steering to 0°. |
| `EMERGENCY_STOP` | Lock ordinary controls and brake rapidly. |
| `RESET_VEHICLE` | Return to `IDLE` with zero speed and centered steering. |

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
