import React, { useState, useRef, useEffect } from 'react';
import { Button, Form } from 'react-bootstrap';
import { callApi } from './api'; // Adjust if using Amplify etc.
import OllamaModelSelector from './OllamaModelSelector';

const API_BASE = 'http://localhost:8080';

function ChatBox({ projectId, diagramId, userEmail, sessionId, onDiagramUpdated }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('ollama-pipeline'); // default to pipeline
  const [ollamaModels, setOllamaModels] = useState({ ideation: '', uml: '', validation: '' });
  const [collapsed, setCollapsed] = useState(false);
  const bottomRef = useRef(null);

  const formatHeading = (iso) => {
    if (!iso) return '';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return '';
    const month = `${d.getMonth() + 1}`.padStart(2, '0');
    const day = `${d.getDate()}`.padStart(2, '0');
    const year = `${d.getFullYear()}`.slice(-2);
    const hours = `${d.getHours()}`.padStart(2, '0');
    const minutes = `${d.getMinutes()}`.padStart(2, '0');
    return `${month}/${day}/${year} ${hours}:${minutes}`;
  };

  const renderMessagesWithHeadings = () => {
    const rows = [];
    let lastDate = '';
    messages.forEach((msg, idx) => {
      const currentDate = msg?.ts ? new Date(msg.ts).toDateString() : '';
      if (currentDate !== lastDate && msg?.ts) {
        lastDate = currentDate;
        rows.push(
          <div key={`heading-${idx}`} className="text-center text-muted small my-2">
            {formatHeading(msg.ts)}
          </div>
        );
      }
      rows.push(
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
          <div>{msg.text}</div>
          {msg.ts && (
            <div className="text-muted small mt-1" style={{ fontSize: '0.75rem', opacity: 0.8 }}>
              {formatHeading(msg.ts)}
            </div>
          )}
        </div>
      );
    });
    return rows;
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load persisted history per diagram
  useEffect(() => {
    const key = diagramId ? `chat-history-${diagramId}` : null;
    if (!key) return;
    try {
      const saved = localStorage.getItem(key);
      if (saved) {
        setMessages(JSON.parse(saved));
      } else {
        setMessages([]);
      }
    } catch (err) {
      console.warn('Failed to load chat history', err);
      setMessages([]);
    }
  }, [diagramId]);

  // Persist history per diagram
  useEffect(() => {
    const key = diagramId ? `chat-history-${diagramId}` : null;
    if (!key) return;
    try {
      localStorage.setItem(key, JSON.stringify(messages));
    } catch (err) {
      console.warn('Failed to persist chat history', err);
    }
  }, [messages, diagramId]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const timestamp = new Date().toISOString();
    const userMsg = { text: input, sender: 'user', ts: timestamp };
    setMessages(prev => [...prev, userMsg]);
    setSending(true);

    const effectiveUser = userEmail || sessionId;
    const modelsPayload =
      selectedAgent.startsWith('ollama') && Object.values(ollamaModels || {}).some(Boolean)
        ? ollamaModels
        : undefined;

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
          AI_Agent: selectedAgent, // 🔥 Include selected AI Agent!
          ollamaModels: modelsPayload,
        }
      });
      setInput('');
      const botMsg = {
        text: response?.message || "Diagram updated.",
        sender: 'bot',
        ts: new Date().toISOString()
      };
      setMessages(prev => [...prev, botMsg]);
      if (response?.diagram && typeof onDiagramUpdated === 'function') {
        onDiagramUpdated(response.diagram);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { text: '⚠️ Error: Could not send message.', sender: 'system', ts: new Date().toISOString() }
      ]);
    }
    setSending(false);
  };

  return (
    <div className="chat-box d-flex flex-column border rounded shadow p-3" style={{ background: "#fafbfc", height: collapsed ? 'auto' : '100%' }}>
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
          <div style={{ flex: 1, overflowY: "auto", marginBottom: '1rem' }}>
            {renderMessagesWithHeadings()}
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
          {selectedAgent.startsWith('ollama') && (
            <div className="mb-3">
              <OllamaModelSelector
                apiBase={API_BASE}
                selectedModels={ollamaModels}
                onChange={setOllamaModels}
                disabled={sending}
              />
            </div>
          )}

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
