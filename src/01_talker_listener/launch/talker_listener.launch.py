"""Stage 1 launch file: start the talker and listener nodes together.

Unlike `ros2 run`, a launch file describes several nodes as one process tree,
so `ros2 launch talker_listener talker_listener.launch.py` brings the whole
pub/sub pair up (and Ctrl+C tears both down) at once.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Entry point `ros2 launch` calls; must return a LaunchDescription."""
    # ---- Publisher node -------------------------------------------------
    talker_node = Node(
        package='talker_listener',
        executable='talker',  # console_scripts entry point from setup.py
        name='talker',        # overrides the node name set in code
        output='screen'       # stream this node's logs to the launching terminal
    )

    # ---- Subscriber node ------------------------------------------------
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
