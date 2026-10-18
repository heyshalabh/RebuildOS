import React from 'react';
import { 
  LayoutDashboard, 
  SearchCode, 
  FileText, 
  BookOpen, 
  Info,
  CheckCircle2
} from 'lucide-react';

export default function Sidebar({ currentPage, onNavigate, hasActiveScan }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'results', label: 'Scan Diagnostics', icon: SearchCode, disabled: !hasActiveScan },
    { id: 'report', label: 'Audit Report', icon: FileText, disabled: !hasActiveScan },
    { id: 'docs', label: 'Documentation', icon: BookOpen },
    { id: 'about', label: 'About & Security', icon: Info },
  ];

  return (
    <aside className="sidebar" style={{
      width: '240px',
      backgroundColor: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border-card)',
      padding: '1.5rem 1rem',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div style={{
          fontSize: '0.7rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          color: 'var(--text-muted)',
          padding: '0 0.75rem 0.5rem 0.75rem',
        }}>
          Navigation
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              disabled={item.disabled}
              onClick={() => onNavigate(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: isActive ? 'var(--bg-card)' : 'transparent',
                color: isActive ? 'var(--accent-primary)' : (item.disabled ? 'var(--text-dim)' : 'var(--text-secondary)'),
                border: '1px solid',
                borderColor: isActive ? 'rgba(34, 197, 94, 0.3)' : 'transparent',
                fontSize: '0.875rem',
                fontWeight: isActive ? 700 : 500,
                textAlign: 'left',
                cursor: item.disabled ? 'not-allowed' : 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              <Icon size={18} color={isActive ? 'var(--accent-primary)' : 'currentColor'} />
              <span>{item.label}</span>
              {item.id === 'results' && hasActiveScan && (
                <span style={{
                  marginLeft: 'auto',
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--accent-primary)',
                }} />
              )}
            </button>
          );
        })}
      </div>

      {/* Footer Info Box */}
      <div style={{
        padding: '0.85rem',
        backgroundColor: 'var(--bg-card)',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--border-subtle)',
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-primary)', fontWeight: 600, marginBottom: '0.25rem' }}>
          <CheckCircle2 size={14} />
          100% Offline Analysis
        </div>
        No third-party AI keys or external code transmissions required.
      </div>
    </aside>
  );
}
