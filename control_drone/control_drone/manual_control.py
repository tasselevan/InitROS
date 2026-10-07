import rclpy
from rclpy.node import Node

from std_msgs.msg import Empty, String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

class ManualControl(Node):

    def __init__(self):
        super().__init__('control_publisher')
        self.takeoff_pub = self.create_publisher(Empty, '/takeoff', 10)
        self.land_pub = self.create_publisher(Empty, '/land', 10)
        self.emergency_pub = self.create_publisher(Empty, '/emergency', 10)
        self.control_pub = self.create_publisher(Twist, '/control', 10)


        self.joy_sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)


    def joy_callback(self, msg):

        TAKEOFF_BUTTON = 0
        EMERGENCY_BUTTON = 1 
        LAND_BUTTON = 2

        AXIS_FORWARD = 1
        AXIS_LEFT = 0
        AXIS_VERTICAL = 3
        AXIS_ROTATION = 2

        if msg.buttons[TAKEOFF_BUTTON] == 1:
            self.takeoff_pub.publish(Empty())
        

        if msg.buttons[LAND_BUTTON] == 1:
            self.land_pub.publish(Empty())
        
        if msg.buttons[EMERGENCY_BUTTON] == 1:
            self.emergency_pub.publish(Empty())
        
        control = Twist()

        control.linear.x = 100 * msg.axes[AXIS_FORWARD]
        control.linear.y = 100 * msg.axes[AXIS_LEFT]
        control.linear.z = 100 * msg.axes[AXIS_VERTICAL]

        control.angular.z = 100 * msg.axes[AXIS_ROTATION]

        self.control_pub.publish(control)

        
        


def main(args=None):
    rclpy.init(args=args)

    manual_control = ManualControl()

    rclpy.spin(manual_control)

    manual_control.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
