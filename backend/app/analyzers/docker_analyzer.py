"""
Docker and Container Configuration Analyzer for RebuildOS.
Performs deterministic static analysis on Dockerfiles and docker-compose files.
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.schemas import Finding, PassedCheck


class DockerAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "Docker"

    def applies_to(self, project_path: Path) -> bool:
        """Checks if the project includes container definitions."""
        has_dockerfile = (project_path / "Dockerfile").exists() or any(project_path.glob("Dockerfile.*"))
        has_compose = any((project_path / f).exists() for f in ["docker-compose.yml", "docker-compose.yaml", "compose.yaml", "compose.yml"])
        return has_dockerfile or has_compose

    def analyze(self, project_path: Path) -> AnalyzerResult:
        result = AnalyzerResult()
        dockerfiles = [p for p in project_path.glob("Dockerfile*") if p.is_file()]
        compose_files = [project_path / f for f in ["docker-compose.yml", "docker-compose.yaml", "compose.yaml", "compose.yml"] if (project_path / f).exists()]
        dockerignore = project_path / ".dockerignore"

        if dockerfiles:
            result.configuration_files.extend([df.name for df in dockerfiles])
            for df in dockerfiles:
                self._analyze_dockerfile(df, result)

            # Check .dockerignore
            if not dockerignore.exists():
                result.missing_or_inconsistent_files.append(".dockerignore")
                result.findings.append(
                    Finding(
                        id="DOCKER_NO_DOCKERIGNORE",
                        title="Missing .dockerignore file",
                        severity="warning",
                        category="build",
                        affected_file=".dockerignore",
                        description="A Dockerfile was found, but no .dockerignore file exists in the repository root.",
                        why_it_matters="Without .dockerignore, local node_modules, .git histories, and sensitive .env files are sent to the Docker build context, bloating images and leaking credentials.",
                        recommended_fix="Create a .dockerignore file excluding .git, node_modules, .venv, and secret files.",
                        practical_example=".git\nnode_modules\n.env\n*.pyc\n__pycache__\ndist\nbuild",
                        detection_type="detected",
                    )
                )
            else:
                result.configuration_files.append(".dockerignore")
                result.passed_checks.append(
                    PassedCheck(
                        id="DOCKER_DOCKERIGNORE_PRESENT",
                        title=".dockerignore is present",
                        category="build",
                        description=".dockerignore protects the build context from bloated artifacts and secrets.",
                    )
                )

        if compose_files:
            result.configuration_files.extend([cf.name for cf in compose_files])
            for cf in compose_files:
                self._analyze_compose(cf, result)

        return result

    def _analyze_dockerfile(self, dockerfile_path: Path, result: AnalyzerResult) -> None:
        """Inspects Dockerfile instructions for reproducibility and security anti-patterns."""
        try:
            content = dockerfile_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            from_lines = []
            copy_lines = []
            run_lines = []
            has_user_directive = False

            for idx, line in enumerate(lines):
                cleaned = line.strip()
                if cleaned.startswith("#") or not cleaned:
                    continue

                upper = cleaned.upper()
                if upper.startswith("FROM "):
                    from_lines.append((idx + 1, cleaned))
                elif upper.startswith("COPY ") or upper.startswith("ADD "):
                    copy_lines.append((idx + 1, cleaned))
                elif upper.startswith("RUN "):
                    run_lines.append((idx + 1, cleaned))
                elif upper.startswith("USER "):
                    has_user_directive = True

            # 1. Base Image Tag Floating Check
            for line_no, from_line in from_lines:
                # e.g. FROM node:latest, FROM python:alpine, FROM ubuntu
                parts = from_line.split()
                if len(parts) >= 2:
                    image_ref = parts[1]
                    if ":" not in image_ref or image_ref.endswith(":latest"):
                        result.findings.append(
                            Finding(
                                id="DOCKER_FLOATING_BASE_IMAGE",
                                title=f"Floating base image tag in {dockerfile_path.name}",
                                severity="warning",
                                category="runtime",
                                affected_file=dockerfile_path.name,
                                description=f"Base image '{image_ref}' on line {line_no} uses ':latest' or no tag.",
                                why_it_matters="Upstream image updates can silently change operating system libraries, breaking future container rebuilds.",
                                recommended_fix="Pin the base image to an explicit version or digest (e.g. 'node:20.18-alpine' or sha256 digest).",
                                practical_example=f"# Replace {image_ref} with:\nFROM python:3.12-slim-bookworm",
                                detection_type="detected",
                            )
                        )
                    elif image_ref.endswith(":alpine") or image_ref.endswith(":slim"):
                        result.findings.append(
                            Finding(
                                id="DOCKER_AMBIGUOUS_TAG",
                                title=f"Unpinned OS variant tag '{image_ref}'",
                                severity="info",
                                category="runtime",
                                affected_file=dockerfile_path.name,
                                description=f"Image '{image_ref}' on line {line_no} specifies variant without language version number.",
                                why_it_matters="Image tags like ':alpine' will jump to new major versions automatically.",
                                recommended_fix="Include the language version (e.g. 'python:3.12-alpine').",
                                practical_example="FROM python:3.12-alpine",
                                detection_type="detected",
                            )
                        )
                    else:
                        result.passed_checks.append(
                            PassedCheck(
                                id=f"DOCKER_BASE_IMAGE_PINNED_{line_no}",
                                title=f"Base image explicitly tagged: {image_ref}",
                                category="runtime",
                                description=f"Line {line_no} pins base image: '{image_ref}'.",
                            )
                        )

            # 2. Layer Caching Efficiency Check
            # Check if 'COPY . .' happens before package install RUN command
            first_copy_all = None
            first_install_run = None

            for line_no, copy_line in copy_lines:
                if re.search(r"COPY\s+\.\s+\.", copy_line, re.IGNORECASE) or re.search(r"COPY\s+\.\s+/", copy_line, re.IGNORECASE):
                    first_copy_all = line_no
                    break

            for line_no, run_line in run_lines:
                if any(kw in run_line.lower() for kw in ["npm install", "yarn install", "pip install", "pnpm install", "mvn package", "gradle build"]):
                    first_install_run = line_no
                    break

            if first_copy_all and first_install_run and first_copy_all < first_install_run:
                result.findings.append(
                    Finding(
                        id="DOCKER_INEFFICIENT_CACHE_ORDER",
                        title=f"Source code copied before dependency installation in {dockerfile_path.name}",
                        severity="info",
                        category="build",
                        affected_file=dockerfile_path.name,
                        description=f"Full source tree is copied on line {first_copy_all} before dependency installation on line {first_install_run}.",
                        why_it_matters="Every single source file change invalidates the dependency cache, forcing a full slow rebuild of all packages.",
                        recommended_fix="Copy only package manifests (package.json or requirements.txt) first, install dependencies, then copy remaining source code.",
                        practical_example="# Optimized order:\nCOPY package*.json ./\nRUN npm ci\nCOPY . .",
                        detection_type="detected",
                    )
                )

            # 3. Non-root user check
            if not has_user_directive:
                result.findings.append(
                    Finding(
                        id="DOCKER_RUNS_AS_ROOT",
                        title=f"Container runs as root user in {dockerfile_path.name}",
                        severity="info",
                        category="environment",
                        affected_file=dockerfile_path.name,
                        description="Dockerfile does not specify a non-root 'USER' directive.",
                        why_it_matters="Running containers as root violates the principle of least privilege.",
                        recommended_fix="Create and switch to an unprivileged user before starting the service.",
                        practical_example="RUN adduser --disabled-password --gecos '' appuser\nUSER appuser",
                        detection_type="detected",
                    )
                )

        except Exception:
            pass

    def _analyze_compose(self, compose_path: Path, result: AnalyzerResult) -> None:
        """Inspects docker-compose.yml for unpinned images and build contexts."""
        try:
            content = compose_path.read_text(encoding="utf-8", errors="ignore")
            if ":latest" in content:
                result.findings.append(
                    Finding(
                        id="COMPOSE_LATEST_IMAGE_TAG",
                        title=f"Floating ':latest' image tag in {compose_path.name}",
                        severity="warning",
                        category="runtime",
                        affected_file=compose_path.name,
                        description="docker-compose file references service images using the floating ':latest' tag.",
                        why_it_matters="New docker-compose pulls may download incompatible database or service versions.",
                        recommended_fix="Pin specific versions for all compose services (e.g. postgres:16-alpine instead of postgres:latest).",
                        practical_example="services:\n  db:\n    image: postgres:16-alpine",
                        detection_type="detected",
                    )
                )
            else:
                result.passed_checks.append(
                    PassedCheck(
                        id="COMPOSE_IMAGES_PINNED",
                        title=f"Services in {compose_path.name} use pinned image tags",
                        category="runtime",
                        description="No floating ':latest' tags detected in docker-compose services.",
                    )
                )
        except Exception:
            pass
