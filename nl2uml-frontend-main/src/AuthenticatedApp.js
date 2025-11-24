import React, { useState } from 'react';
import { Routes, Route, Navigate } from "react-router-dom";

import Navbar from './components/Navbar';
import MainLayout from './components/MainLayout';
import WorkspaceManager from "./components/WorkspaceManager";
import { WebSocketProvider } from './components/WebSocketProvider';

export default function AuthenticatedApp({ sessionId, onNewSession }) {
  const [diagramInput, setDiagramInput] = useState(null);

  return (
    <WebSocketProvider sessionId={sessionId}>
      <div className="App">
        <Navbar sessionId={sessionId} onNewSession={onNewSession} />
        <Routes>
          <Route path="/" element={<Navigate to="/workspace" />} />
          <Route path="/workspace" element={<WorkspaceManager sessionId={sessionId} onLoadDiagram={setDiagramInput} />} />
          <Route
            path="/diagram"
            element={
              diagramInput
                ? <MainLayout sessionId={sessionId} initialPrompt={diagramInput} setPrompt={setDiagramInput} />
                : <Navigate to="/workspace" replace />
            }
          />
        </Routes>
      </div>
    </WebSocketProvider>
  );
}
