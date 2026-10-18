import React, { useState } from 'react';
import { 
  Download, 
  Printer, 
  ArrowLeft, 
  FileJson, 
  FileCode, 
  ShieldCheck, 
  AlertCircle 
} from 'lucide-react';
import { exportReport } from '../services/api';

export default function ReportPage({ scanResult, onBackToResults }) {
  const [downloading, setDownloading] = useState(false);

  if (!scanResult) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <h3>No Active Report Available</h3>
        <p style={{ color: 'var(--text-muted)', margin: '1rem 0' }}>
          Run a project scan first to inspect and download your audit report.
        </p>
        <button onClick={onBackToResults} className="btn btn-primary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const handleDownload = async (format) => {
    setDownloading(true);
    try {
      const content = await exportReport(scanResult, format);
      const filename = `rebuildos_report_${scanResult.project_name.toLowerCase().replace(/[^a-z0-9_-]/g, '_')}.${format === 'json' ? 'json' : 'md'}`;
      const mimeType = format === 'json' ? 'application/json' : 'text/markdown';
      
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Download failed: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Action Header */}
      <div className="no-print" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <button
            onClick={onBackToResults}
            className="btn btn-ghost"
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.65rem', marginBottom: '0.25rem' }}
          >
            <ArrowLeft size={14} /> Back to Diagnostics
          </button>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Audit Report Preview</h2>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => handleDownload('json')}
            disabled={downloading}
            className="btn btn-secondary"
            title="Download structured JSON report"
          >
            <FileJson size={16} />
            Download JSON
          </button>

          <button
            onClick={() => handleDownload('markdown')}
            disabled={downloading}
            className="btn btn-secondary"
            title="Download GitHub Flavored Markdown report"
          >
            <FileCode size={16} />
            Download Markdown
          </button>

          <button
            onClick={handlePrint}
            className="btn btn-primary"
            title="Print or export to PDF"
          >
            <Printer size={16} />
            Print Report
          </button>
        </div>
      </div>

      {/* Printable Report Document Card */}
      <div className="card" style={{
        padding: '2.5rem',
        backgroundColor: 'var(--bg-secondary)',
        lineHeight: 1.6,
      }}>
        {/* Document Header */}
        <div style={{ borderBottom: '2px solid var(--border-card)', paddingBottom: '1.5rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.25rem' }}>
                RebuildOS Reproducibility Audit: {scanResult.project_name}
              </h1>
              <p style={{ fontSize: '0.875rem', color: 'var(--accent-primary)', fontWeight: 600 }}>
                "Works on my machine? Let's prove it."
              </p>
            </div>

            <div style={{ textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <div>Timestamp: <code style={{ color: 'var(--text-secondary)' }}>{scanResult.scan_timestamp}</code></div>
              <div>Scanner Version: <code style={{ color: 'var(--text-secondary)' }}>v{scanResult.scanner_version}</code></div>
              <div>Verification: <code style={{ color: 'var(--text-secondary)' }}>{scanResult.build_verification_status}</code></div>
            </div>
          </div>
        </div>

        {/* Section 1: Executive Score */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.4rem' }}>
            1. Readiness Score & Summary
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: '0.75rem 0' }}>
            <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent-primary)' }}>
              {scanResult.readiness_score} / 100
            </span>
            <span className="badge badge-success" style={{ fontSize: '0.85rem' }}>
              Tier: {scanResult.readiness_label}
            </span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            {scanResult.summary_message}
          </p>
        </div>

        {/* Section 2: Category Breakdown Table */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.75rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.4rem' }}>
            2. Category Breakdown
          </h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-card)', textAlign: 'left', color: 'var(--text-muted)' }}>
                <th style={{ padding: '0.5rem 0.75rem' }}>Category</th>
                <th style={{ padding: '0.5rem 0.75rem' }}>Score</th>
                <th style={{ padding: '0.5rem 0.75rem' }}>Weight</th>
                <th style={{ padding: '0.5rem 0.75rem' }}>Deductions</th>
                <th style={{ padding: '0.5rem 0.75rem' }}>Findings</th>
              </tr>
            </thead>
            <tbody>
              {Object.values(scanResult.category_scores || {}).map((c) => (
                <tr key={c.category} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '0.65rem 0.75rem', fontWeight: 600 }}>{c.name}</td>
                  <td style={{ padding: '0.65rem 0.75rem', color: 'var(--accent-primary)', fontWeight: 700 }}>{c.score}</td>
                  <td style={{ padding: '0.65rem 0.75rem', color: 'var(--text-muted)' }}>{c.weight}</td>
                  <td style={{ padding: '0.65rem 0.75rem', color: c.deductions > 0 ? 'var(--status-critical)' : 'var(--text-muted)' }}>
                    {c.deductions > 0 ? `-${c.deductions}` : '0'}
                  </td>
                  <td style={{ padding: '0.65rem 0.75rem' }}>{c.findings_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Section 3: Diagnostic Findings */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.75rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.4rem' }}>
            3. Diagnostic Findings ({scanResult.findings?.length || 0})
          </h3>
          {(!scanResult.findings || scanResult.findings.length === 0) ? (
            <p style={{ color: 'var(--text-muted)' }}>No issues found! Repository meets all baseline checks.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {scanResult.findings.map((f, idx) => (
                <div key={idx} style={{ padding: '0.75rem 1rem', backgroundColor: 'var(--bg-card)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                    <span className={`badge ${f.severity === 'critical' ? 'badge-critical' : f.severity === 'warning' ? 'badge-warning' : 'badge-info'}`}>
                      {f.severity}
                    </span>
                    <span style={{ fontWeight: 700 }}>{f.title}</span>
                    {f.affected_file && <code style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({f.affected_file})</code>}
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>{f.description}</p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--status-warning)' }}><strong>Why it matters:</strong> {f.why_it_matters}</p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--accent-primary)', marginTop: '0.2rem' }}><strong>Remediation:</strong> {f.recommended_fix}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section 4: Verified Checks */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.75rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.4rem' }}>
            4. Passed Verification Checks ({scanResult.passed_checks?.length || 0})
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.5rem' }}>
            {(scanResult.passed_checks || []).map((p) => (
              <div key={p.id} style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                <span style={{ color: 'var(--accent-primary)', fontWeight: 700 }}>✓</span> {p.title}
              </div>
            ))}
          </div>
        </div>

        {/* Footer Note */}
        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>
          Generated by RebuildOS. Deterministic, local-first repository reproducibility audit.
        </div>
      </div>
    </div>
  );
}
