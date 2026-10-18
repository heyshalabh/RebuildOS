"""
Python Ecosystem Analyzer for RebuildOS.
Performs deterministic static analysis on Python repositories.
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.schemas import Finding, PassedCheck
from app.core.config import IGNORED_DIRS


class PythonAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "Python"

    def applies_to(self, project_path: Path) -> bool:
        """Determines if the project is a Python project."""
        manifests = [
            "requirements.txt",
            "pyproject.toml",
            "Pipfile",
            "setup.py",
            "setup.cfg",
            ".python-version",
            "runtime.txt",
        ]
        if any((project_path / m).exists() for m in manifests):
            return True

        # Check for any .py files outside ignored directories
        for p in project_path.rglob("*.py"):
            rel_parts = p.relative_to(project_path).parts
            if not any(part in IGNORED_DIRS for part in rel_parts):
                return True
        return False

    def analyze(self, project_path: Path) -> AnalyzerResult:
        result = AnalyzerResult()
        result.languages.append("Python")

        has_py_files = False
        uses_env_vars = False
        frameworks_found = set()

        # Scan Python source files for framework imports & os.environ usage
        for p in project_path.rglob("*.py"):
            rel_parts = p.relative_to(project_path).parts
            if any(part in IGNORED_DIRS for part in rel_parts):
                continue
            has_py_files = True

            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                if "fastapi" in content.lower():
                    frameworks_found.add("FastAPI")
                if "flask" in content.lower():
                    frameworks_found.add("Flask")
                if "django" in content.lower():
                    frameworks_found.add("Django")
                if "torch" in content.lower():
                    frameworks_found.add("PyTorch")
                if "pandas" in content.lower():
                    frameworks_found.add("Pandas")
                if "streamlit" in content.lower():
                    frameworks_found.add("Streamlit")
                if "os.environ" in content or "os.getenv" in content or "dotenv" in content:
                    uses_env_vars = True
            except Exception:
                pass

        result.frameworks.extend(sorted(list(frameworks_found)))

        # 1. Dependency Manifests & Lockfiles
        has_req_txt = (project_path / "requirements.txt").exists()
        has_pyproject = (project_path / "pyproject.toml").exists()
        has_pipfile = (project_path / "Pipfile").exists()
        has_setup_py = (project_path / "setup.py").exists()

        poetry_lock = (project_path / "poetry.lock").exists()
        uv_lock = (project_path / "uv.lock").exists()
        pipfile_lock = (project_path / "Pipfile.lock").exists()

        if not any([has_req_txt, has_pyproject, has_pipfile, has_setup_py]):
            if has_py_files:
                result.missing_or_inconsistent_files.append("requirements.txt or pyproject.toml")
                result.findings.append(
                    Finding(
                        id="PY_NO_DEPENDENCY_MANIFEST",
                        title="Missing Python dependency manifest",
                        severity="critical",
                        category="dependency",
                        affected_file=None,
                        description="Project contains Python source code but no dependency manifest (requirements.txt, pyproject.toml, or Pipfile).",
                        why_it_matters="Another developer or automated CI machine cannot install the required third-party packages to run the project.",
                        recommended_fix="Create a requirements.txt or pyproject.toml file declaring all direct dependencies with pinned versions.",
                        practical_example="pip freeze > requirements.txt\n# or use 'uv pip compile' / poetry",
                        detection_type="detected",
                    )
                )
        else:
            # Check requirements.txt
            if has_req_txt:
                result.detected_package_managers.append("pip")
                result.manifests_and_lockfiles.append({"type": "manifest", "file": "requirements.txt"})
                self._check_requirements_txt(project_path / "requirements.txt", result)

            # Check pyproject.toml
            if has_pyproject:
                result.manifests_and_lockfiles.append({"type": "manifest", "file": "pyproject.toml"})
                self._check_pyproject_toml(project_path / "pyproject.toml", poetry_lock, uv_lock, result)

            # Check Pipfile
            if has_pipfile:
                result.detected_package_managers.append("pipenv")
                result.manifests_and_lockfiles.append({"type": "manifest", "file": "Pipfile"})
                if pipfile_lock:
                    result.manifests_and_lockfiles.append({"type": "lockfile", "file": "Pipfile.lock"})
                    result.passed_checks.append(
                        PassedCheck(
                            id="PY_PIPFILE_LOCKED",
                            title="Pipfile.lock is committed",
                            category="dependency",
                            description="Pipfile.lock guarantees exact sub-dependency version resolution.",
                        )
                    )
                else:
                    result.missing_or_inconsistent_files.append("Pipfile.lock")
                    result.findings.append(
                        Finding(
                            id="PY_PIPFILE_LOCK_MISSING",
                            title="Pipfile.lock is missing",
                            severity="critical",
                            category="dependency",
                            affected_file="Pipfile",
                            description="Pipfile exists, but Pipfile.lock was not found in the repository.",
                            why_it_matters="Without Pipfile.lock, installing dependencies will re-resolve packages dynamically, risking breaking changes.",
                            recommended_fix="Run 'pipenv lock' and commit the generated Pipfile.lock into version control.",
                            practical_example="pipenv lock\ngit add Pipfile.lock && git commit -m 'chore: add Pipfile.lock'",
                            detection_type="detected",
                        )
                    )

        # 2. Runtime Version Declarations
        self._check_python_runtime(project_path, result)

        # 3. Environment Configuration & Secret Protection
        self._check_environment(project_path, uses_env_vars, result)

        # 4. Testing Readiness
        self._check_tests(project_path, result)

        # 5. Documentation & Setup Instructions
        self._check_documentation(project_path, result)

        # 6. Version Control Hygiene (.gitignore)
        self._check_gitignore(project_path, result)

        # Deduplicate package managers
        result.detected_package_managers = list(dict.fromkeys(result.detected_package_managers))

        return result

    def _check_requirements_txt(self, req_path: Path, result: AnalyzerResult) -> None:
        """Inspects requirements.txt for pinned versions vs bare dependencies."""
        try:
            content = req_path.read_text(encoding="utf-8", errors="ignore")
            lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]

            if not lines:
                result.findings.append(
                    Finding(
                        id="PY_EMPTY_REQUIREMENTS",
                        title="Empty requirements.txt file",
                        severity="warning",
                        category="dependency",
                        affected_file="requirements.txt",
                        description="requirements.txt exists but contains no dependencies or only comments.",
                        why_it_matters="If the project relies on external libraries, an empty requirements file leads to runtime ImportErrors.",
                        recommended_fix="Add the necessary dependencies or remove requirements.txt if none are needed.",
                        practical_example="echo 'fastapi==0.115.0\nuvicorn==0.32.0' >> requirements.txt",
                        detection_type="detected",
                    )
                )
                return

            unpinned = []
            pinned_exact = []
            for line in lines:
                # ignore flags like -r or -i
                if line.startswith("-"):
                    continue
                pkg_spec = line.split(";")[0].strip()
                if "==" in pkg_spec:
                    pinned_exact.append(pkg_spec)
                elif any(op in pkg_spec for op in [">=", "<=", "~=", ">", "<"]):
                    unpinned.append(pkg_spec)
                else:
                    unpinned.append(pkg_spec)

            if unpinned and len(pinned_exact) == 0:
                result.findings.append(
                    Finding(
                        id="PY_UNPINNED_REQUIREMENTS",
                        title="Python dependencies are unpinned in requirements.txt",
                        severity="critical",
                        category="dependency",
                        affected_file="requirements.txt",
                        description=f"All {len(unpinned)} dependencies in requirements.txt are unpinned (e.g. '{unpinned[0]}') without exact '==' version constraints.",
                        why_it_matters="Unpinned dependencies cause 'works today, breaks tomorrow' when upstream libraries publish breaking updates.",
                        recommended_fix="Pin exact versions using '==' or use a modern lockfile tool such as uv, pip-tools, or poetry.",
                        practical_example="# Replace unpinned names:\n# fastapi -> fastapi==0.115.0\n# or generate lockfile:\nuv pip compile requirements.txt -o requirements.lock",
                        detection_type="detected",
                    )
                )
            elif unpinned:
                result.findings.append(
                    Finding(
                        id="PY_PARTIALLY_UNPINNED_REQUIREMENTS",
                        title="Some Python dependencies are loosely constrained",
                        severity="warning",
                        category="dependency",
                        affected_file="requirements.txt",
                        description=f"Found {len(unpinned)} dependencies without exact '==' pinning (e.g. '{unpinned[0]}').",
                        why_it_matters="Transitive or minor version discrepancies can introduce subtle runtime bugs.",
                        recommended_fix="Pin all production dependencies to exact versions or maintain a companion requirements.lock file.",
                        practical_example="pip-compile --output-file=requirements.lock requirements.txt",
                        detection_type="detected",
                    )
                )
            else:
                result.passed_checks.append(
                    PassedCheck(
                        id="PY_REQUIREMENTS_PINNED",
                        title="Python dependencies are explicitly pinned",
                        category="dependency",
                        description=f"All {len(pinned_exact)} dependencies in requirements.txt use exact '==' version constraints.",
                    )
                )
        except Exception as e:
            result.findings.append(
                Finding(
                    id="PY_INVALID_REQUIREMENTS",
                    title="Unable to parse requirements.txt",
                    severity="warning",
                    category="dependency",
                    affected_file="requirements.txt",
                    description=f"requirements.txt could not be read cleanly: {str(e)}",
                    why_it_matters="Corrupted requirements files prevent automated package installation.",
                    recommended_fix="Ensure requirements.txt is formatted in UTF-8 with standard pip syntax.",
                    detection_type="detected",
                )
            )

    def _check_pyproject_toml(
        self, pyproject_path: Path, poetry_lock: bool, uv_lock: bool, result: AnalyzerResult
    ) -> None:
        """Inspects pyproject.toml for build system, dependencies, and lockfile presence."""
        try:
            content = pyproject_path.read_text(encoding="utf-8", errors="ignore")
            is_poetry = "tool.poetry" in content
            is_uv = "tool.uv" in content or uv_lock

            if is_poetry:
                result.detected_package_managers.append("poetry")
                if poetry_lock:
                    result.manifests_and_lockfiles.append({"type": "lockfile", "file": "poetry.lock"})
                    result.passed_checks.append(
                        PassedCheck(
                            id="PY_POETRY_LOCKED",
                            title="poetry.lock is present",
                            category="dependency",
                            description="poetry.lock guarantees exact reproducible installation across environments.",
                        )
                    )
                else:
                    result.missing_or_inconsistent_files.append("poetry.lock")
                    result.findings.append(
                        Finding(
                            id="PY_POETRY_LOCK_MISSING",
                            title="poetry.lock is missing",
                            severity="critical",
                            category="dependency",
                            affected_file="pyproject.toml",
                            description="pyproject.toml specifies Poetry, but poetry.lock is missing from the repository.",
                            why_it_matters="Poetry dependency resolution without a committed lockfile will pull newer dependency versions and can break builds.",
                            recommended_fix="Run 'poetry lock --no-update' locally and commit poetry.lock.",
                            practical_example="poetry lock\ngit add poetry.lock && git commit -m 'chore: commit poetry.lock'",
                            detection_type="detected",
                        )
                    )

            if is_uv:
                result.detected_package_managers.append("uv")
                if uv_lock:
                    result.manifests_and_lockfiles.append({"type": "lockfile", "file": "uv.lock"})
                    result.passed_checks.append(
                        PassedCheck(
                            id="PY_UV_LOCKED",
                            title="uv.lock is present",
                            category="dependency",
                            description="uv.lock provides deterministic, blazingly fast dependency pinning.",
                        )
                    )
        except Exception:
            pass

    def _check_python_runtime(self, project_path: Path, result: AnalyzerResult) -> None:
        """Checks for explicit Python version declarations."""
        py_version_file = project_path / ".python-version"
        runtime_txt = project_path / "runtime.txt"
        pyproject_path = project_path / "pyproject.toml"

        runtime_version = None

        if py_version_file.exists():
            try:
                runtime_version = py_version_file.read_text(encoding="utf-8", errors="ignore").strip()
                result.configuration_files.append(".python-version")
            except Exception:
                pass
        elif runtime_txt.exists():
            try:
                runtime_version = runtime_txt.read_text(encoding="utf-8", errors="ignore").strip()
                result.configuration_files.append("runtime.txt")
            except Exception:
                pass
        elif pyproject_path.exists():
            try:
                content = pyproject_path.read_text(encoding="utf-8", errors="ignore")
                match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    runtime_version = match.group(1)
                else:
                    match_poetry = re.search(r'python\s*=\s*["\']([^"\']+)["\']', content)
                    if match_poetry:
                        runtime_version = match_poetry.group(1)
            except Exception:
                pass

        if runtime_version:
            result.runtime_versions["Python"] = runtime_version
            result.passed_checks.append(
                PassedCheck(
                    id="PY_RUNTIME_DECLARED",
                    title=f"Python runtime declared ({runtime_version})",
                    category="runtime",
                    description=f"Target Python version is clearly pinned via configuration: {runtime_version}.",
                )
            )
        else:
            result.missing_or_inconsistent_files.append(".python-version")
            result.findings.append(
                Finding(
                    id="PY_RUNTIME_UNDECLARED",
                    title="Python runtime version is not declared",
                    severity="warning",
                    category="runtime",
                    affected_file=".python-version",
                    description="No explicit Python version is specified (.python-version, runtime.txt, or requires-python in pyproject.toml).",
                    why_it_matters="Different Python minor versions (e.g., 3.10 vs 3.12) have breaking syntax changes, standard library deprecations, and C-extension incompatibilities.",
                    recommended_fix="Specify the supported Python version in a .python-version file or pyproject.toml.",
                    practical_example="echo '3.12.0' > .python-version",
                    detection_type="detected",
                )
            )

    def _check_environment(self, project_path: Path, uses_env_vars: bool, result: AnalyzerResult) -> None:
        """Checks for .env.example templates and catches committed .env files."""
        has_env_example = any((project_path / f).exists() for f in [".env.example", ".env.sample", ".env.template"])
        has_committed_env = (project_path / ".env").exists()

        if has_committed_env:
            result.findings.append(
                Finding(
                    id="SECURITY_ENV_FILE_COMMITTED",
                    title="Actual .env file committed to repository",
                    severity="critical",
                    category="environment",
                    affected_file=".env",
                    description="A live '.env' file is committed. This frequently leaks private secrets, API tokens, and passwords.",
                    why_it_matters="Committing credentials violates security best practices and exposes infrastructure to compromise.",
                    recommended_fix="Remove .env from Git, add '.env' to .gitignore, and provide a dummy '.env.example' instead.",
                    practical_example="git rm --cached .env\necho '.env' >> .gitignore\ncp .env .env.example # sanitize values\ngit commit -m 'security: remove .env'",
                    detection_type="detected",
                )
            )

        if has_env_example:
            result.configuration_files.append(".env.example")
            result.passed_checks.append(
                PassedCheck(
                    id="ENV_EXAMPLE_PRESENT",
                    title="Environment configuration template provided",
                    category="environment",
                    description="Found .env.example template documenting required environment variables.",
                )
            )
        elif uses_env_vars:
            result.missing_or_inconsistent_files.append(".env.example")
            result.findings.append(
                Finding(
                    id="PY_ENV_EXAMPLE_MISSING",
                    title="Missing .env.example template for environment variables",
                    severity="warning",
                    category="environment",
                    affected_file=".env.example",
                    description="Python code references environment variables (os.environ/os.getenv), but no .env.example was found.",
                    why_it_matters="New developers will experience crashes on launch without knowing which configuration keys and environment variables are expected.",
                    recommended_fix="Commit a .env.example file listing all required environment keys with dummy values or comments.",
                    practical_example="PORT=8000\nDATABASE_URL=sqlite:///./test.db\nSECRET_KEY=replace_with_random_key",
                    detection_type="inferred",
                )
            )

    def _check_tests(self, project_path: Path, result: AnalyzerResult) -> None:
        """Checks for pytest/unittest configuration and test directory."""
        has_test_dir = any((project_path / d).is_dir() for d in ["tests", "test"])
        has_test_files = False
        if has_test_dir:
            test_dir_name = "tests" if (project_path / "tests").is_dir() else "test"
            has_test_files = any((project_path / test_dir_name).glob("test_*.py")) or any(
                (project_path / test_dir_name).glob("*_test.py")
            )

        has_test_config = any(
            (project_path / f).exists() for f in ["pytest.ini", "tox.ini", ".coveragerc"]
        )

        if has_test_dir and has_test_files:
            result.passed_checks.append(
                PassedCheck(
                    id="PY_TEST_SUITE_PRESENT",
                    title="Automated test suite detected",
                    category="test",
                    description="Found test suite directory with executable test modules.",
                )
            )
        else:
            result.findings.append(
                Finding(
                    id="PY_NO_TEST_SUITE",
                    title="Missing automated test suite",
                    severity="warning",
                    category="test",
                    affected_file="tests/",
                    description="No tests/ directory or test_*.py test files were detected.",
                    why_it_matters="Without automated tests, rebuilding developers cannot verify if their local build is working as expected.",
                    recommended_fix="Add automated tests using pytest and configure a tests/ directory.",
                    practical_example="mkdir tests\necho 'def test_sanity():\n    assert True' > tests/test_basic.py\npytest",
                    detection_type="detected",
                )
            )

    def _check_documentation(self, project_path: Path, result: AnalyzerResult) -> None:
        """Checks for README and documented setup instructions."""
        readme_candidates = ["README.md", "README.rst", "README.txt", "README"]
        readme_file = next((project_path / f for f in readme_candidates if (project_path / f).exists()), None)

        if not readme_file:
            result.missing_or_inconsistent_files.append("README.md")
            result.findings.append(
                Finding(
                    id="DOCS_README_MISSING",
                    title="Missing repository README file",
                    severity="warning",
                    category="documentation",
                    affected_file="README.md",
                    description="No README.md documentation file was found in the project root.",
                    why_it_matters="A repository without a README leaves reviewers and developers without onboarding instructions.",
                    recommended_fix="Create a comprehensive README.md with project overview, prerequisites, and setup instructions.",
                    practical_example="# Project Title\n## Prerequisites\n- Python 3.12\n## Setup\n```bash\npython -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\n```",
                    detection_type="detected",
                )
            )
        else:
            result.configuration_files.append(readme_file.name)
            try:
                content = readme_file.read_text(encoding="utf-8", errors="ignore").lower()
                install_keywords = ["pip install", "poetry install", "uv sync", "pipenv install", "python -m venv"]
                if any(kw in content for kw in install_keywords):
                    result.passed_checks.append(
                        PassedCheck(
                            id="DOCS_SETUP_INSTRUCTIONS_PRESENT",
                            title="README contains setup instructions",
                            category="documentation",
                            description="README documents installation and setup commands.",
                        )
                    )
                else:
                    result.findings.append(
                        Finding(
                            id="DOCS_NO_SETUP_STEPS",
                            title="README lacks executable setup steps",
                            severity="info",
                            category="documentation",
                            affected_file=readme_file.name,
                            description="README exists but does not clearly mention 'pip install', 'venv', or package installation commands.",
                            why_it_matters="Ambiguous setup documentation slows down developer onboarding.",
                            recommended_fix="Add a dedicated 'Getting Started' or 'Installation' section with copy-pasteable commands.",
                            practical_example="## Quickstart\n```bash\npython -m venv .venv\n.venv\\Scripts\\activate # Windows\npip install -r requirements.txt\n```",
                            detection_type="inferred",
                        )
                    )
            except Exception:
                pass

    def _check_gitignore(self, project_path: Path, result: AnalyzerResult) -> None:
        """Verifies .gitignore exists and excludes virtualenvs and cache."""
        gitignore = project_path / ".gitignore"
        if not gitignore.exists():
            result.missing_or_inconsistent_files.append(".gitignore")
            result.findings.append(
                Finding(
                    id="GITIGNORE_MISSING",
                    title="Missing .gitignore file",
                    severity="info",
                    category="build",
                    affected_file=".gitignore",
                    description="No .gitignore file found in the project repository.",
                    why_it_matters="Without .gitignore, ephemeral files like __pycache__, .venv, or build artifacts get accidentally committed.",
                    recommended_fix="Add a standard Python .gitignore file.",
                    practical_example="echo '__pycache__/\n*.py[cod]\n.venv/\nvenv/\n.env' > .gitignore",
                    detection_type="detected",
                )
            )
        else:
            result.configuration_files.append(".gitignore")
            try:
                content = gitignore.read_text(encoding="utf-8", errors="ignore")
                has_pycache = "__pycache__" in content or "*.pyc" in content
                has_venv = ".venv" in content or "venv" in content
                if has_pycache and has_venv:
                    result.passed_checks.append(
                        PassedCheck(
                            id="PY_GITIGNORE_PROPER",
                            title=".gitignore excludes virtualenvs and cache",
                            category="build",
                            description=".gitignore properly ignores __pycache__ and virtual environment directories.",
                        )
                    )
            except Exception:
                pass
