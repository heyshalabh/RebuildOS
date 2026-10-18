/**
 * API Service for connecting to the RebuildOS backend.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (!res.ok) return false;
    const data = await res.json();
    return data.status === 'ok';
  } catch {
    return false;
  }
}

export async function scanZipFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/api/scan`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Scan failed with status ${res.status}`);
  }

  return await res.json();
}

export async function scanLocalDirectory(directoryPath) {
  const res = await fetch(`${API_BASE_URL}/api/scan/local`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ directory_path: directoryPath }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Local scan failed with status ${res.status}`);
  }

  return await res.json();
}

export async function exportReport(scanResult, format = 'markdown') {
  const res = await fetch(`${API_BASE_URL}/api/report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      scan_result: scanResult,
      format: format,
    }),
  });

  if (!res.ok) {
    throw new Error('Failed to generate downloadable report.');
  }

  if (format === 'json') {
    return await res.text();
  } else {
    return await res.text();
  }
}

// LocalStorage helpers for Recent Scans
const STORAGE_KEY = 'rebuildos_recent_scans';

export function getStoredScans() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveScanToStorage(scanResult) {
  try {
    const current = getStoredScans();
    // Keep max 10 recent scans, replace existing with same project_name
    const filtered = current.filter(s => s.project_name !== scanResult.project_name);
    const updated = [
      {
        project_name: scanResult.project_name,
        readiness_score: scanResult.readiness_score,
        readiness_label: scanResult.readiness_label,
        scan_timestamp: scanResult.scan_timestamp,
        detected_languages: scanResult.detected_languages,
        findings_count: scanResult.findings?.length || 0,
        full_result: scanResult,
      },
      ...filtered,
    ].slice(0, 10);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (err) {
    console.error('Failed to save scan to localStorage:', err);
  }
}

export function clearStoredScans() {
  localStorage.removeItem(STORAGE_KEY);
}
