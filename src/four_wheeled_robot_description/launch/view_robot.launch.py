import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_name = 'four_wheeled_robot_description'
    pkg_share = get_package_share_directory(pkg_name)
    
    default_rviz_config_path = os.path.join(pkg_share, 'rviz', 'view_robot.rviz')
    xacro_file = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')

    declare_teleop = DeclareLaunchArgument(
        'teleop',
        default_value='true',
        description='Enable differential drive simulation from cmd_vel'
    )

    declare_gui = DeclareLaunchArgument(
        'gui', 
        default_value='false', 
        description='Flag to enable joint_state_publisher_gui (when teleop is false)'
    )
    
    declare_rviz = DeclareLaunchArgument(
        'rvizconfig', 
        default_value=default_rviz_config_path, 
        description='Absolute path to rviz config file'
    )

    robot_description_content = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )

    diff_drive_sim_node = Node(
        package='four_wheeled_robot_description',
        executable='diff_drive_sim.py',
        name='diff_drive_sim',
        output='screen',
        condition=IfCondition(LaunchConfiguration('teleop'))
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('gui'), "' == 'true' and '", LaunchConfiguration('teleop'), "' != 'true'"]))
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('gui'), "' == 'false' and '", LaunchConfiguration('teleop'), "' != 'true'"]))
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')]
    )

    return LaunchDescription([
        declare_teleop,
        declare_gui,
        declare_rviz,
        robot_state_publisher_node,
        diff_drive_sim_node,
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
