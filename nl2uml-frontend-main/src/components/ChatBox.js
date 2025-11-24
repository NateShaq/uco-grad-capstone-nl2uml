import React, { useState, useRef, useEffect } from 'react';
import { Button, Form } from 'react-bootstrap';
import { callApi } from './api'; // Adjust if using Amplify etc.

const API_BASE = 'http://localhost:8080';

function ChatBox({ projectId, diagramId, userEmail, sessionId, onDiagramUpdated }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('ollama-pipeline'); // default to pipeline
  const [collapsed, setCollapsed] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    setSending(true);

    const effectiveUser = userEmail || sessionId;

    try {
      const response = await callApi({
        endpoint: `${API_BASE}/refine`,
        method: 'POST',
        sessionId: effectiveUser,
        body: {
          projectId,
          diagramId,
          feedback: input,
          userEmail: effectiveUser,
          AI_Agent: selectedAgent // 🔥 Include selected AI Agent!
        }
      });
      setInput('');
      setMessages(prev => [
        ...prev,
        {
          text: response?.message || "Diagram updated.",
          sender: 'bot'
        }
      ]);
      if (response?.diagram && typeof onDiagramUpdated === 'function') {
        onDiagramUpdated(response.diagram);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { text: '⚠️ Error: Could not send message.', sender: 'system' }
      ]);
    }
    setSending(false);
  };

  return (
    <div className="chat-box d-flex flex-column border rounded shadow p-3" style={{ background: "#fafbfc", minHeight: collapsed ? 'auto' : 360 }}>
      <div className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Refinement Editor</h5>
        <Button variant="outline-secondary" size="sm" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? 'Expand' : 'Collapse'}
        </Button>
      </div>
      <hr />
      {!collapsed && (
        <>
          {/* Chat history */}
          <div style={{ flex: 1, overflowY: "auto", marginBottom: '1rem', maxHeight: 280 }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`mb-2 p-2 rounded ${msg.sender === 'bot'
                  ? 'bg-light text-dark'
                  : msg.sender === 'system'
                  ? 'bg-warning text-dark'
                  : 'bg-primary text-white'
                }`}
                style={{
                  alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                  wordBreak: 'break-word'
                }}
              >
                {msg.text}
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          {/* 🔥 AI Agent Selector */}
          <Form.Group className="mb-2">
            <Form.Label>Select AI Agent:</Form.Label>
            <Form.Select
              value={selectedAgent}
              onChange={e => setSelectedAgent(e.target.value)}
              disabled={sending}
            >
              <option value="ollama-pipeline">Ollama Pipeline (Deepseek ➜ Llama3-Code)</option>
              <option value="ollama">Ollama (Mistral 7B Instruct)</option>
              <option value="gronk" disabled>Gronk (X.AI Grok-3 Beta - disabled for local use)</option>
            </Form.Select>
          </Form.Group>

          {/* Input and Send */}
          <Form.Group className="d-flex">
            <Form.Control
              type="text"
              value={input}
              placeholder="Type your refinement or question…"
              onChange={e => setInput(e.target.value)}
              disabled={sending}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <Button
              variant="success"
              onClick={handleSend}
              className="ms-2"
              disabled={sending}
            >
              {sending ? 'Sending…' : 'Send'}
            </Button>
          </Form.Group>
        </>
      )}
    </div>
  );
}

export default ChatBox;
