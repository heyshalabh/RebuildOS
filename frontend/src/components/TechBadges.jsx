import React from 'react';
import { Layers, Package, Cpu, FileWarning, Check } from 'lucide-react';

export default function TechBadges({ 
  languages = [], 
  frameworks = [], 
  packageManagers = [], 
  runtimeVersions = {}, 
  manifests = [], 
  missingFiles = [] 
}) {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Layers size={18} color="var(--accent-primary)" />
        Detected Technology Stack & Manifests
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        {/* Languages & Frameworks */}
        <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
            Languages & Frameworks
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {languages.map((lang) => (
              <span key={lang} className="badge badge-success" style={{ fontSize: '0.75rem' }}>
                {lang}
              </span>
            ))}
            {frameworks.map((fw) => (
              <span key={fw} className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                {fw}
              </span>
            ))}
            {languages.length === 0 && frameworks.length === 0 && (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>None detected</span>
            )}
          </div>
        </div>

        {/* Package Managers */}
        <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
            Package Managers
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {packageManagers.map((pm) => (
              <span key={pm} className="badge badge-neutral" style={{ fontSize: '0.75rem' }}>
                <Package size={12} /> {pm}
              </span>
            ))}
            {packageManagers.length === 0 && (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>None detected</span>
            )}
          </div>
        </div>

        {/* Runtime Versions */}
        <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
            Runtime Versions
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {Object.entries(runtimeVersions).map(([rt, ver]) => (
              <span key={rt} className="badge badge-neutral" style={{ fontSize: '0.75rem' }}>
                <Cpu size={12} /> {rt}: {ver}
              </span>
            ))}
            {Object.keys(runtimeVersions).length === 0 && (
              <span style={{ fontSize: '0.8rem', color: 'var(--status-warning)' }}>
                ⚠️ Not explicitly declared
              </span>
            )}
          </div>
        </div>

        {/* Missing or Inconsistent Files */}
        {missingFiles.length > 0 && (
          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.05)', border: '1px solid var(--status-critical-border)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--status-critical)', marginBottom: '0.5rem', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <FileWarning size={14} /> Missing Critical Files
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {missingFiles.map((f) => (
                <span key={f} className="badge badge-critical" style={{ fontSize: '0.7rem' }}>
                  {f}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
