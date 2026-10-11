#!/usr/bin/env python3
"""Stage 1 publisher node.

Owns the *publish* half of the minimal pub/sub demo: it emits a
``std_msgs/String`` on the ``/chatter`` topic twice per second.

Run standalone with ``ros2 run talker_listener talker``.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    """Publish an incrementing "Hello World: N" string at 2 Hz."""

    def __init__(self):
        # Node name must be unique on the graph; it shows up in `ros2 node list`.
        super().__init__('talker')

        # ---- Publisher -------------------------------------------------
        # Queue depth of 10: up to 10 outgoing messages are buffered if a
        # subscriber is momentarily slower than the 2 Hz publish rate.
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # ---- Timer -----------------------------------------------------
        self.timer_period = 0.5  # seconds (2 Hz)
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        # Message sequence counter, used to build the payload.
        self.count = 0
        self.get_logger().info('Talker node initialized. Publishing to /chatter at 2Hz...')

    def timer_callback(self):
        """Build and publish one message, then advance the counter."""
        msg = String()
        msg.data = f'Hello World: {self.count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1


def main(args=None):
    # Initialise the rclpy context, then block in spin() so callbacks fire.
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Ctrl+C is the normal way to stop a node; not an error condition.
        pass
    finally:
        # Always release the node and the context, even on a crash.
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
