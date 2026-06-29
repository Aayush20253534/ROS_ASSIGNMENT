# Base image: ROS 2 Humble desktop (includes rclpy, ros2 CLI tools, etc.)
FROM osrf/ros:humble-desktop

# Avoid interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Install the tools we need:
# - python3-pip                         -> Python package manager
# - python3-colcon-common-extensions    -> colcon build system for ROS 2 workspaces
# - ros-humble-rosbridge-server         -> the WebSocket <-> ROS 2 bridge (port 9090)
# - ros-humble-std-msgs                 -> standard message types (std_msgs/String)
# - git, nano, curl                     -> handy developer tools
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-rosbridge-server \
    ros-humble-std-msgs \
    git \
    nano \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Automatically source the ROS 2 environment every time a bash shell opens.
# This means students who `docker exec` into the container can immediately
# run `ros2 topic list` without manually sourcing anything.
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

# All ROS 2 workspace work happens here. This folder is mounted from the host
# (see docker-compose.yml), so code changes on the host appear instantly.
WORKDIR /ros2_ws
