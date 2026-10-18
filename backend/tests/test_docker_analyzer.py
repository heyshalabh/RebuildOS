from pathlib import Path
from app.analyzers.docker_analyzer import DockerAnalyzer


def test_docker_analyzer_applies(fixtures_dir):
    analyzer = DockerAnalyzer()
    assert analyzer.applies_to(fixtures_dir / "docker_perfect")
    assert analyzer.applies_to(fixtures_dir / "docker_floating")
    assert not analyzer.applies_to(fixtures_dir / "python_broken")


def test_docker_analyzer_perfect_repo(fixtures_dir):
    analyzer = DockerAnalyzer()
    result = analyzer.analyze(fixtures_dir / "docker_perfect")

    passed_ids = [p.id for p in result.passed_checks]
    assert "DOCKER_DOCKERIGNORE_PRESENT" in passed_ids
    assert "COMPOSE_IMAGES_PINNED" in passed_ids

    # Should not have floating base image tag
    finding_ids = [f.id for f in result.findings]
    assert "DOCKER_FLOATING_BASE_IMAGE" not in finding_ids
    assert "DOCKER_NO_DOCKERIGNORE" not in finding_ids


def test_docker_analyzer_floating_repo(fixtures_dir):
    analyzer = DockerAnalyzer()
    result = analyzer.analyze(fixtures_dir / "docker_floating")

    finding_ids = [f.id for f in result.findings]
    assert "DOCKER_FLOATING_BASE_IMAGE" in finding_ids
    assert "DOCKER_NO_DOCKERIGNORE" in finding_ids
    assert "COMPOSE_LATEST_IMAGE_TAG" in finding_ids
    assert "DOCKER_RUNS_AS_ROOT" in finding_ids
