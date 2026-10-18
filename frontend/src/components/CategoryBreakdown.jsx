import React from 'react';

export default function CategoryBreakdown({ categoryScores }) {
  if (!categoryScores) return null;

  const categories = Object.values(categoryScores);

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Category Breakdown</h3>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Max Penalty Enforced per Category
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
        {categories.map((cat) => {
          const percentage = Math.round((cat.score / cat.weight) * 100);
          
          let fillColor = 'var(--accent-primary)';
          if (percentage < 50) fillColor = 'var(--status-critical)';
          else if (percentage < 75) fillColor = 'var(--status-warning)';
          else if (percentage < 90) fillColor = 'var(--status-info)';

          return (
            <div
              key={cat.category}
              style={{
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '1rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                    {cat.name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Weight: {cat.weight} pts
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '1rem', fontWeight: 700, color: fillColor }}>
                    {cat.score}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    /{cat.weight}
                  </span>
                  {cat.deductions > 0 && (
                    <div style={{ fontSize: '0.7rem', color: 'var(--status-critical)', fontWeight: 600 }}>
                      -{cat.deductions} pts
                    </div>
                  )}
                </div>
              </div>

              {/* Progress bar */}
              <div className="progress-bar-bg">
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: fillColor,
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <span>{cat.findings_count} finding{cat.findings_count !== 1 ? 's' : ''}</span>
                <span>{percentage}% score</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
