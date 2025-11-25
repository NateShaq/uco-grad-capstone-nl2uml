import React, { useEffect, useId, useMemo, useState } from 'react';
import { Form, Spinner, Button } from 'react-bootstrap';

function normalizeSelected(selected) {
  return selected || { ideation: '', uml: '', validation: '' };
}

function buildId(prefix, value) {
  return `${prefix}-${(value || '').replace(/[^a-z0-9]+/gi, '-')}`.toLowerCase();
}

const defaultOptions = { ideation: [], uml: [], validation: [] };

/**
 * Small helper component to surface Ollama model choices when using the pipeline agent.
 */
export default function OllamaModelSelector({
  apiBase = 'http://localhost:8080',
  selectedModels,
  onChange,
  disabled = false,
  namePrefix,
}) {
  const [options, setOptions] = useState(defaultOptions);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const generatedId = useId();
  const radioPrefix = namePrefix || generatedId;
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
    return parts.join(' • ');
  }, [normalizedSelected]);

  const tooltips = {
    ideation: 'Abstract thinking and brainstorming ideas.',
    uml: 'Generates UML syntax and shapes abstract thoughts into PlantUML.',
    validation: 'Fixes PlantUML/code to enforce strict syntax and avoid rendering errors.',
  };

  const renderGroup = (label, key) => (
    <div className="mb-2">
      <div className="small fw-semibold text-muted mb-1">
        {label}
        {tooltips[key] && (
          <span className="ms-1 text-secondary" title={tooltips[key]} aria-label={tooltips[key]} style={{ cursor: 'help' }}>
            ?
          </span>
        )}
      </div>
      {options[key].length === 0 ? (
        <div className="text-muted small">No models configured.</div>
      ) : (
        <div className="d-flex flex-wrap gap-3">
          {options[key].map((model) => (
            <Form.Check
              key={model}
              id={buildId(key, model)}
              type="radio"
              name={`${radioPrefix}-${key}`}
              label={model}
              value={model}
              checked={normalizedSelected[key] === model}
              disabled={disabled || loading}
              onChange={(e) => handleChange(key, e.target.value)}
            />
          ))}
        </div>
      )}
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
          aria-label="Configure Ollama models"
          title="Configure Ollama models"
          style={{ borderRadius: '50%', width: 36, height: 36, padding: 0 }}
        >
          ⚙️
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
            minWidth: 280,
            maxWidth: 360,
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
          {renderGroup('Ideation Model', 'ideation')}
          {renderGroup('UML Model', 'uml')}
          {renderGroup('Validation Model', 'validation')}
        </div>
      )}
    </div>
  );
}
