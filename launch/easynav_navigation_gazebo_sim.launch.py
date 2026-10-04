#
# Copyright (c) 2026 Francisco Martín Rico
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    Shutdown,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


PACKAGE_NAME = 'easynav_playground_omni'


def generate_launch_description():
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='maze2',
        description='Gazebo world to launch',
    )
    robot_arg = DeclareLaunchArgument(
        'robot',
        default_value='3w_v2',
        description='Robot model to spawn',
        choices=['3w', '3w_v2', '4w', '5w', '6w'],
    )
    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=PathJoinSubstitution([
            FindPackageShare(PACKAGE_NAME),
            'config',
            'easynav_costmap_rpp.params.yaml',
        ]),
        description='EasyNav ROS 2 parameters file',
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([
            FindPackageShare(PACKAGE_NAME),
            'rviz',
            'easynav_costmap.rviz',
        ]),
        description='RViz2 configuration file',
    )
    map_override_file_arg = DeclareLaunchArgument(
        'map_override_file',
        default_value=PathJoinSubstitution([
            FindPackageShare(PACKAGE_NAME),
            'config',
            'map_overrides',
            LaunchConfiguration('world'),
            'map.yaml',
        ]),
        description='EasyNav map selection matching the Gazebo world',
    )

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([
            FindPackageShare(PACKAGE_NAME),
            'launch',
            'gazebo_sim.launch.py',
        ])),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'robot': LaunchConfiguration('robot'),
            'use_sim_time': 'true',
        }.items(),
    )

    easynav_system = Node(
        package='easynav_system',
        executable='system_main',
        parameters=[
            LaunchConfiguration('params_file'),
            LaunchConfiguration('map_override_file'),
        ],
        output='screen',
        on_exit=Shutdown(reason='EasyNav system_main exited'),
    )
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        world_arg,
        robot_arg,
        params_file_arg,
        rviz_config_arg,
        map_override_file_arg,
        gazebo_launch,
        TimerAction(period=5.0, actions=[easynav_system]),
        rviz,
    ])
