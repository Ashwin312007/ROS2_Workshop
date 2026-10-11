# Stage 3 package: install-only ament_cmake package holding the modular
# xacro model, its launch file, and the RViz config. No compiled targets.
cmake_minimum_required(VERSION 3.8)
project(four_wheeled_robot_xacro)

find_package(ament_cmake REQUIRED)

# Copies urdf/, launch/, and rviz/ into share/four_wheeled_robot_xacro/.
install(
  DIRECTORY urdf launch rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
