import React, { useState, useEffect, useRef } from 'react';
import { encodePlantUML } from '../utils/plantumlEncoder';
import './Canvas.css';

function Canvas({ umlText, justUpdated }) {
  const [zoom, setZoom] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const containerRef = useRef(null);

  const hasDiagram = !!(umlText && umlText.trim().toLowerCase().includes('@startuml'));
  const encoded = hasDiagram ? encodePlantUML(umlText) : '';
  const imageUrl = hasDiagram ? `https://www.plantuml.com/plantuml/svg/${encoded}` : null;

  const zoomIn = () => setZoom(prev => Math.min(prev + 0.1, 3));
  const zoomOut = () => setZoom(prev => Math.max(prev - 0.1, 0.2));
  const resetZoom = () => setZoom(1);

  const handleWheel = (e) => {
    if (e.ctrlKey) {
      e.preventDefault();
      const delta = e.deltaY;
      setZoom(prev => delta > 0 ? Math.max(prev - 0.1, 0.2) : Math.min(prev + 0.1, 3));
    }
  };

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener("wheel", handleWheel, { passive: false });
      return () => container.removeEventListener("wheel", handleWheel);
    }
  }, []);

  if (!hasDiagram) {
    return (
      <div className="diagram-preview d-flex flex-column align-items-center justify-content-center text-muted" style={{ minHeight: 220 }}>
        <div className="mb-2 fw-semibold">No diagram available to render.</div>
        <div className="small text-center">
          Ensure your diagram includes <code>@startuml</code> and <code>@enduml</code> markers, then regenerate.
        </div>
      </div>
    );
  }

  return (
    <>
      <div
        ref={containerRef}
        className={`diagram-preview position-relative ${justUpdated ? 'updated-glow' : ''}`}
        onClick={() => setShowModal(true)}
        style={{ cursor: 'pointer' }}
      >
        {imageUrl && (
          <img
            src={imageUrl}
            alt="UML Diagram"
            className="diagram-img"
            style={{ transform: `scale(${zoom})`, transformOrigin: 'top left' }}
          />
        )}
        <div className="fullscreen-icon position-absolute top-0 end-0 m-2 text-white bg-dark rounded px-2 py-1" style={{ opacity: 0.8, fontSize: '0.75rem' }}>
          🔍 Fullscreen
        </div>
      </div>

      <div className="zoom-controls mb-2 d-flex align-items-center gap-2">
        <button className="btn btn-outline-secondary btn-sm" onClick={zoomOut}>−</button>
        <button className="btn btn-outline-primary btn-sm" onClick={resetZoom}>Reset</button>
        <button className="btn btn-outline-secondary btn-sm" onClick={zoomIn}>+</button>
        <span className="ms-3 small text-muted">Zoom: {Math.round(zoom * 100)}%</span>
      </div>

      {showModal && (
        <div className="modal d-block" tabIndex="-1" onClick={() => setShowModal(false)} style={{ backgroundColor: "rgba(0,0,0,0.9)" }}>
          <div className="modal-dialog modal-fullscreen">
            <div className="modal-content bg-dark">
              <div className="modal-header border-0">
                <h5 className="text-white">Full Screen Diagram</h5>
                <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)} />
              </div>
              <div className="modal-body d-flex justify-content-center align-items-center">
                <img src={imageUrl} alt="Expanded Diagram" style={{ maxWidth: '100%', maxHeight: '90vh' }} />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Canvas;
