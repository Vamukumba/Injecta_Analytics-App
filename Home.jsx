import React, { useState } from 'react';
import MapViewer from './MapViewer';
import ResultsDashboard from './ResultsDashboard';
import SidebarControls from './SidebarControls';
import Navbar from './Navbar';

function Home({ onLogout }) {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [mapMode, setMapMode] = useState('explore'); 
  const [radius, setRadius] = useState(500); 
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  // 1. RUN ENGINE ANALYSIS FUNCTION
  const handleAnalyze = async () => {
    if (!selectedLocation) {
      alert("Please toggle 'Pinpoint Site' mode and click on the map boundary first!");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('https://geoai-backend.onrender.com/api/analyze'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          longitude: selectedLocation.lng,
          latitude: selectedLocation.lat,
          radius_meters: radius
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setAnalysisResult(data);
        // Save to application runtime session history
        setHistory(prev => [data, ...prev]);
      } else {
        alert(data.message || "Analysis failed outside parameters.");
      }
    } catch (err) {
      alert("Server response error. Verify Flask server connectivity.");
    } finally {
      setLoading(false);
    }
  };

  // 2. REFRESH / CLEAR SYSTEM ENGINE ACTION
  const handleRefreshMap = () => {
    setSelectedLocation(null);
    setAnalysisResult(null);
  };

  // 3. ZERO-DEPENDENCY REPORT DOWNLOAD GENERATOR
  const handleDownloadPDF = () => {
    if (!analysisResult) {
      alert("⚠️ Request Denied: Please run a 'Market Analysis' before printing reports.");
      return;
    }

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>GeoAI Spatial Analysis Summary</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 40px; color: #1f2937; line-height: 1.5; }
            .header { border-bottom: 3px solid #10b981; padding-bottom: 15px; margin-bottom: 25px; }
            .title { font-size: 26px; font-weight: bold; color: #111827; }
            .meta { font-size: 12px; color: #6b7280; margin-top: 5px; }
            .box { background: #f0fdf4; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; border-radius: 4px; }
            .box h2 { margin: 0 0 8px 0; color: #065f46; font-size: 18px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #e5e7eb; padding: 10px; text-align: left; font-size: 14px; }
            th { background-color: #f9fafb; font-weight: bold; }
          </style>
        </head>
        <body>
          <div class="header">
            <div class="title">GeoAI Market Analysis Report</div>
            <div class="meta">Generated: ${new Date().toLocaleString()} | Target Coordinates: ${analysisResult.meta_metrics?.lat?.toFixed(5) || selectedLocation.lat.toFixed(5)}, ${analysisResult.meta_metrics?.lng?.toFixed(5) || selectedLocation.lng.toFixed(5)}</div>
          </div>
          <div class="box">
            <h2>Strategic Proposition Recommendation</h2>
            <strong>Target Model: ${analysisResult.recommended_business || 'General Business Model'}</strong>
            <p>${analysisResult.message || 'Market analysis executed successfully for specified radius.'}</p>
          </div>
          <h3>Empirical Zonal Metrics Vector</h3>
          <table>
            <thead><tr><th>Evaluation Metric</th><th>Calculated Matrix Value</th></tr></thead>
            <tbody>
              <tr><td>Evaluated Sector Population</td><td>${analysisResult.meta_metrics?.population || 'N/A'} Citizens</td></tr>
              <tr><td>Residential Density Profile</td><td>${analysisResult.meta_metrics?.density || 'N/A'} Profile</td></tr>
              <tr><td>Primary Commerce Anchor Vector</td><td>${analysisResult.meta_metrics?.influence_center || 'N/A'}</td></tr>
              <tr><td>Localized Grocery Density Index</td><td>${analysisResult.meta_metrics?.grocery_count || 0} Active Outposts</td></tr>
              <tr><td>Distance Vector to Nearest Core Hub</td><td>${analysisResult.meta_metrics?.distance_to_hub || 'N/A'} km</td></tr>
              <tr><td>Direct Empirical Ground Inquiries</td><td>${analysisResult.meta_metrics?.interviews_conducted || 0} Field Records</td></tr>
              <tr><td>Primary Consumer Purchase Demands</td><td>${analysisResult.meta_metrics?.frequent_goods || 'N/A'}</td></tr>
            </tbody>
          </table>
          <script>window.onload = function() { window.print(); window.close(); };</script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: '#111827' }}>
      <Navbar onLogout={onLogout} isAuthenticated={true} />
      
      <div style={{ display: 'flex', flex: 1, position: 'relative', overflow: 'hidden' }}>
        <SidebarControls 
          onAnalyze={handleAnalyze}
          loading={loading}
          radius={radius}
          setRadius={setRadius}
          mapMode={mapMode}
          setMapMode={setMapMode}
          onToggleHistory={() => setShowHistory(!showHistory)}
          onDownloadPDF={handleDownloadPDF}
          selectedLocation={selectedLocation}
          onRefresh={handleRefreshMap}
        />
        
        <div style={{ flex: 1, position: 'relative', height: '100%' }}>
          <MapViewer 
            selectedLocation={selectedLocation}
            setSelectedLocation={setSelectedLocation}
            mapMode={mapMode}
            radius={radius}
          />
          
          {analysisResult && (
            <ResultsDashboard data={analysisResult} onDownloadPDF={handleDownloadPDF} />
          )}
        </div>
      </div>

      {/* OVERLAY SEARCH HISTORY MODAL PANEL */}
      {showHistory && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
          <div style={{ backgroundColor: '#1f2937', color: 'white', padding: '25px', borderRadius: '12px', width: '450px', maxHeight: '70vh', overflowY: 'auto', border: '1px solid #4b5563' }}>
            <h3 style={{ margin: '0 0 15px 0', borderBottom: '1px solid #4b5563', paddingBottom: '10px' }}>Saved Engine Search History</h3>
            
            {history.length === 0 ? (
              <p style={{ color: '#9ca3af', fontSize: '0.9rem' }}>No logged metrics records captured inside this user terminal session yet.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {history.map((item, index) => (
                  <div key={index} style={{ backgroundColor: '#374151', padding: '12px', borderRadius: '6px', borderLeft: '4px solid #3b82f6' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '0.95rem', color: '#60a5fa' }}>{item.recommended_business || 'Business Analysis'}</div>
                    <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Density: {item.meta_metrics?.density || 'N/A'} | Pop: {item.meta_metrics?.population || 'N/A'}</div>
                  </div>
                ))}
              </div>
            )}
            
            <button 
              onClick={() => setShowHistory(false)}
              style={{ marginTop: '20px', width: '100%', padding: '10px', backgroundColor: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}
            >
              Close History Panel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Home;