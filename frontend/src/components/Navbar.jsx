import React, { useEffect, useState } from 'react';
import { ShieldCheck, Activity, Terminal, ExternalLink } from 'lucide-react';
import { checkBackendHealth } from '../services/api';

export default function Navbar({ onNavigate, currentPage }) {
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    checkBackendHealth().then(setBackendOnline);
    const interval = setInterval(() => {
      checkBackendHealth().then(setBackendOnline);
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0.85rem 2rem',
      backgroundColor: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-card)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '8px',
          backgroundColor: 'var(--bg-card)',
          border: '1px solid rgba(34, 197, 94, 0.4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--accent-primary)',
          cursor: 'pointer',
        }} onClick={() => onNavigate('dashboard')}>
          <ShieldCheck size={22} />
        </div>
        <div style={{ cursor: 'pointer' }} onClick={() => onNavigate('dashboard')}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontWeight: 800, fontSize: '1.2rem', letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>
              Rebuild<span style={{ color: 'var(--accent-primary)' }}>OS</span>
            </span>
            <span className="badge badge-neutral" style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem' }}>
              v1.0.0
            </span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>
            "Works on my machine? Let's prove it."
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* Backend health status pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.45rem',
          padding: '0.35rem 0.75rem',
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-full)',
          fontSize: '0.75rem',
          fontWeight: 600,
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: backendOnline ? 'var(--accent-primary)' : 'var(--status-warning)',
            boxShadow: backendOnline ? '0 0 8px var(--accent-primary)' : 'none',
          }} />
          <span style={{ color: backendOnline ? 'var(--text-secondary)' : 'var(--status-warning)' }}>
            API: {backendOnline ? 'Online (Port 8000)' : 'Offline / Standalone Mode'}
          </span>
        </div>

        {/* Quick CLI docs button */}
        <button
          className="btn btn-secondary"
          style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
          onClick={() => onNavigate('docs')}
        >
          <Terminal size={15} />
          CLI Guide
        </button>
      </div>
    </header>
  );
}
