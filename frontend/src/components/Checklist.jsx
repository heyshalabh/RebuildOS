import React, { useState } from 'react';
import { CheckSquare, Square, CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';

export default function Checklist({ items = [], passedChecks = [] }) {
  // Local state for user-marked resolved items
  const [resolvedMap, setResolvedMap] = useState({});

  const toggleResolved = (id) => {
    setResolvedMap((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const totalItems = items.length;
  const resolvedCount = items.filter((item) => resolvedMap[item.id]).length;
  const progressPercent = totalItems > 0 ? Math.round((resolvedCount / totalItems) * 100) : 100;

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckSquare size={20} color="var(--accent-primary)" />
            Interactive Rebuild Checklist
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Track your manual remediation steps. Marked items are saved in this session.
          </p>
        </div>

        {totalItems > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              {resolvedCount} of {totalItems} Resolved
            </span>
            <div style={{ width: '100px' }} className="progress-bar-bg">
              <div 
                className="progress-bar-fill" 
                style={{ width: `${progressPercent}%`, backgroundColor: 'var(--accent-primary)' }} 
              />
            </div>
          </div>
        )}
      </div>

      {/* Action items list */}
      {items.length === 0 ? (
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          backgroundColor: 'var(--bg-secondary)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
        }}>
          <ShieldCheck size={36} color="var(--accent-primary)" style={{ margin: '0 auto 0.75rem auto' }} />
          <h4 style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
            All Clean! No Pending Actions
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            This repository satisfies all automated rebuild and reproducibility standards.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
          {items.map((item) => {
            const isResolved = Boolean(resolvedMap[item.id]);

            return (
              <div
                key={item.id}
                onClick={() => toggleResolved(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.85rem',
                  padding: '0.85rem 1rem',
                  backgroundColor: isResolved ? 'rgba(34, 197, 94, 0.04)' : 'var(--bg-secondary)',
                  border: '1px solid',
                  borderColor: isResolved ? 'rgba(34, 197, 94, 0.3)' : 'var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ marginTop: '2px', color: isResolved ? 'var(--accent-primary)' : 'var(--text-muted)' }}>
                  {isResolved ? <CheckSquare size={18} /> : <Square size={18} />}
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.2rem' }}>
                    <span style={{
                      fontWeight: 600,
                      fontSize: '0.9rem',
                      color: isResolved ? 'var(--text-muted)' : 'var(--text-primary)',
                      textDecoration: isResolved ? 'line-through' : 'none',
                    }}>
                      {item.title}
                    </span>

                    <span className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>
                      {item.category}
                    </span>

                    {item.affected_file && (
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        ({item.affected_file})
                      </span>
                    )}

                    {isResolved && (
                      <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>
                        User Marked
                      </span>
                    )}
                  </div>

                  <div style={{ fontSize: '0.8rem', color: isResolved ? 'var(--text-dim)' : 'var(--text-secondary)' }}>
                    Action: {item.action}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Automated Verified Checks (Positive confirmation) */}
      {passedChecks.length > 0 && (
        <div style={{ marginTop: '0.5rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-primary)', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <CheckCircle2 size={16} />
            Verified Passing Checks ({passedChecks.length})
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.65rem' }}>
            {passedChecks.map((chk) => (
              <div
                key={chk.id}
                style={{
                  padding: '0.65rem 0.85rem',
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.785rem',
                }}
              >
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.15rem' }}>
                  ✓ {chk.title}
                </div>
                <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                  {chk.description}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
