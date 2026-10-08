import rclpy
from rclpy.node import Node

from pkg_msg.srv import DroneMode
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist

class TelloBehavior(Node):

    MODE = {
        0: "Manuel",
        1: "Surveillance",
        2: "Spielberg",
        3: "Follower"
    }

    def __init__(self):
        super().__init__('tello_behavior')

        self.mode = 0

        self.control_sub = self.create_subscription(Twist, '/secure_cmd', self.control_callback, 10)
        
        self.control_pub = self.create_publisher(Twist, '/control', 10)

        self.drone_mode_service = self.create_service(DroneMode, 'drone_mode', self.drone_mode_callback)

        self.surveillance_client = self.create_client(SetBool, 'surveillance')

        self.get_logger().info(
            f'Mode actuel : {self.MODE[self.mode]}'
        )
    
    # Mode manuel
    def control_callback(self, msg):

        if self.mode == 0:
            self.control_pub.publish(msg)
        
        #else:
        #    stop = Twist()
        #    self.control_pub.publish(stop)
    
    # Model surveillance
    def set_surveillance(self, active):

        if not self.surveillance_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn(
                'Service surveillance_node indisponible'
            )
            return

        request = SetBool.Request()
        request.data = active

        self.get_logger().info(
            'Envoi de la requête au surveillance_node'
        )

        future = self.surveillance_client.call_async(request)

        future.add_done_callback(
            self.surveillance_response_callback
        )
    
    def surveillance_response_callback(self, future):

        try:
            response = future.result()

            if response.success:
                self.get_logger().info(
                    response.message
                )
            else:
                self.get_logger().warn(
                    response.message
                )

        except Exception as e:
            self.get_logger().error(
                f'Erreur service surveillance : {e}'
            )
    
    # Control mode
    def drone_mode_callback(self, request, response):

        if request.mode in self.MODE:
            self.mode = request.mode
            
            # Active la surveillance
            if self.mode == 1:
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
