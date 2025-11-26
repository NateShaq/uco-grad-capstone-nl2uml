import React, { useMemo, useRef, useState } from 'react';
import { Button, Form } from 'react-bootstrap';
import { callApi } from './api';
import './DiagramToCode.css';
import OllamaModelSelector from './OllamaModelSelector';
import { API_BASE } from '../config';

const languageKeywords = {
  python: ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'with', 'as', 'pass', 'yield', 'lambda', 'async', 'await'],
  java: ['class', 'interface', 'enum', 'public', 'private', 'protected', 'void', 'int', 'String', 'return', 'new', 'static', 'final', 'extends', 'implements', 'if', 'else', 'for', 'while', 'try', 'catch', 'package', 'import'],
  csharp: ['class', 'interface', 'enum', 'public', 'private', 'protected', 'void', 'int', 'string', 'return', 'new', 'static', 'readonly', 'sealed', 'async', 'await', 'using', 'namespace', 'if', 'else', 'for', 'while', 'try', 'catch'],
  cpp: ['class', 'struct', 'public', 'private', 'protected', 'void', 'int', 'return', 'new', 'auto', 'const', 'constexpr', 'virtual', 'override', 'namespace', 'template', 'typename', 'if', 'else', 'for', 'while', 'try', 'catch', 'include', 'using']
};

const escapeHtml = (value = '') =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

const highlightCode = (code = '', language) => {
  const keywords = languageKeywords[language] || [];
  let html = escapeHtml(code);

  html = html.replace(/(".*?"|'.*?')/g, '<span class="token string">$1</span>');
  html = html.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="token number">$1</span>');

  if (language === 'python') {
    html = html.replace(/(#.*)/g, '<span class="token comment">$1</span>');
  } else {
    html = html.replace(/(\/\/.*)/g, '<span class="token comment">$1</span>');
    html = html.replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="token comment">$1</span>');
  }

  if (keywords.length) {
    const keywordPattern = new RegExp(`\\b(${keywords.join('|')})\\b`, 'g');
    html = html.replace(keywordPattern, '<span class="token keyword">$1</span>');
  }

  return html;
};

function ConvertDiagramToCode({ projectId, diagramId, sessionId }) {
  const [codeText, setCodeText] = useState('');
  const [sending, setSending] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('ollama-pipeline');
  const [ollamaModels, setOllamaModels] = useState({ ideation: '', uml: '', validation: '', contextWindow: '' });
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [statusMessage, setStatusMessage] = useState('');
  const [collapsed, setCollapsed] = useState(false);
  const textareaRef = useRef(null);
  const preRef = useRef(null);

  const highlightedCode = useMemo(() => {
    if (!codeText) return '';
    return highlightCode(codeText, selectedLanguage);
  }, [codeText, selectedLanguage]);

  const handleConvert = async () => {
    setSending(true);
    setStatusMessage('Generating code from the current diagram...');

    const modelsPayload =
      selectedAgent.startsWith('ollama') && Object.values(ollamaModels || {}).some(Boolean)
        ? ollamaModels
        : undefined;

    try {
      const response = await callApi({
        endpoint: `${API_BASE}/code`,
        method: 'POST',
        sessionId,
        body: {
          projectId,
          diagramId,
          targetLanguage: selectedLanguage,
          agentType: selectedAgent,
          ollamaModels: modelsPayload,
        },
      });

      if (response && response.code) {
        setCodeText(response.code.trim());
        setStatusMessage('Editable code ready below. You can tweak it and copy as needed.');
      } else {
        setStatusMessage('⚠️ Conversion failed.');
      }
    } catch (error) {
      console.error('Conversion error:', error);
      setStatusMessage('⚠️ Error during conversion.');
    }

    setSending(false);
  };

  const syncScroll = () => {
    if (!textareaRef.current || !preRef.current) return;
    preRef.current.scrollTop = textareaRef.current.scrollTop;
    preRef.current.scrollLeft = textareaRef.current.scrollLeft;
  };

  const handleCopy = async () => {
    if (!codeText) return;
    try {
      await navigator.clipboard.writeText(codeText);
      setStatusMessage('Code copied to clipboard.');
    } catch (err) {
      console.error('Copy failed', err);
      setStatusMessage('⚠️ Unable to copy to clipboard in this browser.');
    }
  };

  return (
    <div className="convert-code-box d-flex flex-column border rounded shadow p-3 mt-4" style={{ background: "#f9fafb", minHeight: collapsed ? 'auto' : 300 }}>
      <div className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Convert Diagram to Code</h5>
        <Button variant="outline-secondary" size="sm" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? 'Expand' : 'Collapse'}
        </Button>
      </div>
      <hr />
      {!collapsed && (
        <>
          <Form.Group className="mb-2">
            <Form.Label>AI Agent</Form.Label>
            <Form.Select value={selectedAgent} onChange={e => setSelectedAgent(e.target.value)} disabled={sending}>
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

          <Form.Group className="mb-2">
            <Form.Label>Language</Form.Label>
            <Form.Select value={selectedLanguage} onChange={e => setSelectedLanguage(e.target.value)} disabled={sending}>
              <option value="python">Python</option>
              <option value="java">Java</option>
              <option value="csharp">C#</option>
              <option value="cpp">C++</option>
            </Form.Select>
          </Form.Group>

          <Button variant="success" onClick={handleConvert} disabled={sending}>
            {sending ? 'Converting...' : 'Convert'}
          </Button>

          <div className="code-editor-shell mt-3">
            <div className="code-editor-toolbar">
              <span className="code-editor-pill">Web IDE</span>
              <div className="code-editor-actions">
                <span className="code-editor-lang">{selectedLanguage.toUpperCase()}</span>
                <Button size="sm" variant="outline-light" onClick={handleCopy} disabled={!codeText}>
                  Copy
                </Button>
              </div>
            </div>
            <div className="code-editor-surface">
              <pre className="code-highlighting" aria-hidden="true" ref={preRef}>
                <code dangerouslySetInnerHTML={{ __html: highlightedCode }} />
              </pre>
              <textarea
                ref={textareaRef}
                value={codeText}
                onChange={(e) => setCodeText(e.target.value)}
                onScroll={syncScroll}
                spellCheck={false}
                placeholder=""
              />
            </div>
          </div>
          {statusMessage && <div className="small text-muted mt-2">{statusMessage}</div>}
        </>
      )}
    </div>
  );
}

export default ConvertDiagramToCode;
