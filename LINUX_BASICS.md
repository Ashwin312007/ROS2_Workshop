# Linux Basics for ROS 2

The ~25 shell commands you actually need for this workshop. Everything here is used somewhere in the four modules — nothing is included just for completeness.

> Written for **WSL2 / Ubuntu 24.04** (the ROS 2 Jazzy target). See [section 6](#-6-wsl2-paths--line-endings) for how Windows paths map across.
>
> Companion doc: [ROS2_QUICK_REFERENCE.md](ROS2_QUICK_REFERENCE.md)

---

## 📁 1. Navigation — where am I, where do I go

```bash
pwd                  # print working directory — "where am I?"
ls                   # list files here
ls -la               # list ALL files (incl. hidden) with permissions
ls src               # list a specific folder
```

```bash
cd ~/ros_ws          # go to the workspace
cd src               # go into src/  (relative)
cd ..                # go up one level
cd ~                 # go to your home directory
cd -                 # go back to the previous directory
```

| Symbol | Means | Example |
| :--- | :--- | :--- |
| `~` | your home dir, `/home/<you>` | `cd ~/ros_ws` |
| `.` | the current directory | `./talker.py` |
| `..` | the parent directory | `cd ..` |
| `/` | the root of the filesystem | `cd /opt/ros/jazzy` |

> **Tab completion is your best friend.** Type `cd ~/ros` then press **Tab** — the shell finishes the path. Press Tab twice to see all matches. This prevents most typos.

---

## 📄 2. Creating and moving files

```bash
mkdir src                      # make one directory
mkdir -p ~/ros_ws/src          # make the whole chain, even if parents don't exist
touch <file_name>.py           # create an empty file
```

`mkdir -p` is the important one — it creates missing parents instead of erroring:

```bash
mkdir ros_ws/src        # fails if ros_ws doesn't exist
mkdir -p ros_ws/src     # works: creates both levels
```

```bash
cp file.txt backup.txt         # copy a file
cp -r urdf urdf_backup         # copy a whole directory (-r = recursive)
mv old_name.py new_name.py     # rename
mv file.py ~/ros_ws/src/       # move to another directory
rm unwanted.txt                # delete a file
rm -r build/                   # delete a directory and its contents
```

> **`rm` is permanent.** There is no recycle bin and no undo. Read the path twice before pressing Enter, especially with `-r`. Never run `rm -r` against a path you built from a variable you haven't checked.

---

## 👀 3. Looking at files

```bash
cat setup.py             # print the whole file
cat package.xml          # the standard way to read a small config file
less view_robot.rviz     # scroll through a long file (q to quit)
head -20 file.urdf       # first 20 lines
tail -20 file.urdf       # last 20 lines
```

To **edit** a file, your workshop uses `nano`:

```bash
nano ~/.bashrc           # edit your shell startup file
```

**Essential nano keys:**

| Key | Action |
| :--- | :--- |
| `Ctrl+O` then `Enter` | **save** |
| `Ctrl+X` | **exit** |
| `Ctrl+W` | search |
| `Ctrl+K` | cut line |
| `Ctrl+U` | paste line |

> The number-one beginner trap: you edit a file in nano, then `Ctrl+X` — and it asks *"Save modified buffer?"*. Press `Y`, then `Enter`. If you press `N`, your edits are gone.

---

## 🔎 4. Searching

```bash
find . -name "*.urdf"              # find files by name, from here down
find . -name "*.xacro"             # find all xacro files
```

```bash
grep -r "wheel_radius" .           # search file CONTENTS, recursively
grep -rn "cmd_vel" src/            # -n shows line numbers
```

`grep -r` is how you answer *"where is this joint name defined?"* — far faster than opening files one at a time. Example from this repo:

```bash
grep -rn "front_left_wheel_joint" src/
# src/04_.../scripts/diff_drive_sim.py:185:  'front_left_wheel_joint',
# src/04_.../urdf/wheel.xacro:4:  <joint name="${name}_joint" ...
# src/02_.../urdf/four_wheeled_robot.urdf:61: <joint name="front_left_wheel_joint" ...
```

That single command finds every place a name is used — which is exactly what you need when `/joint_states` names don't match the URDF.

---

## 🔐 5. Permissions — the `chmod` step explained

```bash
ls -l talker.py
# -rw-r--r--  1 user user 1234 Jan 1 12:00 talker.py
#  └┬┘└┬┘└┬┘
#   │  │  └── others: read only
#   │  └───── group:  read only
#   └──────── owner:  read + write
```

The mode string breaks into three triplets: **owner, group, others**, each showing `r`ead / `w`rite / e`x`ecute.

```bash
chmod +x talker.py       # add execute for everyone (what the workshop uses)
chmod 755 script.py      # owner: rwx | group: r-x | others: r-x  (typical for scripts)
chmod 644 file.txt       # owner: rw- | group: r-- | others: r--  (typical for data)
```

The numbers are just the triplets in octal — `r=4`, `w=2`, `x=1`, summed:

| Mode | Owner | Group | Others | Typical use |
| :--- | :--- | :--- | :--- | :--- |
| `755` | `rwx` (7) | `r-x` (5) | `r-x` (5) | executable script |
| `644` | `rw-` (6) | `r--` (4) | `r--` (4) | normal file |
| `600` | `rw-` (6) | `---` (0) | `---` (0) | private file |

**`sudo`** runs a single command as the administrator. Only needed for system-wide changes:

```bash
sudo apt update
sudo apt install ros-dev-tools
```

> Don't put `sudo` in front of `colcon`, `ros2`, or `git`. It creates root-owned files that your normal user can't touch afterwards — a genuinely annoying problem to unwind.

---

## 🛠️ 6. WSL2 paths & line endings

Your Windows `E:\ROS2 Workshop` appears inside WSL as:

```
/mnt/e/ROS2 Workshop
```

| Windows | WSL path |
| :--- | :--- |
| `E:\` | `/mnt/e/` |
| `C:\Users\you` | `/mnt/c/Users/you` |
| `E:\ROS2 Workshop` | `/mnt/e/ROS2 Workshop` |

Because the path contains a **space**, always quote it:

```bash
cd "/mnt/e/ROS2 Workshop"      # ✅ quoted
cd /mnt/e/ROS2 Workshop        # ❌ shell sees two separate arguments
```

> **The line-ending trap.** Windows uses CRLF (`\r\n`); Linux uses LF (`\n`). A `.py` file saved with CRLF in WSL can fail with:
> ```
> bash: ./talker.py: /usr/bin/env: bad interpreter: No such file or directory
> ```
> The `^M` hiding in the shebang line is the culprit. If you hit this, the fastest fix is:
> ```bash
> sed -i 's/\r$//' talker.py     # strip carriage returns
> ```
> Better still, keep your editor set to LF for files in this repo.

---

## 🧭 Cheat Sheet

```bash
# --- where am I ---
pwd                      # current directory
ls -la                   # list all files w/ permissions

# --- move around ---
cd ~/ros_ws              # go to workspace
cd ..                    # up one level
cd -                     # back to previous

# --- make things ---
mkdir -p ~/ros_ws/src    # create full path
touch node.py            # empty file
cp -r src src_backup     # copy a directory
mv a.py b.py             # rename
rm -r build/             # delete a directory (no undo!)

# --- read things ---
cat setup.py             # whole file
less big_file            # scroll (q to quit)
head -20 file            # first 20 lines
nano ~/.bashrc           # edit (Ctrl+O save, Ctrl+X exit)

# --- find things ---
find . -name "*.urdf"            # files by name
grep -rn "cmd_vel" .             # text inside files

# --- permissions ---
ls -l script.py          # read the mode
chmod +x script.py       # make executable
chmod 755 script.py      # owner rwx, others r-x
sudo apt install <pkg>   # admin (system packages only)

# --- WSL ---
cd "/mnt/e/ROS2 Workshop"   # quote paths with spaces
```

---

## Next Steps

- **[ROS2_QUICK_REFERENCE.md](ROS2_QUICK_REFERENCE.md)** — workspace setup, packages, `ros2 run`, launching URDF, and debugging
- **[README.md](README.md)** — the full four-module workshop walkthrough

---

## 📄 License

This project is licensed under the Apache 2.0 License.
