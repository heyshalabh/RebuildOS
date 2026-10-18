import React from 'react';
import { Terminal, Shield, Scale, Layers, BookOpen, CheckCircle } from 'lucide-react';

export default function DocsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1000px' }}>
      <div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem' }}>Documentation</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Comprehensive technical reference for the RebuildOS analysis engine, CLI, scoring methodology, and security boundaries.
        </p>
      </div>

      {/* 1. Quickstart & Installation */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Terminal size={18} color="var(--accent-primary)" />
          1. Quickstart & Installation
        </h3>

        <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>Prerequisites</h4>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          - Python 3.10+ (Python 3.12 recommended)<br />
          - Node.js 18+ (Node 20+ recommended)
        </p>

        <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>Local Backend Setup</h4>
        <pre className="code-block">
          <code>{`cd backend
# Create virtual environment (optional but recommended)
python -m venv .venv
# On Windows: .venv\\Scripts\\activate | On Unix: source .venv/bin/activate
pip install -r requirements.lock

# Start FastAPI server on port 8000
python -m uvicorn app.main:app --reload --port 8000`}</code>
        </pre>

        <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>Local Frontend Setup</h4>
        <pre className="code-block">
          <code>{`cd frontend
npm install
npm run dev
# Open browser at http://localhost:5173`}</code>
        </pre>
      </div>

      {/* 2. Command Line Interface (CLI) */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BookOpen size={18} color="var(--accent-primary)" />
          2. CLI Usage Reference
        </h3>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Scan local directories without launching the web server. Returns standard exit codes: <code>0</code> on pass (score &ge; 75 and no critical issues), <code>1</code> on failure or critical findings.
        </p>

        <pre className="code-block">
          <code>{`# Basic human-readable scan
python -m rebuildos.cli scan ./my-project

# Export structured JSON report
python -m rebuildos.cli scan ./my-project --format json --output report.json

# Export GitHub-ready Markdown audit
python -m rebuildos.cli scan ./my-project --format markdown --output AUDIT.md

# Strict mode: fails if any warning or critical findings exist
python -m rebuildos.cli scan ./my-project --strict

# Custom minimum threshold score (e.g. require 85 points)
python -m rebuildos.cli scan ./my-project --min-score 85`}</code>
        </pre>
      </div>

      {/* 3. Scoring Methodology */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Scale size={18} color="var(--accent-primary)" />
          3. Scoring Methodology & Deductions
        </h3>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Every repository starts with a maximum baseline score of <strong>100 points</strong>. Deductions are subtracted based on severity and capped per category to avoid unfair penalization from duplicate findings.
        </p>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-card)', textAlign: 'left', color: 'var(--text-muted)' }}>
              <th style={{ padding: '0.5rem' }}>Category</th>
              <th style={{ padding: '0.5rem' }}>Weight</th>
              <th style={{ padding: '0.5rem' }}>Max Penalty</th>
              <th style={{ padding: '0.5rem' }}>Primary Focus</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '0.65rem 0.5rem', fontWeight: 600 }}>Dependency Reproducibility</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>30 pts</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>30 pts</td>
              <td style={{ padding: '0.65rem 0.5rem', color: 'var(--text-muted)' }}>Lockfile presence, unpinned dependencies, conflicting lockfiles</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '0.65rem 0.5rem', fontWeight: 600 }}>Runtime Reproducibility</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>25 pts</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>25 pts</td>
              <td style={{ padding: '0.65rem 0.5rem', color: 'var(--text-muted)' }}>Exact language versions (.python-version, engines.node, .nvmrc, pom.xml)</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '0.65rem 0.5rem', fontWeight: 600 }}>Build Configuration</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>15 pts</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>15 pts</td>
              <td style={{ padding: '0.65rem 0.5rem', color: 'var(--text-muted)' }}>Build scripts, wrapper scripts (mvnw/gradlew), .dockerignore, .gitignore</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '0.65rem 0.5rem', fontWeight: 600 }}>Environment Configuration</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>10 pts</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>10 pts</td>
              <td style={{ padding: '0.65rem 0.5rem', color: 'var(--text-muted)' }}>.env.example templates, committed secret protection</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '0.65rem 0.5rem', fontWeight: 600 }}>Documentation & Setup</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>10 pts</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>10 pts</td>
              <td style={{ padding: '0.65rem 0.5rem', color: 'var(--text-muted)' }}>README existence and clear executable installation commands</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '0.65rem 0.5rem', fontWeight: 600 }}>Test & Verification Readiness</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>10 pts</td>
              <td style={{ padding: '0.65rem 0.5rem' }}>10 pts</td>
              <td style={{ padding: '0.65rem 0.5rem', color: 'var(--text-muted)' }}>Automated test runners, test suites, verification commands</td>
            </tr>
          </tbody>
        </table>

        <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          <strong>Severity Deductions:</strong> Critical = -15 pts | Warning = -7 pts | Info = -2 pts.
        </div>
      </div>

      {/* 4. Security Boundaries */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Shield size={18} color="var(--accent-primary)" />
          4. Security Model & Defensive Boundaries
        </h3>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          RebuildOS treats every scanned archive as untrusted input:
        </p>
        <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <li><strong>Zip Slip Defense:</strong> Archive entries with <code>..</code> relative segments, absolute roots (<code>/</code> or <code>\</code>), or Windows drive letters are rejected immediately.</li>
          <li><strong>Resource Limits:</strong> Max upload 50 MB, max uncompressed size 200 MB, max file count 10,000 files to block decompression bombs.</li>
          <li><strong>Zero Code Execution:</strong> Analyzers perform static text and AST scanning only. No repository scripts, Docker builds, or setup files are ever executed automatically during analysis.</li>
          <li><strong>Automatic Cleanup:</strong> Extracted archives reside inside temporary directories and are wiped immediately upon analysis completion.</li>
        </ul>
      </div>
    </div>
  );
}
