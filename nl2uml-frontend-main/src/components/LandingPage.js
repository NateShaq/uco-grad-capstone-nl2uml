import React from 'react';

function LandingPage({ onStart }) {
  return (
    <div className="d-flex align-items-center justify-content-center min-vh-100 bg-dark text-light">
      <div className="text-center p-5 bg-black bg-opacity-50 rounded-4 shadow-lg" style={{ maxWidth: 720 }}>
        <p className="text-uppercase fw-semibold text-warning mb-2" style={{ letterSpacing: 2 }}>nl2uml</p>
        <h1 className="display-5 fw-bold mb-3">Generate and refine UML without signing in</h1>
        <p className="lead text-secondary mb-4">
          Start a fresh workspace, capture diagrams, and iterate with AI. Each session gets a private, random ID so your work stays grouped together.
        </p>
        <button className="btn btn-primary btn-lg px-4" onClick={onStart}>
          Start New Session
        </button>
      </div>
    </div>
  );
}

export default LandingPage;
