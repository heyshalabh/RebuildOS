/**
 * Realistic offline sample scan results for instant UI demonstration and preset tests.
 */
export const SAMPLE_PROJECTS = {
  python_perfect: {
    project_name: "payment-service-py",
    scan_timestamp: new Date().toISOString(),
    scanner_version: "1.0.0",
    readiness_score: 95,
    readiness_label: "Strong",
    summary_message: "Repository demonstrates exceptional reproducibility. Runtime versions, dependencies, and configurations are well-pinned with clear build and verification instructions.",
    build_verification_status: "Static Analysis (Not Rebuilt)",
    scan_summary: {
      total_findings: 1,
      critical_count: 0,
      warning_count: 0,
      info_count: 1,
      passed_checks_count: 6,
    },
    category_scores: {
      runtime: { category: "runtime", name: "Runtime Reproducibility", weight: 25, score: 25, deductions: 0, max_penalty: 25, findings_count: 0 },
      dependency: { category: "dependency", name: "Dependency Reproducibility", weight: 30, score: 30, deductions: 0, max_penalty: 30, findings_count: 0 },
      build: { category: "build", name: "Build Configuration", weight: 15, score: 13, deductions: 2, max_penalty: 15, findings_count: 1 },
      environment: { category: "environment", name: "Environment Configuration", weight: 10, score: 10, deductions: 0, max_penalty: 10, findings_count: 0 },
      documentation: { category: "documentation", name: "Documentation & Setup", weight: 10, score: 10, deductions: 0, max_penalty: 10, findings_count: 0 },
      test: { category: "test", name: "Test & Verification Readiness", weight: 10, score: 10, deductions: 0, max_penalty: 10, findings_count: 0 },
    },
    detected_languages: ["Python"],
    detected_frameworks: ["FastAPI"],
    detected_package_managers: ["pip", "uv"],
    runtime_versions: { Python: "3.12.0" },
    manifests_and_lockfiles: [
      { type: "manifest", file: "requirements.txt" },
      { type: "lockfile", file: "requirements.lock" }
    ],
    configuration_files: [".python-version", ".env.example", ".gitignore", "README.md", "Dockerfile"],
    missing_or_inconsistent_files: [],
    findings: [
      {
        id: "DOCKER_RUNS_AS_ROOT",
        title: "Container runs as root user in Dockerfile",
        severity: "info",
        category: "environment",
        affected_file: "Dockerfile",
        description: "Dockerfile does not specify a non-root 'USER' directive.",
        why_it_matters: "Running containers as root violates the principle of least privilege.",
        recommended_fix: "Create and switch to an unprivileged user before starting the service.",
        practical_example: "RUN adduser --disabled-password --gecos '' appuser\nUSER appuser",
        detection_type: "detected"
      }
    ],
    passed_checks: [
      { id: "PY_REQUIREMENTS_PINNED", title: "Python dependencies are explicitly pinned", category: "dependency", description: "All dependencies in requirements.txt use exact '==' version constraints." },
      { id: "PY_RUNTIME_DECLARED", title: "Python runtime declared (3.12.0)", category: "runtime", description: "Target Python version is clearly pinned via .python-version." },
      { id: "ENV_EXAMPLE_PRESENT", title: "Environment configuration template provided", category: "environment", description: "Found .env.example template documenting required environment keys." },
      { id: "PY_TEST_SUITE_PRESENT", title: "Automated test suite detected", category: "test", description: "Found test suite directory with executable test modules." },
      { id: "DOCS_SETUP_INSTRUCTIONS_PRESENT", title: "README contains setup instructions", category: "documentation", description: "README documents installation and setup commands." },
      { id: "DOCKER_DOCKERIGNORE_PRESENT", title: ".dockerignore is present", category: "build", description: ".dockerignore protects the build context from bloated artifacts and secrets." }
    ],
    checklist: [
      {
        id: "chk_DOCKER_RUNS_AS_ROOT_0",
        title: "Container runs as root user in Dockerfile",
        category: "environment",
        severity: "info",
        affected_file: "Dockerfile",
        action: "Create and switch to an unprivileged user before starting the service.",
        resolved: false,
        is_automated_verified: false
      }
    ]
  },
  node_broken: {
    project_name: "hackathon-dashboard-js",
    scan_timestamp: new Date().toISOString(),
    scanner_version: "1.0.0",
    readiness_score: 42,
    readiness_label: "High risk",
    summary_message: "High rebuild risk. The repository lacks essential dependency manifests, lockfiles, runtime specifications, or installation documentation. Significant setup failures are expected on foreign machines.",
    build_verification_status: "Static Analysis (Not Rebuilt)",
    scan_summary: {
      total_findings: 5,
      critical_count: 2,
      warning_count: 2,
      info_count: 1,
      passed_checks_count: 1,
    },
    category_scores: {
      runtime: { category: "runtime", name: "Runtime Reproducibility", weight: 25, score: 18, deductions: 7, max_penalty: 25, findings_count: 1 },
      dependency: { category: "dependency", name: "Dependency Reproducibility", weight: 30, score: 0, deductions: 30, max_penalty: 30, findings_count: 2 },
      build: { category: "build", name: "Build Configuration", weight: 15, score: 0, deductions: 15, max_penalty: 15, findings_count: 1 },
      environment: { category: "environment", name: "Environment Configuration", weight: 10, score: 3, deductions: 7, max_penalty: 10, findings_count: 1 },
      documentation: { category: "documentation", name: "Documentation & Setup", weight: 10, score: 3, deductions: 7, max_penalty: 10, findings_count: 1 },
      test: { category: "test", name: "Test & Verification Readiness", weight: 10, score: 3, deductions: 7, max_penalty: 10, findings_count: 1 },
    },
    detected_languages: ["JavaScript"],
    detected_frameworks: ["React", "Vite"],
    detected_package_managers: ["npm"],
    runtime_versions: {},
    manifests_and_lockfiles: [{ type: "manifest", file: "package.json" }],
    configuration_files: [],
    missing_or_inconsistent_files: ["package-lock.json", ".nvmrc or engines.node", ".env.example", ".gitignore"],
    findings: [
      {
        id: "NODE_MISSING_LOCKFILE",
        title: "Missing Node.js lockfile (package-lock.json / yarn.lock)",
        severity: "critical",
        category: "dependency",
        affected_file: "package-lock.json",
        description: "package.json declares 14 dependencies, but no lockfile is committed in version control.",
        why_it_matters: "Without a lockfile, npm installs the newest compatible SemVer versions, causing builds to suddenly fail when dependencies publish minor updates.",
        recommended_fix: "Generate and commit package-lock.json (npm install) or yarn.lock (yarn install).",
        practical_example: "npm install\ngit add package-lock.json\ngit commit -m 'chore: add package-lock.json'",
        detection_type: "detected"
      },
      {
        id: "NODE_BUILD_SCRIPT_MISSING",
        title: "Missing 'build' script for compiled/bundled project",
        severity: "critical",
        category: "build",
        affected_file: "package.json",
        description: "Project uses React/Vite but lacks a 'build' script in package.json.",
        why_it_matters: "Production deployments and build verification fail when there is no standardized compilation command.",
        recommended_fix: "Add a 'build' script to package.json (e.g. 'vite build').",
        practical_example: '"scripts": {\n  "build": "vite build"\n}',
        detection_type: "detected"
      },
      {
        id: "NODE_RUNTIME_UNDECLARED",
        title: "Node.js runtime version is not declared",
        severity: "warning",
        category: "runtime",
        affected_file: "package.json",
        description: "No Node.js version constraint is defined via 'engines.node' in package.json or an .nvmrc file.",
        why_it_matters: "Node.js major releases (e.g. Node 18 vs 20 vs 22) frequently introduce breaking changes in OpenSSL, fetch API, or ES module resolution.",
        recommended_fix: "Specify the supported Node version in package.json engines or add a .nvmrc file.",
        practical_example: '// In package.json:\n"engines": {\n  "node": ">=20.0.0"\n}\n// Or run:\necho "20.18.0" > .nvmrc',
        detection_type: "detected"
      },
      {
        id: "NODE_ENV_EXAMPLE_MISSING",
        title: "Missing .env.example template",
        severity: "warning",
        category: "environment",
        affected_file: ".env.example",
        description: "No .env.example file was found to document required runtime environment variables.",
        why_it_matters: "Developers cloning the repo may fail to launch the app due to undefined process.env variables.",
        recommended_fix: "Add a .env.example file containing template keys with dummy values.",
        practical_example: "VITE_API_URL=http://localhost:8000\nVITE_AUTH_DOMAIN=app.example.com",
        detection_type: "inferred"
      },
      {
        id: "GITIGNORE_MISSING",
        title: "Missing .gitignore file",
        severity: "info",
        category: "build",
        affected_file: ".gitignore",
        description: "No .gitignore file found in the project root.",
        why_it_matters: "Build artifacts, dist folders, and node_modules will accidentally get committed into version control.",
        recommended_fix: "Add a standard Node.js .gitignore file.",
        practical_example: "echo 'node_modules/\n.env\ndist/' > .gitignore",
        detection_type: "detected"
      }
    ],
    passed_checks: [
      { id: "NODE_PACKAGE_JSON_VALID", title: "Valid package.json syntax", category: "build", description: "package.json syntax is valid JSON." }
    ],
    checklist: [
      {
        id: "chk_NODE_MISSING_LOCKFILE_0",
        title: "Missing Node.js lockfile",
        category: "dependency",
        severity: "critical",
        affected_file: "package-lock.json",
        action: "Run 'npm install' and commit package-lock.json",
        resolved: false,
        is_automated_verified: false
      },
      {
        id: "chk_NODE_BUILD_SCRIPT_MISSING_1",
        title: "Missing 'build' script",
        category: "build",
        severity: "critical",
        affected_file: "package.json",
        action: "Add 'build': 'vite build' to package.json scripts",
        resolved: false,
        is_automated_verified: false
      },
      {
        id: "chk_NODE_RUNTIME_UNDECLARED_2",
        title: "Node.js runtime version is not declared",
        category: "runtime",
        severity: "warning",
        affected_file: "package.json",
        action: "Specify engines.node in package.json or add .nvmrc",
        resolved: false,
        is_automated_verified: false
      },
      {
        id: "chk_NODE_ENV_EXAMPLE_MISSING_3",
        title: "Missing .env.example template",
        category: "environment",
        severity: "warning",
        affected_file: ".env.example",
        action: "Add .env.example template with dummy values",
        resolved: false,
        is_automated_verified: false
      }
    ]
  }
};
