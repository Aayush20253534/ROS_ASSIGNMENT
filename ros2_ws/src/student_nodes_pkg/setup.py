from setuptools import find_packages, setup

package_name = 'student_nodes_pkg'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Register the package with the ament resource index.
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # Install the package manifest.
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='Student-authored ROS 2 nodes for the React + rosbridge starter.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Each line registers one runnable node:
            #   'name_you_type_in_ros2_run = package.module:function'
            #
            # Run the example with:
            #   ros2 run student_nodes_pkg example_publisher
            'example_publisher = student_nodes_pkg.example_publisher:main',

            # Complete starter demo nodes:
            #   ros2 run student_nodes_pkg temperature_publisher
            #   ros2 run student_nodes_pkg temperature_recorder
            'temperature_publisher = student_nodes_pkg.temperature_publisher:main',
            'temperature_recorder = student_nodes_pkg.temperature_recorder:main',
            'simulated_vehicle = student_nodes_pkg.simulated_vehicle_node:main',

            # ADD YOUR OWN NODES BELOW, one per line. For example:
            #   'my_node = student_nodes_pkg.my_node:main',
        ],
    },
)
