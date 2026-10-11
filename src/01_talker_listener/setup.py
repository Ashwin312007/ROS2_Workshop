"""Build script for the Stage 1 ament_python package.

`data_files` decides what lands in the installed share/ directory, and
`entry_points` creates the `ros2 run talker_listener <name>` executables.
"""

import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'talker_listener'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        # ament resource marker: makes the package discoverable by the index.
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        # Manifest, needed by tools such as `ros2 pkg`.
        ('share/' + package_name, ['package.xml']),
        # Launch files, installed so `ros2 launch` can find them by package name.
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='User',
    maintainer_email='user@todo.todo',
    description='Minimal ROS 2 publisher and subscriber package in Python',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        # Maps executable names to module:function entry points.
        'console_scripts': [
            'talker = talker_listener.talker:main',
            'listener = talker_listener.listener:main',
        ],
    },
)
