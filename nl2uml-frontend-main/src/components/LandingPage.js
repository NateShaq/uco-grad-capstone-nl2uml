import React, { useState } from 'react';
import CapstoneModal from './CapstoneModal';
import projectMeta from '../projectMeta';

function LandingPage({ onStart }) {
  const [showCapstone, setShowCapstone] = useState(false);
  const {
    university,
    student,
    professor,
    department,
    version,
    technologies,
    documentation: { primary, report },
    abstract
  } = projectMeta;

  return (
    <>
      <div
        className="d-flex align-items-center justify-content-center min-vh-100 bg-dark text-light"
        style={{ paddingTop: 48, paddingBottom: 48 }}
      >
        <div className="p-5 bg-black bg-opacity-50 rounded-4 shadow-lg" style={{ maxWidth: 880 }}>
          <div className="text-center mb-3">
            <img
              src={`${process.env.PUBLIC_URL}/UCO_Logo.svg`}
              alt="University of Central Oklahoma logo"
              style={{ maxHeight: 64, width: 'auto' }}
            />
          </div>
          <div className="text-uppercase fw-semibold text-warning mb-2" style={{ letterSpacing: 2 }}>nl2uml</div>
          <h1 className="display-5 fw-bold mb-3">Agent‑orchestrated UML generation and refinement</h1>
          <p className="lead text-secondary mb-4">
            Graduate research prototype that routes natural-language requirements through an LLM pipeline for UML synthesis, validation, and export. Sessions use random IDs so each experiment stays isolated.
          </p>
          <div className="d-flex flex-wrap gap-3 align-items-center">
            <button className="btn btn-primary btn-lg px-4" onClick={onStart}>
              Start New Session
            </button>
            <button className="btn btn-outline-light px-4" onClick={() => setShowCapstone(true)}>
              Capstone Provenance
            </button>
          </div>

          <div className="mt-4 p-4 rounded-4 bg-secondary bg-opacity-10 border border-secondary">
            <div className="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-3">
              <div>
                <div className="text-uppercase text-warning fw-semibold small mb-1">Project context</div>
                <div className="d-flex flex-wrap align-items-center gap-2 mt-1">
                  <span className="badge bg-primary">Version {version}</span>
                  <span className="badge bg-dark border border-light text-light">Research build</span>
                </div>
              </div>
              <div className="d-flex flex-wrap gap-2">
                <a className="btn btn-outline-warning btn-sm" href={primary.url} target="_blank" rel="noreferrer">
                  {primary.label}
                </a>
                <a className="btn btn-outline-primary btn-sm" href={report.url} target="_blank" rel="noreferrer">
                  Public GitHub
                </a>
              </div>
            </div>
            <div className="p-4 bg-black bg-opacity-50 rounded-3 mb-3">
              <div className="text-uppercase text-secondary fw-semibold small mb-2">Project abstract</div>
              <p className="mb-0 text-light">{abstract}</p>
            </div>
            <div className="p-4 bg-black bg-opacity-50 rounded-3">
              <div className="text-uppercase text-secondary fw-semibold small mb-2">Technologies used</div>
              <div className="d-flex flex-wrap gap-2">
                {technologies.map((item) => (
                  <span key={item} className="badge bg-light text-dark">
                    {item}
                  </span>
                ))}
              </div>
            </div>
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
                <span className="fw-semibold text-light">{department.name}</span>
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
