#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    """Minimal ROS 2 publisher node publishing String messages at 2 Hz."""

    def __init__(self):
        super().__init__('talker')
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        self.timer_period = 0.5  # seconds (2 Hz)
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.count = 0
        self.get_logger().info('Talker node initialized. Publishing to /chatter at 2Hz...')

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1


def main(args=None):
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
