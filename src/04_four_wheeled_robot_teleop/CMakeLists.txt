# Stage 4 package: ament_cmake package holding the xacro model plus the
# Python differential drive node. No C++ targets are built.
cmake_minimum_required(VERSION 3.8)
project(four_wheeled_robot_teleop)

find_package(ament_cmake REQUIRED)

# Data files: model, launch files, and RViz config, into share/<pkg>/.
install(
  DIRECTORY urdf launch rviz
  DESTINATION share/${PROJECT_NAME}
)

# The Python node is a *program*, not a library: PROGRAMS sets the executable
# bit and installs into lib/<pkg>/, which is where `ros2 run` looks for it.
install(
  PROGRAMS scripts/diff_drive_sim.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
