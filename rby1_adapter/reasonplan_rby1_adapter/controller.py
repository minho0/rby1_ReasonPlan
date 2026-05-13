import math
from dataclasses import dataclass
from typing import Sequence, Tuple

from geometry_msgs.msg import Twist

TrajectoryPoint = Tuple[float, float]


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


@dataclass
class ControllerConfig:
    max_linear: float = 0.35
    max_angular: float = 0.8
    min_target_distance: float = 0.05
    lookahead_index: int = 2
    linear_gain: float = 0.45
    angular_gain: float = 1.2
    reverse_is_disabled: bool = True


class TrajectoryController:
    """Convert ego-frame ReasonPlan waypoints into a ROS 2 Twist command.

    Assumption:
      - x is forward in base_link/ego frame.
      - y is left in base_link/ego frame.
      - RB-Y1 is controlled with linear.x and angular.z only.
    """

    def __init__(self, config: ControllerConfig | None = None):
        self.config = config or ControllerConfig()

    def select_target(self, trajectory: Sequence[TrajectoryPoint]) -> TrajectoryPoint | None:
        if not trajectory:
            return None

        idx = _clamp(int(self.config.lookahead_index), 0, len(trajectory) - 1)
        target = trajectory[int(idx)]

        # If the selected point is too close, pick the first farther point.
        for point in trajectory[int(idx):]:
            dist = math.hypot(point[0], point[1])
            if dist >= self.config.min_target_distance:
                return point
        return target

    def to_twist(self, trajectory: Sequence[TrajectoryPoint]) -> Twist:
        twist = Twist()
        target = self.select_target(trajectory)
        if target is None:
            return twist

        x, y = float(target[0]), float(target[1])
        distance = math.hypot(x, y)
        if distance < self.config.min_target_distance:
            return twist

        heading_error = math.atan2(y, x)

        # If the target is behind the robot, rotate in place instead of reversing.
        if self.config.reverse_is_disabled and x < 0.0:
            linear_x = 0.0
        else:
            linear_x = self.config.linear_gain * max(0.0, x)

        angular_z = self.config.angular_gain * heading_error

        twist.linear.x = _clamp(linear_x, -self.config.max_linear, self.config.max_linear)
        twist.angular.z = _clamp(angular_z, -self.config.max_angular, self.config.max_angular)
        return twist
