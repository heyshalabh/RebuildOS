"""
Configuration constants and security boundaries for RebuildOS.
"""
from typing import Set, Dict, Any

APP_NAME = "RebuildOS"
APP_TAGLINE = "Works on my machine? Let's prove it."
SCANNER_VERSION = "1.0.0"

# Security limits for uploaded archives
MAX_ZIP_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
MAX_EXTRACTED_FILES: int = 10_000
MAX_UNCOMPRESSED_SIZE_BYTES: int = 200 * 1024 * 1024  # 200 MB
MAX_SINGLE_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB

# Directories to skip during project analysis
IGNORED_DIRS: Set[str] = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "dist",
    "build",
    "out",
    ".next",
    ".nuxt",
    ".turbo",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    "target",
    ".gradle",
    ".idea",
    ".vscode",
    ".vs",
    ".DS_Store",
}

# Scoring Weights and Maximum Penalties per Category (Total: 100 points)
# Points start at 100, deductions subtract from each category's budget.
CATEGORY_CONFIG: Dict[str, Dict[str, Any]] = {
    "runtime": {
        "name": "Runtime Reproducibility",
        "weight": 25,
        "max_penalty": 25,
        "description": "Explicit declarations of language/runtime versions (e.g. Node, Python, Java versions).",
    },
    "dependency": {
        "name": "Dependency Reproducibility",
        "weight": 30,
        "max_penalty": 30,
        "description": "Integrity of package manifests, lockfiles, and pinned dependency versions.",
    },
    "build": {
        "name": "Build Configuration",
        "weight": 15,
        "max_penalty": 15,
        "description": "Standard build scripts, package manager configurations, and compilation setups.",
    },
    "environment": {
        "name": "Environment Configuration",
        "weight": 10,
        "max_penalty": 10,
        "description": "Environment templates (.env.example), secret protection, and runtime variables.",
    },
    "documentation": {
        "name": "Documentation & Setup",
        "weight": 10,
        "max_penalty": 10,
        "description": "Clear step-by-step installation, setup instructions, and prerequisites.",
    },
    "test": {
        "name": "Test & Verification Readiness",
        "weight": 10,
        "max_penalty": 10,
        "description": "Automated test suites, test configurations, and verification commands.",
    },
}

# Penalty weights per severity
SEVERITY_PENALTIES: Dict[str, int] = {
    "critical": 15,
    "warning": 7,
    "info": 2,
}
