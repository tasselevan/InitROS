import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from pkg_msg.srv import DroneMode
from pkg_msg.action import Spielberg
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

        self.spielberg_client = ActionClient(self, Spielberg, 'spielberg')

        self.get_logger().info(
            f'Mode actuel : {self.MODE[self.mode]}'
        )
    
    # Mode manuel
    def control_callback(self, msg):

        if self.mode == 0:
            self.control_pub.publish(msg)
    
    # Mode surveillance
    def set_surveillance(self, active):

        if not self.surveillance_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn(
                'Service surveillance_node indisponible'
            )
            return

        request = SetBool.Request()
        request.data = active

        future = self.surveillance_client.call_async(request)

    # Mode Spielberg
    def feedback_callback(self, feedback_msg):
        status = feedback_msg.feedback.status
        self.get_logger().info(f'[Spielberg] {status}')


    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().warn('Scénario Spielberg refusé')
            return

        self.get_logger().info('Scénario Spielberg accepté')

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)


    def result_callback(self, future):
        result = future.result().result

        if result.success:
            self.get_logger().info(f'[Spielberg] {result.message}')
            self.mode = 0
            self.get_logger().info(
                f'Mode actuel : {self.MODE[self.mode]}'
            )
        else:
            self.get_logger().warn(f'[Spielberg] Échec : {result.message}')

    def start_spielberg(self):
        
        if not self.spielberg_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn('Serveur Spielberg indisponible')
            return

        goal = Spielberg.Goal()

        future = self.spielberg_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )

        future.add_done_callback(self.goal_response_callback)

        self.get_logger().info('Scénario Spielberg demandé')
    
    # Control mode
    def drone_mode_callback(self, request, response):

        if request.mode in self.MODE:
            self.mode = request.mode
            
            if self.mode == 1:
                self.set_surveillance(True)
            else:
                self.set_surveillance(False)

            if self.mode == 2:
                self.start_spielberg()

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
