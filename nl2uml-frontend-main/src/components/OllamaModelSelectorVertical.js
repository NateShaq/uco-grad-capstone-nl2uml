import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Form, Spinner, Button } from 'react-bootstrap';
import { API_BASE } from '../config';
import ModelsPopoverPortal from './ModelsPopoverPortal';

const contextOptions = [2048, 4096, 8192, 16384, 32768];

function normalizeSelected(selected) {
  return { ideation: '', uml: '', validation: '', contextWindow: '', ...(selected || {}) };
}

const defaultOptions = { ideation: [], uml: [], validation: [], defaultNumCtx: null };

/**
 * Vertical layout for Ollama model selection (used in Refinement Editor).
 */
export default function OllamaModelSelectorVertical({
  apiBase = API_BASE,
  selectedModels,
  onChange,
  disabled = false,
}) {
  const [options, setOptions] = useState(defaultOptions);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [collapsed, setCollapsed] = useState(true);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef(null);

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

  const updatePosition = useCallback(() => {
    if (!triggerRef.current) return;
    const rect = triggerRef.current.getBoundingClientRect();
    const popoverWidth = 480;
    const margin = 12;

    let left = rect.left;
    if (left + popoverWidth + margin > window.innerWidth) {
      left = window.innerWidth - popoverWidth - margin;
    }
    if (left < margin) left = margin;

    let top = rect.bottom + 8;
    if (top + 400 > window.innerHeight) {
      top = rect.top - 400 - 8;
    }

    setPosition({ top, left });
  }, []);

  useEffect(() => {
    if (collapsed) return undefined;
    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition, true);
    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition, true);
    };
  }, [collapsed, updatePosition]);

  const renderGroup = (label, key) => (
    <div className="mb-3">
      <div className="small fw-semibold text-muted d-flex align-items-center mb-2">
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
        <div className="text-muted small">No models configured.</div>
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
  );

  return (
    <div className="p-3 border rounded bg-light position-relative" style={{ zIndex: 1 }}>
      <div className="d-flex align-items-center justify-content-between mb-2">
        <div className="d-flex align-items-center">
          <div className="fw-semibold me-2 mb-0">Ollama Pipeline Models</div>
          {loading && <Spinner animation="border" size="sm" role="status" />}
        </div>
        <Button
          variant="outline-secondary"
          size="sm"
          ref={triggerRef}
          onClick={() => setCollapsed((prev) => !prev)}
          disabled={loading}
          aria-label="Edit Ollama models"
          title="Edit Ollama models"
        >
          [ Edit ]
        </Button>
      </div>
      {error && <div className="text-danger small mb-2">{error}</div>}
      <div className="text-muted small">Using defaults{summary ? `: ${summary}` : '.'}</div>

      {!collapsed && (
        <ModelsPopoverPortal>
          <div
            role="presentation"
            onClick={() => setCollapsed(true)}
            style={{
              position: 'fixed',
              inset: 0,
              backgroundColor: 'transparent',
              zIndex: 999998,
            }}
          />
          <div
            className="ollama-models-popover"
            style={{ top: position.top, left: position.left, width: 480, maxWidth: '95vw' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="d-flex justify-content-between align-items-center mb-3">
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
            <div className="mb-3">
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
                className="w-100"
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
            {renderGroup('Ideation Model', 'ideation')}
            {renderGroup('UML Model', 'uml')}
            {renderGroup('Validation Model', 'validation')}
          </div>
        </ModelsPopoverPortal>
      )}
    </div>
  );
}
