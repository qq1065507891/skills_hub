"""安装服务"""
import hashlib
import json
import platform
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Skill


class InstallService:
    """技能安装服务"""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.skills_dir = Path.home() / ".skillhub" / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def _get_platform_display_path(self, skill_name: str, version: str) -> str:
        """根据操作系统返回对应的显示路径"""
        system = platform.system()
        user_home = Path.home()
        
        if system == "Windows":
            # Windows: C:\Users\用户名\.skillhub\skills
            return f"C:\\Users\\{user_home.name}\\.skillhub\\skills\\{skill_name}-{version}"
        elif system == "Linux":
            # Linux: 检查是否是 root 用户
            if user_home.name == "root":
                return f"/root/.skillhub/skills/{skill_name}-{version}"
            else:
                return f"/home/{user_home.name}/.skillhub/skills/{skill_name}-{version}"
        elif system == "Darwin":
            # macOS: /Users/用户名/.skillhub/skills
            return f"/Users/{user_home.name}/.skillhub/skills/{skill_name}-{version}"
        else:
            # 其他系统使用通用格式
            return f"~/.skillhub/skills/{skill_name}-{version}"

    def download_skill(self, skill_id: int) -> Dict[str, Any]:
        """下载技能包"""
        skill = self.db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ValueError("Skill not found")

        # 创建 zip 文件
        return self._create_skill_zip_package(skill)

    def _create_skill_zip_package(self, skill: Skill) -> Dict[str, Any]:
        """创建技能 zip 包"""
        # 确保上传目录存在
        upload_dir = self.settings.UPLOAD_DIR
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # 创建 zip 文件
        zip_filename = f"skill_{skill.id}_{skill.name.replace(' ', '_')}-{skill.version}.zip"
        zip_path = upload_path / zip_filename
        
        # 创建临时目录存放技能文件
        temp_dir = Path(tempfile.mkdtemp())
        skill_dir = temp_dir / f"{skill.name}-{skill.version}"
        skill_dir.mkdir(exist_ok=True)
        
        # 创建技能清单文件
        manifest = {
            "name": skill.name,
            "version": skill.version,
            "description": skill.description or "",
            "author": skill.author.username if skill.author else "Unknown",
            "license": skill.license or "MIT",
            "category": skill.category or "",
            "tags": skill.tags.split(",") if skill.tags else [],
        }
        
        with open(skill_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        # 创建一个简单的技能文件
        with open(skill_dir / "skill.py", "w", encoding="utf-8") as f:
            f.write(
                f'''"""
{skill.name} - {skill.description or 'No description'}
Version: {skill.version}
"""

def execute():
    """执行技能"""
    print(f"Executing {skill.name} v{skill.version}")

'''
            )
        
        # 创建 README
        with open(skill_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(f"# {skill.name}\n\n{skill.description or 'No description'}\n\n## Version\n{skill.version}\n")
        
        # 压缩为 zip
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir)
        
        return {
            "skill_id": skill.id,
            "name": skill.name,
            "version": skill.version,
            "file_path": str(zip_path),
            "install_path": str(zip_path),
            "checksum": self._calculate_file_checksum(zip_path),
            "success": True,
        }
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """计算文件的校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def get_skill_package_path(self, skill_id: int) -> Optional[str]:
        """获取技能包文件路径"""
        import os
        from typing import Optional
        
        skill = self.db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            return None
            
        # 尝试从上传目录查找最新上传的技能包
        upload_dir = Path(self.settings.UPLOAD_DIR) / self.settings.SKILL_PACKAGES_DIR
        if not upload_dir.exists():
            return None
            
        # 查找格式为 `skill_{skill_id}_*` 的文件
        matching_files = list(upload_dir.glob(f"skill_{skill_id}_*"))
        
        if not matching_files:
            return None
            
        # 根据最后修改时间排序，获取最新的文件
        matching_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return str(matching_files[0])

    def validate_skill(
        self, install_path: str, expected_checksum: Optional[str] = None
    ) -> bool:
        """验证已安装的技能"""
        path = Path(install_path)

        if not path.exists():
            return False

        # 如果是 zip 文件，验证校验和
        if path.suffix == '.zip':
            if expected_checksum:
                actual_checksum = self._calculate_file_checksum(path)
                return actual_checksum == expected_checksum
            return True
        
        # 如果是目录，检查必要文件
        if not (path / "manifest.json").exists():
            return False

        # 验证校验和
        if expected_checksum:
            actual_checksum = self._calculate_file_checksum(path)
            if actual_checksum != expected_checksum:
                return False

        return True

    def install_skill(self, skill_id: int) -> Dict[str, Any]:
        """完整安装流程"""
        # 1. 下载技能
        download_result = self.download_skill(skill_id)

        # 2. 验证技能
        is_valid = self.validate_skill(
            download_result["file_path"], download_result["checksum"]
        )

        if not is_valid:
            raise RuntimeError("Skill validation failed")

        # 3. 更新数据库
        skill = self.db.query(Skill).filter(Skill.id == skill_id).first()
        skill.download_count += 1
        self.db.commit()
        
        # 4. 解压技能到安装目录
        self._extract_skill_to_install_dir(
            download_result["file_path"],
            skill.name,
            skill.version
        )

        # 返回用户友好的路径（根据操作系统显示对应的路径格式）
        display_install_path = self._get_platform_display_path(skill.name, skill.version)
        
        return {
            "skill_id": skill.id,
            "name": skill.name,
            "version": skill.version,
            "file_path": download_result["file_path"],
            "install_path": display_install_path,
            "download_count": skill.download_count,
            "success": True,
        }
    
    def _extract_skill_to_install_dir(self, zip_path: str, skill_name: str, version: str) -> str:
        """将技能 zip 解压到安装目录"""
        import zipfile
        
        # 创建安装目录
        install_dir = self.skills_dir / f"{skill_name}-{version}"
        install_dir.mkdir(parents=True, exist_ok=True)
        
        # 解压 zip 文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 获取 zip 中的文件列表
            file_list = zip_ref.namelist()
            
            if file_list and len(file_list) > 0:
                # 检查是否有嵌套目录
                first_item = file_list[0].split('/')[0]
                all_same_prefix = bool(first_item) and all(name.startswith(first_item + '/') for name in file_list)
                
                if all_same_prefix:
                    # 如果所有文件都在同一个目录下，去掉前缀
                    for file_info in zip_ref.infolist():
                        if file_info.filename.endswith('/'):
                            continue
                        
                        # 去掉前面的目录前缀
                        dest_path = file_info.filename[len(first_item) + 1:]
                        if dest_path:
                            dest_file = install_dir / dest_path
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            # 复制文件内容
                            with zip_ref.open(file_info.filename) as source, \
                                 open(dest_file, 'wb') as dest:
                                dest.write(source.read())
                else:
                    # 否则直接解压
                    zip_ref.extractall(install_dir)
        
        return str(install_dir)

    def uninstall_skill(self, skill_id: int) -> Dict[str, Any]:
        """卸载技能"""
        skill = self.db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ValueError("Skill not found")

        # 删除安装目录
        skill_dir = self.skills_dir / f"{skill.name}-{skill.version}"
        if skill_dir.exists():
            import shutil

            shutil.rmtree(skill_dir)

        return {
            "skill_id": skill.id,
            "name": skill.name,
            "version": skill.version,
            "success": True,
        }

    def list_installed_skills(self) -> list[Dict[str, Any]]:
        """列出已安装的技能"""
        installed = []

        if not self.skills_dir.exists():
            return installed

        for item in self.skills_dir.iterdir():
            if item.is_dir():
                manifest_path = item / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                    installed.append(
                        {
                            "name": manifest.get("name"),
                            "version": manifest.get("version"),
                            "install_path": str(item),
                            "manifest": manifest,
                        }
                    )

        return installed
