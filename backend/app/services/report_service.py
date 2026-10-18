"""
Report generation service for RebuildOS.
Generates human-readable Markdown and structured JSON audit reports.
"""
import html
from typing import Dict, Any
from app.models.schemas import ScanResult


def escape_markdown(text: str) -> str:
    """Escapes pipes and angle brackets to avoid table and HTML injection in reports."""
    if not text:
        return ""
    text = text.replace("|", "\\|")
    return html.escape(text, quote=False)


def generate_json_report(scan_result: ScanResult) -> str:
    """Serializes the scan result to a nicely formatted JSON string."""
    return scan_result.model_dump_json(indent=2)


def generate_markdown_report(scan_result: ScanResult) -> str:
    """Generates an executive, developer-friendly Markdown report."""
    md = []
    md.append(f"# RebuildOS Audit Report: {escape_markdown(scan_result.project_name)}\n")
    md.append(f"> **Tagline**: Works on my machine? Let's prove it.\n")
    md.append(f"- **Scan Timestamp**: `{scan_result.scan_timestamp}`")
    md.append(f"- **Scanner Version**: `v{scan_result.scanner_version}`")
    md.append(f"- **Build Verification**: `{scan_result.build_verification_status}`\n")

    # Score Card
    md.append("## 1. Readiness Score Overview\n")
    md.append(f"### Score: **{scan_result.readiness_score} / 100** — `{scan_result.readiness_label}`\n")
    md.append(f"{escape_markdown(scan_result.summary_message)}\n")

    # Category Breakdown Table
    md.append("### Category Breakdown\n")
    md.append("| Category | Score | Weight | Deductions | Findings | Status |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :--- |")

    for cat_key, cat in scan_result.category_scores.items():
        status = "Strong" if cat.score >= (cat.weight * 0.9) else ("Needs Work" if cat.score < (cat.weight * 0.6) else "Good")
        md.append(
            f"| **{escape_markdown(cat.name)}** | {cat.score} | {cat.weight} | -{cat.deductions} | {cat.findings_count} | `{status}` |"
        )
    md.append("\n")

    # Detected Technology Stack
    md.append("## 2. Detected Technology Stack\n")
    langs = ", ".join(scan_result.detected_languages) if scan_result.detected_languages else "None"
    fws = ", ".join(scan_result.detected_frameworks) if scan_result.detected_frameworks else "None"
    pms = ", ".join(scan_result.detected_package_managers) if scan_result.detected_package_managers else "None"
    
    md.append(f"- **Languages**: {escape_markdown(langs)}")
    md.append(f"- **Frameworks / Libraries**: {escape_markdown(fws)}")
    md.append(f"- **Package Managers**: {escape_markdown(pms)}")
    if scan_result.runtime_versions:
        runtimes = ", ".join([f"{k} ({v})" for k, v in scan_result.runtime_versions.items()])
        md.append(f"- **Runtime Versions**: {escape_markdown(runtimes)}")
    if scan_result.configuration_files:
        configs = ", ".join(scan_result.configuration_files)
        md.append(f"- **Configuration Files**: `{escape_markdown(configs)}`")
    if scan_result.missing_or_inconsistent_files:
        missing = ", ".join(scan_result.missing_or_inconsistent_files)
        md.append(f"- **Missing / Inconsistent Files**: `{escape_markdown(missing)}`")
    md.append("\n")

    # Findings Grouped by Severity
    md.append("## 3. Diagnostic Findings (Build Doctor)\n")
    if not scan_result.findings:
        md.append("No issues found! The repository meets all baseline reproducibility checks.\n")
    else:
        critical_findings = [f for f in scan_result.findings if f.severity == "critical"]
        warning_findings = [f for f in scan_result.findings if f.severity == "warning"]
        info_findings = [f for f in scan_result.findings if f.severity == "info"]

        if critical_findings:
            md.append("### Critical Issues (High Risk)\n")
            for f in critical_findings:
                md.append(f"#### [{f.id}] {escape_markdown(f.title)}")
                if f.affected_file:
                    md.append(f"- **Affected File**: `{escape_markdown(f.affected_file)}`")
                md.append(f"- **Category**: `{f.category}` | **Detection**: `{f.detection_type}`")
                md.append(f"- **Description**: {escape_markdown(f.description)}")
                md.append(f"- **Why It Matters**: {escape_markdown(f.why_it_matters)}")
                md.append(f"- **Recommended Fix**: {escape_markdown(f.recommended_fix)}")
                if f.practical_example:
                    md.append(f"```bash\n{f.practical_example}\n```")
                md.append("\n")

        if warning_findings:
            md.append("### Warnings (Moderate Risk)\n")
            for f in warning_findings:
                md.append(f"#### [{f.id}] {escape_markdown(f.title)}")
                if f.affected_file:
                    md.append(f"- **Affected File**: `{escape_markdown(f.affected_file)}`")
                md.append(f"- **Category**: `{f.category}` | **Detection**: `{f.detection_type}`")
                md.append(f"- **Description**: {escape_markdown(f.description)}")
                md.append(f"- **Why It Matters**: {escape_markdown(f.why_it_matters)}")
                md.append(f"- **Recommended Fix**: {escape_markdown(f.recommended_fix)}")
                if f.practical_example:
                    md.append(f"```bash\n{f.practical_example}\n```")
                md.append("\n")

        if info_findings:
            md.append("### Informational Suggestions (Best Practices)\n")
            for f in info_findings:
                md.append(f"#### [{f.id}] {escape_markdown(f.title)}")
                if f.affected_file:
                    md.append(f"- **Affected File**: `{escape_markdown(f.affected_file)}`")
                md.append(f"- **Category**: `{f.category}` | **Detection**: `{f.detection_type}`")
                md.append(f"- **Description**: {escape_markdown(f.description)}")
                md.append(f"- **Recommended Fix**: {escape_markdown(f.recommended_fix)}")
                if f.practical_example:
                    md.append(f"```bash\n{f.practical_example}\n```")
                md.append("\n")

    # Passed Checks
    md.append("## 4. Passed Verification Checks\n")
    if not scan_result.passed_checks:
        md.append("No positive checks recorded.\n")
    else:
        for chk in scan_result.passed_checks:
            md.append(f"- [x] **{escape_markdown(chk.title)}** (`{chk.category}`): {escape_markdown(chk.description)}")
        md.append("\n")

    # Rebuild Checklist
    md.append("## 5. Actionable Rebuild Checklist\n")
    if not scan_result.checklist:
        md.append("All checklist items cleared. Repository is ready for rebuild.\n")
    else:
        for item in scan_result.checklist:
            resolved_box = "[x]" if item.resolved else "[ ]"
            file_note = f" (File: `{escape_markdown(item.affected_file)}`)" if item.affected_file else ""
            md.append(f"- {resolved_box} **{escape_markdown(item.title)}**{file_note}")
            md.append(f"  - Action: {escape_markdown(item.action)}")
        md.append("\n")

    md.append("---\n")
    md.append("*Generated by RebuildOS — Open-source local-first repository reproducibility analyzer.*")
    return "\n".join(md)
