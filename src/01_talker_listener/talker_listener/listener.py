#!/usr/bin/env python3
"""Stage 1 subscriber node.

Owns the *receive* half of the minimal pub/sub demo: it subscribes to the
``/chatter`` topic and logs whatever the talker publishes.

Run standalone with ``ros2 run talker_listener listener``.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    """Log every ``std_msgs/String`` received on ``/chatter``."""

    def __init__(self):
        super().__init__('listener')

        # ---- Subscription ----------------------------------------------
        # create_subscription(message_type, topic, callback, queue_depth).
        # Topic names are relative here, so they resolve into the node's
        # namespace and stay compatible with the talker's relative 'chatter'.
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.chatter_callback,
            10
        )
        self.get_logger().info('Listener node initialized. Subscribed to /chatter...')

    def chatter_callback(self, msg: String):
        """Handle one inbound message (called from inside spin())."""
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    # spin() keeps the process alive and dispatches inbound messages to
    # chatter_callback().
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
