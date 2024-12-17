import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
import xacro


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    gazebo_params_file = os.path.join(get_package_share_directory("diablo_bot"),'config','gazebo_params.yaml')

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
                ),
                    launch_arguments={'extra_gazebo_args': '--ros-args --params-file ' + gazebo_params_file}.items()
             )
    
    pkg_path = os.path.join(get_package_share_directory('diablo_bot'))
    xacro_file = os.path.join(pkg_path,'description','robot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    
    # Create a robot_state_publisher node
    params = {'robot_description': robot_description_config.toxml(), 'use_sim_time': use_sim_time}
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'diffbot',
                                   '-x', '0.0',
                                   '-y', '0.0',
                                   '-z', '0.53',
                                   '-R', '0.0',
                                   '-P', '0.0',
                                   '-Y', '0.0',
                                   '-package_to_model',
                                   ],
                        output='screen')

    joint_state_broadcaster= Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"]
    )
    
    diff_drive_base_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_base_controller"],
    )

    trajectory_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["trajectory_controller"]
    )

    position_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["position_controller"]
    )

    
    # Launch them all!
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),
        node_robot_state_publisher,
        gazebo,
        spawn_entity,
        joint_state_broadcaster,
        trajectory_controller,
        diff_drive_base_controller
    ])