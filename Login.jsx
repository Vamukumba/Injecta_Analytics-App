import React, { useState } from 'react';

function Login({ onLoginSuccess }) {
  // Navigation & View States
  const [activeSection, setActiveSection] = useState('home'); 
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);
  
  // Form input states
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');

  // Pricing State Simulation
  const handlePriceTierClick = (tierName, price) => {
    alert(`Redirecting to Secure Payment Gateway for the ${tierName} plan ($${price}). After payment confirmation, your account quota will update automatically.`);
  };

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    const endpoint = isLoginMode ? 'login' : 'register';
    const payload = isLoginMode ? { username, password } : { username, password };

    try {
      const response = await fetch(`http://localhost:5000/api/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      
      if (data.success) {
        if (isLoginMode) {
          setShowAuthModal(false);
          onLoginSuccess();
        } else {
          alert("Account created successfully! Please log in.");
          setIsLoginMode(true);
        }
      } else {
        setAuthError(data.message || "Authentication failed. Please verify configurations.");
      }
    } catch (err) {
      setAuthError("Could not connect to back-end server engine.");
    }
  };

  return (
    <div style={{ backgroundColor: '#111827', color: '#f9fafb', fontFamily: 'sans-serif', minHeight: '100vh', scrollBehavior: 'smooth' }}>
      
      {/* Reference Styled Header Nav Bar */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, height: '70px', backgroundColor: '#1f2937', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 40px', borderBottom: '1px solid #374151', zIndex: 5000 }}>
        <h2 style={{ color: '#60a5fa', margin: 0, letterSpacing: '1px', fontWeight: 'bold', cursor: 'pointer' }} onClick={() => setActiveSection('home')}>GeoAI Engine</h2>
        <div style={{ display: 'flex', gap: '30px', alignItems: 'center' }}>
          <span style={{ cursor: 'pointer', color: activeSection === 'features' ? '#60a5fa' : '#d1d5db', fontWeight: '500' }} onClick={() => { setActiveSection('home'); setTimeout(() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' }), 10); }}>Products</span>
          <span style={{ cursor: 'pointer', color: activeSection === 'about' ? '#60a5fa' : '#d1d5db', fontWeight: '500' }} onClick={() => { setActiveSection('home'); setTimeout(() => document.getElementById('about').scrollIntoView({ behavior: 'smooth' }), 10); }}>About Us</span>
          <span style={{ cursor: 'pointer', color: activeSection === 'pricing' ? '#60a5fa' : '#d1d5db', fontWeight: '500' }} onClick={() => { setActiveSection('home'); setTimeout(() => document.getElementById('pricing').scrollIntoView({ behavior: 'smooth' }), 10); }}>Pricing</span>
          <button onClick={() => { setIsLoginMode(true); setShowAuthModal(true); }} style={{ padding: '8px 18px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Sign In</button>
        </div>
      </nav>

      {/* Hero Section Container */}
      <div style={{ paddingTop: '130px', pb: '80px', textAlign: 'center', backgroundImage: 'radial-gradient(circle at top, #1e3a8a 0%, #111827 70%)', paddingBottom: '100px' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', padding: '0 20px' }}>
          <span style={{ backgroundColor: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', padding: '6px 16px', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 'bold', uppercase: 'true', letterSpacing: '1px' }}>GEOSPATIAL AI BEYOND TRADITIONAL MAPS</span>
          <h1 style={{ fontSize: '3rem', fontWeight: '800', marginTop: '20px', marginBottom: '20px', lineHeight: '1.2', color: '#ffffff' }}>Spatial Intelligence for Next-Gen Site Suitability</h1>
          <p style={{ fontSize: '1.2rem', color: '#9ca3af', marginBottom: '40px', lineHeight: '1.6' }}>
            Unlocking demographic structural volumes and commercial point densities. Move past static geographic visualizations and generate actionable business recommendations powered by localized geographic machine learning.
          </p>
          <button onClick={() => { setIsLoginMode(false); setShowAuthModal(true); }} style={{ padding: '16px 32px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '8px', fontSize: '1.1rem', fontWeight: 'bold', cursor: 'pointer', boxShadow: '0 4px 14px rgba(16, 185, 129, 0.4)' }}>
            Get Started For Free
          </button>
        </div>
      </div>

      {/* Section: Platform Product Capabilities */}
      <div id="features" style={{ padding: '80px 40px', backgroundColor: '#0f172a', borderTop: '1px solid #1e293b' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{ text: 'center', fontSize: '2rem', fontWeight: '700', marginBottom: '50px', color: '#ffffff', textAlign: 'center' }}>Engineered Web-GIS Functions</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>
            <div style={{ backgroundColor: '#1f2937', padding: '30px', borderRadius: '10px', border: '1px solid #374151' }}>
              <div style={{ fontSize: '2rem', marginBottom: '15px' }}></div>
              <h3 style={{ color: '#60a5fa', fontSize: '1.3rem', margin: '0 0 10px 0' }}>Pinpoint Site Targeting</h3>
              <p style={{ color: '#9ca3af', lineHeight: '1.5', margin: 0 }}>Toggle precise spatial bounds on interactive dark canvasses to extract real-time point-in-polygon query intersections instantly.</p>
            </div>
            <div style={{ backgroundColor: '#1f2937', padding: '30px', borderRadius: '10px', border: '1px solid #374151' }}>
              <div style={{ fontSize: '2rem', marginBottom: '15px' }}></div>
              <h3 style={{ color: '#60a5fa', fontSize: '1.3rem', margin: '0 0 10px 0' }}>Dynamic Catchment Radius</h3>
              <p style={{ color: '#9ca3af', lineHeight: '1.5', margin: 0 }}>Configure buffers dynamically up to 1000 meters to accurately count structural vectors, places of worship, schools, and existing stores.</p>
            </div>
            <div style={{ backgroundColor: '#1f2937', padding: '30px', borderRadius: '10px', border: '1px solid #374151' }}>
              <div style={{ fontSize: '2rem', marginBottom: '15px' }}></div>
              <h3 style={{ color: '#60a5fa', fontSize: '1.3rem', margin: '0 0 10px 0' }}>Automated Market Mining</h3>
              <p style={{ color: '#9ca3af', lineHeight: '1.5', margin: 0 }}>Process localized household interview indicators using our rule-driven Flask inference backend to find optimal commercial allocations.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Section: About Us */}
      <div id="about" style={{ padding: '80px 40px', backgroundColor: '#111827' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '25px', color: '#ffffff' }}>About Our Engine</h2>
          <p style={{ color: '#9ca3af', fontSize: '1.1rem', lineHeight: '1.7', margin: 0 }}>
            GeoAI Market Engine is a sophisticated corporate location intelligence integration built to optimize location-based retail investments. By cross-referencing dense municipal point datasets with active target zone multi-polygons, our system eliminates human blindspots in real-estate feasibility profiling.
          </p>
        </div>
      </div>

      {/* Section: Reference Style Pricing Matrix */}
      <div id="pricing" style={{ padding: '80px 40px', backgroundColor: '#0f172a', borderTop: '1px solid #1e293b' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <h2 style={{ text: 'center', fontSize: '2rem', fontWeight: '700', marginBottom: '15px', color: '#ffffff', textAlign: 'center' }}>Transparent Spatial Quotas</h2>
          <p style={{ textAlign: 'center', color: '#9ca3af', marginBottom: '50px' }}>Select an explicit transactional buffer footprint configuration. Tap your targeted plan to execute an instant billing query.</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '30px' }}>
            {/* Free Tier */}
            <div style={{ backgroundColor: '#1f2937', padding: '35px 25px', borderRadius: '12px', border: '1px solid #374151', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', margin: '0 0 10px 0', color: '#ffffff' }}>Free Discovery</h3>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#60a5fa', marginBottom: '15px' }}>$0 <span style={{ fontSize: '1rem', color: '#9ca3af' }}>/ forever</span></div>
                <ul style={{ color: '#9ca3af', paddingLeft: '20px', lineHeight: '2', margin: '0 0 30px 0' }}>
                  <li>1 Full Spatial Location Analysis</li>
                  <li>Complete Demographic Vector Mining</li>
                  <li>Standard dark mode map support</li>
                </ul>
              </div>
              <button onClick={() => { setIsLoginMode(false); setShowAuthModal(true); }} style={{ width: '100%', padding: '12px', backgroundColor: '#374151', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Get Started Free</button>
            </div>

            {/* $5 Tier */}
            <div style={{ backgroundColor: '#1f2937', padding: '35px 25px', borderRadius: '12px', border: '2px solid #3b82f6', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', position: 'relative' }}>
              <span style={{ position: 'absolute', top: '-12px', right: '20px', backgroundColor: '#3b82f6', color: 'white', fontSize: '0.75rem', fontWeight: 'bold', padding: '4px 12px', borderRadius: '10px' }}>POPULAR</span>
              <div>
                <h3 style={{ fontSize: '1.25rem', margin: '0 0 10px 0', color: '#ffffff' }}>Growth Analyst</h3>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#60a5fa', marginBottom: '15px' }}>$5 <span style={{ fontSize: '1rem', color: '#9ca3af' }}>/ instance</span></div>
                <ul style={{ color: '#9ca3af', paddingLeft: '20px', lineHeight: '2', margin: '0 0 30px 0' }}>
                  <li>3 Distinct Locations Allocation</li>
                  <li>1 Analytical Report Per Location</li>
                  <li>Dynamic Catchment Buffer Adjustments</li>
                </ul>
              </div>
              <button onClick={() => handlePriceTierClick('Growth Analyst', 5)} style={{ width: '100%', padding: '12px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Pay $5 Now</button>
            </div>

            {/* Enterprise Tier */}
            <div style={{ backgroundColor: '#1f2937', padding: '35px 25px', borderRadius: '12px', border: '1px solid #374151', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', margin: '0 0 10px 0', color: '#ffffff' }}>Spatial Enterprise</h3>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#60a5fa', marginBottom: '15px' }}>Custom <span style={{ fontSize: '1rem', color: '#9ca3af' }}>/ quota</span></div>
                <ul style={{ color: '#9ca3af', paddingLeft: '20px', lineHeight: '2', margin: '0 0 30px 0' }}>
                  <li>Unlimited Boundary Intersections</li>
                  <li>Bulk Batch Multi-Polygon Mining</li>
                  <li>Direct API Endpoint Integration</li>
                </ul>
              </div>
              <button onClick={() => alert('Contacting enterprise architecture department at sales@injectaanalytics.com')} style={{ width: '100%', padding: '12px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Contact Sales</button>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Floating Authentication Modal */}
      {showAuthModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10000, backdropFilter: 'blur(5px)' }}>
          <div style={{ backgroundColor: '#1f2937', padding: '40px', borderRadius: '12px', width: '420px', border: '1px solid #374151', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h3 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 'bold', color: '#ffffff' }}>
                {isLoginMode ? 'Secure Platform Login' : 'Create Platform Account'}
              </h3>
              <button onClick={() => setShowAuthModal(false)} style={{ background: 'none', border: 'none', color: '#9ca3af', fontSize: '1.5rem', cursor: 'pointer' }}>&times;</button>
            </div>

            {authError && <div style={{ backgroundColor: '#ef4444', color: 'white', padding: '10px', borderRadius: '6px', marginBottom: '15px', fontSize: '0.9rem' }}>{authError}</div>}

            <form onSubmit={handleAuthSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                style={{ padding: '12px', borderRadius: '6px', border: '1px solid #4b5563', backgroundColor: '#374151', color: 'white', outline: 'none', fontSize: '1rem' }}
              />
              
              {!isLoginMode && (
                <input
                  type="email"
                  placeholder="Email Address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  style={{ padding: '12px', borderRadius: '6px', border: '1px solid #4b5563', backgroundColor: '#374151', color: 'white', outline: 'none', fontSize: '1rem' }}
                />
              )}

              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ padding: '12px', borderRadius: '6px', border: '1px solid #4b5563', backgroundColor: '#374151', color: 'white', outline: 'none', fontSize: '1rem' }}
              />

              <button type="submit" style={{ padding: '14px', borderRadius: '6px', border: 'none', backgroundColor: '#3b82f6', color: 'white', fontSize: '1rem', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px' }}>
                {isLoginMode ? 'Verify Credentials' : 'Register Engine Account'}
              </button>
            </form>

            <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '0.9rem', color: '#d1d5db' }}>
              {isLoginMode ? "Don't have an account? " : "Already registered? "}
              <span onClick={() => setIsLoginMode(!isLoginMode)} style={{ color: '#60a5fa', cursor: 'pointer', fontWeight: 'bold', textDecoration: 'underline' }}>
                {isLoginMode ? "Register here" : "Log in"}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Login;