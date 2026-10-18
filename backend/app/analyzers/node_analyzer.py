"""
Node.js / JavaScript / TypeScript Ecosystem Analyzer for RebuildOS.
Performs deterministic static analysis on Node.js repositories.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.schemas import Finding, PassedCheck
from app.core.config import IGNORED_DIRS


class NodeAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "Node.js"

    def applies_to(self, project_path: Path) -> bool:
        """Determines if the project is a Node.js / JavaScript project."""
        if (project_path / "package.json").exists():
            return True
        lockfiles = ["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb"]
        if any((project_path / f).exists() for f in lockfiles):
            return True
        # Check for .js / .ts files outside ignored dirs
        for ext in ["*.js", "*.mjs", "*.cjs", "*.ts", "*.jsx", "*.tsx"]:
            for p in project_path.rglob(ext):
                rel_parts = p.relative_to(project_path).parts
                if not any(part in IGNORED_DIRS for part in rel_parts):
                    return True
        return False

    def analyze(self, project_path: Path) -> AnalyzerResult:
        result = AnalyzerResult()
        pkg_json_path = project_path / "package.json"

        # Check for committed node_modules (severe anti-pattern)
        if (project_path / "node_modules").is_dir():
            result.findings.append(
                Finding(
                    id="NODE_COMMITTED_NODE_MODULES",
                    title="node_modules directory committed to repository",
                    severity="critical",
                    category="dependency",
                    affected_file="node_modules/",
                    description="The 'node_modules' directory is committed in the repository.",
                    why_it_matters="node_modules contains platform-specific binaries and tens of thousands of files that break cross-platform builds and inflate repo size.",
                    recommended_fix="Remove node_modules from git, add 'node_modules/' to .gitignore, and install via lockfile.",
                    practical_example="git rm -r --cached node_modules\necho 'node_modules/' >> .gitignore\ngit commit -m 'chore: remove node_modules'",
                    detection_type="detected",
                )
            )

        if not pkg_json_path.exists():
            result.languages.append("JavaScript")
            result.missing_or_inconsistent_files.append("package.json")
            result.findings.append(
                Finding(
                    id="NODE_NO_PACKAGE_JSON",
                    title="Missing package.json manifest",
                    severity="critical",
                    category="dependency",
                    affected_file=None,
                    description="JavaScript or TypeScript files were found, but no package.json manifest exists.",
                    why_it_matters="Without package.json, Node.js cannot install dependencies or run standard build/start scripts.",
                    recommended_fix="Run 'npm init -y' to generate package.json and declare dependencies.",
                    practical_example="npm init -y",
                    detection_type="detected",
                )
            )
            return result

        # Parse package.json safely
        result.manifests_and_lockfiles.append({"type": "manifest", "file": "package.json"})
        try:
            pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8", errors="ignore"))
        except Exception as e:
            result.languages.append("JavaScript")
            result.findings.append(
                Finding(
                    id="NODE_INVALID_PACKAGE_JSON",
                    title="Malformed package.json syntax",
                    severity="critical",
                    category="build",
                    affected_file="package.json",
                    description=f"package.json contains invalid JSON syntax: {str(e)}",
                    why_it_matters="NPM, Yarn, and PNPM will completely abort installation if package.json cannot be parsed.",
                    recommended_fix="Validate and fix JSON syntax errors in package.json.",
                    practical_example="npx jsonlint package.json",
                    detection_type="detected",
                )
            )
            return result

        # Detect TypeScript vs JavaScript
        is_typescript = any(project_path.rglob("*.ts")) or any(project_path.rglob("*.tsx")) or (project_path / "tsconfig.json").exists()
        if is_typescript:
            result.languages.extend(["TypeScript", "JavaScript"])
            result.configuration_files.append("tsconfig.json" if (project_path / "tsconfig.json").exists() else "TypeScript Config")
        else:
            result.languages.append("JavaScript")

        # Detect Frameworks from dependencies & devDependencies
        all_deps = {}
        all_deps.update(pkg_data.get("dependencies", {}))
        all_deps.update(pkg_data.get("devDependencies", {}))

        framework_map = {
            "react": "React",
            "next": "Next.js",
            "vue": "Vue.js",
            "nuxt": "Nuxt.js",
            "@angular/core": "Angular",
            "svelte": "Svelte",
            "express": "Express",
            "fastify": "Fastify",
            "nestjs": "NestJS",
            "vite": "Vite",
            "tailwindcss": "TailwindCSS",
        }
        for dep_key, fw_name in framework_map.items():
            if dep_key in all_deps:
                result.frameworks.append(fw_name)
        result.frameworks = sorted(list(set(result.frameworks)))

        # 1. Lockfile Detection & Inconsistency Checks
        self._check_lockfiles(project_path, all_deps, result)

        # 2. Runtime Version Checks (.nvmrc, .node-version, engines.node)
        self._check_node_runtime(project_path, pkg_data, result)

        # 3. Scripts Analysis (build, test, start)
        self._check_scripts(pkg_data, result.frameworks, is_typescript, result)

        # 4. Environment & Secret Protection
        self._check_environment(project_path, result)

        # 5. Documentation & Setup
        self._check_documentation(project_path, result)

        # 6. .gitignore Checks
        self._check_gitignore(project_path, result)

        # Deduplicate package managers
        result.detected_package_managers = list(dict.fromkeys(result.detected_package_managers))

        return result

    def _check_lockfiles(self, project_path: Path, all_deps: Dict[str, Any], result: AnalyzerResult) -> None:
        """Detects lockfiles, verifies presence if deps exist, and detects conflicting lockfiles."""
        lockfiles_present = []

        if (project_path / "package-lock.json").exists():
            lockfiles_present.append(("npm", "package-lock.json"))
        if (project_path / "yarn.lock").exists():
            lockfiles_present.append(("yarn", "yarn.lock"))
        if (project_path / "pnpm-lock.yaml").exists():
            lockfiles_present.append(("pnpm", "pnpm-lock.yaml"))
        if (project_path / "bun.lockb").exists():
            lockfiles_present.append(("bun", "bun.lockb"))
        elif (project_path / "bun.lock").exists():
            lockfiles_present.append(("bun", "bun.lock"))

        for pm, lf in lockfiles_present:
            result.detected_package_managers.append(pm)
            result.manifests_and_lockfiles.append({"type": "lockfile", "file": lf, "package_manager": pm})

        # Check for multiple conflicting lockfiles
        if len(lockfiles_present) > 1:
            conflict_names = ", ".join([lf for _, lf in lockfiles_present])
            result.missing_or_inconsistent_files.append(f"Multiple lockfiles ({conflict_names})")
            result.findings.append(
                Finding(
                    id="NODE_INCONSISTENT_LOCKFILES",
                    title="Conflicting package manager lockfiles detected",
                    severity="warning",
                    category="dependency",
                    affected_file="Multiple lockfiles",
                    description=f"Repository contains multiple conflicting lockfiles: {conflict_names}.",
                    why_it_matters="Different package managers will resolve dependencies differently, leading to unpredictable 'works on my machine' errors.",
                    recommended_fix="Standardize on one package manager (npm, yarn, pnpm, or bun) and delete the redundant lockfiles.",
                    practical_example="# To standardize on npm:\nrm yarn.lock pnpm-lock.yaml\ngit commit -m 'chore: standardize on npm'",
                    detection_type="detected",
                )
            )
        elif len(lockfiles_present) == 1:
            pm, lf = lockfiles_present[0]
            result.passed_checks.append(
                PassedCheck(
                    id="NODE_LOCKFILE_PRESENT",
                    title=f"Deterministic lockfile committed ({lf})",
                    category="dependency",
                    description=f"Using {pm} with committed {lf} ensures exact dependency versions across machines.",
                )
            )
        else:
            # Default to npm if no lockfile
            result.detected_package_managers.append("npm")
            if len(all_deps) > 0:
                result.missing_or_inconsistent_files.append("package-lock.json")
                result.findings.append(
                    Finding(
                        id="NODE_MISSING_LOCKFILE",
                        title="Missing Node.js lockfile (package-lock.json / yarn.lock / pnpm-lock.yaml)",
                        severity="critical",
                        category="dependency",
                        affected_file="package-lock.json",
                        description=f"package.json declares {len(all_deps)} dependencies, but no lockfile is committed.",
                        why_it_matters="Without a lockfile, npm/yarn installs the newest compatible SemVer versions, causing builds to suddenly fail when dependencies publish minor updates.",
                        recommended_fix="Generate and commit package-lock.json (npm install) or yarn.lock (yarn install).",
                        practical_example="npm install\ngit add package-lock.json\ngit commit -m 'chore: add package-lock.json'",
                        detection_type="detected",
                    )
                )

    def _check_node_runtime(self, project_path: Path, pkg_data: Dict[str, Any], result: AnalyzerResult) -> None:
        """Checks for explicit Node.js runtime version declarations."""
        nvmrc_path = project_path / ".nvmrc"
        node_version_path = project_path / ".node-version"
        engines_node = pkg_data.get("engines", {}).get("node")

        version_found = None

        if engines_node:
            version_found = engines_node
            result.runtime_versions["Node.js"] = f"engines.node: {engines_node}"
            result.passed_checks.append(
                PassedCheck(
                    id="NODE_ENGINES_DECLARED",
                    title=f"Node.js engines version declared ({engines_node})",
                    category="runtime",
                    description="package.json defines compatible Node.js versions in the engines field.",
                )
            )
        elif nvmrc_path.exists():
            try:
                version_found = nvmrc_path.read_text(encoding="utf-8", errors="ignore").strip()
                result.configuration_files.append(".nvmrc")
                result.runtime_versions["Node.js"] = f".nvmrc: {version_found}"
                result.passed_checks.append(
                    PassedCheck(
                        id="NODE_NVMRC_DECLARED",
                        title=f".nvmrc declares Node version ({version_found})",
                        category="runtime",
                        description="Project specifies exact Node version in .nvmrc for NVM / Volta / FNM.",
                    )
                )
            except Exception:
                pass
        elif node_version_path.exists():
            try:
                version_found = node_version_path.read_text(encoding="utf-8", errors="ignore").strip()
                result.configuration_files.append(".node-version")
                result.runtime_versions["Node.js"] = f".node-version: {version_found}"
                result.passed_checks.append(
                    PassedCheck(
                        id="NODE_VERSION_FILE_DECLARED",
                        title=f".node-version declares Node version ({version_found})",
                        category="runtime",
                        description="Project specifies exact Node version in .node-version file.",
                    )
                )
            except Exception:
                pass

        if not version_found:
            result.missing_or_inconsistent_files.append(".nvmrc or engines.node")
            result.findings.append(
                Finding(
                    id="NODE_RUNTIME_UNDECLARED",
                    title="Node.js runtime version is not declared",
                    severity="warning",
                    category="runtime",
                    affected_file="package.json",
                    description="No Node.js version constraint is defined via 'engines.node' in package.json or an .nvmrc file.",
                    why_it_matters="Node.js major releases (e.g. Node 18 vs 20 vs 22) frequently introduce breaking changes in OpenSSL, fetch API, or ES module resolution.",
                    recommended_fix="Specify the supported Node version in package.json engines or add a .nvmrc file.",
                    practical_example='// In package.json:\n"engines": {\n  "node": ">=20.0.0"\n}\n// Or run:\necho "20.18.0" > .nvmrc',
                    detection_type="detected",
                )
            )

    def _check_scripts(
        self, pkg_data: Dict[str, Any], frameworks: List[str], is_typescript: bool, result: AnalyzerResult
    ) -> None:
        """Inspects package.json scripts for build, test, and start definitions."""
        scripts = pkg_data.get("scripts", {})

        # Test script check
        test_script = scripts.get("test", "")
        if not test_script or "echo \"Error: no test specified\"" in test_script or "exit 1" in test_script:
            result.findings.append(
                Finding(
                    id="NODE_TEST_SCRIPT_MISSING",
                    title="Missing or placeholder test script",
                    severity="warning",
                    category="test",
                    affected_file="package.json",
                    description="package.json lacks an automated 'test' script or contains the default placeholder 'no test specified'.",
                    why_it_matters="Developers and CI workflows cannot automatically verify if the built project functions properly.",
                    recommended_fix="Add an automated test runner such as Vitest, Jest, or Node test runner to package.json scripts.",
                    practical_example='"scripts": {\n  "test": "vitest run"\n}',
                    detection_type="detected",
                )
            )
        else:
            result.passed_checks.append(
                PassedCheck(
                    id="NODE_TEST_SCRIPT_PRESENT",
                    title="Automated test script configured",
                    category="test",
                    description=f"npm test is configured with: '{test_script[:40]}'.",
                )
            )

        # Build script check for buildable projects
        needs_build = is_typescript or any(fw in ["React", "Next.js", "Vite", "Vue.js", "Nuxt.js", "Svelte"] for fw in frameworks)
        build_script = scripts.get("build")

        if needs_build:
            if not build_script:
                result.findings.append(
                    Finding(
                        id="NODE_BUILD_SCRIPT_MISSING",
                        title="Missing 'build' script for compiled/bundled project",
                        severity="critical",
                        category="build",
                        affected_file="package.json",
                        description="Project uses TypeScript or a modern frontend framework but lacks a 'build' script in package.json.",
                        why_it_matters="Production deployments and build verification fail when there is no standardized compilation command.",
                        recommended_fix="Add a 'build' script to package.json (e.g. 'vite build' or 'tsc && vite build').",
                        practical_example='"scripts": {\n  "build": "vite build"\n}',
                        detection_type="detected",
                    )
                )
            else:
                result.passed_checks.append(
                    PassedCheck(
                        id="NODE_BUILD_SCRIPT_PRESENT",
                        title="Build script configured in package.json",
                        category="build",
                        description=f"Found 'build' script: '{build_script[:40]}'.",
                    )
                )

    def _check_environment(self, project_path: Path, result: AnalyzerResult) -> None:
        """Verifies environment files (.env.example vs committed .env)."""
        has_committed_env = (project_path / ".env").exists()
        has_env_example = any((project_path / f).exists() for f in [".env.example", ".env.sample", ".env.template"])

        if has_committed_env:
            result.findings.append(
                Finding(
                    id="SECURITY_ENV_FILE_COMMITTED",
                    title="Actual .env file committed to repository",
                    severity="critical",
                    category="environment",
                    affected_file=".env",
                    description="A live '.env' file is committed. This risks leaking private tokens, DB passwords, and secrets.",
                    why_it_matters="Security exposure and potential unauthorized access to databases or cloud accounts.",
                    recommended_fix="Remove .env from Git tracking, add to .gitignore, and provide .env.example with placeholders.",
                    practical_example="git rm --cached .env\necho '.env' >> .gitignore\ngit commit -m 'fix: remove .env from git'",
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
                    description="Found .env.example template documenting required environment keys.",
                )
            )
        else:
            result.missing_or_inconsistent_files.append(".env.example")
            result.findings.append(
                Finding(
                    id="NODE_ENV_EXAMPLE_MISSING",
                    title="Missing .env.example template",
                    severity="warning",
                    category="environment",
                    affected_file=".env.example",
                    description="No .env.example file was found to document required runtime environment variables.",
                    why_it_matters="Developers cloning the repo may fail to launch the app due to undefined process.env variables.",
                    recommended_fix="Add a .env.example file containing template keys with dummy values.",
                    practical_example="PORT=3000\nDATABASE_URL=postgresql://user:password@localhost:5432/mydb\nNEXT_PUBLIC_API_URL=http://localhost:8000",
                    detection_type="inferred",
                )
            )

    def _check_documentation(self, project_path: Path, result: AnalyzerResult) -> None:
        """Checks for README.md and setup commands."""
        readme = project_path / "README.md"
        if not readme.exists():
            readme = next((project_path / f for f in ["README.txt", "README"] if (project_path / f).exists()), None)

        if not readme:
            result.missing_or_inconsistent_files.append("README.md")
            result.findings.append(
                Finding(
                    id="DOCS_README_MISSING",
                    title="Missing repository README file",
                    severity="warning",
                    category="documentation",
                    affected_file="README.md",
                    description="No README.md documentation was found in the repository root.",
                    why_it_matters="Without setup instructions, new developers cannot easily install or run the project.",
                    recommended_fix="Create a README.md detailing prerequisites, installation commands, and running the project.",
                    practical_example="# Project Name\n## Setup\n```bash\nnpm install\nnpm run dev\n```",
                    detection_type="detected",
                )
            )
        else:
            result.configuration_files.append(readme.name)
            try:
                content = readme.read_text(encoding="utf-8", errors="ignore").lower()
                if any(cmd in content for cmd in ["npm install", "yarn install", "pnpm install", "npm i", "bun install"]):
                    result.passed_checks.append(
                        PassedCheck(
                            id="DOCS_SETUP_INSTRUCTIONS_PRESENT",
                            title="README documents package installation",
                            category="documentation",
                            description="README includes setup commands for installing dependencies.",
                        )
                    )
            except Exception:
                pass

    def _check_gitignore(self, project_path: Path, result: AnalyzerResult) -> None:
        """Verifies .gitignore exists and ignores node_modules."""
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
                    description="No .gitignore file found in the project root.",
                    why_it_matters="Build artifacts, dist folders, and node_modules will accidentally get committed into version control.",
                    recommended_fix="Add a standard Node.js .gitignore file.",
                    practical_example="echo 'node_modules/\n.env\ndist/\nbuild/\n.DS_Store' > .gitignore",
                    detection_type="detected",
                )
            )
        else:
            result.configuration_files.append(".gitignore")
            try:
                content = gitignore.read_text(encoding="utf-8", errors="ignore")
                if "node_modules" in content:
                    result.passed_checks.append(
                        PassedCheck(
                            id="NODE_GITIGNORE_IGNORES_MODULES",
                            title=".gitignore excludes node_modules",
                            category="build",
                            description=".gitignore properly prevents committing node_modules dependencies.",
                        )
                    )
            except Exception:
                pass
