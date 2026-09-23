# ROS 2 Workshop: 4-Wheeled Robot Description

A modular, production-ready ROS 2 package containing a four-wheeled robot defined using parameterized Xacro files, fully visualized and teleoperable directly in **RViz2** without Gazebo, Ignition, or physics engine dependencies.

Designed for **ROS 2 Jazzy Jalisco** running on **Ubuntu 24.04 LTS** inside **WSL2** (WSLg enabled).

---

## 📁 Repository Structure

```text
.
├── README.md
└── src/
    └── four_wheeled_robot_description/
        ├── CMakeLists.txt
        ├── package.xml
        ├── scripts/
        │   └── diff_drive_sim.py          # Differential drive kinematics & auto-stop simulator
        ├── launch/
        │   └── view_robot.launch.py       # Launch file for state publishers & RViz2
        ├── rviz/
        │   └── view_robot.rviz            # Pre-configured RViz display profile
        └── urdf/
            ├── properties.xacro           # Dimensional constants & inertia macros
            ├── materials.xacro            # RGBA color definitions (no Gazebo tags)
            ├── chassis.xacro              # base_footprint and base_link definition
            ├── wheel.xacro                # Parameterized continuous wheel macro
            └── robot.urdf.xacro           # Top-level robot assembly
```

---

## ⚙️ Kinematic & Physical Specifications

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Chassis Dimensions** | `0.5m x 0.3m x 0.15m` | Length x Width x Height of `base_link` box |
| **Chassis Mass** | `5.0 kg` | Mass of main robot body |
| **Chassis Elevation** | `0.10 m` | Height offset from `base_footprint` to `base_link` |
| **Wheel Radius** | `0.08 m` | Outer radius of each wheel |
| **Wheel Width** | `0.05 m` | Cylinder thickness |
| **Wheel Mass** | `0.5 kg` | Mass per wheel (4 wheels total = 2.0 kg) |
| **Wheelbase** | `0.30 m` | Longitudinal distance between front and rear axles (`2 * 0.15m`) |
| **Track Width** | `0.37 m` | Transverse distance between left and right wheels (`2 * 0.185m`) |
| **Joint Type** | `continuous` | Unbounded rotational joint around local Y-axis (`0 1 0`) |

### Inertial Tensor Highlights
- **Box Inertia**: Calculated dynamically using standard uniform box formulas:
  $$I_{xx} = \frac{m}{12}(y^2 + z^2), \quad I_{yy} = \frac{m}{12}(x^2 + z^2), \quad I_{zz} = \frac{m}{12}(x^2 + y^2)$$
- **Cylinder Inertia**: Correctly aligned to the cylinder's rotational axis (Y-axis):
  $$I_{xx} = I_{zz} = \frac{m}{12}(3r^2 + h^2), \quad I_{yy} = \frac{m}{2}r^2$$

---

## 🧩 Modular Xacro Architecture

- **`properties.xacro`**: Contains all geometric parameters, physical masses, and reusable inertia macros.
- **`materials.xacro`**: Pure RViz RGBA material colors (`blue`, `black`, `white`, `grey`, `orange`). Excludes simulator-specific plugins.
- **`chassis.xacro`**: Instantiates a zero-mass `base_footprint` dummy root link at ground contact level and connects to `base_link` via a fixed joint.
- **`wheel.xacro`**: Reusable macro generating the continuous joint, collision, visual, and inertial parameters for any wheel instance.
- **`robot.urdf.xacro`**: Main entry point assembling `chassis` with `front_left_wheel`, `front_right_wheel`, `rear_left_wheel`, and `rear_right_wheel`.

---

## 🚀 Getting Started (WSL2 / Ubuntu 24.04)

### 1. Prerequisites
Ensure ROS 2 Jazzy and the required description / visualization packages are installed:

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-rviz2 \
  ros-jazzy-xacro \
  ros-jazzy-urdf
```

### 2. Build the Package
Navigate to the root of the workspace (e.g., `/mnt/e/ROS2 Workshop`):

```bash
cd "/mnt/e/ROS2 Workshop"

# Source ROS 2 Jazzy underlay
source /opt/ros/jazzy/setup.bash

# Build using colcon
colcon build --symlink-install --packages-select four_wheeled_robot_description

# Source workspace overlay
source install/setup.bash
```

### 3. Launch Visualization & Teleoperation
Start the full stack (robot state publisher, differential drive simulator, and RViz2):

```bash
ros2 launch four_wheeled_robot_description view_robot.launch.py
```

In a separate terminal, launch the keyboard teleoperation node:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

- **Hold to drive**: Hold keys (`i` forward, `,` backward, `j`/`l` turn).
- **Auto-stop watchdog**: If no key is pressed for >0.5s, the robot automatically stops.
- To use the manual joint slider GUI instead of teleoperation:
```bash
ros2 launch four_wheeled_robot_description view_robot.launch.py teleop:=false gui:=true
```

---

## 🖥️ WSL2 / WSLg Graphical Troubleshooting

If RViz2 fails to launch, displays a black viewport, or throws OpenGL errors in WSL2, configure software rendering or OpenGL profile overrides:

```bash
# Force Mesa software rasterizer (resolves OpenGL driver mismatches)
export LIBGL_ALWAYS_SOFTWARE=1

# Override OpenGL core profile version
export MESA_GL_VERSION_OVERRIDE=3.3

# Confirm WSLg Wayland/X11 sockets
export WAYLAND_DISPLAY=wayland-0
export DISPLAY=:0
```

---

## 📄 License
This project is licensed under the Apache 2.0 License.
