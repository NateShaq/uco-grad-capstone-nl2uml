import React, { useEffect, useState } from "react";
import Canvas from './Canvas';
import ChatBox from './ChatBox';
import './MainLayout.css';
import { Button } from 'react-bootstrap';
import jsPDF from 'jspdf';
import { useNavigate } from 'react-router-dom';
import DiagramWrapper from './DiagramWrapper';

function MainLayout({ initialPrompt, setPrompt, sessionId }) {
  const navigate = useNavigate();
  const [diagramRefreshKey, setDiagramRefreshKey] = useState(0);

  useEffect(() => {
    if (!initialPrompt) {
      navigate('/workspace');
    }
  }, [initialPrompt, navigate]);

  const handleExportAsPDF = () => {
    const doc = new jsPDF();
    const lines = doc.splitTextToSize(initialPrompt.plantuml, 180);
    doc.text(lines, 10, 10);
    doc.save(`${initialPrompt.diagramType.replace(' ', '_')}.pdf`);
  };

  return (
    <div className="main-layout">
      <div className="canvas-pane">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <button className="btn btn-secondary mb-3" onClick={() => navigate('/workspace', { state: { selectedProjectId: initialPrompt.projectId } })}>
            ← Back to Workspace
          </button>
          <Button variant="outline-secondary" onClick={handleExportAsPDF}>
            Export .puml
          </Button>
        </div>
        <DiagramWrapper
          projectId={initialPrompt?.projectId}
          diagramId={initialPrompt?.diagramId}
          refreshKey={diagramRefreshKey}
          sessionId={sessionId}
          onRefresh={() => setDiagramRefreshKey((prev) => prev + 1)}
        />
      </div>
      <div className="chat-pane">
        <ChatBox
          projectId={initialPrompt?.projectId}
          diagramId={initialPrompt?.diagramId}
          sessionId={sessionId}
          onDiagramUpdated={() => setDiagramRefreshKey((prev) => prev + 1)}
        />
      </div>
    </div>
  );
}

export default MainLayout;
