import React, { useState } from 'react';
import { 
  AlertCircle, 
  AlertTriangle, 
  Info as InfoIcon, 
  FileCode, 
  Check, 
  Copy, 
  HelpCircle, 
  Wrench,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

export default function FindingCard({ finding }) {
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);

  const copyExample = () => {
    if (finding.practical_example) {
      navigator.clipboard.writeText(finding.practical_example);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  let sevBadgeClass = 'badge-info';
  let SevIcon = InfoIcon;
  let borderColor = 'var(--border-card)';

  if (finding.severity === 'critical') {
    sevBadgeClass = 'badge-critical';
    SevIcon = AlertCircle;
    borderColor = 'var(--status-critical-border)';
  } else if (finding.severity === 'warning') {
    sevBadgeClass = 'badge-warning';
    SevIcon = AlertTriangle;
    borderColor = 'var(--status-warning-border)';
  }

  return (
    <div style={{
      backgroundColor: 'var(--bg-card)',
      border: `1px solid ${borderColor}`,
      borderRadius: 'var(--radius-md)',
      padding: '1.25rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '0.85rem',
      transition: 'box-shadow 0.15s ease',
    }}>
      {/* Header Row */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
          <span className={`badge ${sevBadgeClass}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <SevIcon size={12} />
            {finding.severity}
          </span>

          <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
            {finding.category}
          </span>

          <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
            [{finding.id}]
          </span>

          {finding.affected_file && (
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.3rem',
              fontSize: '0.75rem',
              fontFamily: 'var(--font-mono)',
              color: 'var(--accent-primary)',
              backgroundColor: 'var(--bg-subtle)',
              padding: '0.15rem 0.45rem',
              borderRadius: 'var(--radius-sm)',
            }}>
              <FileCode size={12} />
              {finding.affected_file}
            </span>
          )}
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="btn btn-ghost"
          style={{ padding: '0.2rem 0.5rem', height: '28px', fontSize: '0.75rem' }}
          title={isExpanded ? "Collapse" : "Expand"}
        >
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* Title */}
      <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
        {finding.title}
      </h4>

      {isExpanded && (
        <>
          {/* Description */}
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {finding.description}
          </p>

          {/* Why It Matters Callout */}
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.02)',
            borderLeft: '3px solid var(--status-warning)',
            padding: '0.75rem 0.9rem',
            borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
            fontSize: '0.8125rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 700, color: 'var(--status-warning)', marginBottom: '0.2rem' }}>
              <HelpCircle size={14} />
              Why This Matters for Rebuilds
            </div>
            <div style={{ color: 'var(--text-secondary)' }}>
              {finding.why_it_matters}
            </div>
          </div>

          {/* Recommended Fix */}
          <div style={{
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.85rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 700, color: 'var(--accent-primary)', fontSize: '0.8125rem', marginBottom: '0.35rem' }}>
              <Wrench size={14} />
              Recommended Remediation
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-primary)', marginBottom: finding.practical_example ? '0.75rem' : '0' }}>
              {finding.recommended_fix}
            </div>

            {/* Practical Example Code */}
            {finding.practical_example && (
              <div style={{ position: 'relative' }}>
                <pre className="code-block" style={{ margin: 0, paddingRight: '3rem' }}>
                  <code>{finding.practical_example}</code>
                </pre>
                <button
                  onClick={copyExample}
                  style={{
                    position: 'absolute',
                    top: '0.5rem',
                    right: '0.5rem',
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-card)',
                    color: copied ? 'var(--accent-primary)' : 'var(--text-muted)',
                    borderRadius: '4px',
                    padding: '0.25rem 0.5rem',
                    cursor: 'pointer',
                    fontSize: '0.7rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                  }}
                  title="Copy code snippet"
                >
                  {copied ? <Check size={12} /> : <Copy size={12} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
            )}
          </div>

          {/* Footer Metadata */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
            Detection: <span style={{ color: 'var(--text-muted)', marginLeft: '0.25rem', textTransform: 'capitalize' }}>{finding.detection_type}</span>
          </div>
        </>
      )}
    </div>
  );
}
