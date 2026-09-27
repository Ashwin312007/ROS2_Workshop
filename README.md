# ROS 2 Workshop: From Nodes to Teleoperated Mobile Robots

A progressive, multi-stage hands-on ROS 2 workshop designed for **ROS 2 Jazzy Jalisco** (Ubuntu 24.04 LTS / WSL2). This repository guides learners step-by-step from core node communication to building, parameterizing, and teleoperating a 4-wheeled mobile robot directly in **RViz2** without heavy simulator overhead.

---

## 📁 Repository Structure

```text
E:\ROS2 Workshop\
├── README.md
└── src/
    ├── 01_talker_listener/              # Stage 1: Basic ROS 2 Pub/Sub
    │   ├── package.xml                  # ament_python package manifest
    │   ├── setup.py & setup.cfg         # Python package build scripts
    │   ├── resource/talker_listener     # ament resource marker
    │   ├── talker_listener/
    │   │   ├── __init__.py
    │   │   ├── talker.py                # String publisher on /chatter at 2 Hz
    │   │   └── listener.py              # Subscriber logging messages from /chatter
    │   └── launch/
    │       └── talker_listener.launch.py# Launch file running both nodes
    │
    ├── 02_four_wheeled_robot_urdf/      # Stage 2: Pure XML Static URDF
    │   ├── package.xml                  # ament_cmake package manifest
    │   ├── CMakeLists.txt               # Installs urdf, launch, rviz
    │   ├── urdf/
    │   │   └── four_wheeled_robot.urdf  # Self-contained static URDF robot model
    │   ├── launch/
    │   │   └── view_robot.launch.py     # Launches robot_state_publisher, joint GUI, RViz2
    │   └── rviz/
    │       └── view_robot.rviz          # Config with fixed frame: base_footprint
    │
    ├── 03_four_wheeled_robot_xacro/     # Stage 3: Modular, Parameterized Xacro
    │   ├── package.xml
    │   ├── CMakeLists.txt
    │   ├── urdf/
    │   │   ├── properties.xacro         # Dimensions, masses, and inertia macros
    │   │   ├── materials.xacro          # Pure RViz color materials
    │   │   ├── chassis.xacro            # base_footprint and base_link definition
    │   │   ├── wheel.xacro              # Reusable continuous wheel macro
    │   │   └── robot.urdf.xacro         # Top-level assembly
    │   ├── launch/
    │   │   └── view_robot.launch.py     # Launches xacro conversion, joint GUI, RViz2
    │   └── rviz/
    │       └── view_robot.rviz          # Config with fixed frame: base_footprint
    │
    └── 04_four_wheeled_robot_teleop/    # Stage 4: Differential Drive Teleop & Simulation
        ├── package.xml
        ├── CMakeLists.txt
        ├── scripts/
        │   └── diff_drive_sim.py        # Odometry, TF (odom->base_footprint), joint states
        ├── urdf/                        # Complete modular Xacro model
        ├── launch/
        │   └── view_robot.launch.py     # Launches robot state publisher, sim node, RViz2
        └── rviz/
            └── view_robot.rviz          # Config with fixed frame: odom & Odometry trail
```

---

## ⚙️ Robot Kinematic & Physical Specifications

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Chassis Dimensions** | `0.5m x 0.3m x 0.15m` | Length x Width x Height of `base_link` box |
| **Chassis Mass** | `5.0 kg` | Mass of robot main body |
| **Chassis Elevation** | `0.10 m` | Z-offset from `base_footprint` to `base_link` |
| **Wheel Radius** | `0.08 m` | Outer radius of each cylinder wheel |
| **Wheel Width** | `0.05 m` | Cylinder thickness along Y-axis |
| **Wheel Mass** | `0.5 kg` | Mass per wheel (4 wheels total = 2.0 kg) |
| **Wheelbase** | `0.30 m` | Distance between front and rear axles (`2 * 0.15m`) |
| **Track Width** | `0.37 m` | Distance between left and right wheels (`2 * 0.185m`) |
| **Wheel Joint Type** | `continuous` | Rotation around local Y-axis (`0 1 0`) |

### Inertia Formulations
- **Box Inertia** (`base_link`):
  $$I_{xx} = \frac{m}{12}(y^2 + z^2) = 0.046875, \quad I_{yy} = \frac{m}{12}(x^2 + z^2) = 0.113542, \quad I_{zz} = \frac{m}{12}(x^2 + y^2) = 0.141667$$
- **Cylinder Inertia** (wheels aligned with rotation axis $Y$):
  $$I_{xx} = I_{zz} = \frac{m}{12}(3r^2 + h^2) = 0.000904, \quad I_{yy} = \frac{m}{2}r^2 = 0.001600$$

---

## 🛠️ Prerequisites & Installation

On **Ubuntu 24.04 LTS** (or Windows WSL2 with WSLg enabled):

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-rviz2 \
  ros-jazzy-xacro \
  ros-jazzy-urdf \
  ros-jazzy-teleop-twist-keyboard
```

---

## 🚀 Building the Workspace

From the workspace root directory:

```bash
cd "/mnt/e/ROS2 Workshop"

# Source ROS 2 underlay
source /opt/ros/jazzy/setup.bash

# Build all packages
colcon build --symlink-install

# Or build an individual package:
# colcon build --symlink-install --packages-select talker_listener
# colcon build --symlink-install --packages-select four_wheeled_robot_urdf
# colcon build --symlink-install --packages-select four_wheeled_robot_xacro
# colcon build --symlink-install --packages-select four_wheeled_robot_teleop

# Source workspace overlay
source install/setup.bash
```

---

## 📖 Module Walkthrough & Execution

### 1️⃣ Module 1: Talker / Listener (`01_talker_listener`)
Demonstrates minimal Python publisher-subscriber architecture in ROS 2.
- **Publisher (`talker.py`)**: Emits `std_msgs/String` on topic `/chatter` at 2 Hz (`timer_period = 0.5s`).
- **Subscriber (`listener.py`)**: Subscribes to `/chatter` and logs received messages.

**Running individual nodes:**
```bash
# Terminal 1: Run talker
ros2 run talker_listener talker

# Terminal 2: Run listener
ros2 run talker_listener listener
```

**Running via launch file:**
```bash
ros2 launch talker_listener talker_listener.launch.py
```

---

### 2️⃣ Module 2: Pure XML Static URDF (`02_four_wheeled_robot_urdf`)
Demonstrates how raw Unified Robot Description Format (URDF) XML files are structured without templating.
- Contains the static `four_wheeled_robot.urdf` with all links, joints, materials, visual, collision, and inertia tags.
- Launches `robot_state_publisher`, `joint_state_publisher_gui`, and `rviz2`.
- Allows manual joint rotation via GUI sliders in RViz2 (`Fixed Frame: base_footprint`).

**Running:**
```bash
ros2 launch four_wheeled_robot_urdf view_robot.launch.py
```

---

### 3️⃣ Module 3: Modular Xacro Architecture (`03_four_wheeled_robot_xacro`)
Refactors the monolithic URDF into reusable, parameterized XML macros:
- **`properties.xacro`**: Central location for robot dimensions and automatic inertia computation macros.
- **`materials.xacro`**: Clean, modular color definitions.
- **`chassis.xacro`**: `base_footprint` and `base_link` definitions.
- **`wheel.xacro`**: Reusable macro defining wheel joint, collision, visual, and cylinder inertia.
- **`robot.urdf.xacro`**: Top-level assembly instantiating 4 wheel macros with offsets.
- **Launch file**: Evaluates the Xacro file on-the-fly using `Command(['xacro ', xacro_file])`.

**Running:**
```bash
ros2 launch four_wheeled_robot_xacro view_robot.launch.py
```

---

### 4️⃣ Module 4: Differential Drive Simulation & Teleop (`04_four_wheeled_robot_teleop`)
Simulates planar robot motion and differential drive kinematics in real time without external physics engines:
- **`diff_drive_sim.py`**:
  - Subscribes to `/cmd_vel` (`geometry_msgs/Twist`).
  - Computes wheel angular velocities from linear velocity ($v$) and angular velocity ($\omega$):
    $$v_L = v - \frac{\omega \cdot W}{2}, \quad v_R = v + \frac{\omega \cdot W}{2}$$
  - Publishes wheel joint positions and velocities on `/joint_states` to spin the wheels.
  - Broadcasts TF transform: `odom -> base_footprint`.
  - Publishes `/odom` (`nav_msgs/Odometry`).
  - Built-in safety watchdog stops the robot if no keypress is received for >0.5 seconds.
- **RViz2**: Displays the robot navigating across the `odom` world frame, showing its odometry trajectory.

**Running the simulation & RViz2:**
```bash
ros2 launch four_wheeled_robot_teleop view_robot.launch.py
```

**Running keyboard teleoperation (in another terminal):**
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
*Use keys `i` (forward), `,` (backward), `j` / `l` (turn left / right), `k` (stop).*

---

## 🖥️ Graphical Troubleshooting (WSL2 / WSLg)

If RViz2 displays a blank black window or crashes with OpenGL errors under WSL2:

```bash
# Force Mesa software rasterizer (bypasses Windows driver OpenGL issues)
export LIBGL_ALWAYS_SOFTWARE=1

# Override OpenGL core profile
export MESA_GL_VERSION_OVERRIDE=3.3

# Verify display and Wayland environment variables
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0
```

---

## 📄 License
This project is licensed under the Apache 2.0 License.
