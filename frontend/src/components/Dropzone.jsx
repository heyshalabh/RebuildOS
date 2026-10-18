import React, { useState, useRef } from 'react';
import { UploadCloud, FileArchive, AlertCircle, Loader2 } from 'lucide-react';

export default function Dropzone({ onFileSelected, isLoading, error }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [localError, setLocalError] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const validateAndProcessFile = (file) => {
    setLocalError('');
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.zip')) {
      setLocalError('Invalid file type. Please upload a valid .zip project archive.');
      return;
    }

    // 50MB maximum limit
    if (file.size > 50 * 1024 * 1024) {
      setLocalError(`Archive is too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Max limit is 50 MB.`);
      return;
    }

    if (file.size === 0) {
      setLocalError('The selected archive is empty.');
      return;
    }

    setSelectedFile(file);
    onFileSelected(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndProcessFile(e.target.files[0]);
    }
  };

  const displayError = error || localError;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isLoading && fileInputRef.current?.click()}
        style={{
          border: '2px dashed',
          borderColor: isDragging ? 'var(--accent-primary)' : 'var(--border-card)',
          borderRadius: 'var(--radius-md)',
          padding: '2.5rem 1.5rem',
          backgroundColor: isDragging ? 'rgba(34, 197, 94, 0.05)' : 'var(--bg-card)',
          cursor: isLoading ? 'wait' : 'pointer',
          textAlign: 'center',
          transition: 'all 0.2s ease',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.85rem',
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          style={{ display: 'none' }}
          onChange={handleFileInputChange}
          disabled={isLoading}
        />

        {isLoading ? (
          <>
            <Loader2 size={42} color="var(--accent-primary)" style={{ animation: 'spin 1s linear infinite' }} />
            <div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)' }}>
                Analyzing Project Archive...
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Running deterministic AST & configuration checks across runtime, dependencies, and build specs.
              </div>
            </div>
          </>
        ) : (
          <>
            <div style={{
              width: '54px',
              height: '54px',
              borderRadius: '50%',
              backgroundColor: 'var(--bg-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-primary)',
            }}>
              <UploadCloud size={28} />
            </div>

            <div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)', marginBottom: '0.2rem' }}>
                Drag & drop your repository <span style={{ color: 'var(--accent-primary)' }}>.ZIP</span> archive here
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                or click to browse from your computer (Max 50 MB)
              </div>
            </div>

            {selectedFile && !displayError && (
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-card)',
                padding: '0.35rem 0.75rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.8rem',
                color: 'var(--text-secondary)',
              }}>
                <FileArchive size={14} color="var(--accent-primary)" />
                {selectedFile.name} ({(selectedFile.size / 1024).toFixed(0)} KB)
              </div>
            )}
          </>
        )}
      </div>

      {displayError && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.75rem 1rem',
          backgroundColor: 'var(--status-critical-bg)',
          border: '1px solid var(--status-critical-border)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.85rem',
          color: 'var(--status-critical)',
        }}>
          <AlertCircle size={16} style={{ flexShrink: 0 }} />
          <span>{displayError}</span>
        </div>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
