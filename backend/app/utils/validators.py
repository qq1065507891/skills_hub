"""验证工具"""
import re

VALID_LICENSES = [
    "MIT",
    "Apache-2.0",
    "GPL-3.0",
    "BSD-3-Clause",
    "BSD-2-Clause",
    "MPL-2.0",
    "LGPL-3.0",
    "AGPL-3.0",
    "Unlicense",
    "CC0-1.0",
]

VALID_CATEGORIES = [
    "开发工具",
    "机器学习",
    "数据分析",
    "Web开发",
    "移动开发",
    "测试",
    "DevOps",
    "文档",
    "设计",
    "安全",
    "其他",
]


def validate_version(version):
    if not version:
        return False
    pattern = r"^\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def validate_license(license_type):
    if license_type is None:
        return True
    return license_type in VALID_LICENSES


def validate_category(category):
    if category is None:
        return True
    return category in VALID_CATEGORIES


def validate_tags(tags):
    if tags is None or tags.strip() == "":
        return True
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    if len(tag_list) > 10:
        return False
    for tag in tag_list:
        if len(tag) < 1 or len(tag) > 50:
            return False
    return True


def parse_tags(tags):
    if tags is None or tags.strip() == "":
        return []
    return [t.strip() for t in tags.split(",") if t.strip()]


def join_tags(tags):
    return ", ".join(tags)
