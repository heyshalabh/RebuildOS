# Contributing to RebuildOS

We welcome contributions from open-source developers, students, and engineers!

## Getting Started

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/rebuildos.git
   cd rebuildos
   ```

2. Set up the Python backend:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.lock
   ```

3. Set up the React frontend:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

4. Run the automated test suite before committing:
   ```bash
   cd ../backend
   python -m pytest
   ```

## Adding a New Language Analyzer

To add support for a new language (e.g. Rust, Go, Ruby):
1. Create a new analyzer under `backend/app/analyzers/<language>_analyzer.py` subclassing `BaseAnalyzer`.
2. Implement `name`, `applies_to(path)`, and `analyze(path)`.
3. Register the analyzer in `backend/app/analyzers/__init__.py`.
4. Add unit test fixtures in `backend/tests/fixtures/` and test cases in `backend/tests/`.

## Code Style & Standards
- Python: PEP 8, typed dataclasses/schemas via Pydantic.
- JavaScript: Modern ES Modules, React 18, clean semantic HTML.
- Deterministic analysis: Never add dependencies that require external cloud APIs or paid services for baseline rules.
