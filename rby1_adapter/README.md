# ReasonPlan RB-Y1 Adapter

This package is a minimal ROS 2 adapter for using ReasonPlan-style trajectory outputs with an RB-Y1 mobile base.

It does **not** modify the ReasonPlan training or CARLA evaluation pipeline. It only converts generated text such as:

```text
planning trajectory should be: (0.5, 0.0), (1.0, 0.2), (1.5, 0.3)
```

into `geometry_msgs/msg/Twist` on `/cmd_vel`.

## Assumptions

- The ReasonPlan trajectory is in the robot ego frame.
- `x` is forward.
- `y` is left.
- RB-Y1 accepts `linear.x` and `angular.z` on `/cmd_vel`.
- This package is for low-speed testing first. Keep a safety stop available.

## Build

From a ROS 2 workspace:

```bash
mkdir -p ~/rby1_reasonplan_ws/src
cd ~/rby1_reasonplan_ws/src
ln -s /path/to/rby1_ReasonPlan/rby1_adapter .
cd ~/rby1_reasonplan_ws
colcon build --packages-select reasonplan_rby1_adapter
source install/setup.bash
```

## Run

```bash
ros2 launch reasonplan_rby1_adapter adapter.launch.py
```

or:

```bash
ros2 run reasonplan_rby1_adapter adapter_node
```

## Test without the model

In another terminal:

```bash
ros2 topic pub --once /reasonplan/predicted_answer std_msgs/msg/String \
"{data: 'The future planning trajectory should be: (0.5, 0.0), (1.0, 0.2), (1.5, 0.3).'}"
```

Check output:

```bash
ros2 topic echo /cmd_vel
```

## Parameters

| Parameter | Default | Meaning |
|---|---:|---|
| `input_topic` | `/reasonplan/predicted_answer` | Text output topic from ReasonPlan |
| `output_topic` | `/cmd_vel` | Twist command topic |
| `max_linear` | `0.35` | Maximum `linear.x` in m/s |
| `max_angular` | `0.8` | Maximum `angular.z` in rad/s |
| `lookahead_index` | `2` | Which waypoint to track |
| `linear_gain` | `0.45` | Distance-to-speed gain |
| `angular_gain` | `1.2` | Heading-error-to-yaw-rate gain |
| `stop_on_parse_failure` | `true` | Publish zero Twist if parsing fails |

## Connection to ReasonPlan

Current closed-loop code in this repository appears to use the front camera image and text prompt through `team_code/dataset_utils.py`, then decodes the generated text into a planning trajectory. This adapter starts after that point:

```text
ReasonPlan predicted_answer
        ↓
parse planning trajectory
        ↓
lookahead controller
        ↓
/cmd_vel
```

For real robot testing, begin with low `max_linear` and `max_angular` values.
