import React from 'react';
import { Form } from 'react-bootstrap';

function DiagramSelector() {
  return (
    <Form.Group className="mb-3">
      <Form.Label>Select Diagram Type</Form.Label>
      <Form.Select>
      <option>Use Case Diagram</option>
      <option>Activity Diagram</option>
      <option>Component Diagram</option>
      <option>Class Diagram</option>
      <option>Sequence Diagram</option>
      <option>State Diagram</option>
      <option>Enhanced Entity Relationship Diagram</option>
      </Form.Select>
    </Form.Group>
  );
}

export default DiagramSelector;
