import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import ScanResultsPage from './pages/ScanResultsPage';
import ReportPage from './pages/ReportPage';
import DocsPage from './pages/DocsPage';
import AboutPage from './pages/AboutPage';
import { getStoredScans, saveScanToStorage } from './services/api';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [currentScan, setCurrentScan] = useState(null);
  const [recentScans, setRecentScans] = useState([]);

  // Load recent scans from browser storage on mount
  const refreshRecentScans = () => {
    setRecentScans(getStoredScans());
  };

  useEffect(() => {
    refreshRecentScans();
  }, []);

  const handleScanComplete = (scanResult) => {
    setCurrentScan(scanResult);
    saveScanToStorage(scanResult);
    refreshRecentScans();
    setCurrentPage('results');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectRecent = (scanResult) => {
    setCurrentScan(scanResult);
    setCurrentPage('results');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar onNavigate={setCurrentPage} currentPage={currentPage} />

      <div className="app-container">
        <Sidebar
          currentPage={currentPage}
          onNavigate={setCurrentPage}
          hasActiveScan={Boolean(currentScan)}
        />

        <main className="main-content">
          {currentPage === 'dashboard' && (
            <DashboardPage
              onScanComplete={handleScanComplete}
              recentScans={recentScans}
              onSelectRecent={handleSelectRecent}
              onRefreshRecent={refreshRecentScans}
            />
          )}

          {currentPage === 'results' && (
            <ScanResultsPage
              scanResult={currentScan}
              onRescan={() => setCurrentPage('dashboard')}
              onViewReport={() => setCurrentPage('report')}
            />
          )}

          {currentPage === 'report' && (
            <ReportPage
              scanResult={currentScan}
              onBackToResults={() => setCurrentPage('results')}
            />
          )}

          {currentPage === 'docs' && <DocsPage />}

          {currentPage === 'about' && <AboutPage />}
        </main>
      </div>
    </div>
  );
}
