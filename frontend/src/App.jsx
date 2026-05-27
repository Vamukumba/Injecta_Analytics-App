import React, { useState } from 'react';
import Home from './Components/Home';
import Login from './Components/Login';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <div>
      {!isAuthenticated ? (
        <Login onLoginSuccess={() => setIsAuthenticated(true)} />
      ) : (
        <Home onLogout={() => setIsAuthenticated(false)} />
      )}
    </div>
  );
}

export default App;