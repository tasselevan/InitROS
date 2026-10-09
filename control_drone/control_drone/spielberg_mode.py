import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from geometry_msgs.msg import Twist
from pkg_msg.action import Spielberg

import time


class SpielbergMode(Node):

    def __init__(self):
        super().__init__('spielberg_mode')

        self.control_pub = self.create_publisher(
            Twist,
            '/control',
            10
        )

        self.spielberg_server = ActionServer(
            self, 
            Spielberg, 
            'spielberg', 
            self.execute_callback
        )

        self.get_logger().info('Spielberg node set !')


    def travelling(self, goal_handle):

        self.get_logger().info('Début du travelling')

        msg = Twist()
        msg.angular.z = 100.0

        feedback_msg = Spielberg.Feedback()

        for i in range(30):
            self.control_pub.publish(msg)
            feedback_msg.status = f'Progression : {(i + 1) * 100 // 60}%'
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(0.1)
        
        msg = Twist()
        msg.linear.y = 30.0

        feedback_msg = Spielberg.Feedback()

        for i in range(20):
            self.control_pub.publish(msg)
            feedback_msg.status = f'Progression : {(i + 1) * 100 // 60}%'
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(0.1)

        msg = Twist()
        msg.angular.z = -100.0

        for i in range(30):
            self.control_pub.publish(msg)
            feedback_msg.status = f'Progression : {(i + 31) * 100 // 60}%'
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(0.1)

        # Arrêt
        msg = Twist()
        self.control_pub.publish(msg)

        self.get_logger().info('Fin du travelling')
    
    def execute_callback(self, goal_handle):
        self.get_logger().info('Exécution du scénario Spielberg')

        self.travelling(goal_handle)

        msg = Twist()
        self.control_pub.publish(msg)

        goal_handle.succeed()

        result = Spielberg.Result()
        result.success = True
        result.message = 'Travelling terminé'

        return result


def main(args=None):
    rclpy.init(args=args)

    spielberg_mode = SpielbergMode()

    rclpy.spin(spielberg_mode)

    spielberg_mode.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()