from pathlib import Path
from app.analyzers.java_analyzer import JavaAnalyzer


def test_java_analyzer_applies(fixtures_dir):
    analyzer = JavaAnalyzer()
    assert analyzer.applies_to(fixtures_dir / "java_maven_perfect")
    assert not analyzer.applies_to(fixtures_dir / "python_perfect")


def test_java_analyzer_perfect_repo(fixtures_dir):
    analyzer = JavaAnalyzer()
    result = analyzer.analyze(fixtures_dir / "java_maven_perfect")

    assert "Java" in result.languages
    assert "Spring Boot" in result.frameworks
    assert "maven" in result.detected_package_managers
    assert result.runtime_versions.get("Java") == "17"

    passed_ids = [p.id for p in result.passed_checks]
    assert "JAVA_MAVEN_WRAPPER_PRESENT" in passed_ids
    assert "JAVA_VERSION_PINNED_POM" in passed_ids
    assert "JAVA_TEST_SUITE_PRESENT" in passed_ids
