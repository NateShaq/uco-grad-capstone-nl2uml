// WorkspaceManager.js
import React, { useEffect, useState } from "react";
import { callApi } from './api';
import { useNavigate, useLocation } from 'react-router-dom';
import OllamaModelSelector from "./OllamaModelSelector";

const API_BASE = 'http://localhost:8080';

const WorkspaceManager = ({ onLoadDiagram, sessionId }) => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectName, setProjectName] = useState("");
  const [projectDesc, setProjectDesc] = useState("");
  const [loading, setLoading] = useState(false);
  const [diagrams, setDiagrams] = useState([]);
  const [diagramName, setDiagramName] = useState("");
  const [diagramType, setDiagramType] = useState("");
  const [diagramPrompt, setDiagramPrompt] = useState("");
  const [agentType, setAgentType] = useState("ollama-pipeline");
  const [ollamaModels, setOllamaModels] = useState({ ideation: '', uml: '', validation: '' });
  const [includeProjectDiagrams, setIncludeProjectDiagrams] = useState(false);
  const [selectedDiagramIds, setSelectedDiagramIds] = useState([]);
  const [designApproach, setDesignApproach] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    const preselectId = location.state?.selectedProjectId;
    if (preselectId && projects.length > 0 && !selectedProject) {
      const found = projects.find(p => p.projectId === preselectId);
      if (found) {
        setSelectedProject(found);
        fetchDiagrams(found.projectId);
      }
    }
  }, [location.state?.selectedProjectId, projects, selectedProject]);

  async function fetchProjects() {
    setLoading(true);
    try {
      const resp = await callApi({ endpoint: `${API_BASE}/projects`, method: 'GET', sessionId });
      setProjects(resp.projects || []);
    } catch (err) {
      console.error("Error fetching projects:", err);
      setProjects([]);
    }
    setLoading(false);
  }

  async function fetchDiagrams(projectId) {
    if (!projectId) return;
    setLoading(true);
    try {
      const resp = await callApi({ endpoint: `${API_BASE}/projects/${projectId}/diagrams`, method: 'GET', sessionId });
      setDiagrams(resp.diagrams || []);
    } catch (err) {
      console.error("Error fetching diagrams:", err);
      setDiagrams([]);
    }
    setLoading(false);
  }

  function handleSelectProject(project) {
    setSelectedProject(project);
    fetchDiagrams(project.projectId);
  }

  async function addProject(e) {
    e.preventDefault();
    setLoading(true);
    try {
      await callApi({
        endpoint: `${API_BASE}/projects`,
        method: 'POST',
        sessionId,
        body: {
          name: projectName,
          description: projectDesc,
          designApproach: designApproach
        },
      });
      setProjectName("");
      setProjectDesc("");
      setDesignApproach("");
      fetchProjects();
    } catch (err) {
      alert("Failed to add project");
    }
    setLoading(false);
  }

  async function deleteProject(projectId, e) {
    e.stopPropagation();
    setLoading(true);
    try {
      setProjects(projects.filter(p => p.projectId !== projectId));
      await callApi({ endpoint: `${API_BASE}/projects/${projectId}`, method: 'DELETE', sessionId });
      setSelectedProject(null);
      setDiagrams([]);
      fetchProjects();
    } catch (err) {
      alert("Failed to delete project: " + err.message);
      fetchProjects();
    }
    setLoading(false);
  }

  async function createDiagram(e) {
    e.preventDefault();
    setLoading(true);
    try {

      console.log("test me");

      console.log("[createDiagram] payload ->", {
        projectId: selectedProject?.projectId,
        name: diagramName,
        diagramType,
        prompt: diagramPrompt,
        AI_Agent: (agentType || "").toLowerCase(),
        attachedDiagramIds: includeProjectDiagrams ? selectedDiagramIds : []
      });

      const modelsPayload =
        agentType.startsWith("ollama") && Object.values(ollamaModels || {}).some(Boolean)
          ? ollamaModels
          : undefined;

      const resp = await callApi({
        endpoint: `${API_BASE}/uml/generate`,
        method: 'POST',
        sessionId,
        body: {
          projectId: selectedProject.projectId,
          name: diagramName,
          diagramType,
          prompt: diagramPrompt,
          AI_Agent: agentType,
          ollamaModels: modelsPayload,
          attachedDiagramIds: includeProjectDiagrams ? selectedDiagramIds : []
        }
      });

      if (resp?.diagramId) await fetchDiagrams(selectedProject.projectId);
      setDiagramName("");
      setDiagramType("");
      setDiagramPrompt("");
      setAgentType("ollama-pipeline");
      setIncludeProjectDiagrams(false);
      setSelectedDiagramIds([]);
    } catch (err) {
      alert("Failed to create diagram");
    }
    setLoading(false);
  }

  async function handleDeleteDiagram(diagramId) {
    if (!window.confirm("Are you sure you want to delete this diagram?")) return;
    setLoading(true);
    try {
      await callApi({ endpoint: `${API_BASE}/diagrams/${diagramId}`, method: 'DELETE', sessionId });
      setDiagrams(diagrams.filter(d => d.diagramId !== diagramId));
    } catch (err) {
      alert("Failed to delete diagram: " + err.message);
    }
    setLoading(false);
  }

  const handleLoadDiagram = async (diagramId) => {
    try {
      const diagram = await callApi({ endpoint: `${API_BASE}/diagrams/${diagramId}`, method: 'GET', sessionId });
      onLoadDiagram(diagram);
      navigate('/diagram', { state: { selectedProjectId: selectedProject?.projectId } });
    } catch (error) {
      console.error('Failed to load diagram:', error);
      alert('Could not load diagram.');
    }
  };


  return (
    <div className="container py-5">
      <div className="row justify-content-between">
        <div className="col-lg-5">
          <div className="card shadow mb-4">
            <div className="card-body">
              <h3 className="card-title text-center mb-4">Your Projects</h3>

              <form className="row g-3 mb-4" onSubmit={addProject}>
                <div className="col-md-6">
                  <input
                    className="form-control"
                    value={projectName}
                    onChange={e => setProjectName(e.target.value)}
                    placeholder="Project Name"
                    required
                  />
                </div>
                <div className="col-md-6">
                  <input
                    className="form-control"
                    value={projectDesc}
                    onChange={e => setProjectDesc(e.target.value)}
                    placeholder="Description"
                  />
                </div>
                <div className="col-md-6">
                  <select
                    className="form-select"
                    value={designApproach}
                    onChange={e => setDesignApproach(e.target.value)}
                    required
                  >
                    <option value="" disabled>Select Design Approach</option>
                    <option value="Domain-Driven Design">Domain-Driven Design</option>
                    <option value="Architecture-First / Microservices">Architecture-First / Microservices</option>
                    <option value="Behavior-Driven Design">Behavior-Driven Design</option>
                    <option value="Test-Driven Development">Test-Driven Development</option>
                    <option value="Model-Driven Architecture">Model-Driven Architecture</option>
                    <option value="Event-Driven Architecture">Event-Driven Architecture</option>
                    <option value="Cognitive Load–Driven Design">Cognitive Load–Driven Design</option>
                    <option value="UX-Driven / User-Centered Design">UX-Driven / User-Centered Design</option>
                    <option value="Security-First Design">Security-First Design</option>
                  </select>
                </div>
                <div className="col-md-6 d-grid">
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    Add
                  </button>
                </div>
              </form>
              <div className="table-responsive">
                <table className="table table-hover align-middle">
                  <thead className="table-light">
                    <tr>
                      <th>Project Name</th>
                      <th>Description</th>
                      <th style={{ width: "130px" }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projects.length === 0 ? (
                      <tr><td colSpan={3} className="text-center text-muted">No projects found.</td></tr>
                    ) : (
                      projects.map((proj) => (
                        <tr key={proj.projectId} onClick={() => handleSelectProject(proj)} style={{ cursor: 'pointer', backgroundColor: selectedProject?.projectId === proj.projectId ? '#d1e7fd' : 'white' }}>
                          <td><b>{proj.name}</b></td>
                          <td>{proj.description}</td>
                          <td>
                            <button className="btn btn-outline-danger btn-sm" onClick={(e) => deleteProject(proj.projectId, e)} disabled={loading}>Delete</button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          {selectedProject && (
            <div className="card shadow mb-4">
              <div className="card-body">
                <h3 className="card-title mb-4">Diagrams for {selectedProject.name}</h3>
                <form onSubmit={createDiagram}>
                  <div className="mb-3">
                    <label className="form-label">Diagram Name</label>
                    <input className="form-control" value={diagramName} onChange={e => setDiagramName(e.target.value)} placeholder="Diagram Name" required />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Diagram Type</label>
                    <select className="form-control" value={diagramType} onChange={e => setDiagramType(e.target.value)} required>
                      <option value="" disabled>Select diagram type</option>
                      <option value="use_case">Use Case Diagram</option>
                      <option value="activity">Activity Diagram</option>
                      <option value="component">Component Diagram</option>
                      <option value="class">Class Diagram</option>
                      <option value="sequence">Sequence Diagram</option>
                      <option value="state">State Diagram</option>
                      <option value="eerd">Enhanced Entity Relationship Diagram</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Initial Prompt</label>
                    <textarea className="form-control" rows="4" value={diagramPrompt} onChange={e => setDiagramPrompt(e.target.value)} placeholder="Enter your prompt here..." required />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Select AI Agent</label>
                    <select className="form-control" value={agentType} onChange={e => setAgentType(e.target.value)}>
                      <option value="ollama-pipeline">Ollama Pipeline (Deepseek ➜ Llama3-Code)</option>
                      <option value="ollama">Ollama (Mistral 7B Instruct)</option>
                      <option value="gronk" disabled>Gronk (X.AI Grok-3 Beta - disabled for local use)</option>
                    </select>
                  </div>
                  {agentType.startsWith("ollama") && (
                    <div className="mb-3">
                      <OllamaModelSelector
                        apiBase={API_BASE}
                        selectedModels={ollamaModels}
                        onChange={setOllamaModels}
                        disabled={loading}
                      />
                    </div>
                  )}
                  <div className="form-check form-switch mb-3 d-flex align-items-center">
                    <input className="form-check-input me-2" type="checkbox" id="includeDiagramsToggle" checked={includeProjectDiagrams} onChange={() => {
                      setIncludeProjectDiagrams(!includeProjectDiagrams);
                      if (!includeProjectDiagrams === false) setSelectedDiagramIds([]);
                    }} />
                    <label className="form-check-label fw-semibold" htmlFor="includeDiagramsToggle">
                      Include Project Diagrams in Generation
                      {includeProjectDiagrams && (
                        <span className="badge bg-info text-dark ms-2">{selectedDiagramIds.length} selected</span>
                      )}
                    </label>
                  </div>
                  <button type="submit" className="btn btn-primary" disabled={loading}>Create Diagram</button>
                </form>
                <hr />
                <h5 className="mt-4">Existing Diagrams</h5>
                <div className="table-responsive">
                  <table className="table table-striped align-middle">
                    <thead className="table-light">
                      <tr>
                        {includeProjectDiagrams && <th>Select</th>}
                        <th>Name</th>
                        <th>Type</th>
                        <th style={{ width: "180px" }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {diagrams.length === 0 ? (
                        <tr><td colSpan={includeProjectDiagrams ? 4 : 3} className="text-center text-muted">No diagrams found for this project.</td></tr>
                      ) : (
                        diagrams.map((diagram) => (
                          <tr key={diagram.diagramId}>
                            {includeProjectDiagrams && (
                              <td>
                                <div className="form-check">
                                  <input className="form-check-input" type="checkbox" id={`check-${diagram.diagramId}`} checked={selectedDiagramIds.includes(diagram.diagramId)} disabled={!includeProjectDiagrams} onChange={() => {
                                    setSelectedDiagramIds((prev) =>
                                      prev.includes(diagram.diagramId) ? prev.filter(id => id !== diagram.diagramId) : [...prev, diagram.diagramId]
                                    );
                                  }} />
                                  <label className="form-check-label visually-hidden" htmlFor={`check-${diagram.diagramId}`}>Select {diagram.name}</label>
                                </div>
                              </td>
                            )}
                            <td>{diagram.name}</td>
                            <td>{diagram.diagramType}</td>
                            <td>
                              <button className="btn btn-primary btn-sm me-2" onClick={() => handleLoadDiagram(diagram.diagramId)}>Load</button>
                              <button className="btn btn-outline-danger btn-sm" onClick={() => handleDeleteDiagram(diagram.diagramId)} disabled={loading}>Delete</button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkspaceManager;
