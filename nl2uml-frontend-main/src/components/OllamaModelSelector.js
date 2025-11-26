import React, { useEffect, useMemo, useState } from 'react';
import { Form, Spinner, Button } from 'react-bootstrap';
import { API_BASE } from '../config';

const contextOptions = [2048, 4096, 8192, 16384, 32768];

function normalizeSelected(selected) {
  return { ideation: '', uml: '', validation: '', contextWindow: '', ...(selected || {}) };
}

const defaultOptions = { ideation: [], uml: [], validation: [], defaultNumCtx: null };

/**
 * Small helper component to surface Ollama model choices when using the pipeline agent.
 */
export default function OllamaModelSelector({
  apiBase = API_BASE,
  selectedModels,
  onChange,
  disabled = false,
}) {
  const [options, setOptions] = useState(defaultOptions);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [collapsed, setCollapsed] = useState(true);

  const normalizedSelected = useMemo(() => normalizeSelected(selectedModels), [selectedModels]);

  useEffect(() => {
    let cancelled = false;
    const fetchModels = async () => {
      setLoading(true);
      setError('');
      try {
        const resp = await fetch(`${apiBase}/ollama/models`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        if (cancelled) return;
        setOptions({
          ideation: data.ideationModels || [],
          uml: data.umlModels || [],
          validation: data.validationModels || [],
          defaultNumCtx: data.defaultNumCtx || null,
        });
      } catch (err) {
        if (cancelled) return;
        setError('Could not load Ollama model list. Check docker-compose values.');
        setOptions(defaultOptions);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchModels();
    return () => {
      cancelled = true;
    };
  }, [apiBase]);

  useEffect(() => {
    if (loading) return;
    const next = { ...normalizedSelected };
    let changed = false;
    if (!next.ideation && options.ideation.length) {
      next.ideation = options.ideation[0];
      changed = true;
    }
    if (!next.uml && options.uml.length) {
      next.uml = options.uml[0];
      changed = true;
    }
    if (!next.validation && options.validation.length) {
      next.validation = options.validation[0];
      changed = true;
    }
    if (!next.contextWindow && options.defaultNumCtx) {
      next.contextWindow = options.defaultNumCtx;
      changed = true;
    }
    if (changed && typeof onChange === 'function') {
      onChange(next);
    }
  }, [loading, normalizedSelected, onChange, options]);

  const handleChange = (key, value) => {
    if (typeof onChange === 'function') {
      onChange({ ...normalizedSelected, [key]: value });
    }
  };

  const summary = useMemo(() => {
    const parts = [];
    if (normalizedSelected.ideation) parts.push(`I: ${normalizedSelected.ideation}`);
    if (normalizedSelected.uml) parts.push(`U: ${normalizedSelected.uml}`);
    if (normalizedSelected.validation) parts.push(`V: ${normalizedSelected.validation}`);
    if (normalizedSelected.contextWindow) parts.push(`CTX: ${normalizedSelected.contextWindow}`);
    return parts.join(' • ');
  }, [normalizedSelected]);

  const tooltips = {
    ideation: 'Abstract thinking and brainstorming ideas.',
    uml: 'Generates UML syntax and shapes abstract thoughts into PlantUML.',
    validation: 'Fixes PlantUML/code to enforce strict syntax and avoid rendering errors.',
  };

  const renderGroup = (label, key) => (
    <div className="col-12 col-md-4 d-flex">
      <div
        className="border border-primary p-3 w-100 d-flex flex-column"
        style={{ borderRadius: 12 }}
      >
        <div className="small fw-semibold text-muted text-center mb-2">
          {label}
          {tooltips[key] && (
            <span
              className="ms-1 text-secondary"
              title={tooltips[key]}
              aria-label={tooltips[key]}
              style={{ cursor: 'help' }}
            >
              ?
            </span>
          )}
        </div>
        {options[key].length === 0 ? (
          <div className="text-muted small text-center">No models configured.</div>
        ) : (
          <div className="d-flex flex-column gap-2">
            {options[key].map((model) => {
              const isActive = normalizedSelected[key] === model;
              return (
                <Button
                  key={model}
                  variant={isActive ? 'primary' : 'outline-secondary'}
                  size="sm"
                  className="w-100 text-start"
                  disabled={disabled || loading}
                  onClick={() => handleChange(key, model)}
                >
                  {model}
                </Button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="p-3 border rounded bg-light position-relative">
      <div className="d-flex align-items-center justify-content-between mb-2">
        <div className="d-flex align-items-center">
          <div className="fw-semibold me-2 mb-0">Ollama Pipeline Models</div>
          {loading && <Spinner animation="border" size="sm" role="status" />}
        </div>
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          disabled={loading}
          aria-label="Edit Ollama models"
          title="Edit Ollama models"
        >
          [ Edit ]
        </Button>
      </div>
      {error && <div className="text-danger small mb-2">{error}</div>}
      <div className="text-muted small">
        Using defaults{summary ? `: ${summary}` : '.'}
      </div>

      {!collapsed && (
        <div
          className="p-3 border rounded bg-white shadow"
          style={{
            position: 'absolute',
            top: '10%',
            right: '5%',
            zIndex: 1000,
            minWidth: 720,
            maxWidth: '90vw',
          }}
        >
          <div className="d-flex justify-content-between align-items-center mb-2">
            <div className="fw-semibold">Ollama Pipeline Models</div>
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={() => setCollapsed(true)}
              aria-label="Close model selection"
            >
              ✕
            </Button>
          </div>
          <div className="d-flex flex-column align-items-center mb-4">
            <div className="small fw-semibold text-muted mb-1">
              Context Window
              <span
                className="ms-1 text-secondary"
                title="Sets Ollama num_ctx; higher allows longer prompts/responses but uses more VRAM."
                aria-label="Sets Ollama num_ctx; higher allows longer prompts/responses but uses more VRAM."
                style={{ cursor: 'help' }}
              >
                ?
              </span>
            </div>
            <Form.Select
              size="sm"
              className="w-auto"
              style={{ minWidth: 180 }}
              value={normalizedSelected.contextWindow || ''}
              onChange={(e) => handleChange('contextWindow', e.target.value ? Number(e.target.value) : '')}
              disabled={disabled || loading}
            >
              <option value="">
                Default {options.defaultNumCtx ? `(${options.defaultNumCtx})` : ''}
              </option>
              {contextOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </Form.Select>
          </div>
          <div className="d-flex gap-3 flex-wrap justify-content-between">
            <div className="row g-3 w-100">
              {renderGroup('Ideation Model', 'ideation')}
              {renderGroup('UML Model', 'uml')}
              {renderGroup('Validation Model', 'validation')}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
