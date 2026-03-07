"""安全扫描服务 - 基础代码安全检查"""
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SecurityIssue:
    """安全问题模型"""

    def __init__(
        self,
        severity: str,
        issue_type: str,
        description: str,
        file_path: str,
        line_number: int = 0,
        line_content: str = "",
        recommendation: str = "",
    ):
        self.severity = severity
        self.issue_type = issue_type
        self.description = description
        self.file_path = file_path
        self.line_number = line_number
        self.line_content = line_content
        self.recommendation = recommendation

    def to_dict(self) -> Dict:
        return {
            "severity": self.severity,
            "issue_type": self.issue_type,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "line_content": self.line_content,
            "recommendation": self.recommendation,
        }


class ScanService:
    """安全扫描服务类"""

    DANGEROUS_PATTERNS = [
        (r"os\.system\s*\(", "high", "command_injection", "使用 os.system 可能导致命令注入"),
        (
            r"subprocess\.call\s*\(",
            "high",
            "command_injection",
            "使用 subprocess.call 可能导致命令注入",
        ),
        (
            r"subprocess\.Popen\s*\(",
            "high",
            "command_injection",
            "使用 subprocess.Popen 可能导致命令注入",
        ),
        (r"eval\s*\(", "high", "code_injection", "使用 eval 可能导致代码注入"),
        (r"exec\s*\(", "high", "code_injection", "使用 exec 可能导致代码注入"),
        (r"execute\s*\([^)]*format\s*\(", "high", "sql_injection", "字符串格式化可能导致 SQL 注入"),
        (r"execute\s*\([^)]*%\s*[^)]*\)", "high", "sql_injection", "百分号格式化可能导致 SQL 注入"),
        (r"execute\s*\([^)]*\+\s*[^)]*\)", "high", "sql_injection", "字符串拼接可能导致 SQL 注入"),
        (r"password\s*=\s*[\"'][^\"']+[\"']", "medium", "hardcoded_secret", "发现硬编码密码"),
        (
            r"api[_-]?key\s*=\s*[\"'][^\"']+[\"']",
            "medium",
            "hardcoded_secret",
            "发现硬编码 API 密钥",
        ),
        (r"secret\s*=\s*[\"'][^\"']+[\"']", "medium", "hardcoded_secret", "发现硬编码密钥"),
        (r"token\s*=\s*[\"'][^\"']+[\"']", "medium", "hardcoded_secret", "发现硬编码 Token"),
        (r"random\.random\s*\(", "low", "insecure_random", "使用不安全的随机数生成器"),
        (r"random\.randint\s*\(", "low", "insecure_random", "使用不安全的随机数生成器"),
        (r"pickle\.loads\s*\(", "high", "deserialization", "使用 pickle 反序列化可能导致远程代码执行"),
        (r"pickle\.load\s*\(", "high", "deserialization", "使用 pickle 反序列化可能导致远程代码执行"),
    ]

    SHELL_DANGEROUS_PATTERNS = [
        (r"\$\(", "high", "command_substitution", "发现命令替换，可能导致命令注入"),
        (r"`[^`]+`", "high", "command_substitution", "发现反引号命令替换，可能导致命令注入"),
        (r"rm\s+-rf", "high", "dangerous_command", "发现危险命令 rm -rf"),
        (r"curl\s+\|", "high", "remote_code_execution", "发现 curl pipe 执行模式，可能导致远程代码执行"),
        (r"wget\s+\|", "high", "remote_code_execution", "发现 wget pipe 执行模式，可能导致远程代码执行"),
    ]

    JS_DANGEROUS_PATTERNS = [
        (r"innerHTML\s*=", "medium", "xss", "使用 innerHTML 可能导致 XSS 攻击"),
        (r"document\.write\s*\(", "medium", "xss", "使用 document.write 可能导致 XSS 攻击"),
        (r"eval\s*\(", "high", "code_injection", "使用 eval 可能导致代码注入"),
        (r"Function\s*\(", "high", "code_injection", "使用 Function 构造函数可能导致代码注入"),
    ]

    SCAN_EXTENSIONS = {
        ".py": "python",
        ".sh": "shell",
        ".js": "javascript",
        ".ts": "javascript",
        ".jsx": "javascript",
        ".tsx": "javascript",
    }

    EXCLUDE_DIRS = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        "node_modules",
        "venv",
        "env",
        ".venv",
        "dist",
        "build",
    }

    @staticmethod
    def scan_file(file_path: str) -> List[SecurityIssue]:
        issues = []
        path = Path(file_path)

        if not path.exists() or not path.is_file():
            return issues

        ext = path.suffix.lower()
        if ext not in ScanService.SCAN_EXTENSIONS:
            return issues

        file_type = ScanService.SCAN_EXTENSIONS[ext]

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                if file_type == "python":
                    patterns = ScanService.DANGEROUS_PATTERNS
                elif file_type == "shell":
                    patterns = ScanService.SHELL_DANGEROUS_PATTERNS
                elif file_type == "javascript":
                    patterns = ScanService.JS_DANGEROUS_PATTERNS
                else:
                    continue

                for pattern, severity, issue_type, description in patterns:
                    if re.search(pattern, line):
                        issue = SecurityIssue(
                            severity=severity,
                            issue_type=issue_type,
                            description=description,
                            file_path=str(path),
                            line_number=line_num,
                            line_content=line.strip(),
                            recommendation=ScanService._get_recommendation(issue_type),
                        )
                        issues.append(issue)

        except Exception as e:
            logger.warning(f"扫描文件 {file_path} 时出错: {e}")

        return issues

    @staticmethod
    def scan_directory(directory_path: str) -> Tuple[List[SecurityIssue], int, int]:
        all_issues = []
        files_scanned = 0
        path = Path(directory_path)

        if not path.exists() or not path.is_dir():
            return all_issues, 0, 0

        for root, dirs, files in os.walk(directory_path):
            dirs[:] = [d for d in dirs if d not in ScanService.EXCLUDE_DIRS]

            for file in files:
                file_path = os.path.join(root, file)
                issues = ScanService.scan_file(file_path)
                if issues:
                    all_issues.extend(issues)
                files_scanned += 1

        return all_issues, files_scanned, len(all_issues)

    @staticmethod
    def scan_skill_code(
        skill_id: Optional[int] = None,
        code_content: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> Dict:
        if code_content:
            issues = ScanService._scan_code_content(code_content)
            files_scanned = 1
        elif file_path:
            issues = ScanService.scan_file(file_path)
            files_scanned = 1
        else:
            return {
                "success": False,
                "message": "请提供 code_content 或 file_path",
                "issues": [],
                "files_scanned": 0,
                "summary": {},
            }

        summary = ScanService._generate_summary(issues)

        return {
            "success": True,
            "message": "扫描完成",
            "skill_id": skill_id,
            "issues": [issue.to_dict() for issue in issues],
            "files_scanned": files_scanned,
            "total_issues": len(issues),
            "summary": summary,
        }

    @staticmethod
    def _scan_code_content(code_content: str) -> List[SecurityIssue]:
        issues = []
        lines = code_content.split("\n")

        is_python = any(
            kw in code_content for kw in ["def ", "import ", "class ", "print("]
        )
        is_js = any(
            kw in code_content for kw in ["function ", "const ", "let ", "var ", "=>"]
        )
        is_shell = code_content.startswith("#!") or any(
            kw in code_content for kw in ["#!/bin", "echo ", "export "]
        )

        patterns = []
        if is_python:
            patterns = ScanService.DANGEROUS_PATTERNS
        elif is_js:
            patterns = ScanService.JS_DANGEROUS_PATTERNS
        elif is_shell:
            patterns = ScanService.SHELL_DANGEROUS_PATTERNS
        else:
            patterns = (
                ScanService.DANGEROUS_PATTERNS
                + ScanService.JS_DANGEROUS_PATTERNS
                + ScanService.SHELL_DANGEROUS_PATTERNS
            )

        for line_num, line in enumerate(lines, 1):
            for pattern, severity, issue_type, description in patterns:
                if re.search(pattern, line):
                    issue = SecurityIssue(
                        severity=severity,
                        issue_type=issue_type,
                        description=description,
                        file_path="inline_code",
                        line_number=line_num,
                        line_content=line.strip(),
                        recommendation=ScanService._get_recommendation(issue_type),
                    )
                    issues.append(issue)

        return issues

    @staticmethod
    def _get_recommendation(issue_type: str) -> str:
        recommendations = {
            "command_injection": "使用 subprocess.run 并设置 shell=False，或使用 shlex.quote 转义参数",
            "code_injection": "避免使用 eval/exec，使用更安全的替代方案",
            "sql_injection": "使用参数化查询或 ORM 框架",
            "hardcoded_secret": "使用环境变量或密钥管理服务",
            "insecure_random": "使用 secrets 模块替代 random 模块",
            "deserialization": "避免使用 pickle，使用 JSON 或其他安全的序列化格式",
            "xss": "使用 textContent 替代 innerHTML，或对内容进行转义",
            "dangerous_command": "避免使用危险命令，或添加安全检查",
            "command_substitution": "避免在命令中使用用户输入的变量",
            "remote_code_execution": "避免直接执行远程下载的内容",
        }
        return recommendations.get(issue_type, "请审查此代码的安全性")

    @staticmethod
    def _generate_summary(issues: List[SecurityIssue]) -> Dict:
        high_count = sum(1 for i in issues if i.severity == "high")
        medium_count = sum(1 for i in issues if i.severity == "medium")
        low_count = sum(1 for i in issues if i.severity == "low")

        issue_types = {}
        for issue in issues:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1

        return {
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "issue_types": issue_types,
            "risk_level": "high"
            if high_count > 0
            else "medium"
            if medium_count > 0
            else "low",
        }
