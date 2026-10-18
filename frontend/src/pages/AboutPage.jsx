import React from 'react';
import { ShieldCheck, Heart, GitFork, Cpu, Award } from 'lucide-react';

export default function AboutPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '900px' }}>
      <div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem' }}>About RebuildOS</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          "Works on my machine? Let's prove it."
        </p>
      </div>

      {/* Purpose & Mission */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Award size={18} color="var(--accent-primary)" />
          The Problem & Our Mission
        </h3>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          Every year in hackathons, open-source communities, and code reviews, thousands of high-quality software projects fail evaluation simply because they cannot be rebuilt on another engineer's machine. 
        </p>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          Missing lockfiles cause upstream SemVer breakage. Undocumented environment variables crash apps silently on startup. Floating Docker tags introduce unexpected C-library incompatibilities.
        </p>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <strong>RebuildOS solves this deterministically.</strong> By conducting deep, static linting across language manifests, lockfiles, runtime declarations, and Docker specifications, it reveals exactly what will break before you push or submit.
        </p>
      </div>

      {/* Architecture Highlights */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={18} color="var(--accent-primary)" />
          Zero External Dependencies & Offline-First
        </h3>
        <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <li><strong>No Paid APIs:</strong> 100% of the analysis engine runs locally on your computer.</li>
          <li><strong>Deterministic:</strong> Consistent, verifiable rules that always produce the same score for the same codebase.</li>
          <li><strong>Privacy First:</strong> Your source code never leaves your workstation or network.</li>
          <li><strong>Unified Engine:</strong> The exact same analysis engine powers the Web Dashboard, FastAPI REST backend, and Terminal CLI.</li>
        </ul>
      </div>

      {/* Project Metadata */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <GitFork size={18} color="var(--accent-primary)" />
          Open Source & Community
        </h3>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          RebuildOS is open-source under the <strong>MIT License</strong>. Contributions are welcome for adding new language analyzers (Rust, Go, Ruby), enhancing build rules, and improving report formats.
        </p>

        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <div><strong>Version:</strong> v1.0.0</div>
          <div><strong>License:</strong> MIT License</div>
          <div><strong>Track:</strong> Developer Tools & Open Source</div>
        </div>
      </div>
    </div>
  );
}
