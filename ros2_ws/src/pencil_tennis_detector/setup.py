from glob import glob
from setuptools import find_packages, setup


package_name = "pencil_tennis_detector"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="xhr",
    maintainer_email="xhr@example.com",
    description="YOLO26n pencil and tennis ball detection and test recording.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "detector_node = pencil_tennis_detector.detector_node:main",
            "test_recorder_node = pencil_tennis_detector.test_recorder_node:main",
        ],
    },
)
