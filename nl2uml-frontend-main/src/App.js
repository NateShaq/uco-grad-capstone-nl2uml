import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

import AuthenticatedApp from './AuthenticatedApp';
import LandingPage from './components/LandingPage';

const SESSION_STORAGE_KEY = 'nl2uml-session-id';

function generateSessionId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for older browsers
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function App() {
  const [sessionId, setSessionId] = useState(() => window.localStorage.getItem(SESSION_STORAGE_KEY) || '');

  useEffect(() => {
    if (sessionId) {
      window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
      window.localStorage.setItem("userEmail", sessionId);
    }
  }, [sessionId]);

  const handleStartSession = () => {
    const newSession = generateSessionId();
    setSessionId(newSession);
  };

  if (!sessionId) {
    return <LandingPage onStart={handleStartSession} />;
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/*"
          element={<AuthenticatedApp key={sessionId} sessionId={sessionId} onNewSession={handleStartSession} />}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
