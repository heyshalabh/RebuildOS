import React, { useState } from 'react';
import { 
  ArrowLeft, 
  FileText, 
  Search, 
  Filter, 
  RotateCcw, 
  AlertCircle, 
  AlertTriangle, 
  Info as InfoIcon,
  ShieldCheck 
} from 'lucide-react';
import ScoreGauge from '../components/ScoreGauge';
import CategoryBreakdown from '../components/CategoryBreakdown';
import TechBadges from '../components/TechBadges';
import FindingCard from '../components/FindingCard';
import Checklist from '../components/Checklist';

export default function ScanResultsPage({ scanResult, onRescan, onViewReport }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');

  if (!scanResult) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>No Active Scan Results</h3>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
          Please upload a repository or scan a local path first.
        </p>
        <button onClick={onRescan} className="btn btn-primary">
          Go to Dashboard
        </button>
      </div>
    );
  }

  // Filter findings
  const allFindings = scanResult.findings || [];
  const filteredFindings = allFindings.filter((f) => {
    // Severity filter
    if (selectedSeverity !== 'all' && f.severity !== selectedSeverity) {
      return false;
    }
    // Category filter
    if (selectedCategory !== 'all' && f.category !== selectedCategory) {
      return false;
    }
    // Search query filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = f.title.toLowerCase().includes(q);
      const matchDesc = f.description.toLowerCase().includes(q);
      const matchFile = (f.affected_file || '').toLowerCase().includes(q);
      const matchId = f.id.toLowerCase().includes(q);
      return matchTitle || matchDesc || matchFile || matchId;
    }
    return true;
  });

  const criticalCount = allFindings.filter(f => f.severity === 'critical').length;
  const warningCount = allFindings.filter(f => f.severity === 'warning').length;
  const infoCount = allFindings.filter(f => f.severity === 'info').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Top action bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <button
            onClick={onRescan}
            className="btn btn-ghost"
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.65rem', marginBottom: '0.25rem' }}
          >
            <ArrowLeft size={14} /> Back to Dashboard
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>
              {scanResult.project_name}
            </h2>
            <span className="badge badge-neutral" style={{ fontSize: '0.75rem' }}>
              {new Date(scanResult.scan_timestamp).toLocaleDateString()}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button onClick={onRescan} className="btn btn-secondary">
            <RotateCcw size={15} />
            Rescan
          </button>

          <button onClick={onViewReport} className="btn btn-primary">
            <FileText size={15} />
            View Full Report
          </button>
        </div>
      </div>

      {/* 1. Score Gauge */}
      <ScoreGauge
        score={scanResult.readiness_score}
        label={scanResult.readiness_label}
        summaryMessage={scanResult.summary_message}
      />

      {/* 2. Detected Stack Badges */}
      <TechBadges
        languages={scanResult.detected_languages}
        frameworks={scanResult.detected_frameworks}
        packageManagers={scanResult.detected_package_managers}
        runtimeVersions={scanResult.runtime_versions}
        manifests={scanResult.manifests_and_lockfiles}
        missingFiles={scanResult.missing_or_inconsistent_files}
      />

      {/* 3. Category Breakdown */}
      <CategoryBreakdown categoryScores={scanResult.category_scores} />

      {/* 4. Interactive Checklist */}
      <Checklist
        items={scanResult.checklist}
        passedChecks={scanResult.passed_checks}
      />

      {/* 5. Build Doctor Diagnostic Findings */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              Build Doctor Diagnostic Findings ({allFindings.length})
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Traceable static findings ranked by rebuild and reproducibility impact
            </p>
          </div>

          {/* Search Input */}
          <div style={{ position: 'relative', minWidth: '220px' }}>
            <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search issues or files..."
              className="input-text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '2rem', fontSize: '0.8125rem' }}
            />
          </div>
        </div>

        {/* Severity Filter Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => setSelectedSeverity('all')}
            className={`btn ${selectedSeverity === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}
          >
            All ({allFindings.length})
          </button>

          <button
            onClick={() => setSelectedSeverity('critical')}
            className={`btn ${selectedSeverity === 'critical' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}
          >
            <AlertCircle size={13} color="var(--status-critical)" />
            Critical ({criticalCount})
          </button>

          <button
            onClick={() => setSelectedSeverity('warning')}
            className={`btn ${selectedSeverity === 'warning' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}
          >
            <AlertTriangle size={13} color="var(--status-warning)" />
            Warning ({warningCount})
          </button>

          <button
            onClick={() => setSelectedSeverity('info')}
            className={`btn ${selectedSeverity === 'info' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}
          >
            <InfoIcon size={13} color="var(--status-info)" />
            Info ({infoCount})
          </button>

          {/* Category Dropdown Filter */}
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Filter size={13} color="var(--text-muted)" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input-text"
              style={{ width: 'auto', fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
            >
              <option value="all">All Categories</option>
              <option value="runtime">Runtime</option>
              <option value="dependency">Dependency</option>
              <option value="build">Build</option>
              <option value="environment">Environment</option>
              <option value="documentation">Documentation</option>
              <option value="test">Test</option>
            </select>
          </div>
        </div>

        {/* Findings List */}
        {filteredFindings.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
            <ShieldCheck size={32} color="var(--accent-primary)" style={{ margin: '0 auto 0.5rem auto' }} />
            <h4 style={{ fontWeight: 700 }}>No issues matching current filters</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Try adjusting your search query or severity filters.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {filteredFindings.map((finding, idx) => (
              <FindingCard key={`${finding.id}_${idx}`} finding={finding} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
