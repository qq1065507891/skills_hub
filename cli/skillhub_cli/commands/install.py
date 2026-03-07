from typing import Optional
from typing import Optional

import click

from skillhub_cli.utils.api_client import SkillHubAPIClient
from skillhub_cli.utils.path_utils import convert_to_local_path, get_local_install_path


@click.group()
def install():
    """技能安装管理"""
    pass


@install.command()
@click.argument("skill_identifier", type=str)
@click.option("--version", type=str, default=None, help="指定要安装的版本号")
@click.option("--api-url", default="http://localhost:8000", help="API 服务器地址")
def add(skill_identifier: str, version: Optional[str], api_url: str):
    """安装指定技能（下载到本地机器环境，类似于 npm）"""
    import os
    import shutil
    import tempfile
    import zipfile
    
    try:
        client = SkillHubAPIClient(api_url)
        
        # 判断是 ID 还是名称
        if skill_identifier.isdigit():
            skill_id = int(skill_identifier)
            click.echo(f"正在获取技能 ID: {skill_id}...")
            skill = client.get_skill(skill_id)
        else:
            # 通过名称查找技能
            click.echo(f"正在查找技能名称: {skill_identifier}...")
            skills = client.search_skills(skill_identifier)
            
            if not skills.get("items"):
                click.secho(f"✗ 未找到技能: {skill_identifier}", fg="red")
                return
            
            # 使用第一个匹配的技能
            skill = skills["items"][0]
            if version:
                if skill.get("version") != version:
                    click.secho(f"⚠ 提示: 最新找到的版本是 {skill.get('version')}，与您要求的 {version} 可能不符", fg="yellow")
                    
        skill_id = skill["id"]
        skill_name = skill.get("name", "unknown")
        skill_version = skill.get("version", "unknown")
        
        click.echo(f"准备下载技能: {skill_name} (ID: {skill_id})")
        
        # 转换路径为本地格式
        local_dir = get_local_install_path(skill_name, skill_version)
        if os.path.exists(local_dir):
            click.secho(f"⚠ 警告: 目录 {local_dir} 已经被占用，将被覆盖！", fg="yellow")
            shutil.rmtree(local_dir)
            
        click.echo("正在下载...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp_path = tmp.name
            
        try:
            client.download_skill_file(skill_id, tmp_path)
            
            click.echo(f"正在解压技能包到: {local_dir}")
            os.makedirs(local_dir, exist_ok=True)
            with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                # 检查是否有嵌套根目录
                file_list = zip_ref.namelist()
                if file_list and len(file_list) > 0:
                    first_item = file_list[0].split('/')[0]
                    all_same_prefix = bool(first_item) and all(name.startswith(first_item + '/') for name in file_list)
                    
                    if all_same_prefix:
                        # 如果所有文件都在同一个目录下，去掉前缀
                        for member in file_list:
                            # 忽略根目录自身
                            if member == first_item + '/':
                                continue
                            
                            # 获取去掉前缀的相对路径
                            relative_path = member[len(first_item) + 1:]
                            if not relative_path:
                                continue
                                
                            target_path = os.path.join(local_dir, relative_path)
                            
                            if member.endswith('/'):
                                os.makedirs(target_path, exist_ok=True)
                            else:
                                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                                with zip_ref.open(member) as source, open(target_path, "wb") as target:
                                    shutil.copyfileobj(source, target)
                    else:
                        zip_ref.extractall(local_dir)
            
            click.secho(f"✓ '{skill_name}' 下载并安装成功！", fg="green")
            click.echo(f"  版本: {skill_version}")
            click.echo(f"  本地安装路径: {local_dir}")
            
            # 由于没有触发服务器的 install 接口，如果需要计数可以在这发一次空统计请求。

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        click.secho(f"✗ 安装失败: {e}", fg="red")


@install.command()
@click.argument("skill_id", type=int)
@click.option("--api-url", default="http://localhost:8000", help="API 服务器地址")
def download(skill_id: int, api_url: str):
    """仅下载技能包，不执行完整安装"""
    click.echo(f"正在下载技能 ID: {skill_id}...")

    try:
        client = SkillHubAPIClient(api_url)
        result = client.download_skill(skill_id)

        if result.get("success"):
            # 转换路径为本地格式
            skill_name = result.get('name', 'unknown')
            version = result.get('version', 'unknown')
            local_path = convert_to_local_path(
                result.get('install_path', ''),
                skill_name,
                version
            )
            
            click.secho(f"✓ 技能下载成功！", fg="green")
            click.echo(f"  名称: {skill_name}")
            click.echo(f"  版本: {version}")
            click.echo(f"  保存路径: {local_path}")
            click.echo(f"  校验和: {result.get('checksum')}")
        else:
            click.secho("✗ 技能下载失败", fg="red")
    except Exception as e:
        click.secho(f"✗ 下载失败: {e}", fg="red")


@install.command()
@click.argument("skill_id", type=int)
@click.option("--api-url", default="http://localhost:8000", help="API 服务器地址")
def remove(skill_id: int, api_url: str):
    """卸载指定技能"""
    click.echo(f"正在卸载技能 ID: {skill_id}...")

    try:
        client = SkillHubAPIClient(api_url)
        result = client.uninstall_skill(skill_id)

        if result.get("success"):
            click.secho(f"✓ 技能卸载成功！", fg="green")
            click.echo(f"  名称: {result.get('name')}")
            click.echo(f"  版本: {result.get('version')}")
        else:
            click.secho("✗ 技能卸载失败", fg="red")
    except Exception as e:
        click.secho(f"✗ 卸载失败: {e}", fg="red")


@install.command(name="list")
@click.option("--api-url", default="http://localhost:8000", help="API 服务器地址")
def list_installed(api_url: str):
    """列出已安装的技能"""
    click.echo("正在获取已安装技能列表...")

    try:
        client = SkillHubAPIClient(api_url)
        skills = client.list_installed_skills()

        if not skills:
            click.echo("没有已安装的技能")
            return

        click.echo("\n已安装的技能:")
        click.echo("-" * 60)

        for i, skill in enumerate(skills, 1):
            manifest = skill.get("manifest", {})
            skill_name = manifest.get('name', 'Unknown')
            version = manifest.get('version', 'Unknown')
            
            # 转换路径为本地格式
            remote_path = skill.get('install_path', '')
            local_path = convert_to_local_path(remote_path, skill_name, version)
            
            click.echo(
                f"{i}. {skill_name} v{version}"
            )
            click.echo(f"   描述: {manifest.get('description', 'No description')}")
            click.echo(f"   作者: {manifest.get('author', 'Unknown')}")
            click.echo(f"   安装路径: {local_path}")
            click.echo()

        click.echo(f"总计: {len(skills)} 个已安装技能")
    except Exception as e:
        click.secho(f"✗ 获取列表失败: {e}", fg="red")


@install.command()
@click.argument("install_path")
@click.option("--checksum", help="期望的校验和")
@click.option("--api-url", default="http://localhost:8000", help="API 服务器地址")
def validate(install_path: str, checksum: Optional[str], api_url: str):
    """验证已安装的技能"""
    click.echo(f"正在验证技能: {install_path}")

    try:
        client = SkillHubAPIClient(api_url)
        result = client.validate_skill(install_path, checksum)

        if result.get("is_valid"):
            click.secho("✓ 技能验证通过！", fg="green")
        else:
            click.secho("✗ 技能验证失败", fg="red")
    except Exception as e:
        click.secho(f"✗ 验证失败: {e}", fg="red")
