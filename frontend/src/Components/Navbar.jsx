import React from 'react';

function Navbar({ onLogout, isAuthenticated }) {
  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '15px 30px',
      backgroundColor: '#1f2937',
      color: 'white',
      borderBottom: '1px solid #374151',
      fontFamily: 'sans-serif',
      zIndex: 4000
    }}>
      <h2 style={{ color: '#60a5fa', margin: 0, letterSpacing: '1px' }}>GeoAI Engine Dashboard</h2>
      
      <div>
        {isAuthenticated ? (
          <button 
            onClick={onLogout} 
            style={{
              padding: '8px 16px',
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 'bold',
              transition: 'background-color 0.2s'
            }}
          >
            Logout
          </button>
        ) : (
          <span style={{ color: '#9ca3af', fontSize: '0.9rem' }}>Public Workspace Portal</span>
        )}
      </div>
    </nav>
  );
}

export default Navbar;