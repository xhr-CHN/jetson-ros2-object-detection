"""Launch the pencil and tennis ball detector."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    arguments = [
        DeclareLaunchArgument(
            "model", default_value="models/pencil_tennis_yolo26n_best.pt"
        ),
        DeclareLaunchArgument("camera", default_value="0"),
        DeclareLaunchArgument("confidence", default_value="0.25"),
        DeclareLaunchArgument("image_size", default_value="640"),
        DeclareLaunchArgument("device", default_value="cuda:0"),
    ]
    detector = Node(
        package="pencil_tennis_detector",
        executable="detector_node",
        name="pencil_tennis_detector",
        output="screen",
        parameters=[
            {
                "model": LaunchConfiguration("model"),
                "camera": ParameterValue(LaunchConfiguration("camera"), value_type=int),
                "confidence": ParameterValue(
                    LaunchConfiguration("confidence"), value_type=float
                ),
                "image_size": ParameterValue(
                    LaunchConfiguration("image_size"), value_type=int
                ),
                "device": LaunchConfiguration("device"),
            }
        ],
    )
    return LaunchDescription(arguments + [detector])
