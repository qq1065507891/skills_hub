"""安全扫描相关 Pydantic 模型"""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SecurityIssueItem(BaseModel):
    """单个安全问题模型"""

    severity: str = Field(..., description="严重程度: high, medium, low")
    issue_type: str = Field(..., description="问题类型")
    description: str = Field(..., description="问题描述")
    file_path: str = Field(..., description="文件路径")
    line_number: int = Field(0, description="行号")
    line_content: str = Field("", description="行内容")
    recommendation: str = Field("", description="修复建议")


class ScanSummary(BaseModel):
    """扫描摘要"""

    high: int = Field(0, description="高危问题数量")
    medium: int = Field(0, description="中危问题数量")
    low: int = Field(0, description="低危问题数量")
    issue_types: Dict[str, int] = Field(default_factory=dict, description="问题类型统计")
    risk_level: str = Field("low", description="风险等级: high, medium, low")


class ScanResult(BaseModel):
    """扫描结果"""

    success: bool = Field(True, description="是否成功")
    message: str = Field("扫描完成", description="消息")
    skill_id: Optional[int] = Field(None, description="技能 ID")
    issues: List[SecurityIssueItem] = Field(default_factory=list, description="安全问题列表")
    files_scanned: int = Field(0, description="扫描的文件数")
    total_issues: int = Field(0, description="总问题数")
    summary: ScanSummary = Field(default_factory=ScanSummary, description="扫描摘要")


class ScanCodeRequest(BaseModel):
    """扫描代码请求"""

    skill_id: Optional[int] = Field(None, description="技能 ID")
    code_content: Optional[str] = Field(None, description="代码内容")
    file_path: Optional[str] = Field(None, description="文件路径")


class ScanDirectoryRequest(BaseModel):
    """扫描目录请求"""

    directory_path: str = Field(..., description="目录路径")
    skill_id: Optional[int] = Field(None, description="技能 ID")


class ScanDirectoryResult(BaseModel):
    """扫描目录结果"""

    success: bool = Field(True, description="是否成功")
    message: str = Field("扫描完成", description="消息")
    skill_id: Optional[int] = Field(None, description="技能 ID")
    issues: List[SecurityIssueItem] = Field(default_factory=list, description="安全问题列表")
    files_scanned: int = Field(0, description="扫描的文件数")
    total_issues: int = Field(0, description="总问题数")
    summary: ScanSummary = Field(default_factory=ScanSummary, description="扫描摘要")


class ScanHealthResponse(BaseModel):
    """扫描服务健康检查响应"""

    status: str = Field("ok", description="服务状态")
    version: str = Field("1.0.0", description="版本")
