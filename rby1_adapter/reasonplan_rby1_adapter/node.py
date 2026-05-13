from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

from .controller import ControllerConfig, TrajectoryController
from .parser import parse_trajectory


class ReasonPlanRby1Adapter(Node):
    def __init__(self) -> None:
        super().__init__('reasonplan_rby1_adapter')

        self.declare_parameter('input_topic', '/reasonplan/predicted_answer')
        self.declare_parameter('output_topic', '/cmd_vel')
        self.declare_parameter('max_linear', 0.35)
        self.declare_parameter('max_angular', 0.8)
        self.declare_parameter('min_target_distance', 0.05)
        self.declare_parameter('lookahead_index', 2)
        self.declare_parameter('linear_gain', 0.45)
        self.declare_parameter('angular_gain', 1.2)
        self.declare_parameter('reverse_is_disabled', True)
        self.declare_parameter('stop_on_parse_failure', True)
        self.declare_parameter('max_points', 16)

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        self.publisher = self.create_publisher(Twist, output_topic, 10)
        self.subscription = self.create_subscription(String, input_topic, self.on_prediction, 10)

        self.get_logger().info(
            f'RB-Y1 ReasonPlan adapter started: {input_topic} -> {output_topic}'
        )

    def _make_controller(self) -> TrajectoryController:
        config = ControllerConfig(
            max_linear=float(self.get_parameter('max_linear').value),
            max_angular=float(self.get_parameter('max_angular').value),
            min_target_distance=float(self.get_parameter('min_target_distance').value),
            lookahead_index=int(self.get_parameter('lookahead_index').value),
            linear_gain=float(self.get_parameter('linear_gain').value),
            angular_gain=float(self.get_parameter('angular_gain').value),
            reverse_is_disabled=bool(self.get_parameter('reverse_is_disabled').value),
        )
        return TrajectoryController(config)

    def on_prediction(self, msg: String) -> None:
        max_points = int(self.get_parameter('max_points').value)
        trajectory = parse_trajectory(msg.data, max_points=max_points)

        if trajectory is None:
            self.get_logger().warn('Failed to parse ReasonPlan trajectory.')
            if bool(self.get_parameter('stop_on_parse_failure').value):
                self.publisher.publish(Twist())
            return

        twist = self._make_controller().to_twist(trajectory)
        self.publisher.publish(twist)
        self.get_logger().info(
            f'Parsed {len(trajectory)} points -> cmd_vel '
            f'linear.x={twist.linear.x:.3f}, angular.z={twist.angular.z:.3f}'
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ReasonPlanRby1Adapter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
