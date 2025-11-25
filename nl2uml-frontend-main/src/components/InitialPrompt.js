import React, { useState } from 'react';
import { Button, Form } from 'react-bootstrap';
import { callApi } from './api';

function InitialPrompt({ onSubmit, sessionId }) {
  const [input, setInput] = useState('');
  const [diagramType, setDiagramType] = useState('Class Diagram');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!input.trim()) return;

    setLoading(true);
    const activeSession = sessionId || window.localStorage.getItem('nl2uml-session-id') || window.localStorage.getItem('userEmail');
    try {
      const data = await callApi({
        endpoint: 'http://localhost:8080/generate',
        method: 'POST',
        sessionId: activeSession,
        body: {
          prompt: input,
          diagramType: diagramType // send diagramType if your backend supports it
        },
      });
      onSubmit({ ...data, input, diagramType });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <h2>Start Your UML Diagram</h2>
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Select Diagram Type</Form.Label>
          <Form.Select value={diagramType} onChange={(e) => setDiagramType(e.target.value)}>
            <option>Use Case Diagram</option>
            <option>Activity Diagram</option>
            <option>Component Diagram</option>
            <option>Class Diagram</option>
            <option>Sequence Diagram</option>
            <option>State Diagram</option>
            <option>Enhanced Entity Relationship Diagram</option>
          </Form.Select>
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Describe your system or feature:</Form.Label>
          <Form.Control
            as="textarea"
            rows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g., A login system where users can register, login, and reset passwords"
          />
        </Form.Group>
        <Button variant="primary" type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate Diagram"}
        </Button>
        {error && <div className="mt-3 text-danger">{error}</div>}
      </Form>
    </div>
  );
}

export default InitialPrompt;
