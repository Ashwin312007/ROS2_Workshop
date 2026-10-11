"""Stage 3 launch file: expand the xacro model and view it in RViz2.

Same node set as Stage 2, except robot_description is produced by running
`xacro` on robot.urdf.xacro at launch time instead of reading a static URDF.
The `gui:=true|false` argument swaps the slider GUI for the headless
joint_state_publisher.
"""

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_name = 'four_wheeled_robot_xacro'
    pkg_share = get_package_share_directory(pkg_name)

    default_rviz_config_path = os.path.join(pkg_share, 'rviz', 'view_robot.rviz')
    xacro_file = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')

    # ---- Launch arguments -------------------------------------------------
    # gui:=true shows the joint sliders; gui:=false runs the non-GUI publisher.
    declare_gui = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Flag to enable joint_state_publisher_gui'
    )

    declare_rviz = DeclareLaunchArgument(
        'rvizconfig',
        default_value=default_rviz_config_path,
        description='Absolute path to rviz config file'
    )

    # ---- Robot description ------------------------------------------------
    # Command() defers execution to launch time and captures stdout, so the
    # xacro file is expanded into a URDF string. ParameterValue(..., str)
    # keeps the result a string instead of trying to parse it as YAML.
    robot_description_content = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )

    # Exactly one joint-state source runs, chosen by the `gui` argument.
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('gui'))
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')]
    )

    return LaunchDescription([
        declare_gui,
        declare_rviz,
        robot_state_publisher_node,
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
