import React from 'react';

function SidebarControls({ 
  onAnalyze, 
  loading, 
  radius, 
  setRadius, 
  onDownloadPDF, 
  onToggleHistory, 
  mapMode, 
  setMapMode,
  selectedLocation, // Injected to detect active sessions
  onRefresh        // Injected to trigger state resets
}) {
  
  const activeBtnStyle = { flex: 1, padding: '10px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', transition: '0.2s' };
  const inactiveBtnStyle = { flex: 1, padding: '10px', backgroundColor: '#374151', color: '#9ca3af', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', transition: '0.2s' };
  const actionButtonStyle = { width: '100%', padding: '12px', backgroundColor: '#1f2937', color: '#e5e7eb', border: '1px solid #4b5563', borderRadius: '6px', cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s', textAlign: 'center' };

  return (
    <div style={{ width: '320px', backgroundColor: '#1f2937', color: '#f9fafb', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px', boxShadow: '2px 0 10px rgba(0,0,0,0.5)', zIndex: 10, overflowY: 'auto' }}>
      
      <div>
        <h3 style={{ margin: '0 0 10px 0', color: '#f3f4f6' }}>Map Tools</h3>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button type="button" onClick={() => setMapMode('explore')} style={mapMode === 'explore' ? activeBtnStyle : inactiveBtnStyle}>Explore Map</button>
          <button type="button" onClick={() => setMapMode('select')} style={mapMode === 'select' ? activeBtnStyle : inactiveBtnStyle}>Select Site</button>
        </div>
      </div>

      <div>
        <label style={{ display: 'block', fontSize: '0.9rem', color: '#9ca3af', fontWeight: '500' }}>
          Catchment Radius: <span style={{color: '#10b981'}}>{radius} m</span>
        </label>
        <input 
          type="range" 
          min="50" 
          max="1000" 
          step="50"
          value={radius} 
          onChange={(e) => setRadius(Number(e.target.value))}
          style={{ width: '100%', marginTop: '10px', cursor: 'pointer', accentColor: '#10b981' }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <button 
          type="button"
          onClick={onAnalyze} 
          disabled={loading || !selectedLocation}
          style={{ 
            backgroundColor: (loading || !selectedLocation) ? '#4b5563' : '#10b981', 
            color: 'white', 
            padding: '14px', 
            borderRadius: '8px', 
            border: 'none', 
            cursor: (loading || !selectedLocation) ? 'not-allowed' : 'pointer', 
            fontWeight: 'bold', 
            fontSize: '1rem', 
            transition: '0.2s',
            width: '100%'
          }}
        >
          {loading ? 'Mining Data Matrix...' : 'Run Market Analysis'}
        </button>

        {/* NEW: Dynamic Refresh Button displayed right after selection or analysis execution */}
        {selectedLocation && (
          <button 
            type="button"
            onClick={onRefresh}
            style={{ width: '100%', padding: '10px', backgroundColor: '#374151', color: '#f3f4f6', border: '1px solid #4b5563', borderRadius: '6px', cursor: 'pointer', fontSize: '0.85rem', fontWeight: '600' }}
          >
            🔄 Reset & Clear Map Selection
          </button>
        )}
      </div>

      <hr style={{ border: 'none', borderTop: '1px solid #4b5563', margin: '5px 0' }} />

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <button type="button" onClick={onDownloadPDF} style={actionButtonStyle}>Download Report (PDF)</button>
        <button type="button" onClick={onToggleHistory} style={actionButtonStyle}>View Search History</button>
      </div>

    </div>
  );
}

export default SidebarControls;