"""
Command Line Interface for RebuildOS.
Runs local-first repository reproducibility and rebuild readiness scans.
"""
import sys
import os
import argparse
from pathlib import Path

# Ensure parent directory (containing 'app') is importable
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import APP_NAME, APP_TAGLINE, SCANNER_VERSION
from app.services.scanner import scan_project_directory
from app.services.report_service import generate_json_report, generate_markdown_report


def print_banner():
    banner = f"""
================================================================================
   ____       __          _ _     _  ____   _____ 
  |  _ \ ___ / _|        (_) |   | |/ __ \ / ____|
  | |_) / _ \ |_ ___  ___ _| | __| | |  | | (___  
  |  _ <  __/  _/ _ \/ _ \ | |/ _` | |  | |\___ \ 
  | |_) \___|_| \___/\___/_|_|\__,_|\____/ ____) |
                                          |_____/ 
  {APP_TAGLINE}
  Version: v{SCANNER_VERSION}
================================================================================
"""
    print(banner)


def format_cli_summary(result) -> str:
    lines = []
    lines.append(f"Project Name   : {result.project_name}")
    lines.append(f"Scan Time      : {result.scan_timestamp}")
    lines.append(f"Readiness Score: {result.readiness_score}/100 [{result.readiness_label}]")
    lines.append(f"Summary        : {result.summary_message}")
    lines.append("-" * 78)
    
    # Detected Stack
    langs = ", ".join(result.detected_languages) if result.detected_languages else "None"
    fws = ", ".join(result.detected_frameworks) if result.detected_frameworks else "None"
    pms = ", ".join(result.detected_package_managers) if result.detected_package_managers else "None"
    lines.append(f"Languages      : {langs}")
    lines.append(f"Frameworks     : {fws}")
    lines.append(f"Pkg Managers   : {pms}")
    if result.runtime_versions:
        rts = ", ".join([f"{k}: {v}" for k, v in result.runtime_versions.items()])
        lines.append(f"Runtime Vers   : {rts}")
    lines.append("-" * 78)

    # Category breakdown
    lines.append("CATEGORY READINESS BREAKDOWN:")
    for cat_key, cat in result.category_scores.items():
        bar_len = int((cat.score / max(1, cat.weight)) * 20)
        bar = "=" * bar_len + "-" * (20 - bar_len)
        lines.append(f"  {cat.name:<30} [{bar}] {cat.score:>2}/{cat.weight:<2} (-{cat.deductions} pts, {cat.findings_count} findings)")
    lines.append("-" * 78)

    # Findings
    if result.findings:
        lines.append(f"DIAGNOSTIC FINDINGS ({len(result.findings)} issue(s)):")
        for idx, f in enumerate(result.findings, 1):
            sev_tag = f"[{f.severity.upper()}]"
            file_tag = f"({f.affected_file})" if f.affected_file else ""
            lines.append(f"  {idx}. {sev_tag:<10} {f.title} {file_tag}")
            lines.append(f"     Why: {f.why_it_matters}")
            lines.append(f"     Fix: {f.recommended_fix}")
    else:
        lines.append("DIAGNOSTIC FINDINGS: None! Project passed all reproducibility checks.")

    lines.append("-" * 78)
    lines.append(f"SUMMARY: {result.scan_summary.critical_count} Critical | {result.scan_summary.warning_count} Warning | {result.scan_summary.info_count} Info | {result.scan_summary.passed_checks_count} Passed Checks")
    lines.append("=" * 78)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="rebuildos",
        description=f"{APP_NAME} — {APP_TAGLINE}",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan a local repository directory for rebuild reproducibility")
    scan_parser.add_argument("target_path", help="Path to local repository directory")
    scan_parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="Output format (default: text)")
    scan_parser.add_argument("--output", "-o", help="Save report to specified file path")
    scan_parser.add_argument("--min-score", type=int, default=75, help="Minimum readiness score required to pass (default: 75)")
    scan_parser.add_argument("--strict", action="store_true", help="Fail if any critical or warning findings exist")

    # version subcommand
    subparsers.add_parser("version", help="Print RebuildOS version information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "version":
        print(f"{APP_NAME} v{SCANNER_VERSION}")
        sys.exit(0)

    if args.command == "scan":
        target = Path(args.target_path).resolve()
        if not target.exists():
            print(f"Error: Target path does not exist: {args.target_path}", file=sys.stderr)
            sys.exit(2)
        if not target.is_dir():
            print(f"Error: Target path is a file, not a directory: {args.target_path}", file=sys.stderr)
            sys.exit(2)

        try:
            result = scan_project_directory(target, project_name=target.name)
        except Exception as e:
            print(f"Error during repository scan: {str(e)}", file=sys.stderr)
            sys.exit(3)

        # Generate output according to chosen format
        if args.format == "json":
            output_content = generate_json_report(result)
        elif args.format == "markdown":
            output_content = generate_markdown_report(result)
        else:
            print_banner()
            output_content = format_cli_summary(result)

        if args.output:
            out_file = Path(args.output).resolve()
            out_file.write_text(output_content, encoding="utf-8")
            print(f"\nReport written to: {out_file}")
        else:
            print(output_content)

        # Determine exit code
        has_critical = result.scan_summary.critical_count > 0
        has_warning = result.scan_summary.warning_count > 0
        score_failed = result.readiness_score < args.min_score

        if has_critical or score_failed or (args.strict and has_warning):
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
