# Stage 2 package: install-only ament_cmake package.
# There is no compiled code; CMake is used purely to copy resources into
# install/share/four_wheeled_robot_urdf/.
cmake_minimum_required(VERSION 3.8)
project(four_wheeled_robot_urdf)

find_package(ament_cmake REQUIRED)

# Install the model, launch, and RViz config directories in one go.
install(
  DIRECTORY urdf launch rviz
  DESTINATION share/${PROJECT_NAME}
)

# Registers the package with ament (generates the package index entries).
ament_package()
