from setuptools import find_packages, setup

package_name = 'reasonplan_rby1_adapter'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/adapter.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='minho0',
    maintainer_email='alsgh000118@naver.com',
    description='ROS 2 adapter that converts ReasonPlan planning trajectory text into RB-Y1 /cmd_vel commands.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'adapter_node = reasonplan_rby1_adapter.node:main',
        ],
    },
)
