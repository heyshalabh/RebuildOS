import subprocess
import sys
import json
from pathlib import Path


def test_cli_version():
    res = subprocess.run(
        [sys.executable, "-m", "rebuildos.cli", "version"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "RebuildOS v" in res.stdout


def test_cli_scan_text(fixtures_dir):
    target = str(fixtures_dir / "python_perfect")
    res = subprocess.run(
        [sys.executable, "-m", "rebuildos.cli", "scan", target],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "CATEGORY READINESS BREAKDOWN" in res.stdout
    assert "DIAGNOSTIC FINDINGS" in res.stdout


def test_cli_scan_json(fixtures_dir):
    target = str(fixtures_dir / "python_perfect")
    res = subprocess.run(
        [sys.executable, "-m", "rebuildos.cli", "scan", target, "--format", "json"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    parsed = json.loads(res.stdout)
    assert "readiness_score" in parsed
    assert parsed["project_name"] == "python_perfect"


def test_cli_scan_broken_exit_code(fixtures_dir):
    target = str(fixtures_dir / "python_broken")
    res = subprocess.run(
        [sys.executable, "-m", "rebuildos.cli", "scan", target],
        capture_output=True,
        text=True,
    )
    # python_broken has critical findings (unpinned requirements, etc.), so exit code should be 1
    assert res.returncode == 1
