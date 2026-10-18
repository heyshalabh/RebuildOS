from pathlib import Path
from app.analyzers.python_analyzer import PythonAnalyzer


def test_python_analyzer_applies(fixtures_dir):
    analyzer = PythonAnalyzer()
    assert analyzer.applies_to(fixtures_dir / "python_perfect")
    assert analyzer.applies_to(fixtures_dir / "python_broken")
    assert not analyzer.applies_to(fixtures_dir / "node_perfect")


def test_python_analyzer_perfect_repo(fixtures_dir):
    analyzer = PythonAnalyzer()
    result = analyzer.analyze(fixtures_dir / "python_perfect")

    assert "Python" in result.languages
    assert "FastAPI" in result.frameworks
    assert "pip" in result.detected_package_managers
    assert result.runtime_versions.get("Python") == "3.12.0"

    # Pinned requirements check should pass
    passed_ids = [p.id for p in result.passed_checks]
    assert "PY_REQUIREMENTS_PINNED" in passed_ids
    assert "PY_RUNTIME_DECLARED" in passed_ids
    assert "PY_TEST_SUITE_PRESENT" in passed_ids
    assert "ENV_EXAMPLE_PRESENT" in passed_ids

    # Critical findings should be 0
    critical_findings = [f for f in result.findings if f.severity == "critical"]
    assert len(critical_findings) == 0


def test_python_analyzer_broken_repo(fixtures_dir):
    analyzer = PythonAnalyzer()
    result = analyzer.analyze(fixtures_dir / "python_broken")

    finding_ids = [f.id for f in result.findings]
    assert "PY_UNPINNED_REQUIREMENTS" in finding_ids
    assert "PY_RUNTIME_UNDECLARED" in finding_ids
    assert "PY_ENV_EXAMPLE_MISSING" in finding_ids
    assert "PY_NO_TEST_SUITE" in finding_ids
    assert "DOCS_README_MISSING" in finding_ids
