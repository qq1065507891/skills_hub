"""安装相关 API"""
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user_optional
from app.dependencies.database import get_db
from app.models.skill import Skill
from app.models.user import User
from app.services.install_service import InstallService

router = APIRouter()


@router.post("/{skill_id}", response_model=Dict[str, Any])
def install_skill(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """完整安装技能流程"""
    try:
        service = InstallService(db)
        result = service.install_skill(skill_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{skill_id}/download", response_model=Dict[str, Any])
def download_skill_only(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """仅下载技能包，不执行完整安装"""
    try:
        service = InstallService(db)
        result = service.download_skill(skill_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{skill_id}/download-file")
def download_skill_file(
    skill_id: int,
    version: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """下载技能 zip 文件，支持可选的 version 历史版本 ID 查询"""
    from io import BytesIO
    from fastapi.responses import FileResponse, StreamingResponse
    import os
    
    try:
        service = InstallService(db)
        
        # 1. 查询此技能
        from app.models.skill import Skill
        from app.models.skill_version import SkillVersion
        
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="技能不存在")
            
        target_version_str = skill.version
            
        # 提取真实文件路径（若指定了历史 version，这里可做更进一步的历史包匹配，因为文件带时间戳可推断）
        # 目前暂时返回最新的或 fallback
        real_file_path = service.get_skill_package_path(skill_id)
        
        if version:
            v_record = db.query(SkillVersion).filter(SkillVersion.id == version, SkillVersion.skill_id == skill_id).first()
            if not v_record:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="版本记录不存在")
            # 增加下载计数
            v_record.download_count += 1
            target_version_str = v_record.version
            
        # 给当前 skill 增加计数
        skill.download_count += 1
        db.commit()

        # 2. 如果存在真实资源文件，直接流式下载真实文件
        if real_file_path and os.path.exists(real_file_path):
            return FileResponse(
                path=real_file_path,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename=skill_{skill.name.replace(' ', '_')}-{target_version_str}.zip"
                }
            )
        
        # 3. Fallback: 在内存中创建 mock 的 zip 文件
        import zipfile
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            manifest = {
                "name": skill.name,
                "version": target_version_str,
                "description": skill.description or "",
                "author": skill.author.username if skill.author else "Unknown",
                "license": skill.license or "MIT",
                "category": skill.category or "",
                "tags": skill.tags.split(",") if skill.tags else [],
            }
            zipf.writestr(f"{skill.name}/manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            
            skill_code = f'''"""\n{skill.name} - {skill.description}\nVersion: {target_version_str}\n"""\n\ndef execute():\n    print(f"Executing {skill.name} v{target_version_str}")\n'''
            zipf.writestr(f"{skill.name}/skill.py", skill_code)
            
            readme = f"# {skill.name}\n\n{skill.description or 'No description'}\n\n## Version\n{target_version_str}\n"
            zipf.writestr(f"{skill.name}/README.md", readme)
        
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=skill_{skill.name.replace(' ', '_')}-{target_version_str}.zip"
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载失败：{str(e)}",
        )


@router.post("/{skill_id}/uninstall", response_model=Dict[str, Any])
def uninstall_skill(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """卸载技能"""
    try:
        service = InstallService(db)
        result = service.uninstall_skill(skill_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/installed", response_model=List[Dict[str, Any]])
def list_installed_skills(
    db: Session = Depends(get_db),
):
    """列出已安装的技能"""
    service = InstallService(db)
    return service.list_installed_skills()


@router.post("/validate", response_model=Dict[str, Any])
def validate_installed_skill(
    install_path: str,
    expected_checksum: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """验证已安装的技能"""
    service = InstallService(db)
    is_valid = service.validate_skill(install_path, expected_checksum)
    return {
        "install_path": install_path,
        "is_valid": is_valid,
    }
