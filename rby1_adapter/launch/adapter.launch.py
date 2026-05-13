from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='reasonplan_rby1_adapter',
            executable='adapter_node',
            name='reasonplan_rby1_adapter',
            output='screen',
            parameters=[{
                'input_topic': '/reasonplan/predicted_answer',
                'output_topic': '/cmd_vel',
                'max_linear': 0.35,
                'max_angular': 0.8,
                'lookahead_index': 2,
                'linear_gain': 0.45,
                'angular_gain': 1.2,
                'stop_on_parse_failure': True,
            }],
        )
    ])
