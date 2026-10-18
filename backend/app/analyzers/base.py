"""
Base Analyzer interface and AnalyzerResult dataclass for RebuildOS.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.models.schemas import Finding, PassedCheck


class AnalyzerResult(BaseModel):
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    detected_package_managers: List[str] = Field(default_factory=list)
    runtime_versions: Dict[str, str] = Field(default_factory=dict)
    manifests_and_lockfiles: List[Dict[str, Any]] = Field(default_factory=list)
    configuration_files: List[str] = Field(default_factory=list)
    missing_or_inconsistent_files: List[str] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    passed_checks: List[PassedCheck] = Field(default_factory=list)


class BaseAnalyzer(ABC):
    """Abstract base class for all language and ecosystem analyzers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the analyzer (e.g. 'Python', 'Node.js', 'Java', 'Docker')."""
        pass

    @abstractmethod
    def applies_to(self, project_path: Path) -> bool:
        """Returns True if the project contains files relevant to this analyzer."""
        pass

    @abstractmethod
    def analyze(self, project_path: Path) -> AnalyzerResult:
        """Executes static analysis on the project directory and returns findings."""
        pass
