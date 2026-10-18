"""
Pydantic schemas and data models for RebuildOS.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


SeverityLevel = Literal["critical", "warning", "info"]
FindingCategory = Literal[
    "runtime",
    "dependency",
    "build",
    "environment",
    "documentation",
    "test"
]
DetectionType = Literal["detected", "inferred", "verified"]
ReadinessLabel = Literal["Strong", "Good", "Needs work", "High risk"]


class Finding(BaseModel):
    id: str = Field(..., description="Unique finding identifier, e.g. PY_NO_LOCKFILE")
    title: str = Field(..., description="Short descriptive title of the finding")
    severity: SeverityLevel = Field(..., description="Finding severity: critical, warning, or info")
    category: FindingCategory = Field(..., description="Category affected by this finding")
    affected_file: Optional[str] = Field(None, description="Path to the file related to this finding")
    description: str = Field(..., description="Detailed description of what was discovered")
    why_it_matters: str = Field(..., description="Explanation of reproducibility or rebuild risk")
    recommended_fix: str = Field(..., description="Concrete steps to remediate the issue")
    practical_example: Optional[str] = Field(None, description="Code snippet or command demonstrating the fix")
    detection_type: DetectionType = Field("detected", description="How the issue was determined")


class PassedCheck(BaseModel):
    id: str = Field(..., description="Unique identifier of the check")
    title: str = Field(..., description="Check name")
    category: FindingCategory = Field(..., description="Category of the check")
    description: str = Field(..., description="Why this check passed")


class CategoryScore(BaseModel):
    category: FindingCategory
    name: str
    weight: int = Field(..., description="Max points possible for this category")
    score: int = Field(..., description="Current score after deductions (0 to weight)")
    deductions: int = Field(0, description="Total points deducted in this category")
    max_penalty: int = Field(..., description="Maximum allowed penalty for this category")
    findings_count: int = Field(0, description="Number of findings in this category")


class ChecklistItem(BaseModel):
    id: str
    title: str
    category: FindingCategory
    severity: SeverityLevel
    affected_file: Optional[str] = None
    action: str
    resolved: bool = False
    is_automated_verified: bool = False


class ScanSummary(BaseModel):
    total_findings: int
    critical_count: int
    warning_count: int
    info_count: int
    passed_checks_count: int


class ScanResult(BaseModel):
    project_name: str
    scan_timestamp: str
    scanner_version: str
    readiness_score: int = Field(..., ge=0, le=100)
    readiness_label: ReadinessLabel
    summary_message: str
    category_scores: Dict[FindingCategory, CategoryScore]
    detected_languages: List[str]
    detected_frameworks: List[str]
    detected_package_managers: List[str]
    runtime_versions: Dict[str, str]
    manifests_and_lockfiles: List[Dict[str, Any]]
    configuration_files: List[str]
    missing_or_inconsistent_files: List[str]
    findings: List[Finding]
    passed_checks: List[PassedCheck]
    checklist: List[ChecklistItem]
    scan_summary: ScanSummary
    build_verification_status: str = "Static Analysis (Not Rebuilt)"


class LocalScanRequest(BaseModel):
    directory_path: str = Field(..., description="Absolute or relative path to a local directory on the server")


class ReportExportRequest(BaseModel):
    scan_result: ScanResult
    format: Literal["json", "markdown"] = "markdown"


class HealthResponse(BaseModel):
    status: str
    version: str
    service: str
