# ROS 2 Quick Reference — Workspace to URDF

A condensed command reference covering the workflow used in this repository: creating a workspace, scaffolding a Python package, wiring up an executable node, running it, launching the robot model in RViz2, and debugging it when something does not work.

**Contents:** [1. Workspace](#1-create-a-ros-2-workspace) · [2. Package](#2-create-a-package) · [2b. Entry point](#2b-register-the-node-as-an-executable) · [3. Run a node](#3-run-a-node-from-the-terminal) · [4. Launch URDF](#4-launch-the-robot-model-urdf) · [5. Debugging](#5-debugging--inspection) · [Pitfalls](#common-pitfalls) · [Cheat sheet](#cheat-sheet)

> Targets **ROS 2 Jazzy Jalisco** (Ubuntu 24.04 LTS / WSL2).

---

## 📁 1. Create a ROS 2 Workspace

A workspace is just a directory with a `src/` folder inside it. `colcon` builds everything it finds there.

```bash
mkdir -p ~/ros_ws/src        # workspace root + source folder
cd ~/ros_ws
colcon build                 # build everything under src/
```

**If `colcon` is not found:**

```bash
sudo apt install ros-dev-tools
```

> On Ubuntu 24.04 the package may be named `python3-colcon-common-extensions` instead. Either provides `colcon`.

**Source the overlay** so your packages become visible to `ros2`:

```bash
cd install
source setup.bash
```

**Make that permanent** — add it to your shell startup so every new terminal already knows about the workspace:

```bash
nano ~/.bashrc
```

Add this line at the end, using your real workspace path:

```bash
source ~/ros_ws/install/setup.bash
```

Then either open a new terminal or reload the current one:

```bash
source ~/.bashrc
```

> **Order matters.** Always source the ROS 2 underlay (`/opt/ros/jazzy/setup.bash`) *before* your workspace overlay. The overlay extends the underlay; sourcing it the other way round leaves your packages broken.

---

## 📦 2. Create a Package

```bash
ros2 pkg create <pkg_name> --build-type ament_python --dependencies rclpy
```

| Flag | Meaning |
| :--- | :--- |
| `--build-type ament_python` | pure Python package (use `ament_cmake` for C++) |
| `--dependencies rclpy` | declares `rclpy` in `package.xml` up front |

**Create a node file** inside the package directory:

```bash
cd <pkg_name>/<pkg_name>     # the inner folder with the same name
touch <file_name>.py
```

> The folder layout is `<pkg_name>/<pkg_name>/<file_name>.py`. The outer directory is the package; the inner one is the Python module that `entry_points` imports from.

**Build just this package** (faster than rebuilding the whole workspace):

```bash
colcon build --packages-select <pkg_name>
```

**Make the file executable:**

```bash
chmod +x <file_name>.py
```

---

## 🔌 2b. Register the Node as an Executable

A Python file is not runnable as a node until it is declared in `setup.py`.

Open `setup.py` and find the `entry_points` → `console_scripts` block:

```python
entry_points={
    'console_scripts': [
        '<exe_node_name> = <pkg_name>.<file_name_without_py_extension>:<function_name>',
    ],
},
```

**Example:**

```python
'py_node = my_pkg.my_node:main',
```

| Part | Value in the example | Meaning |
| :--- | :--- | :--- |
| `<exe_node_name>` | `py_node` | the name you pass to `ros2 run` |
| `<pkg_name>` | `my_pkg` | the Python package (module) |
| `<file>` | `my_node` | the file, **without** `.py` |
| `<function_name>` | `main` | the function to call |

**Rebuild after editing `setup.py`** — entry points are baked in at build time:

```bash
colcon build --packages-select <pkg_name>
source install/setup.bash
```

**Run the file directly** (bypassing the ROS 2 launch machinery — useful while debugging):

```bash
./<file_name>.py
python3 <file_name>.py
```

> Direct execution only works if the file ends with a `main()` guard:
> ```python
> if __name__ == '__main__':
>     main()
> ```

---

## 🚀 3. Run a Node from the Terminal

Once built and sourced, run the node by its **package** and **executable name**:

```bash
ros2 run <pkg_name> <exe_node_name>
```

**Concrete examples from this repo:**

```bash
ros2 run talker_listener talker       # Stage 1 publisher
ros2 run talker_listener listener     # Stage 1 subscriber
```

Handy companions while a node is running:

```bash
ros2 node list              # nodes currently on the graph
ros2 topic list             # active topics
ros2 topic echo /chatter    # print messages on a topic
ros2 topic hz /chatter      # measure publish rate
```

---

## 🤖 4. Launch the Robot Model (URDF)

```bash
ros2 launch four_wheeled_robot_urdf view_robot.launch.py
```

This starts `robot_state_publisher`, `joint_state_publisher_gui`, and `rviz2` together. Drag the sliders in the GUI panel to spin the wheels.

**The other stage launch files:**

```bash
# Stage 3 — modular xacro model
ros2 launch four_wheeled_robot_xacro view_robot.launch.py

# Stage 4 — differential drive teleop simulation
ros2 launch four_wheeled_robot_teleop view_robot.launch.py
```

**Stage 4 teleoperation** (in a second terminal):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Keys: `i` forward, `,` backward, `j` / `l` turn, `k` stop.

---

## 🔍 5. Debugging & Inspection

When a launch succeeds but RViz2 shows nothing, or the robot will not move, the answer is almost always in one of these four places.

### 5a. Is the node alive?

```bash
ros2 node list                  # every node currently on the graph
ros2 node info /diff_drive_sim  # its publishers, subscribers, services
```

A node that crashed on startup simply will not appear here. Start with this check.

### 5b. Topics — what is actually flowing

```bash
ros2 topic list -t              # topics with their message types
ros2 topic info /joint_states   # publisher/subscriber counts
ros2 topic hz /joint_states     # actual publish rate
ros2 topic echo /odom --once    # print a single message
```

**`ros2 topic hz` is the highest-value command in this list.** It distinguishes two failures that look identical in RViz2:

| Observation | Meaning |
| :--- | :--- |
| `no new messages` | nothing is publishing — the producer side is broken |
| a rate far below expected | publishing, but too slowly to look smooth |
| expected rate (e.g. `~50 Hz`) | data is flowing; the problem is on the **display** side |

If the rate is healthy but RViz2 is still empty, the fault is a **Fixed Frame** mismatch — see 5d.

### 5c. The topics these modules actually use

| Topic | Type | Published by | Used for |
| :--- | :--- | :--- | :--- |
| `/chatter` | `std_msgs/String` | Stage 1 talker | pub/sub demo |
| `/cmd_vel` | `geometry_msgs/Twist` | teleop keyboard | velocity commands |
| `/joint_states` | `sensor_msgs/JointState` | Stage 4 sim, or the GUI | wheel angles |
| `/odom` | `nav_msgs/Odometry` | Stage 4 sim | pose + travelled path |
| `/tf` | `tf2_msgs/TFMessage` | Stage 4 sim + `robot_state_publisher` | the frame tree |
| `/robot_description` | `std_msgs/String` | `robot_state_publisher` | the URDF itself |

Two of these are worth checking early when Stage 4 misbehaves:

```bash
ros2 topic echo /cmd_vel --once              # are the keypresses arriving?
ros2 topic echo /joint_states --field name   # are the joint names right?
```

> **Silent failure to know about:** if a joint name in `/joint_states` does not match the URDF exactly, `robot_state_publisher` skips it **without any warning**. The robot then drives across the grid with completely frozen wheels. If the wheels do not spin, compare `ros2 topic echo /joint_states --field name` against the joint names in the URDF.

### 5d. TF — the frame tree

RViz2 draws nothing unless every link can be traced back to the **Fixed Frame**. Check the tree directly:

```bash
ros2 run tf2_tools view_frames        # writes frames.pdf in the current directory
ros2 run tf2_ros tf2_echo odom base_footprint
```

`view_frames` generates a PDF diagram of the whole tree. What you want to see for Stage 4:

```
odom ──► base_footprint ──► base_link ──► front_left_wheel_link
                                       ├─► front_right_wheel_link
                                       ├─► rear_left_wheel_link
                                       └─► rear_right_wheel_link
```

The top link `odom → base_footprint` comes from `diff_drive_sim.py`; everything below it comes from `robot_state_publisher`. **If the tree is split into two disconnected pieces, that is your bug** — the two nodes disagree about a frame name.

`tf2_echo` shows a live transform. If it prints numbers that change as you drive, TF is healthy:

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

**Fixed Frame must match the config:**

| Stage | RViz `Fixed Frame` |
| :--- | :--- |
| 2 and 3 | `base_footprint` |
| 4 | `odom` |

```bash
ros2 run tf2_ros tf2_echo odom base_footprint   # verify the frame exists first
```

If the Fixed Frame does not exist in the tree, every display silently renders empty — no error message, just a blank grid.

### 5e. Parameters

Stage 4's node declares four parameters. Inspect and override them live:

```bash
ros2 param list                                   # all parameters on all nodes
ros2 param list /diff_drive_sim                   # just one node
ros2 param get /diff_drive_sim wheel_radius       # read a value
ros2 param set /diff_drive_sim cmd_timeout 2.0    # change at runtime
```

Override at launch time instead:

```bash
ros2 run four_wheeled_robot_teleop diff_drive_sim.py --ros-args -p wheel_radius:=0.1
```

| Parameter | Default | Effect if wrong |
| :--- | :--- | :--- |
| `wheel_radius` | `0.08` | wheels spin at the wrong rate (robot appears to slide) |
| `track_width` | `0.37` | turning radius is wrong |
| `publish_rate` | `50.0` | motion looks choppy if too low |
| `cmd_timeout` | `0.5` | robot keeps moving after you release a key if too high |

> `wheel_radius` and `track_width` **must match the URDF**. Nothing enforces this — the numbers are a convention between two files. Change one without the other and the simulation silently drifts from the model.

### 5f. Inspecting the model itself

```bash
# print the URDF that robot_state_publisher actually received
ros2 param get /robot_state_publisher robot_description

# check it parses, and see the links/joints
check_urdf install/<pkg>/share/<pkg>/urdf/<file>.urdf

# expand a xacro file by hand to see the generated URDF
xacro install/four_wheeled_robot_xacro/share/four_wheeled_robot_xacro/urdf/robot.urdf.xacro
```

Running `xacro` by hand is the fastest way to catch macro errors before launching — it prints a Python traceback pointing at the offending line.

### 5g. Logs

Node output goes to `~/.ros/log/` unless the launch file sets `output='screen'`. All four launch files in this repo **do** set it, so node messages appear in your terminal.

```bash
ls ~/.ros/log/latest/            # per-node log files from the last run
ros2 launch <pkg> <file>.launch.py --show-args     # list a launch file's arguments
```

---

## ⚠️ Common Pitfalls

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `Package '<pkg>' not found` | overlay not sourced | `source install/setup.bash` |
| `No executable found` | `setup.py` changed without rebuilding | `colcon build --packages-select <pkg>` |
| Edits have no effect | editing `src/` but launching the `install/` copy | rebuild, or use `--symlink-install` |
| `colcon: command not found` | dev tools missing | `sudo apt install ros-dev-tools` |
| RViz2 blank / OpenGL crash (WSL2) | driver issue | see below |
| RViz2 empty but nodes are running | **Fixed Frame** not in the TF tree | check 5d — use `base_footprint` (Stages 2–3) or `odom` (Stage 4) |
| Robot drives, wheels frozen | `/joint_states` names ≠ URDF joint names | compare 5c — no warning is printed |
| Robot will not move | no `/cmd_vel` arriving | `ros2 topic hz /cmd_vel`, then check teleop focus |
| Robot keeps moving after key release | `cmd_timeout` too high | `ros2 param set /diff_drive_sim cmd_timeout 0.5` |
| Wheels spin but robot slides | `wheel_radius` ≠ URDF radius | match 5e against the model |

**Build with symlinks** so source edits are picked up without rebuilding every time:

```bash
colcon build --symlink-install
```

**WSL2 / WSLg graphical fixes:**

```bash
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_GL_VERSION_OVERRIDE=3.3
export DISPLAY=:0
```

---

## 🧭 Cheat Sheet

```bash
# --- workspace ---
mkdir -p ~/ros_ws/src && cd ~/ros_ws
colcon build [--symlink-install] [--packages-select <pkg>]
source install/setup.bash

# --- package ---
ros2 pkg create <pkg> --build-type ament_python --dependencies rclpy
touch <pkg>/<pkg>/<node>.py
chmod +x <node>.py

# --- run ---
ros2 run <pkg> <exe>                    # via entry point
python3 <node>.py                       # directly

# --- inspect ---
ros2 node list | ros2 topic list -t | ros2 topic echo <topic>
ros2 topic hz <topic>                   # is data actually flowing?
ros2 param list | ros2 param get <node> <param>
ros2 run tf2_tools view_frames           # draw the TF tree -> frames.pdf
ros2 run tf2_ros tf2_echo <parent> <child>

# --- launch ---
ros2 launch <pkg> <file>.launch.py [--show-args]
```

---

## 📄 License

This project is licensed under the Apache 2.0 License.
