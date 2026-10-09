import rclpy
from rclpy.node import Node

from std_msgs.msg import Empty, String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from tello_msg.msg import TelloStatus
from pkg_msg.srv import DroneMode

class ManualControl(Node):

    def __init__(self):
        super().__init__('manual_control')
        self.distance_tof = 0
        self.request = DroneMode.Request()

        self.takeoff_pub = self.create_publisher(Empty, '/takeoff', 10)
        self.land_pub = self.create_publisher(Empty, '/land', 10)
        self.emergency_pub = self.create_publisher(Empty, '/emergency', 10)
        self.control_pub = self.create_publisher(Twist, '/secure_cmd', 10)
        self.flip_pub = self.create_publisher(String, '/flip', 10)
        self.control_mode_client = self.create_client(DroneMode, 'drone_mode')

        self.joy_sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        self.status_sub = self.create_subscription(TelloStatus, '/status', self.status_callback, 10)

    def status_callback(self, msg):
        self.distance_tof = msg.distance_tof
    
    def dead_zone(self, v, dz = 0.1):
        if abs(v) > dz:
            return v
        return 0.0

    def joy_callback(self, msg):

        TOF_GROUND_THRESHOLD = 20

        TAKEOFF_BUTTON = 0
        EMERGENCY_BUTTON = 1 
        LAND_BUTTON = 2

        AXIS_FORWARD = 1
        AXIS_LEFT = 0
        AXIS_VERTICAL = 3
        AXIS_ROTATION = 2
        AXIS_FLIP_DEVANT = 5
        AXIS_FLIP_COTE = 4

        MODE_MANUAL = 8
        MODE_SURVEILLANCE = 6
        MODE_SPIELBERG = 5
        MODE_FOLLOWER = 7

        if msg.buttons[TAKEOFF_BUTTON] == 1 and self.distance_tof <= TOF_GROUND_THRESHOLD:
            self.takeoff_pub.publish(Empty())
        
        if msg.buttons[LAND_BUTTON] == 1  and self.distance_tof >= TOF_GROUND_THRESHOLD:
            self.land_pub.publish(Empty())
        
        if msg.buttons[EMERGENCY_BUTTON] == 1:
            self.emergency_pub.publish(Empty())
        
        if msg.buttons[MODE_MANUAL] == 1:
            self.request.mode = 0
            future = self.control_mode_client.call_async(self.request)
        elif msg.buttons[MODE_SURVEILLANCE] == 1:
            self.request.mode = 1
            future = self.control_mode_client.call_async(self.request)
        elif msg.buttons[MODE_SPIELBERG] == 1:
            self.request.mode = 2
            future = self.control_mode_client.call_async(self.request)
        elif msg.buttons[MODE_FOLLOWER] == 1:
            self.request.mode = 3
            future = self.control_mode_client.call_async(self.request)
        
        if msg.axes[AXIS_FLIP_COTE] == 1:
            self.flip_pub.publish(String(data='l'))
        elif msg.axes[AXIS_FLIP_COTE] == -1:
            self.flip_pub.publish(String(data='r'))
        elif msg.axes[AXIS_FLIP_DEVANT] == 1:
            self.flip_pub.publish(String(data='f'))
        elif msg.axes[AXIS_FLIP_DEVANT] == -1:
            self.flip_pub.publish(String(data='b'))
        
        control = Twist()

        control.linear.x = -100 * self.dead_zone(msg.axes[AXIS_LEFT])
        control.linear.y = 100 * self.dead_zone(msg.axes[AXIS_FORWARD])
        control.linear.z = 100 * self.dead_zone(msg.axes[AXIS_VERTICAL])

        control.angular.z = -100 * self.dead_zone(msg.axes[AXIS_ROTATION])

        self.control_pub.publish(control)

        
        


def main(args=None):
    rclpy.init(args=args)

    manual_control = ManualControl()

    rclpy.spin(manual_control)

    manual_control.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
