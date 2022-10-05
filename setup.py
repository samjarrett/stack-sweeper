"""
Setup script.
"""

import os
from setuptools import find_packages, setup

if __name__ == "__main__":
    with open("requirements.in") as requirements:
        setup(
            name="stack-sweeper",
            use_scm_version="BUILD_STAGE" not in os.environ,
            description="Deletes stacks that meet certain age criteria",
            author="Sam Jarrett",
            author_email="samstah@gmail.com",
            url="",
            # long_description="",
            classifiers=[
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.8",
            ],
            packages=find_packages(exclude=["tests"]),
            include_package_data=True,
            entry_points={
                "console_scripts": ["stack-sweeper = stack_sweeper.cli:entry_point"]
            },
            python_requires=">=3.6",
            setup_requires=["setuptools >= 18.0", "setuptools_scm"],
            install_requires=requirements.readlines(),
            test_suite="tests",
        )
