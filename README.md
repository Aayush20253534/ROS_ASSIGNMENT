# ros2-react-starter

A beginner-friendly project that connects a **React web GUI** to **ROS 2
Humble**. Send commands from the browser, watch a live fake sensor, and record
its readings to CSV — all inside Docker, with **no local ROS installation
required**.

## What this starter demonstrates

- How a web app can talk to ROS 2 using **rosbridge** + **roslibjs** over WebSockets.
- How to publish a ROS 2 message (`std_msgs/String`) from JavaScript.
- How a ROS 2 Python node (`rclpy`) subscribes to a topic and reacts to messages.
- How a Python node publishes `std_msgs/Float32` data for a live React display.
- How browser commands can start, stop, and reset a ROS-side CSV recorder.
- How Docker Compose can package ROS 2 + a web dev server so students run **one command**.

## Architecture

```text
React GUI  <-- WebSocket / roslibjs -->  rosbridge_server  <-->  ROS 2
   │                                                      ├─ button_listener
   │                                                      ├─ temperature_publisher
   └─ commands + live temperature + recorder status       └─ temperature_recorder → CSV
```

## Prerequisites

- **Docker Desktop** (required) — installs Docker Engine + Docker Compose.
  - Download: https://www.docker.com/products/docker-desktop/
- **Git** — to clone the repository.
- **VS Code** (optional) — a nice editor for exploring the code.
- **No local ROS 2 install required.** Everything runs inside containers.

## How to run

```bash
# 1. Clone the repository
git clone <your-repo-url> ros2-react-starter
cd ros2-react-starter

# 2. Start everything (builds the ROS image on first run)
#    macOS / Linux:
./start.sh
#    Windows:
start.bat

# 3. Open the GUI in your browser
#    http://localhost:5173

# 4. Watch the live temperature, then try the message and recorder controls.
```

> The **first run takes several minutes** because Docker downloads the ROS 2
> image and installs dependencies. Later runs are much faster.

## GitHub Codespaces

Prefer to run everything in the cloud? This repo ships a ready-to-use
[GitHub Codespaces](https://github.com/features/codespaces) setup. **No Docker
Desktop, no WSL, and no local ROS installation required.**

1. On GitHub, click **Code → Codespaces → Create codespace on main**.
2. **Wait for setup to finish.** On first launch the container builds, ROS 2
   `ros2_ws` is compiled with colcon, and `web_gui` npm dependencies are
   installed automatically (via `.devcontainer/post-create.sh`).
3. **That's it — nothing else to start.** On every container start,
   `.devcontainer/start-ros.sh` automatically launches rosbridge (port 9090)
   and all three demo nodes in the background, while the `web` container
   serves the Vite dev server on port 5173.
4. Open the **forwarded port 5173** (the **Ports** tab, or the "Open in
   Browser" toast) to use the GUI. The status badge should already read
   **Connected to ROS 2**, and the temperature card should update live.
5. To watch the node react to your clicks, either tail the background log
   (`tail -f /tmp/ros-logs/button_listener.log`) or run the **Run ROS** task to
   see the listener live in a terminal.

> **Tip:** If the GUI shows "Disconnected", the background rosbridge may not be
> up yet — give it a few seconds and refresh, or run the **Run ROS** task
> manually. The GUI reaches rosbridge through a `/rosbridge` proxy on the same
> 5173 origin, so you do **not** need to change any port visibility.

The local Docker workflow above is unchanged — Codespaces support is purely
additive (`.devcontainer/`, `.vscode/tasks.json`, and `scripts/`).

## Expected output

- In the **browser**, the connection badge turns green, temperature updates
  about four times per second, and recorder controls become available.
- Press **Start recording**, wait a moment, then press **Stop recording**. The
  row count rises and the CSV is written to
  `ros2_ws/data/temperature_readings.csv`.
- In the **terminal** running `docker compose up`, the ROS 2 node logs:

```
ros2_react_starter_ros  | [INFO] [button_listener_node]: Button listener started
ros2_react_starter_ros  | [INFO] [button_listener_node]: Waiting for messages on /button_press
ros2_react_starter_ros  | [INFO] [temperature_publisher_node]: Fake temperature publisher started
ros2_react_starter_ros  | [INFO] [temperature_recorder_node]: Temperature recorder started (idle)
ros2_react_starter_ros  | [INFO] [button_listener_node]: Received: "Recording started from React GUI. Count = 1"
```

## Understanding the topics

- **`/button_press`** — the ROS 2 *topic* (a named channel). The React app
  **publishes** to it; the Python node **subscribes** to it.
- **`std_msgs/String`** — the *message type*. It carries one text field called
  `data`. Both the React side and the Python side must agree on this type, or
  they cannot communicate.
- **`/sensor/temperature`** — the fake sensor publishes `std_msgs/Float32`; the
  React GUI and recorder both subscribe.
- **`/recorder/command`** — React publishes `start`, `stop`, or `reset`.
- **`/recorder/status`** — the recorder publishes its state and written-row count.

## Useful debugging commands

Open a shell inside the ROS 2 container and inspect topics live:

```bash
# Get a bash shell inside the running ROS 2 container
docker exec -it ros2_react_starter_ros bash

# Inside the container, make ROS 2 commands available
source /opt/ros/humble/setup.bash

# List all active topics
ros2 topic list

# Print messages as they arrive on /button_press
ros2 topic echo /button_press

# Watch fake sensor readings
ros2 topic echo /sensor/temperature
```

## Where to add your own code

The ROS 2 workspace is split into clear packages under `ros2_ws/src/`:

```
ros2_ws/src/
├── README.md            # full guide: file roles + recipe to add nodes
├── TOPICS.md            # central list of every topic + message type
├── gui_interface/       # SHARED: all topic names defined once (topics.py)
├── button_listener_pkg/ # PROVIDED EXAMPLE: a node that listens (GUI -> ROS)
└── student_nodes_pkg/   # YOUR PACKAGE: add your own nodes here
```

Students work mainly in **`student_nodes_pkg/`**. To add a node: create a
`.py` file, register it in that package's `setup.py` under `console_scripts`,
then rebuild. See [ros2_ws/src/README.md](ros2_ws/src/README.md) for the full
step-by-step recipe (including when a rebuild is needed) and
[ros2_ws/src/TOPICS.md](ros2_ws/src/TOPICS.md) for the topic reference.

> Because rosbridge exposes **every** ROS 2 topic to the browser, any topic you
> create is automatically reachable by the React GUI — just subscribe/publish
> to the same topic name on the JavaScript side.

## Included extension levels

- **Level 1:** Start Recording, Stop Recording, and Reset CSV buttons publish
  distinct events that appear in the listener logs.
- **Level 2:** `temperature_publisher` publishes fake `Float32` readings four
  times per second.
- **Level 3:** React subscribes to the sensor topic and renders the live value.
- **Level 4:** `temperature_recorder` saves timestamped readings to CSV and is
  controlled from the browser.

For another challenge, add a second sensor, plot recent readings, or expose the
CSV through a ROS service.

## Troubleshooting

**Docker not installed**
- Install Docker Desktop from the link in Prerequisites, then restart your terminal.

**Docker daemon not running**
- You'll see: `Docker is not running. Start Docker Desktop and run this script again.`
- Open Docker Desktop, wait until it says "Running", then re-run the start script.

**React shows "Disconnected" or "Connection error"**
- The ROS 2 container may still be building (first run is slow). Wait for the
  `Button listener started` log, then refresh the browser.
- Make sure rosbridge is reachable at `ws://localhost:9090`.

**Port 9090 already in use**
- Another program (or a previous container) is using rosbridge's port.
- Stop it, or change the host port mapping in `docker-compose.yml` (e.g. `"9091:9090"`)
  and update `VITE_ROSBRIDGE_PROXY_TARGET` to match.

**Port 5173 already in use**
- The Vite dev server port is taken. Stop the other process, or change the
  mapping in `docker-compose.yml` (e.g. `"5174:5173"`).

**First run takes a long time**
- This is normal. Docker is downloading the ROS 2 Humble image and installing
  packages. Subsequent runs reuse the cached image and start quickly.

## Project structure

```
ros2-react-starter/
├── docker/Dockerfile               # ROS 2 Humble image + rosbridge + tools
├── ros2_ws/                        # ROS 2 workspace (colcon builds all packages)
│   ├── data/                       # generated temperature CSV lives here
│   └── src/
│       ├── README.md               # guide: file roles + how to add nodes
│       ├── TOPICS.md               # central list of every topic
│       ├── gui_interface/          # shared topic-name definitions
│       ├── button_listener_pkg/    # provided example node (GUI -> ROS)
│       └── student_nodes_pkg/      # fake sensor, recorder, and student nodes
├── web_gui/                        # React + Vite app
├── docker-compose.yml              # Wires the ros2 + web containers together
├── start.sh / start.bat            # One-command startup scripts
└── README.md
```

## License

MIT — free to use for coursework and learning.
