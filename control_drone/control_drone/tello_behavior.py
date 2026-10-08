import rclpy
from rclpy.node import Node

from pkg_msg.srv import DroneMode
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist

class TelloBehavior(Node):

    MODE = {
        0: "Manuel",
        1: "Follower",
        2: "Spielberg",
        3: "Surveillance"
    }

    def __init__(self):
        super().__init__('tello_behavior')

        self.mode = 0

        self.control_sub = self.create_subscription(Twist, '/secure_cmd', self.control_callback, 10)
        
        self.control_pub = self.create_publisher(Twist, '/control', 10)

        self.drone_mode_service = self.create_service(DroneMode, 'drone_mode', self.drone_mode_callback)

        self.surveillance_client = self.create_client(SetBool, '/surveillance')

        self.get_logger().info(
            f'Mode actuel : {self.MODE[self.mode]}'
        )
    
    # Mode manuel
    def control_callback(self, msg):

        if self.mode == 0:
            self.control_pub.publish(msg)
        
        else:
            stop = Twist()
            self.control_pub.publish(stop)
    
    # Model surveillance
    def set_surveillance(self, active):
        request = SetBool.Request()
        request.data = active

        self.surveillance_client.call_async(request)
    
    # Control mode
    def drone_mode_callback(self, request, response):

        if request.mode in self.MODE:
            self.mode = request.mode
            
            # Active la surveillance
            if self.mode == 3:
                self.set_surveillance(True)

            # Désactive la surveillance
            else:
                self.set_surveillance(False)

            response.success = True

            self.get_logger().info(
                f'Mode changé : {self.MODE[self.mode]}'
            )
        
        else:
            response.success = False

            self.get_logger().info(
                f'Mode invalide : {self.MODE[self.mode]}'
            )
        
        return response



def main(args=None):
    rclpy.init(args=args)

    tello_behavior = TelloBehavior()

    rclpy.spin(tello_behavior)

    tello_behavior.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
