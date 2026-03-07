"""路径工具模块"""
import os
import platform
from pathlib import Path


def get_local_install_path(skill_name: str, version: str) -> str:
    """
    根据本地操作系统返回对应的安装路径
    
    Args:
        skill_name: 技能名称
        version: 技能版本
        
    Returns:
        本地化的安装路径字符串
    """
    system = platform.system()
    user_home = Path.home()
    skill_dir = f"{skill_name}-{version}"
    
    if system == "Windows":
        # Windows: C:\Users\用户名\.skillhub\skills
        return f"C:\\Users\\{user_home.name}\\.skillhub\\skills\\{skill_dir}"
    elif system == "Linux":
        # Linux: 检查是否是 root 用户
        if user_home.name == "root":
            return f"/root/.skillhub/skills/{skill_dir}"
        else:
            return f"/home/{user_home.name}/.skillhub/skills/{skill_dir}"
    elif system == "Darwin":
        # macOS: /Users/用户名/.skillhub/skills
        return f"/Users/{user_home.name}/.skillhub/skills/{skill_dir}"
    else:
        # 其他系统使用通用格式
        return f"~/.skillhub/skills/{skill_dir}"


def convert_to_local_path(remote_path: str, skill_name: str, version: str) -> str:
    """
    将远程路径转换为本地路径
    
    Args:
        remote_path: 后端返回的路径
        skill_name: 技能名称
        version: 技能版本
        
    Returns:
        本地化的路径字符串
    """
    # 直接根据本地操作系统生成路径，忽略远程路径格式
    return get_local_install_path(skill_name, version)
