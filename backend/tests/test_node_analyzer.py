from pathlib import Path
from app.analyzers.node_analyzer import NodeAnalyzer


def test_node_analyzer_applies(fixtures_dir):
    analyzer = NodeAnalyzer()
    assert analyzer.applies_to(fixtures_dir / "node_perfect")
    assert analyzer.applies_to(fixtures_dir / "node_conflicting")
    assert not analyzer.applies_to(fixtures_dir / "python_perfect")


def test_node_analyzer_perfect_repo(fixtures_dir):
    analyzer = NodeAnalyzer()
    result = analyzer.analyze(fixtures_dir / "node_perfect")

    assert "JavaScript" in result.languages
    assert "React" in result.frameworks
    assert "npm" in result.detected_package_managers
    assert "Node.js" in result.runtime_versions

    passed_ids = [p.id for p in result.passed_checks]
    assert "NODE_LOCKFILE_PRESENT" in passed_ids
    assert "NODE_ENGINES_DECLARED" in passed_ids
    assert "NODE_TEST_SCRIPT_PRESENT" in passed_ids
    assert "NODE_BUILD_SCRIPT_PRESENT" in passed_ids

    critical_findings = [f for f in result.findings if f.severity == "critical"]
    assert len(critical_findings) == 0


def test_node_analyzer_conflicting_locks(fixtures_dir):
    analyzer = NodeAnalyzer()
    result = analyzer.analyze(fixtures_dir / "node_conflicting")

    finding_ids = [f.id for f in result.findings]
    assert "NODE_INCONSISTENT_LOCKFILES" in finding_ids
