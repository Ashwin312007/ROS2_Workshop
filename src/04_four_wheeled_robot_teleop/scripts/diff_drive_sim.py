#!/usr/bin/env python3
"""Stage 4 differential drive simulation node.

Turns `/cmd_vel` twist commands from a keyboard teleop into motion of a
4-wheeled robot, without any physics engine:

  * integrates a 2D pose (x, y, yaw) with differential drive kinematics,
  * broadcasts the TF chain odom -> base_footprint,
  * publishes nav_msgs/Odometry on /odom and wheel angles on /joint_states,
  * stops the robot if no /cmd_vel arrives within `cmd_timeout` seconds.

Run via `ros2 run four_wheeled_robot_teleop diff_drive_sim.py`.
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster


class DiffDriveSim(Node):
    """Differential drive simulation node for four-wheeled robot.

    Subscribes to /cmd_vel, updates 2D odometry using differential drive
    kinematics, broadcasts TF (odom -> base_footprint), and publishes Odometry
    and JointState messages for visualization in RViz2.
    """

    def __init__(self):
        super().__init__('diff_drive_sim')

        # ---- Parameters ---------------------------------------------------
        # Declared with defaults so the node runs standalone; override at
        # launch time with e.g. -p wheel_radius:=0.1.
        self.declare_parameter('wheel_radius', 0.08)
        self.declare_parameter('track_width', 0.37)
        self.declare_parameter('publish_rate', 50.0)
        self.declare_parameter('cmd_timeout', 0.5)

        # Read the values back out of the parameter server.
        self.wheel_radius = self.get_parameter('wheel_radius').get_parameter_value().double_value
        self.track_width = self.get_parameter('track_width').get_parameter_value().double_value
        self.rate = self.get_parameter('publish_rate').get_parameter_value().double_value
        self.cmd_timeout = self.get_parameter('cmd_timeout').get_parameter_value().double_value

        # ---- Robot state --------------------------------------------------
        # Pose in the odom frame, plus accumulated wheel rotation angles (rad).
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.left_wheel_pos = 0.0
        self.right_wheel_pos = 0.0

        # ---- Commanded velocities -----------------------------------------
        # Last twist received; zeroed by the watchdog when commands go stale.
        self.linear_x = 0.0
        self.angular_z = 0.0
        self.last_cmd_time = self.get_clock().now()

        # ---- ROS publishers & subscribers ---------------------------------
        # Queue depth 10 is ample: the 50 Hz timer always outpaces cmd_vel.
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10
        )
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # ---- Integration timer --------------------------------------------
        # prev_time is the timestamp of the previous update_and_publish() call,
        # used to derive dt for each integration step.
        self.prev_time = self.get_clock().now()
        self.timer = self.create_timer(1.0 / self.rate, self.update_and_publish)
        self.get_logger().info('DiffDriveSim node initialized. Subscribing to /cmd_vel...')

    def cmd_vel_callback(self, msg: Twist):
        """Latch the latest velocity command and stamp its arrival time."""
        self.linear_x = msg.linear.x
        self.angular_z = msg.angular.z
        self.last_cmd_time = self.get_clock().now()

    def update_and_publish(self):
        """Integrate one time step, then publish TF, odometry, and joint states."""
        # ---- Time step ----------------------------------------------------
        # dt is measured from the node clock, not assumed from the timer
        # period, so scheduling jitter does not distort the pose.
        now = self.get_clock().now()
        dt = (now - self.prev_time).nanoseconds / 1e9
        self.prev_time = now

        # Skip nonsense steps: non-positive dt on the first tick or after a
        # clock jump, and very large gaps that would teleport the robot.
        if dt <= 0.0 or dt > 1.0:
            return

        # ---- Auto-stop watchdog -------------------------------------------
        # If teleop stops sending (key released, terminal closed), the robot
        # coasts to a halt instead of running away with the last command.
        time_since_cmd = (now - self.last_cmd_time).nanoseconds / 1e9
        if time_since_cmd > self.cmd_timeout:
            self.linear_x = 0.0
            self.angular_z = 0.0

        # ---- Differential drive kinematics --------------------------------
        # Split the body twist into per-side linear speeds: the inner wheel
        # travels slower when turning, the outer wheel faster.
        v_l = self.linear_x - (self.angular_z * self.track_width / 2.0)
        v_r = self.linear_x + (self.angular_z * self.track_width / 2.0)

        # Convert linear wheel speed to angular speed (v = omega * r).
        omega_l = v_l / self.wheel_radius
        omega_r = v_r / self.wheel_radius

        # Accumulate joint angles for robot_state_publisher to draw rotation.
        self.left_wheel_pos += omega_l * dt
        self.right_wheel_pos += omega_r * dt

        # ---- Pose integration ---------------------------------------------
        # Midpoint (2nd-order Runge-Kutta) integration: sample the heading at
        # the middle of the step, which is far more accurate than using the
        # start-of-step yaw when the robot is turning.
        delta_yaw = self.angular_z * dt
        delta_x = self.linear_x * math.cos(self.yaw + delta_yaw / 2.0) * dt
        delta_y = self.linear_x * math.sin(self.yaw + delta_yaw / 2.0) * dt

        self.x += delta_x
        self.y += delta_y
        self.yaw += delta_yaw

        # ---- Quaternion representation ------------------------------------
        # Planar motion only, so the quaternion is a pure rotation about Z:
        # (x, y, z, w) = (0, 0, sin(yaw/2), cos(yaw/2)).
        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        now_msg = now.to_msg()

        # ---- 1. Publish TF odom -> base_footprint -------------------------
        # This is what lets RViz place the robot in the world frame. The
        # remaining base_footprint -> wheel links come from robot_state_publisher.
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

        # ---- 2. Publish Odometry ------------------------------------------
        # Same pose as the TF above, but as a message so the RViz Odometry
        # display can draw the travelled path and the twist can be consumed
        # by other nodes (e.g. a future controller).
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

        # ---- 3. Publish JointState ----------------------------------------
        # Names must match the joint names in the xacro model exactly, or
        # robot_state_publisher will ignore the wheel motion. There are four
        # joints but only two values: both left wheels share one angle, and
        # both right wheels share the other (no separate steering).
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
        # Normal shutdown path: Ctrl+C stops spin() and falls through.
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
