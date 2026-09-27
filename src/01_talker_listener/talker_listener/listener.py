#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    """Minimal ROS 2 subscriber node listening to String messages on /chatter."""

    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.chatter_callback,
            10
        )
        self.get_logger().info('Listener node initialized. Subscribed to /chatter...')

    def chatter_callback(self, msg: String):
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
