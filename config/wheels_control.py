import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

class JointAggregator(Node):
    def __init__(self):
        super().__init__('joint_aggregator')

        # Define joint topics
        left_joints = [f"/l{i}_controller/command" for i in range(1, 5)]
        right_joints = [f"/r{i}_controller/command" for i in range(1, 5)]

        # Create publishers for real joints
        self.left_pubs = [self.create_publisher(Float64, joint, 10) for joint in left_joints]
        self.right_pubs = [self.create_publisher(Float64, joint, 10) for joint in right_joints]

        # Create subscribers for virtual joints
        self.create_subscription(Float64, "/left_virtual_joint/command", 
                                 lambda msg: self.redistribute_velocity(msg, self.left_pubs), 10)
        self.create_subscription(Float64, "/right_virtual_joint/command", 
                                 lambda msg: self.redistribute_velocity(msg, self.right_pubs), 10)

    def redistribute_velocity(self, virtual_joint, real_pubs):
        velocity = virtual_joint.data  # Get velocity from virtual joint
        for pub in real_pubs:
            msg = Float64()
            msg.data = velocity / len(real_pubs)  # Distribute equally
            pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = JointAggregator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__=="__main__":
    main()
