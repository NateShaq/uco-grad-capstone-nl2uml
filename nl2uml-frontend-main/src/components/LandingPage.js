import React, { useState } from 'react';
import CapstoneModal from './CapstoneModal';
import projectMeta from '../projectMeta';

function LandingPage({ onStart }) {
  const [showCapstone, setShowCapstone] = useState(false);
  const { university, student, professor } = projectMeta;

  return (
    <>
      <div className="d-flex align-items-center justify-content-center min-vh-100 bg-dark text-light">
        <div className="p-5 bg-black bg-opacity-50 rounded-4 shadow-lg" style={{ maxWidth: 880 }}>
          <div className="text-uppercase fw-semibold text-warning mb-2" style={{ letterSpacing: 2 }}>nl2uml</div>
          <h1 className="display-5 fw-bold mb-3">Generate and refine UML without signing in</h1>
          <p className="lead text-secondary mb-4">
            Start a fresh workspace, capture diagrams, and iterate with AI. Each session gets a private, random ID so your work stays grouped together.
          </p>
          <div className="d-flex flex-wrap gap-3 align-items-center">
            <button className="btn btn-primary btn-lg px-4" onClick={onStart}>
              Start New Session
            </button>
            <button className="btn btn-outline-light px-4" onClick={() => setShowCapstone(true)}>
              Capstone provenance
            </button>
          </div>

          <div className="mt-4 p-3 rounded-3 bg-secondary bg-opacity-25">
            <div className="text-uppercase text-warning fw-semibold small mb-1">Graduate Capstone</div>
            <div className="fw-bold">{university.name}</div>
            <p className="mb-2 text-secondary small">{university.description}</p>
            <div className="d-flex flex-wrap gap-3 text-secondary small">
              <div className="d-flex align-items-center gap-2">
                <span className="badge bg-primary">Student</span>
                <span className="fw-semibold text-light">{student.name}</span>
              </div>
              <div className="d-flex align-items-center gap-2">
                <span className="badge bg-light text-dark">Professor</span>
                <span className="fw-semibold text-light">{professor.name}</span>
              </div>
              <div className="d-flex align-items-center gap-2">
                <span className="badge bg-dark border border-light">Department</span>
                <span className="fw-semibold text-light">{projectMeta.department.name}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <CapstoneModal show={showCapstone} onHide={() => setShowCapstone(false)} />
    </>
  );
}

export default LandingPage;
