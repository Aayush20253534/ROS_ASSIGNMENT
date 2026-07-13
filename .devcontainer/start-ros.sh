#!/usr/bin/env bash
#
# start-ros.sh - starts rosbridge and all three demo nodes automatically.
#
# Wired to "postStartCommand" in devcontainer.json so that every time the
# Codespace / Dev Container starts, rosbridge is already listening on port 9090
# and the React GUI connects with zero manual steps. It runs the processes in
# the BACKGROUND (nohup ... &) and returns immediately so container startup is
# not blocked.
#
# It is idempotent: if rosbridge / demo nodes are already running it does
# not start a second copy, so re-running (or also using the "Run ROS" task) is
# safe.

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> [start-ros] Sourcing ROS 2 Humble"
source /opt/ros/humble/setup.bash

cd "${REPO_ROOT}/ros2_ws"

# Build the workspace if it has not been built yet (post-create usually does
# this, but this guard makes startup robust after a fresh rebuild).
if [ ! -f install/setup.bash ]; then
  echo "==> [start-ros] Workspace not built yet; building with colcon"
  colcon build --symlink-install
fi

# shellcheck disable=SC1091
source install/setup.bash

mkdir -p /tmp/ros-logs

# Start rosbridge (port 9090) in the background if it is not already running.
if pgrep -f rosbridge_websocket >/dev/null 2>&1; then
  echo "==> [start-ros] rosbridge already running"
else
  echo "==> [start-ros] Starting rosbridge websocket server on port 9090"
  nohup ros2 launch rosbridge_server rosbridge_websocket_launch.xml \
    > /tmp/ros-logs/rosbridge.log 2>&1 &
  # Give rosbridge a moment to come up before starting the listener.
  sleep 3
fi

# Start the button_listener node in the background if not already running.
if pgrep -f button_listener >/dev/null 2>&1; then
  echo "==> [start-ros] button_listener already running"
else
  echo "==> [start-ros] Starting button_listener node"
  nohup ros2 run button_listener_pkg button_listener \
    > /tmp/ros-logs/button_listener.log 2>&1 &
fi

# Publish fake temperature values for the GUI's live sensor card.
if pgrep -f temperature_publisher >/dev/null 2>&1; then
  echo "==> [start-ros] temperature_publisher already running"
else
  echo "==> [start-ros] Starting temperature_publisher node"
  nohup ros2 run student_nodes_pkg temperature_publisher \
    > /tmp/ros-logs/temperature_publisher.log 2>&1 &
fi

# Record temperature values to CSV when the browser sends a start command.
if pgrep -f temperature_recorder >/dev/null 2>&1; then
  echo "==> [start-ros] temperature_recorder already running"
else
  echo "==> [start-ros] Starting temperature_recorder node"
  nohup ros2 run student_nodes_pkg temperature_recorder \
    > /tmp/ros-logs/temperature_recorder.log 2>&1 &
fi

echo "==> [start-ros] Done. rosbridge + all demo nodes are running."
echo "==> [start-ros] Logs are available under /tmp/ros-logs/."
