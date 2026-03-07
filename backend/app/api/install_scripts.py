"""安装脚本生成 API"""
import json
import zipfile
from io import BytesIO
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models.skill import Skill
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


def _create_skill_zip(skill: Skill, base_url: str) -> BytesIO:
    """创建技能 zip 包"""
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        manifest = {
            "name": skill.name,
            "version": skill.version or "1.0.0",
            "description": skill.description or "",
            "author": skill.author.username if skill.author else "Unknown",
            "license": skill.license or "MIT",
            "category": skill.category or "",
            "tags": skill.tags.split(",") if skill.tags else [],
        }
        zipf.writestr(f"{skill.name}/manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

        skill_code = f'''"""
{skill.name} - {skill.description or 'No description'}
Version: {skill.version or '1.0.0'}
"""

def execute():
    """执行技能"""
    print(f"Executing {skill.name} v{skill.version or '1.0.0'}")
'''
        zipf.writestr(f"{skill.name}/skill.py", skill_code)

        readme = f"# {skill.name}\n\n{skill.description or 'No description'}\n\n## Version\n{skill.version or '1.0.0'}\n"
        zipf.writestr(f"{skill.name}/README.md", readme)

    buffer.seek(0)
    return buffer


def _generate_bash_script(skill: Skill, base_url: str) -> str:
    """生成 Bash 安装脚本"""
    version = skill.version or "1.0.0"
    return f'''#!/bin/bash
set -e

SKILL_NAME="{skill.name}"
SKILL_VERSION="{version}"
INSTALL_DIR="$HOME/.skillhub/skills/${{SKILL_NAME}}-${{SKILL_VERSION}}"
ZIP_URL="{base_url}/api/install-scripts/{skill.id}/zip"

echo "📦 正在安装 $SKILL_NAME v$SKILL_VERSION..."

mkdir -p "$INSTALL_DIR"

cd "$INSTALL_DIR" || exit 1

if command -v curl &> /dev/null; then
    curl -sSL "$ZIP_URL" -o skill.zip
elif command -v wget &> /dev/null; then
    wget -q "$ZIP_URL" -O skill.zip
else
    echo "❌ 错误: 需要 curl 或 wget"
    exit 1
fi

unzip -q skill.zip
rm skill.zip

echo ""
echo "✅ 安装成功！"
echo "   名称: $SKILL_NAME"
echo "   版本: $SKILL_VERSION"
echo "   路径: $INSTALL_DIR"
'''


def _generate_powershell_script(skill: Skill, base_url: str) -> str:
    """生成 PowerShell 安装脚本"""
    version = skill.version or "1.0.0"
    return f'''$ErrorActionPreference = "Stop"

$SkillName = "{skill.name}"
$SkillVersion = "{version}"
$InstallDir = Join-Path $env:USERPROFILE ".skillhub\\skills\\${{SkillName}}-${{SkillVersion}}"
$ZipUrl = "{base_url}/api/install-scripts/{skill.id}/zip"

Write-Host "📦 正在安装 $SkillName v$SkillVersion..." -ForegroundColor Cyan

if (-not (Test-Path $InstallDir)) {{
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}}

$ZipPath = Join-Path $InstallDir "skill.zip"
Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath -UseBasicParsing

Expand-Archive -Path $ZipPath -DestinationPath $InstallDir -Force
Remove-Item $ZipPath -Force

Write-Host ""
Write-Host "✅ 安装成功！" -ForegroundColor Green
Write-Host "   名称: $SkillName"
Write-Host "   版本: $SkillVersion"
Write-Host "   路径: $InstallDir"
'''


def _generate_python_script(skill: Skill, base_url: str) -> str:
    """生成 Python 安装脚本"""
    version = skill.version or "1.0.0"
    return f'''#!/usr/bin/env python3
import os
import sys
import zipfile
from pathlib import Path

try:
    import urllib.request
except ImportError:
    print("❌ 错误: 需要 urllib.request")
    sys.exit(1)

SKILL_NAME = "{skill.name}"
SKILL_VERSION = "{version}"
BASE_URL = "{base_url}"

home = Path.home()
install_dir = home / ".skillhub" / "skills" / f"{{SKILL_NAME}}-{{SKILL_VERSION}}"
zip_url = f"{{BASE_URL}}/api/install-scripts/{skill.id}/zip"

print(f"📦 正在安装 {{SKILL_NAME}} v{{SKILL_VERSION}}...")

install_dir.mkdir(parents=True, exist_ok=True)

zip_path = install_dir / "skill.zip"

try:
    urllib.request.urlretrieve(zip_url, zip_path)
except Exception as e:
    print(f"❌ 下载失败: {{e}}")
    sys.exit(1)

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(install_dir)

zip_path.unlink()

print()
print("✅ 安装成功！")
print(f"   名称: {{SKILL_NAME}}")
print(f"   版本: {{SKILL_VERSION}}")
print(f"   路径: {{install_dir}}")
'''


@router.get("/{skill_id}/zip")
def download_skill_zip(
    skill_id: int,
    db: Session = Depends(get_db)
):
    """下载技能 zip 包"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    base_url = "http://localhost:8000"
    buffer = _create_skill_zip(skill, base_url)

    skill.download_count += 1
    db.commit()

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={skill.name}-{skill.version or '1.0.0'}.zip"}
    )


@router.get("/{skill_id}/bash")
def get_bash_script(
    skill_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取 Bash 安装脚本"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost:8000')}"
    script = _generate_bash_script(skill, base_url)

    return Response(
        content=script,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=install-{skill.name}.sh"}
    )


@router.get("/{skill_id}/powershell")
def get_powershell_script(
    skill_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取 PowerShell 安装脚本"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost:8000')}"
    script = _generate_powershell_script(skill, base_url)

    return Response(
        content=script,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=install-{skill.name}.ps1"}
    )


@router.get("/{skill_id}/python")
def get_python_script(
    skill_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取 Python 安装脚本"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost:8000')}"
    script = _generate_python_script(skill, base_url)

    return Response(
        content=script,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=install-{skill.name}.py"}
    )


@router.get("/{skill_id}/commands")
def get_install_commands(
    skill_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取所有安装命令"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost:8000')}"

    return {
        "skill_id": skill.id,
        "name": skill.name,
        "version": skill.version or "1.0.0",
        "commands": {
            "bash": f"curl -sSL {base_url}/api/install-scripts/{skill.id}/bash | bash",
            "powershell": f"irm {base_url}/api/install-scripts/{skill.id}/powershell | iex",
            "python": f"python <(curl -sSL {base_url}/api/install-scripts/{skill.id}/python)",
            "zip": f"{base_url}/api/install-scripts/{skill.id}/zip"
        }
    }
