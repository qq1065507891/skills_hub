"""发布命令模块"""

import os

import click

from skillhub_cli.utils.api_client import SkillHubAPIClient


@click.command()
@click.argument("skill_package")
@click.option("--skill-id", "-s", type=int, required=True, help="技能ID")
@click.option("--notes", "-n", help="发布说明")
@click.option("--user-id", "-u", type=int, default=1, help="用户ID")
@click.option("--api-url", "-a", default="http://localhost:8000", help="API地址")
def publish(skill_package, skill_id, notes, user_id, api_url):
    """发布技能包

    SKILL_PACKAGE: 技能包文件路径（支持 zip、tar.gz、tgz 格式）
    """
    click.echo(f"正在发布技能...")
    click.echo(f"  技能ID: {skill_id}")
    click.echo(f"  技能包: {skill_package}")
    if notes:
        click.echo(f"  发布说明: {notes}")

    # 验证文件存在
    if not os.path.exists(skill_package):
        click.echo(click.style(f"错误: 文件不存在 - {skill_package}", fg="red"), err=True)
        return

    # 验证文件扩展名
    allowed_extensions = [".zip", ".tar.gz", ".tgz"]
    valid = False
    for ext in allowed_extensions:
        if skill_package.lower().endswith(ext):
            valid = True
            break
    if not valid:
        click.echo(
            click.style(f"错误: 不支持的文件格式。仅支持: {', '.join(allowed_extensions)}", fg="red"),
            err=True,
        )
        return

    try:
        client = SkillHubAPIClient(base_url=api_url)

        # 1. 上传技能包
        click.echo("\n正在上传技能包...")
        upload_result = client.upload_skill_package(skill_id, skill_package)
        click.echo(click.style(f"✓ 技能包上传成功", fg="green"))
        click.echo(f"  保存位置: {upload_result['data']['file_path']}")

        # 2. 提交发布
        click.echo("\n正在提交发布...")
        publication = client.submit_publication(skill_id, user_id, notes)
        click.echo(click.style(f"✓ 发布提交成功", fg="green"))
        click.echo(f"  发布ID: {publication['id']}")
        click.echo(f"  状态: {publication['status']}")
        click.echo(f"  创建时间: {publication['created_at']}")

        click.echo("\n" + click.style("技能发布已提交，等待审核！", fg="green", bold=True))

    except Exception as e:
        click.echo(click.style(f"\n错误: {str(e)}", fg="red"), err=True)
        return 1
