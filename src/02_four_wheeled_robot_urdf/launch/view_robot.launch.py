import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = 'four_wheeled_robot_urdf'
    pkg_share = get_package_share_directory(pkg_name)

    urdf_path = os.path.join(pkg_share, 'urdf', 'four_wheeled_robot.urdf')
    default_rviz_config = os.path.join(pkg_share, 'rviz', 'view_robot.rviz')

    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    declare_rviz_arg = DeclareLaunchArgument(
        'rvizconfig',
        default_value=default_rviz_config,
        description='Path to rviz config file'
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

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
