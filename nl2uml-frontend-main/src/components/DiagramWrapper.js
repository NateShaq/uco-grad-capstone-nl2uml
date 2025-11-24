import React, { useState, useEffect, useCallback } from "react";
import Canvas from './Canvas';
import { useWebSocket } from "./WebSocketProvider";
import { callApi } from './api';

const API_BASE = 'http://localhost:8080';

function DiagramWrapper({ projectId, diagramId, refreshKey = 0, sessionId }) {
  const [umlText, setUmlText] = useState('');
  const [explanation, setExplanation] = useState('');
  const [justUpdated, setJustUpdated] = useState(false);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const { on } = useWebSocket();

  // Fetch the diagram initially or when IDs change
  const fetchDiagram = useCallback(async () => {
    if (!projectId || !diagramId) return;
    try {
      const result = await callApi({
        endpoint: `${API_BASE}/diagrams/${diagramId}`,
        method: 'GET',
        sessionId,
      });
      setUmlText(result.plantuml || '');
      setExplanation(result.explanation || '');
    } catch (err) {
      setUmlText('');
      setExplanation('Error loading diagram.');
    }
  }, [projectId, diagramId, sessionId]);

  useEffect(() => {
    fetchDiagram();
  }, [fetchDiagram, refreshKey]);

  // Listen for diagram.updated messages
  useEffect(() => {
    const unsubscribe = on("diagram.updated", (msg) => {
      if (
        msg.payload?.diagramId === diagramId &&
        msg.payload?.projectId === projectId
      ) {
        const uml = msg.payload.plantUml || msg.payload.plantuml || '';
        setUmlText(uml);
        setExplanation(msg.payload.explanation || '');
        setJustUpdated(true);
        setTimeout(() => setJustUpdated(false), 3000);
      }
    });
    return unsubscribe;
  }, [on, diagramId, projectId]);

  const handleUndo = async () => {
    try {
      const data = await callApi({
        endpoint: `${API_BASE}/undo`,
        method: 'POST',
        sessionId,
        body: {
          diagramId,
          projectId,
        }
      });
      if (data.plantuml) setUmlText(data.plantuml);
    } catch (e) {
      alert('Undo failed: ' + e.message);
    }
  };
  
  const handleRedo = async () => {
    try {
      const data = await callApi({
        endpoint: `${API_BASE}/redo`,
        method: 'POST',
        sessionId,
        body: {
          diagramId,
          projectId,
        }
      });
      if (data.plantuml) setUmlText(data.plantuml);
    } catch (e) {
      alert('Redo failed: ' + e.message);
    }
  };

  const handleSave = async () => {
    try {
      await callApi({
        endpoint: `${API_BASE}/save-diagram`,
        method: 'POST',
        sessionId,
        body: {
          diagramId,
          projectId,
          plantuml: umlText,
        }
      });
      alert('Diagram saved!');
    } catch (e) {
      alert('Save failed: ' + e.message);
    }
  };

  const handleExplain = async () => {
    setLoadingExplanation(true);
    try {
      const result = await callApi({
        endpoint: `${API_BASE}/explain?diagramId=${diagramId}`,
        method: 'GET',
        sessionId,
      });
      setExplanation(result.explanation || result); // in case backend returns raw text
    } catch (e) {
      alert('Explain failed: ' + e.message);
      setExplanation('Failed to get explanation.');
    } finally {
      setLoadingExplanation(false);
    }
  };

  return (
    <div>
      <Canvas
        umlText={umlText}
        justUpdated={justUpdated}
        diagramId={diagramId}
        projectId={projectId}
      />

      <div className="mb-3 d-flex flex-wrap justify-content-center gap-2">
        <button className="btn btn-outline-secondary btn-sm" onClick={handleUndo}>
          Undo
        </button>
        <button className="btn btn-outline-secondary btn-sm" onClick={handleRedo}>
          Redo
        </button>
        <button className="btn btn-primary btn-sm" onClick={handleSave}>
          Save
        </button>
        <button className="btn btn-info btn-sm text-white" onClick={handleExplain}>
          Get Diagram Explanation
        </button>
      </div>
      <div style={{whiteSpace: "pre-wrap", padding: 12, background: "#f8f8f8", borderRadius: 6, margin: 8}}>
        <strong>Explanation:</strong>
        <br />
        {loadingExplanation ? (
          <span style={{ fontStyle: 'italic', color: '#888' }}>Loading explanation...</span>
        ) : (
          explanation
        )}
      </div>
    </div>
  );
}

export default DiagramWrapper;
