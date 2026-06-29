from setuptools import find_packages, setup

package_name = 'button_listener_pkg'

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
    description='Example button listener node for the React + rosbridge starter.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # This makes `ros2 run button_listener_pkg button_listener` work.
            # Format: 'executable_name = package.module:function'
            'button_listener = button_listener_pkg.button_listener:main',
        ],
    },
)
