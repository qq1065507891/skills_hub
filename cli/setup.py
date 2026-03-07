#!/usr/bin/env python3
"""SkillHub CLI 安装脚本"""

from setuptools import setup, find_packages

setup(
    name="skillhub-cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "skillhub = skillhub_cli.main:cli",
        ],
    },
    author="SkillHub Team",
    description="SkillHub 命令行工具",
    license="MIT",
    keywords="ai agent skills",
    url="https://github.com/skillhub-org/skillhub",
)
