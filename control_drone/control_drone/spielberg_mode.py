import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

import time


class SpielbergMode(Node):

    def __init__(self):
        super().__init__('spielberg_mode')

        self.control_pub = self.create_publisher(
            Twist,
            '/control',
            10
        )

    def travelling(self):

        self.get_logger().info('Début du travelling')

        # Commande d'avance
        msg = Twist()
        msg.linear.x = 100.0

        self.control_pub.publish(msg)

        # Maintenir la commande pendant 3 secondes
        time.sleep(5.0)

        # Arrêt
        msg = Twist()
        self.control_pub.publish(msg)

        self.get_logger().info('Fin du travelling')


def main(args=None):
    rclpy.init(args=args)

    node = SpielbergMode()

    node.travelling()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()