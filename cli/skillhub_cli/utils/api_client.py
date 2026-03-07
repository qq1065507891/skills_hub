"""API 客户端模块"""
import json
import os
from typing import Any, Dict, List, Optional

import requests


class SkillHubAPIClient:
    """SkillHub API 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发起 API 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API 请求失败: {e}")

    def install_skill(self, skill_id: int) -> Dict[str, Any]:
        """安装技能"""
        return self._make_request("POST", f"/api/v1/install/{skill_id}")

    def download_skill(self, skill_id: int) -> Dict[str, Any]:
        """让服务器下载技能（已弃用，旧版逻辑）"""
        return self._make_request("POST", f"/api/v1/install/{skill_id}/download")

    def download_skill_file(self, skill_id: int, output_path: str) -> str:
        """从服务器下载技能 ZIP 包到本地文件"""
        url = f"{self.base_url}/api/v1/install/{skill_id}/download-file"
        try:
            with self.session.get(url, stream=True) as response:
                response.raise_for_status()
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192): 
                        f.write(chunk)
            return output_path
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"下载技能包失败: {e}")

    def uninstall_skill(self, skill_id: int) -> Dict[str, Any]:
        """卸载技能"""
        return self._make_request("POST", f"/api/v1/install/{skill_id}/uninstall")

    def list_installed_skills(self) -> List[Dict[str, Any]]:
        """列出已安装的技能"""
        return self._make_request("GET", "/api/v1/install/installed")

    def validate_skill(
        self, install_path: str, expected_checksum: Optional[str] = None
    ) -> Dict[str, Any]:
        """验证已安装的技能"""
        params = {"install_path": install_path}
        if expected_checksum:
            params["expected_checksum"] = expected_checksum
        return self._make_request("POST", "/api/v1/install/validate", params=params)

    def search_skills(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """搜索技能"""
        params = {"query": query, "page": page, "page_size": page_size}
        return self._make_request("GET", "/api/v1/search", params=params)

    def get_skill(self, skill_id: int) -> Dict[str, Any]:
        """获取技能详情"""
        return self._make_request("GET", f"/api/v1/skills/{skill_id}")

    def upload_skill_package(self, skill_id: int, file_path: str) -> Dict[str, Any]:
        """上传技能包"""
        url = f"{self.base_url}/api/v1/publish/upload"
        params = {"skill_id": skill_id}

        if not os.path.exists(file_path):
            raise RuntimeError(f"文件不存在: {file_path}")

        filename = os.path.basename(file_path)
        try:
            with open(file_path, "rb") as f:
                files = {"file": (filename, f)}
                response = self.session.post(url, params=params, files=files)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"上传技能包失败: {e}")

    def submit_publication(
        self, skill_id: int, user_id: int = 1, notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """提交发布"""
        params = {"user_id": user_id}
        if notes:
            params["notes"] = notes
        return self._make_request(
            "POST", f"/api/v1/publish/submit/{skill_id}", params=params
        )

    def get_publication(self, publication_id: int) -> Dict[str, Any]:
        """获取发布记录"""
        return self._make_request("GET", f"/api/v1/publish/{publication_id}")

    def get_skill_publications(self, skill_id: int) -> List[Dict[str, Any]]:
        """获取技能的发布记录"""
        return self._make_request("GET", f"/api/v1/publish/skill/{skill_id}")
