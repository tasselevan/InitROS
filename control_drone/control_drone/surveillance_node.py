import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool

class SurveillanceNode(Node):

    def __init__(self):
        super().__init__('surveillance_mode')
        self.active = False

        self.control_pub = self.create_publisher(Twist, '/control', 10)

        self.surveillance_service = self.create_service(
            SetBool, 
            'surveillance',
            self.surveillance_callback
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_rotation
        )
    
    def surveillance_callback(self, request, response):
        self.active = request.data

        response.success = True

        if self.active:
            response.message = "Surveillance activée"
        else:
            response.message = "Surveillance désactivée"
        
        return response

    def publish_rotation(self):

        if not self.active:
            return
        
        msg = Twist()

        msg.angular.z = 100

        self.control_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)

    surveillance_node = SurveillanceNode()

    rclpy.spin(surveillance_node)

    surveillance_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
