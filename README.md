# ROS 2 + React Simulated SDC Dashboard

A beginner-friendly **React + ROS 2 Humble** project that demonstrates a real
browser-to-ROS topic flow. The dashboard controls an authoritative simulated
self-driving car, displays live telemetry and ROS events, and records every
telemetry value to CSV. Everything runs in Docker; no local ROS installation is
required.

## Features

- React connects to ROS 2 through **roslibjs**, **rosbridge**, and WebSockets.
- ROS-confirmed states: `IDLE`, `RUNNING`, `STOPPED`, and `EMERGENCY_STOP`.
- Start, stop, accelerate, brake, steering, emergency-stop, and reset controls.
- Smooth ROS-generated speed and steering values—React does not fake telemetry.
- Simulated temperature and slowly decreasing vehicle battery.
- Live ROS event log retaining the latest 50 received events.
- Start, stop, and reset controls for an all-telemetry CSV recorder.
- Docker Desktop and GitHub Codespaces one-command startup paths.

## Architecture

```text
React dashboard
  │ publish commands / subscribe to telemetry
  ▼
roslibjs ── WebSocket /rosbridge ──► rosbridge_server
                                          │
                                          ▼
                                    ROS 2 topic graph
                                      ├─ button_listener
                                      ├─ temperature_publisher
                                      ├─ simulated_vehicle
                                      └─ temperature_recorder ──► CSV
```

Vehicle controls follow this complete path:

```text
React button → /sdc/command → simulated_vehicle → status + telemetry + events → React
```

The displayed vehicle state is never guessed from a local click. It always
comes back from ROS on `/sdc/status` after validation.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with the
  Linux engine running
- Git
- VS Code (optional)

No local Node.js or ROS 2 installation is required for the Docker workflow.

## Run locally with Docker

### Windows PowerShell

```powershell
git clone <your-repo-url> ROS_ASSIGNMENT
cd ROS_ASSIGNMENT
.\start.bat
```

### Linux or macOS

```bash
git clone <your-repo-url> ROS_ASSIGNMENT
cd ROS_ASSIGNMENT
chmod +x start.sh
./start.sh
```

The equivalent direct command on every platform is:

```bash
docker compose up --build
```

The first run takes several minutes while Docker downloads ROS 2 and installs
dependencies. Keep the terminal open, then visit:

```text
http://localhost:5173
```

Stop the project with `Ctrl+C`, followed by:

```bash
docker compose down
```

## GitHub Codespaces

1. Fork the repository.
2. Select **Code → Codespaces → Create codespace on main**.
3. Wait for the post-create build to finish.
4. Open forwarded port **5173**.

`.devcontainer/start-ros.sh` automatically starts rosbridge and all four demo
nodes. The GUI connects through the same-origin `/rosbridge` proxy, so port
9090 does not need to be made public.

Codespaces logs are stored under `/tmp/ros-logs/`:

```bash
tail -f /tmp/ros-logs/simulated_vehicle.log
tail -f /tmp/ros-logs/temperature_recorder.log
tail -f /tmp/ros-logs/button_listener.log
```

## Dashboard workflow

1. Wait for **Connected to ROS 2** and the ROS-confirmed `IDLE` state.
2. Click **Start vehicle**; ROS validates it and publishes `RUNNING`.
3. Click **Accelerate** one or more times. Speed smoothly approaches the target.
4. Use steering and braking controls and observe ROS telemetry and events.
5. Click **Emergency stop** to lock normal controls and brake rapidly.
6. Click **Reset vehicle** to return to `IDLE`.
7. Start recording to save temperature and all vehicle telemetry to CSV.

## Topics

| Topic | Type | Direction | Purpose |
|-------|------|-----------|---------|
| `/button_press` | `std_msgs/msg/String` | React → ROS | Original test/control-event example. |
| `/sensor/temperature` | `std_msgs/msg/Float32` | ROS → React/recorder | Simulated temperature at 4 Hz. |
| `/recorder/command` | `std_msgs/msg/String` | React → ROS | `start`, `stop`, or `reset`. |
| `/recorder/status` | `std_msgs/msg/String` | ROS → React | Recorder state and row count. |
| `/sdc/command` | `std_msgs/msg/String` | React → ROS | Exact vehicle commands. |
| `/sdc/status` | `std_msgs/msg/String` | ROS → React/recorder | Authoritative vehicle state. |
| `/sdc/speed` | `std_msgs/msg/Float32` | ROS → React/recorder | Speed in km/h. |
| `/sdc/steering` | `std_msgs/msg/Float32` | ROS → React/recorder | Steering angle in degrees. |
| `/sdc/battery` | `std_msgs/msg/Float32` | ROS → React/recorder | Battery percentage. |
| `/sdc/events` | `std_msgs/msg/String` | ROS → React | Human-readable vehicle/recorder events. |

The Python constants are defined in
`ros2_ws/src/gui_interface/gui_interface/topics.py`. The JavaScript mirror is
`web_gui/src/services/rosTopics.js`. See
[`ros2_ws/src/TOPICS.md`](ros2_ws/src/TOPICS.md) for the full topic contract.

## Vehicle commands and states

React publishes these exact strings to `/sdc/command`:

| Command | Behaviour |
|---------|-----------|
| `START_VEHICLE` | Allowed from `IDLE` or `STOPPED`; enters `RUNNING`. |
| `STOP_VEHICLE` | Smoothly reaches zero, centers steering, then enters `STOPPED`. |
| `ACCELERATE` | Adds 10 km/h to the target, up to 80 km/h. |
| `BRAKE` | Removes 10 km/h from the target, down to zero. |
| `STEER_LEFT` | Moves the target left by 10°, limited to -30°. |
| `STEER_RIGHT` | Moves the target right by 10°, limited to +30°. |
| `CENTER_STEERING` | Smoothly returns steering to 0°. |
| `EMERGENCY_STOP` | Enters `EMERGENCY_STOP`, locks controls, and rapidly brakes. |
| `RESET_VEHICLE` | Returns to `IDLE` with zero speed and centered steering. |

The battery remains between 0% and 100% and drains slowly only while running.
If it reaches zero, the vehicle targets zero speed and stops. Reset preserves
the battery value.

## Telemetry recording

The recorder writes four snapshots per second only while recording is active:

```csv
timestamp,temperature,speed,steering,battery,vehicle_status
2026-07-13T16:30:21.125+00:00,22.47,18.6,-4.5,99.98,RUNNING
```

Output path:

```text
ros2_ws/data/temperature_readings.csv
```

- **Start recording:** opens the CSV and begins appending snapshots.
- **Stop recording:** flushes and closes the file without deleting rows.
- **Reset CSV:** safely recreates the header; active recording continues.

Open it on Windows:

```powershell
notepad .\ros2_ws\data\temperature_readings.csv
Get-Content .\ros2_ws\data\temperature_readings.csv -Wait
```

Open or follow it on Linux/macOS:

```bash
tail -f ros2_ws/data/temperature_readings.csv
```

## Inspect ROS manually

Enter the running ROS container:

```bash
docker exec -it ros2_react_starter_ros bash
source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash
```

Inspect nodes and topics:

```bash
ros2 node list
ros2 topic list
ros2 topic echo /sdc/status
ros2 topic echo /sdc/speed
ros2 topic echo /sdc/steering
ros2 topic echo /sdc/battery
ros2 topic echo /sdc/events
ros2 topic echo /recorder/status
```

Expected nodes include:

```text
/button_listener_node
/temperature_publisher_node
/temperature_recorder_node
/simulated_vehicle_node
/rosbridge_websocket
```

## Publish test commands manually

Run these inside the sourced ROS container:

```bash
ros2 topic pub --once /sdc/command std_msgs/msg/String "{data: 'START_VEHICLE'}"
ros2 topic pub --once /sdc/command std_msgs/msg/String "{data: 'ACCELERATE'}"
ros2 topic pub --once /sdc/command std_msgs/msg/String "{data: 'EMERGENCY_STOP'}"
ros2 topic pub --once /sdc/command std_msgs/msg/String "{data: 'RESET_VEHICLE'}"
```

Recorder tests:

```bash
ros2 topic pub --once /recorder/command std_msgs/msg/String "{data: 'start'}"
ros2 topic pub --once /recorder/command std_msgs/msg/String "{data: 'stop'}"
ros2 topic pub --once /recorder/command std_msgs/msg/String "{data: 'reset'}"
```

## Rebuild after editing

Docker rebuild and restart:

```bash
docker compose down
docker compose up --build
```

Rebuild only the ROS workspace inside the running container:

```bash
docker exec -it ros2_react_starter_ros bash
cd /ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Adding a new `console_scripts` entry requires a colcon rebuild. Editing an
existing Python node under `--symlink-install` requires only a node restart.

## View logs

```bash
docker compose ps
docker compose logs ros2 --tail 200
docker compose logs web --tail 100
docker compose logs -f ros2
```

## Verification checklist

- [ ] Docker starts both containers and React opens on port 5173.
- [ ] The GUI connects and shows initial state `IDLE`.
- [ ] The original test message reaches `button_listener`.
- [ ] Temperature updates approximately four times per second.
- [ ] Start changes state to `RUNNING` through `/sdc/status`.
- [ ] Accelerate and brake change speed smoothly within 0–80 km/h.
- [ ] Steering changes smoothly within -30° to +30°.
- [ ] Battery decreases slowly while the vehicle is running.
- [ ] Emergency stop locks normal controls and rapidly reduces speed.
- [ ] Reset returns the system to `IDLE`.
- [ ] Vehicle and recorder events appear in the live event log.
- [ ] Start recording writes all six CSV columns.
- [ ] Stop recording stops adding rows.
- [ ] Reset CSV recreates only its header and resets the row count.
- [ ] Browser refresh reconnects without duplicate event messages.
- [ ] Docker restart brings every node back automatically.

## Troubleshooting

### Docker engine is unavailable

Start Docker Desktop and wait until its Linux engine is running. Confirm both
Client and Server sections appear:

```powershell
docker version
docker info
```

### GUI shows Disconnected

The GUI automatically retries every two seconds. The first ROS build can take
several minutes. Check:

```bash
docker compose ps
docker compose logs ros2 --tail 200
```

`ws://localhost:5173/rosbridge` is expected: Vite proxies that same-origin path
to `ws://ros2:9090` inside Docker.

### Port already in use

Stop the conflicting process or change the relevant host mapping in
`docker-compose.yml`. If changing the rosbridge target, also update
`VITE_ROSBRIDGE_PROXY_TARGET`.

## Project structure

```text
ROS_ASSIGNMENT/
├── .devcontainer/                 # Codespaces lifecycle scripts
├── docker/Dockerfile              # ROS 2 Humble + rosbridge image
├── ros2_ws/
│   ├── data/                      # generated telemetry CSV
│   └── src/
│       ├── gui_interface/         # shared Python topic constants
│       ├── button_listener_pkg/   # original GUI → ROS example
│       └── student_nodes_pkg/
│           ├── temperature_publisher.py
│           ├── temperature_recorder.py
│           └── simulated_vehicle_node.py
├── web_gui/src/
│   ├── components/                # dashboard UI sections
│   ├── hooks/useRosBridge.js      # one connection + topic lifecycle
│   ├── services/rosTopics.js      # JavaScript topic contract
│   ├── App.jsx
│   └── App.css
├── docker-compose.yml
├── start.sh
└── start.bat
```

## License

MIT — free to use for coursework and learning.
