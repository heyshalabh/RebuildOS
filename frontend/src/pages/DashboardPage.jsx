import React, { useState } from 'react';
import { 
  FolderSearch, 
  Terminal, 
  Copy, 
  Check, 
  Sparkles, 
  Zap, 
  ShieldAlert, 
  Cpu, 
  CheckCircle2, 
  FileCode2 
} from 'lucide-react';
import Dropzone from '../components/Dropzone';
import RecentScans from '../components/RecentScans';
import { scanZipFile, scanLocalDirectory, clearStoredScans } from '../services/api';
import { SAMPLE_PROJECTS } from '../services/mockData';

export default function DashboardPage({ onScanComplete, recentScans, onSelectRecent, onRefreshRecent }) {
  const [localPath, setLocalPath] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [cliCopied, setCliCopied] = useState(false);

  const handleZipFile = async (file) => {
    setIsLoading(true);
    setErrorMsg('');
    try {
      const result = await scanZipFile(file);
      onScanComplete(result);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to scan uploaded archive.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLocalScan = async (e) => {
    e.preventDefault();
    if (!localPath.trim()) return;

    setIsLoading(true);
    setErrorMsg('');
    try {
      const result = await scanLocalDirectory(localPath.trim());
      onScanComplete(result);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to scan local path. Verify the directory exists on your machine.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadPreset = (presetKey) => {
    const sample = SAMPLE_PROJECTS[presetKey];
    if (sample) {
      onScanComplete(sample);
    }
  };

  const copyCliCommand = () => {
    navigator.clipboard.writeText('python -m rebuildos.cli scan ./my-project');
    setCliCopied(true);
    setTimeout(() => setCliCopied(false), 2000);
  };

  const handleClearHistory = () => {
    clearStoredScans();
    onRefreshRecent();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Hero Header */}
      <div style={{
        background: 'linear-gradient(180deg, rgba(34, 197, 94, 0.08) 0%, rgba(21, 27, 35, 0) 100%)',
        border: '1px solid var(--border-card)',
        borderRadius: 'var(--radius-lg)',
        padding: '2.5rem 2rem',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.45rem',
          padding: '0.3rem 0.8rem',
          backgroundColor: 'var(--accent-dim)',
          border: '1px solid rgba(34, 197, 94, 0.3)',
          borderRadius: 'var(--radius-full)',
          fontSize: '0.75rem',
          fontWeight: 700,
          color: 'var(--accent-primary)',
          marginBottom: '1rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        }}>
          <Zap size={14} /> Open-Source Rebuild Diagnostic Engine
        </div>

        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '0.75rem', letterSpacing: '-0.03em' }}>
          "Works on my machine?" <span style={{ color: 'var(--accent-primary)' }}>Let's prove it.</span>
        </h1>

        <p style={{ maxWidth: '680px', margin: '0 auto 1.5rem auto', fontSize: '1.05rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          RebuildOS statically analyzes project structures and manifests, detects unpinned dependencies and missing runtime configurations, calculates a transparent readiness score (0-100), and generates actionable rebuild checklists.
        </p>

        {/* Quick Presets for Instant Demo */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Try an example:</span>
          <button
            onClick={() => loadPreset('python_perfect')}
            className="btn btn-secondary"
            style={{ fontSize: '0.785rem', padding: '0.35rem 0.75rem' }}
          >
            <CheckCircle2 size={14} color="var(--accent-primary)" />
            Pinned Python Service (Score: 95)
          </button>

          <button
            onClick={() => loadPreset('node_broken')}
            className="btn btn-secondary"
            style={{ fontSize: '0.785rem', padding: '0.35rem 0.75rem' }}
          >
            <ShieldAlert size={14} color="var(--status-critical)" />
            Unpinned Node.js App (Score: 42)
          </button>
        </div>
      </div>

      {/* Main Scan Input Methods Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Method 1: Upload ZIP Archive */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '6px',
              backgroundColor: 'var(--bg-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-primary)',
            }}>
              1
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Upload Project ZIP</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Safe sandbox extraction with zip-slip & size guardrails
              </p>
            </div>
          </div>

          <Dropzone
            onFileSelected={handleZipFile}
            isLoading={isLoading}
            error={errorMsg}
          />
        </div>

        {/* Method 2: Local Directory Scan */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '6px',
              backgroundColor: 'var(--bg-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-primary)',
            }}>
              2
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Analyze Local Path</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Direct filesystem scan for local machine projects
              </p>
            </div>
          </div>

          <form onSubmit={handleLocalScan} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                Directory Absolute Path
              </label>
              <input
                type="text"
                className="input-text"
                placeholder="e.g. C:\Users\Projects\my-app or ./examples/python-example"
                value={localPath}
                onChange={(e) => setLocalPath(e.target.value)}
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || !localPath.trim()}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '0.5rem' }}
            >
              <FolderSearch size={16} />
              {isLoading ? 'Scanning Directory...' : 'Scan Local Directory'}
            </button>
          </form>

          {/* Local CLI Command Shortcut */}
          <div style={{
            marginTop: 'auto',
            padding: '0.85rem',
            backgroundColor: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Terminal size={13} /> Or Run via Terminal CLI
              </span>
              <button
                onClick={copyCliCommand}
                style={{
                  background: 'none',
                  border: 'none',
                  color: cliCopied ? 'var(--accent-primary)' : 'var(--text-muted)',
                  cursor: 'pointer',
                  fontSize: '0.7rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                }}
              >
                {cliCopied ? <Check size={12} /> : <Copy size={12} />}
                {cliCopied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <code style={{ fontSize: '0.75rem', color: '#a5d6ff', wordBreak: 'break-all' }}>
              python -m rebuildos.cli scan ./my-project
            </code>
          </div>
        </div>
      </div>

      {/* Recent Scans Section */}
      <RecentScans
        scans={recentScans}
        onSelectScan={onSelectRecent}
        onClear={handleClearHistory}
      />

      {/* Feature Highlights Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
        <div className="card">
          <div style={{ color: 'var(--accent-primary)', marginBottom: '0.5rem' }}>
            <Cpu size={24} />
          </div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.35rem' }}>
            Deterministic Static Rules
          </h4>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            No hallucinations or paid AI services. Analysis uses strict AST, lockfile checks, and package manifest rules.
          </p>
        </div>

        <div className="card">
          <div style={{ color: 'var(--accent-primary)', marginBottom: '0.5rem' }}>
            <FileCode2 size={24} />
          </div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.35rem' }}>
            Multi-Ecosystem Support
          </h4>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Dedicated deep analyzers for Python (pip, poetry, uv, pipenv), Node.js (npm, yarn, pnpm, bun), Java (Maven, Gradle), and Docker.
          </p>
        </div>

        <div className="card">
          <div style={{ color: 'var(--accent-primary)', marginBottom: '0.5rem' }}>
            <Sparkles size={24} />
          </div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.35rem' }}>
            Actionable Build Doctor
          </h4>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Every finding explains why it breaks foreign builds and provides copy-pasteable remediation commands.
          </p>
        </div>
      </div>
    </div>
  );
}
