from setuptools import find_packages, setup


package_name = 'control_drone'
package_msg  = 'pkg_msg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='evan.tassel',
    maintainer_email='evan.tassel@todo.todo',
    description='Manual control for Tello',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'manual_control = control_drone.manual_control:main',
            'tello_behavior = control_drone.tello_behavior:main',
            'surveillance = control_drone.surveillance_node:main'
        ],
    },
)
