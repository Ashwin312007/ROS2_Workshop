"""Stage 2 launch file: view the static URDF robot in RViz2.

Reads the plain URDF file from disk and hands its text to
robot_state_publisher, which converts the joint tree into TF frames. The
joint_state_publisher_gui supplies wheel angles so you can drag them.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Resolve install/share/<pkg> so paths work regardless of where the
    # workspace was built. Never use relative paths here.
    pkg_name = 'four_wheeled_robot_urdf'
    pkg_share = get_package_share_directory(pkg_name)

    urdf_path = os.path.join(pkg_share, 'urdf', 'four_wheeled_robot.urdf')
    default_rviz_config = os.path.join(pkg_share, 'rviz', 'view_robot.rviz')

    # ---- Robot description ------------------------------------------------
    # No xacro involved yet: the file is already valid URDF, so it is read
    # verbatim and passed as the robot_description parameter below.
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    # Expose the RViz config path as `rvizconfig:=<path>` on the CLI.
    declare_rviz_arg = DeclareLaunchArgument(
        'rvizconfig',
        default_value=default_rviz_config,
        description='Path to rviz config file'
    )

    # Publishes TF for every link/joint in the URDF.
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    # Slider GUI that publishes joint_states for the four continuous joints.
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # `-d <file>` makes RViz2 open with the saved display configuration.
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')]
    )

    return LaunchDescription([
        declare_rviz_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
