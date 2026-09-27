from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    talker_node = Node(
        package='talker_listener',
        executable='talker',
        name='talker',
        output='screen'
    )

    listener_node = Node(
        package='talker_listener',
        executable='listener',
        name='listener',
        output='screen'
    )

    return LaunchDescription([
        talker_node,
        listener_node
    ])
