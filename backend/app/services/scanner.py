"""
Core Scanning Orchestration Service for RebuildOS.
Coordinates applicable ecosystem analyzers, calculates readiness scores,
and generates personalized rebuild checklists.
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.core.config import SCANNER_VERSION, APP_NAME
from app.core.scoring import calculate_readiness_score
from app.core.security import safe_extract_zip
from app.analyzers import ALL_ANALYZERS
from app.models.schemas import (
    ScanResult,
    Finding,
    PassedCheck,
    ChecklistItem,
    ScanSummary,
)


def scan_project_directory(project_path: Path, project_name: Optional[str] = None) -> ScanResult:
    """
    Scans a local project directory using all registered ecosystem analyzers.
    Deduplicates findings, calculates readiness score, and builds checklist.
    """
    if not project_path.exists() or not project_path.is_dir():
        raise ValueError(f"Target path '{project_path}' is not a valid accessible directory.")

    if not project_name:
        project_name = project_path.name or "Untitled Project"

    # Aggregated collections
    detected_languages = []
    detected_frameworks = []
    detected_package_managers = []
    runtime_versions = {}
    manifests_and_lockfiles = []
    configuration_files = []
    missing_or_inconsistent_files = []
    all_findings: List[Finding] = []
    all_passed_checks: List[PassedCheck] = []

    # Run each registered analyzer if it applies
    matched_any_analyzer = False
    for analyzer in ALL_ANALYZERS:
        if analyzer.applies_to(project_path):
            matched_any_analyzer = True
            result = analyzer.analyze(project_path)

            detected_languages.extend(result.languages)
            detected_frameworks.extend(result.frameworks)
            detected_package_managers.extend(result.detected_package_managers)
            runtime_versions.update(result.runtime_versions)
            manifests_and_lockfiles.extend(result.manifests_and_lockfiles)
            configuration_files.extend(result.configuration_files)
            missing_or_inconsistent_files.extend(result.missing_or_inconsistent_files)
            all_findings.extend(result.findings)
            all_passed_checks.extend(result.passed_checks)

    # If no analyzer matched at all, detect generic project structure
    if not matched_any_analyzer:
        detected_languages.append("Unknown")
        all_findings.append(
            Finding(
                id="PROJECT_UNRECOGNIZED_STACK",
                title="Unrecognized project ecosystem or empty directory",
                severity="critical",
                category="build",
                affected_file=None,
                description="RebuildOS could not detect any recognized package manifests (e.g. package.json, requirements.txt, pom.xml).",
                why_it_matters="Without recognized build configuration, automated reproducibility and rebuild cannot be assessed.",
                recommended_fix="Ensure the repository includes standard manifest files (package.json, requirements.txt, pyproject.toml, or pom.xml).",
                detection_type="detected",
            )
        )

    # Deduplicate lists preserving order
    detected_languages = list(dict.fromkeys(detected_languages))
    detected_frameworks = list(dict.fromkeys(detected_frameworks))
    detected_package_managers = list(dict.fromkeys(detected_package_managers))
    configuration_files = list(dict.fromkeys(configuration_files))
    missing_or_inconsistent_files = list(dict.fromkeys(missing_or_inconsistent_files))

    # Calculate 0-100 score and category scores
    final_score, label, summary_msg, category_scores = calculate_readiness_score(all_findings)

    # Generate Personalized Rebuild Checklist from findings
    checklist: List[ChecklistItem] = []
    for idx, finding in enumerate(all_findings):
        checklist.append(
            ChecklistItem(
                id=f"chk_{finding.id}_{idx}",
                title=finding.title,
                category=finding.category,
                severity=finding.severity,
                affected_file=finding.affected_file,
                action=finding.recommended_fix,
                resolved=False,
                is_automated_verified=False,
            )
        )

    # Build Scan Summary metrics
    critical_count = sum(1 for f in all_findings if f.severity == "critical")
    warning_count = sum(1 for f in all_findings if f.severity == "warning")
    info_count = sum(1 for f in all_findings if f.severity == "info")

    summary = ScanSummary(
        total_findings=len(all_findings),
        critical_count=critical_count,
        warning_count=warning_count,
        info_count=info_count,
        passed_checks_count=len(all_passed_checks),
    )

    now_iso = datetime.now(timezone.utc).isoformat()

    return ScanResult(
        project_name=project_name,
        scan_timestamp=now_iso,
        scanner_version=SCANNER_VERSION,
        readiness_score=final_score,
        readiness_label=label,
        summary_message=summary_msg,
        category_scores=category_scores,
        detected_languages=detected_languages,
        detected_frameworks=detected_frameworks,
        detected_package_managers=detected_package_managers,
        runtime_versions=runtime_versions,
        manifests_and_lockfiles=manifests_and_lockfiles,
        configuration_files=configuration_files,
        missing_or_inconsistent_files=missing_or_inconsistent_files,
        findings=all_findings,
        passed_checks=all_passed_checks,
        checklist=checklist,
        scan_summary=summary,
        build_verification_status="Static Analysis (Not Rebuilt)",
    )


def scan_zip_archive(zip_path: Path, project_name: Optional[str] = None) -> ScanResult:
    """
    Safely extracts an uploaded ZIP archive into an isolated temporary folder,
    scans it, and guarantees immediate cleanup.
    """
    if not project_name:
        project_name = zip_path.stem

    with safe_extract_zip(zip_path) as extracted_root:
        return scan_project_directory(extracted_root, project_name=project_name)
