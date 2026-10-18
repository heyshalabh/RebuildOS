import json
from app.services.scanner import scan_project_directory
from app.services.report_service import generate_json_report, generate_markdown_report, escape_markdown


def test_escape_markdown():
    unsafe = "<script>alert('xss')</script> | Evil |"
    escaped = escape_markdown(unsafe)
    assert "<script>" not in escaped
    assert "\\|" in escaped


def test_json_and_markdown_reports(fixtures_dir):
    result = scan_project_directory(fixtures_dir / "python_perfect", project_name="Test Python")
    
    # JSON report
    json_str = generate_json_report(result)
    parsed = json.loads(json_str)
    assert parsed["project_name"] == "Test Python"
    assert parsed["readiness_score"] >= 80

    # Markdown report
    md_str = generate_markdown_report(result)
    assert "# RebuildOS Audit Report: Test Python" in md_str
    assert "Category Breakdown" in md_str
    assert "Actionable Rebuild Checklist" in md_str
