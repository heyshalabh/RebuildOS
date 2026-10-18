import React from 'react';
import { History, Trash2, ArrowRight } from 'lucide-react';
import { clearStoredScans } from '../services/api';

export default function RecentScans({ scans = [], onSelectScan, onClear }) {
  if (!scans || scans.length === 0) return null;

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <History size={16} color="var(--accent-primary)" />
          Recent Scans (Saved Locally in Browser)
        </h3>

        <button
          onClick={onClear}
          className="btn btn-ghost"
          style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', color: 'var(--text-muted)' }}
          title="Clear scan history"
        >
          <Trash2 size={13} />
          Clear
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {scans.map((item, idx) => {
          let badgeClass = 'badge-success';
          if (item.readiness_score < 50) badgeClass = 'badge-critical';
          else if (item.readiness_score < 75) badgeClass = 'badge-warning';
          else if (item.readiness_score < 90) badgeClass = 'badge-info';

          const timeFormatted = new Date(item.scan_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

          return (
            <div
              key={`${item.project_name}_${idx}`}
              onClick={() => onSelectScan(item.full_result)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.65rem 0.85rem',
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                transition: 'border-color 0.15s ease, background-color 0.15s ease',
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = 'rgba(34, 197, 94, 0.4)'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className={`badge ${badgeClass}`} style={{ fontSize: '0.75rem', width: '38px', justifyContent: 'center' }}>
                  {item.readiness_score}
                </span>

                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                    {item.project_name}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {timeFormatted} • {item.findings_count} finding{item.findings_count !== 1 ? 's' : ''} • {(item.detected_languages || []).join(', ') || 'General'}
                  </div>
                </div>
              </div>

              <div style={{ color: 'var(--text-muted)' }}>
                <ArrowRight size={15} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
