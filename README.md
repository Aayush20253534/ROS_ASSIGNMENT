# ros2-react-starter

A beginner-friendly starter project that connects a **React web GUI** to a
**ROS 2 Humble** node. Click a button in the browser, and a ROS 2 Python node
receives that event through a ROS topic — all running inside Docker, with
**no local ROS installation required**.

## What this starter demonstrates

- How a web app can talk to ROS 2 using **rosbridge** + **roslibjs** over WebSockets.
- How to publish a ROS 2 message (`std_msgs/String`) from JavaScript.
- How a ROS 2 Python node (`rclpy`) subscribes to a topic and reacts to messages.
- How Docker Compose can package ROS 2 + a web dev server so students run **one command**.

## Architecture

```
  ┌──────────────┐   click    ┌──────────────┐   WebSocket   ┌────────────────────┐
  │  React GUI   │ ─────────► │   roslibjs   │ ────────────► │  rosbridge_server  │
  │  (browser)   │            │ (in browser) │   port 9090   │   (ROS 2 container) │
  └──────────────┘            └──────────────┘               └─────────┬──────────┘
                                                                        │
                                                            ROS 2 topic │ /button_press
                                                            std_msgs/   │ String
                                                                String  ▼
                                                              ┌────────────────────┐
                                                              │  button_listener   │
                                                              │  Python ROS 2 node │
                                                              │  (logs the message)│
                                                              └────────────────────┘
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

# 4. Click the "Send Message to ROS" button.
```

> The **first run takes several minutes** because Docker downloads the ROS 2
> image and installs dependencies. Later runs are much faster.

## Expected output

- In the **browser**, the status badge shows **"Connected to ROS 2"** and the
  click counter increments each time you press the button.
- In the **terminal** running `docker compose up`, the ROS 2 node logs:

```
ros2_react_starter_ros  | [INFO] [button_listener_node]: Button listener started
ros2_react_starter_ros  | [INFO] [button_listener_node]: Waiting for messages on /button_press
ros2_react_starter_ros  | [INFO] [button_listener_node]: Received: "Button clicked from React GUI. Count = 1"
```

## Understanding the topic

- **`/button_press`** — the ROS 2 *topic* (a named channel). The React app
  **publishes** to it; the Python node **subscribes** to it.
- **`std_msgs/String`** — the *message type*. It carries one text field called
  `data`. Both the React side and the Python side must agree on this type, or
  they cannot communicate.

## Useful debugging commands

Open a shell inside the ROS 2 container and inspect topics live:

```bash
# Get a bash shell inside the running ROS 2 container
docker exec -it ros2_react_starter_ros bash

# Inside the container, make ROS 2 commands available
source /opt/ros/humble/setup.bash

# List all active topics (you should see /button_press)
ros2 topic list

# Print messages as they arrive on /button_press
ros2 topic echo /button_press
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

## Student extension tasks

Once the basic demo works, try extending it. Each level builds on the previous one.

### Level 1 — More buttons
- Add **Start Recording**, **Stop Recording**, and **Reset** buttons to the React GUI.
- Publish a different message string for each, and watch them appear in the node logs.

### Level 2 — A fake sensor node
- Create a new ROS 2 node that **publishes** a fake temperature value to
  `/sensor/temperature` (use `std_msgs/Float32`) a few times per second.

### Level 3 — Live sensor display
- In the React app, **subscribe** to `/sensor/temperature` with roslibjs and
  display the live value on screen.

### Level 4 — Data recorder
- Create a **recorder node** that subscribes to `/sensor/temperature` and saves
  each reading (with a timestamp) to a CSV file.

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
  and update `VITE_ROSBRIDGE_URL` to match.

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
│   └── src/
│       ├── README.md               # guide: file roles + how to add nodes
│       ├── TOPICS.md               # central list of every topic
│       ├── gui_interface/          # shared topic-name definitions
│       ├── button_listener_pkg/    # provided example node (GUI -> ROS)
│       └── student_nodes_pkg/      # students add their own nodes here
├── web_gui/                        # React + Vite app
├── docker-compose.yml              # Wires the ros2 + web containers together
├── start.sh / start.bat            # One-command startup scripts
└── README.md
```

## License

MIT — free to use for coursework and learning.
