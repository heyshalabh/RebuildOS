import React from 'react';

export default function ScoreGauge({ score, label, summaryMessage }) {
  // Determine color theme based on score tier
  let strokeColor = '#22c55e'; // Green
  let badgeClass = 'badge-success';

  if (score < 50) {
    strokeColor = '#ef4444'; // Red
    badgeClass = 'badge-critical';
  } else if (score < 75) {
    strokeColor = '#f59e0b'; // Amber
    badgeClass = 'badge-warning';
  } else if (score < 90) {
    strokeColor = '#3b82f6'; // Blue
    badgeClass = 'badge-info';
  }

  // Circular SVG progress math (radius 54, circumference 2 * PI * 54 = ~339.29)
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="card" style={{
      display: 'flex',
      alignItems: 'center',
      gap: '2rem',
      flexWrap: 'wrap',
      background: 'linear-gradient(135deg, rgba(21, 27, 35, 1) 0%, rgba(13, 17, 23, 1) 100%)',
    }}>
      {/* Radial Gauge SVG */}
      <div style={{ position: 'relative', width: '136px', height: '136px', flexShrink: 0 }}>
        <svg width="136" height="136" viewBox="0 0 136 136">
          {/* Background Track */}
          <circle
            cx="68"
            cy="68"
            r={radius}
            stroke="var(--bg-subtle)"
            strokeWidth="10"
            fill="transparent"
          />
          {/* Animated Value Arc */}
          <circle
            cx="68"
            cy="68"
            r={radius}
            stroke={strokeColor}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: 'stroke-dashoffset 0.8s ease-out, stroke 0.4s ease',
              transform: 'rotate(-90deg)',
              transformOrigin: '50% 50%',
            }}
          />
        </svg>

        {/* Center Number */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <span style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
            {score}
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, marginTop: '2px' }}>
            / 100
          </span>
        </div>
      </div>

      {/* Score Description & Disclaimer */}
      <div style={{ flex: 1, minWidth: '260px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.5rem' }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Readiness Score</h2>
          <span className={`badge ${badgeClass}`} style={{ fontSize: '0.8rem', padding: '0.25rem 0.65rem' }}>
            {label}
          </span>
        </div>

        <p style={{ fontSize: '0.925rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', lineHeight: 1.45 }}>
          {summaryMessage}
        </p>

        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
          * Estimates repository rebuild preparedness on foreign environments. Does not guarantee build execution without live container compilation.
        </p>
      </div>
    </div>
  );
}
