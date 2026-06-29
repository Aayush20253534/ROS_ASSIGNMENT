from setuptools import find_packages, setup

package_name = 'gui_interface'

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
    description='Shared topic-name definitions for the React + rosbridge starter.',
    license='MIT',
    tests_require=['pytest'],
    # This package is a library only -> no console_scripts / no nodes to run.
    entry_points={
        'console_scripts': [],
    },
)
