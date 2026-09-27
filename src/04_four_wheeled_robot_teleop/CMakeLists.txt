cmake_minimum_required(VERSION 3.8)
project(four_wheeled_robot_teleop)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf launch rviz
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/diff_drive_sim.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
