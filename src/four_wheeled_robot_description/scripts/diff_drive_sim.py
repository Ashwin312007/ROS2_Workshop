#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster

class DiffDriveSim(Node):
    def __init__(self):
        super().__init__('diff_drive_sim')

        # Parameters
        self.declare_parameter('wheel_radius', 0.08)
        self.declare_parameter('track_width', 0.37)
        self.declare_parameter('publish_rate', 50.0)
        self.declare_parameter('cmd_timeout', 0.5)

        self.wheel_radius = self.get_parameter('wheel_radius').get_parameter_value().double_value
        self.track_width = self.get_parameter('track_width').get_parameter_value().double_value
        self.rate = self.get_parameter('publish_rate').get_parameter_value().double_value
        self.cmd_timeout = self.get_parameter('cmd_timeout').get_parameter_value().double_value

        # Robot state
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.left_wheel_pos = 0.0
        self.right_wheel_pos = 0.0

        # Commanded velocities
        self.linear_x = 0.0
        self.angular_z = 0.0
        self.last_cmd_time = self.get_clock().now()

        # ROS publishers & subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10
        )
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.prev_time = self.get_clock().now()
        self.timer = self.create_timer(1.0 / self.rate, self.update_and_publish)
        self.get_logger().info('DiffDriveSim node initialized. Subscribing to /cmd_vel...')

    def cmd_vel_callback(self, msg: Twist):
        self.linear_x = msg.linear.x
        self.angular_z = msg.angular.z
        self.last_cmd_time = self.get_clock().now()

    def update_and_publish(self):
        now = self.get_clock().now()
        dt = (now - self.prev_time).nanoseconds / 1e9
        self.prev_time = now

        if dt <= 0.0 or dt > 1.0:
            return

        # Auto-stop watchdog: if no new cmd_vel received within timeout, stop the robot
        time_since_cmd = (now - self.last_cmd_time).nanoseconds / 1e9
        if time_since_cmd > self.cmd_timeout:
            self.linear_x = 0.0
            self.angular_z = 0.0

        # Differential drive kinematics
        v_l = self.linear_x - (self.angular_z * self.track_width / 2.0)
        v_r = self.linear_x + (self.angular_z * self.track_width / 2.0)

        omega_l = v_l / self.wheel_radius
        omega_r = v_r / self.wheel_radius

        self.left_wheel_pos += omega_l * dt
        self.right_wheel_pos += omega_r * dt

        # Update pose
        delta_yaw = self.angular_z * dt
        delta_x = self.linear_x * math.cos(self.yaw + delta_yaw / 2.0) * dt
        delta_y = self.linear_x * math.sin(self.yaw + delta_yaw / 2.0) * dt

        self.x += delta_x
        self.y += delta_y
        self.yaw += delta_yaw

        # Quaternion for yaw
        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        now_msg = now.to_msg()

        # 1. Publish TF odom -> base_footprint
        t = TransformStamped()
        t.header.stamp = now_msg
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(t)

        # 2. Publish Odometry
        odom = Odometry()
        odom.header.stamp = now_msg
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = self.linear_x
        odom.twist.twist.angular.z = self.angular_z
        self.odom_pub.publish(odom)

        # 3. Publish JointState
        js = JointState()
        js.header.stamp = now_msg
        js.name = [
            'front_left_wheel_joint',
            'front_right_wheel_joint',
            'rear_left_wheel_joint',
            'rear_right_wheel_joint'
        ]
        js.position = [
            self.left_wheel_pos,
            self.right_wheel_pos,
            self.left_wheel_pos,
            self.right_wheel_pos
        ]
        js.velocity = [omega_l, omega_r, omega_l, omega_r]
        self.joint_pub.publish(js)

def main(args=None):
    rclpy.init(args=args)
    node = DiffDriveSim()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
