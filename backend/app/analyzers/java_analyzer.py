"""
Java / JVM Ecosystem Analyzer for RebuildOS.
Performs deterministic static analysis on Maven and Gradle repositories.
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.schemas import Finding, PassedCheck
from app.core.config import IGNORED_DIRS


class JavaAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "Java"

    def applies_to(self, project_path: Path) -> bool:
        """Determines if the project is a Java / JVM project."""
        manifests = ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"]
        if any((project_path / m).exists() for m in manifests):
            return True
        for ext in ["*.java", "*.kt", "*.scala"]:
            for p in project_path.rglob(ext):
                rel_parts = p.relative_to(project_path).parts
                if not any(part in IGNORED_DIRS for part in rel_parts):
                    return True
        return False

    def analyze(self, project_path: Path) -> AnalyzerResult:
        result = AnalyzerResult()
        result.languages.append("Java")

        has_pom = (project_path / "pom.xml").exists()
        has_gradle = (project_path / "build.gradle").exists() or (project_path / "build.gradle.kts").exists()

        if not has_pom and not has_gradle:
            result.missing_or_inconsistent_files.append("pom.xml or build.gradle")
            result.findings.append(
                Finding(
                    id="JAVA_NO_BUILD_MANIFEST",
                    title="Missing Java build manifest (pom.xml or build.gradle)",
                    severity="critical",
                    category="build",
                    affected_file=None,
                    description="Java source files found, but neither Maven (pom.xml) nor Gradle (build.gradle) build manifests exist.",
                    why_it_matters="Without a build descriptor, compilers cannot resolve external libraries or compile the project.",
                    recommended_fix="Add pom.xml for Maven or build.gradle for Gradle.",
                    practical_example="<!-- Add a minimal pom.xml or build.gradle with dependencies and Java version -->",
                    detection_type="detected",
                )
            )
            return result

        # 1. Maven Analysis
        if has_pom:
            result.detected_package_managers.append("maven")
            result.manifests_and_lockfiles.append({"type": "manifest", "file": "pom.xml"})
            self._analyze_maven(project_path, result)

        # 2. Gradle Analysis
        if has_gradle:
            result.detected_package_managers.append("gradle")
            gradle_file = "build.gradle.kts" if (project_path / "build.gradle.kts").exists() else "build.gradle"
            result.manifests_and_lockfiles.append({"type": "manifest", "file": gradle_file})
            self._analyze_gradle(project_path, gradle_file, result)

        # 3. Environment & Documentation Checks
        self._check_java_env_and_docs(project_path, result)

        # 4. Test Verification
        self._check_java_tests(project_path, result)

        result.detected_package_managers = list(dict.fromkeys(result.detected_package_managers))
        result.frameworks = list(dict.fromkeys(result.frameworks))
        return result

    def _analyze_maven(self, project_path: Path, result: AnalyzerResult) -> None:
        """Inspects Maven configuration, wrapper presence, and Java compiler source."""
        pom_path = project_path / "pom.xml"
        has_mvnw = (project_path / "mvnw").exists() or (project_path / "mvnw.cmd").exists()
        has_mvn_wrapper_props = (project_path / ".mvn" / "wrapper" / "maven-wrapper.properties").exists()

        if has_mvnw and has_mvn_wrapper_props:
            result.configuration_files.append("mvnw")
            result.passed_checks.append(
                PassedCheck(
                    id="JAVA_MAVEN_WRAPPER_PRESENT",
                    title="Maven Wrapper (mvnw) is committed",
                    category="build",
                    description="mvnw allows anyone to build the project without pre-installing a specific Maven distribution.",
                )
            )
        else:
            result.findings.append(
                Finding(
                    id="JAVA_MAVEN_WRAPPER_MISSING",
                    title="Maven Wrapper (mvnw) is missing",
                    severity="warning",
                    category="build",
                    affected_file="mvnw",
                    description="Project uses Maven but does not include the official Maven Wrapper (mvnw and .mvn/wrapper).",
                    why_it_matters="Developers must manually install and match the exact Maven version on their host system.",
                    recommended_fix="Generate the Maven wrapper by running 'mvn wrapper:wrapper' and commit the wrapper scripts.",
                    practical_example="mvn wrapper:wrapper\ngit add mvnw mvnw.cmd .mvn/\ngit commit -m 'chore: add maven wrapper'",
                    detection_type="detected",
                )
            )

        # Parse pom.xml for Java version and frameworks
        try:
            content = pom_path.read_text(encoding="utf-8", errors="ignore")
            if "spring-boot" in content:
                result.frameworks.append("Spring Boot")
            if "quarkus" in content:
                result.frameworks.append("Quarkus")
            if "micronaut" in content:
                result.frameworks.append("Micronaut")

            java_version = None
            java_ver_match = re.search(r"<java\.version>(.*?)</java\.version>", content)
            if java_ver_match:
                java_version = java_ver_match.group(1).strip()
            else:
                source_match = re.search(r"<maven\.compiler\.source>(.*?)</maven\.compiler\.source>", content)
                if source_match:
                    java_version = source_match.group(1).strip()

            if java_version:
                result.runtime_versions["Java"] = java_version
                result.passed_checks.append(
                    PassedCheck(
                        id="JAVA_VERSION_PINNED_POM",
                        title=f"Java version declared in pom.xml ({java_version})",
                        category="runtime",
                        description=f"pom.xml declares target Java release version: {java_version}.",
                    )
                )
            else:
                result.findings.append(
                    Finding(
                        id="JAVA_VERSION_NOT_PINNED",
                        title="Ambiguous Java compiler/runtime version in pom.xml",
                        severity="warning",
                        category="runtime",
                        affected_file="pom.xml",
                        description="pom.xml does not declare <java.version> or <maven.compiler.source> / <maven.compiler.target> properties.",
                        why_it_matters="Build behavior will default to whatever JDK version is active on the host machine, leading to bytecode incompatibility.",
                        recommended_fix="Add <java.version>17</java.version> inside <properties> in pom.xml.",
                        practical_example="<properties>\n  <java.version>17</java.version>\n  <maven.compiler.source>17</maven.compiler.source>\n  <maven.compiler.target>17</maven.compiler.target>\n</properties>",
                        detection_type="detected",
                    )
                )
        except Exception:
            pass

    def _analyze_gradle(self, project_path: Path, gradle_filename: str, result: AnalyzerResult) -> None:
        """Inspects Gradle build script and wrapper presence."""
        gradle_path = project_path / gradle_filename
        has_gradlew = (project_path / "gradlew").exists() or (project_path / "gradlew.bat").exists()
        has_wrapper_props = (project_path / "gradle" / "wrapper" / "gradle-wrapper.properties").exists()

        if has_gradlew and has_wrapper_props:
            result.configuration_files.append("gradlew")
            result.passed_checks.append(
                PassedCheck(
                    id="JAVA_GRADLE_WRAPPER_PRESENT",
                    title="Gradle Wrapper (gradlew) is committed",
                    category="build",
                    description="gradlew ensures consistent Gradle execution without host-level Gradle installation.",
                )
            )
        else:
            result.findings.append(
                Finding(
                    id="JAVA_GRADLE_WRAPPER_MISSING",
                    title="Gradle Wrapper (gradlew) is missing",
                    severity="warning",
                    category="build",
                    affected_file="gradlew",
                    description="Gradle build detected but gradlew wrapper scripts are missing.",
                    why_it_matters="Gradle releases frequently break backward compatibility across major versions.",
                    recommended_fix="Run 'gradle wrapper' to generate gradlew and gradle-wrapper.properties.",
                    practical_example="gradle wrapper\ngit add gradlew gradlew.bat gradle/wrapper/\ngit commit -m 'chore: add gradle wrapper'",
                    detection_type="detected",
                )
            )

        # Check for dependency lockfile
        has_gradle_lock = (project_path / "gradle.lockfile").exists()
        if has_gradle_lock:
            result.manifests_and_lockfiles.append({"type": "lockfile", "file": "gradle.lockfile"})
            result.passed_checks.append(
                PassedCheck(
                    id="JAVA_GRADLE_LOCKFILE_PRESENT",
                    title="Gradle dependency locking enabled",
                    category="dependency",
                    description="gradle.lockfile locks dynamic dependency versions.",
                )
            )

        # Parse gradle file for frameworks & java compatibility
        try:
            content = gradle_path.read_text(encoding="utf-8", errors="ignore")
            if "org.springframework.boot" in content:
                result.frameworks.append("Spring Boot")
            if "io.quarkus" in content:
                result.frameworks.append("Quarkus")

            # Look for Java version
            match = re.search(r'sourceCompatibility\s*=\s*[\'"]?([0-9\.]+)[\'"]?', content)
            if match:
                ver = match.group(1)
                result.runtime_versions["Java"] = ver
                result.passed_checks.append(
                    PassedCheck(
                        id="JAVA_VERSION_PINNED_GRADLE",
                        title=f"Java sourceCompatibility declared ({ver})",
                        category="runtime",
                        description=f"Gradle specifies Java version: {ver}.",
                    )
                )
        except Exception:
            pass

    def _check_java_env_and_docs(self, project_path: Path, result: AnalyzerResult) -> None:
        """Checks for application.properties/yaml templates and README."""
        has_readme = any((project_path / f).exists() for f in ["README.md", "README"])
        if not has_readme:
            result.missing_or_inconsistent_files.append("README.md")
            result.findings.append(
                Finding(
                    id="DOCS_README_MISSING",
                    title="Missing repository README file",
                    severity="warning",
                    category="documentation",
                    affected_file="README.md",
                    description="No README.md documentation found.",
                    why_it_matters="Developers will not know how to run or configure the Java application.",
                    recommended_fix="Create a README.md documenting JDK version prerequisites and build commands.",
                    practical_example="# Java Service\n## Requirements\n- JDK 17+\n## Build\n`./mvnw clean package`",
                    detection_type="detected",
                )
            )
        else:
            result.configuration_files.append("README.md")

    def _check_java_tests(self, project_path: Path, result: AnalyzerResult) -> None:
        """Verifies presence of src/test directory."""
        test_dir = project_path / "src" / "test"
        if test_dir.is_dir() and any(test_dir.rglob("*.java")):
            result.passed_checks.append(
                PassedCheck(
                    id="JAVA_TEST_SUITE_PRESENT",
                    title="Automated Java test suite found in src/test",
                    category="test",
                    description="Standard test directory with test cases is present.",
                )
            )
        else:
            result.findings.append(
                Finding(
                    id="JAVA_NO_TESTS_FOUND",
                    title="Missing automated Java tests in src/test",
                    severity="warning",
                    category="test",
                    affected_file="src/test",
                    description="No JUnit or TestNG test classes were detected in src/test.",
                    why_it_matters="Cannot verify if the compiled jar executes unit and integration logic properly.",
                    recommended_fix="Add unit tests using JUnit 5 under src/test/java.",
                    practical_example="// src/test/java/AppTest.java\n@Test\nvoid testApp() { assertTrue(true); }",
                    detection_type="detected",
                )
            )
