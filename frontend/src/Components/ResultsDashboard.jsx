import React from 'react';

function ResultsDashboard({ data, onDownloadPDF }) {
  if (!data || data.recommended_business === "Out of Bounds") return null;

  return (
    <div style={styles.dashboardCard}>
      <h3 style={styles.header}>Feasibility Results</h3>
      
      <div style={styles.detailSection}>
        <div style={styles.recommendationContainer}>
          <strong style={styles.subHeader}>Optimal Business Selection</strong><br/>
          <span style={styles.businessTitle}>{data.recommended_business}</span>
        </div>
        
        <p style={styles.detailText}>
          {data.message}
        </p>

        <button onClick={onDownloadPDF} style={styles.pdfButton}>
          Download Report (PDF)
        </button>
      </div>
    </div>
  );
}

const styles = {
  dashboardCard: {
    position: 'absolute', 
    top: '20px',
    right: '20px',
    width: '330px',
    backgroundColor: '#ffffff',
    padding: '24px',
    borderRadius: '12px',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    border: '1px solid #e2e8f0',
    zIndex: 9999, 
    fontFamily: 'sans-serif'
  },
  header: { 
    margin: '0 0 18px 0', 
    color: '#0f172a', 
    fontSize: '17px', 
    fontWeight: '700',
    borderBottom: '2px solid #f1f5f9', 
    paddingBottom: '10px' 
  },
  detailSection: { 
    display: 'flex', 
    flexDirection: 'column' 
  },
  recommendationContainer: { 
    backgroundColor: '#eff6ff', 
    padding: '14px', 
    borderRadius: '8px', 
    borderLeft: '4px solid #3b82f6', 
    marginBottom: '16px' 
  },
  subHeader: { 
    color: '#1e3a8a', 
    fontSize: '11px', 
    textTransform: 'uppercase', 
    letterSpacing: '0.5px' 
  },
  businessTitle: { 
    fontSize: '17px', 
    fontWeight: '700', 
    color: '#1e40af',
    display: 'inline-block',
    marginTop: '4px'
  },
  detailText: { 
    margin: '0 0 20px 0', 
    fontSize: '13px', 
    color: '#475569', 
    lineHeight: '1.6', 
    textAlign: 'justify' 
  },
  pdfButton: {
    padding: '12px',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontSize: '13px',
    transition: 'background-color 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px'
  }
};

export default ResultsDashboard;