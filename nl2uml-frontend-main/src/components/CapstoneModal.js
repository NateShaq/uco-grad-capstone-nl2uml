import React from 'react';
import { Modal, Button, Row, Col, Badge } from 'react-bootstrap';
import projectMeta from '../projectMeta';

function CapstoneModal({ show, onHide }) {
  const { projectName, university, department, professor, student } = projectMeta;

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton className="border-0 pb-0">
        <div>
          <Badge bg="primary" className="mb-2">Graduate Capstone</Badge>
          <Modal.Title className="fw-bold">{university.name}</Modal.Title>
          <div className="text-muted small">Master&apos;s capstone · {department.name}</div>
        </div>
      </Modal.Header>
      <Modal.Body className="pt-3 pb-4">
        <div className="bg-light p-3 rounded-3 mb-3">
          <div className="fw-semibold mb-1">{university.location}</div>
          <p className="mb-0 text-secondary small">{university.description}</p>
        </div>

        <Row className="gy-3">
          <Col md={7}>
            <div className="p-3 border rounded-3 h-100">
              <div className="text-uppercase text-primary fw-semibold small mb-1">Student</div>
              <div className="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <div className="fw-bold">{student.name}</div>
                  <div className="text-secondary small">{projectName} · Graduate Capstone</div>
                </div>
                <Button
                  variant="outline-primary"
                  size="sm"
                  href={student.link}
                  target="_blank"
                  rel="noreferrer"
                >
                  View Profile
                </Button>
              </div>

              <div className="text-uppercase text-primary fw-semibold small mb-1">Sponsoring Professor</div>
              <div className="fw-bold">{professor.name}</div>
              <div className="text-secondary small mb-2">{professor.title}</div>
              <div className="text-secondary small mb-2">
                Research interests:
              </div>
              <ul className="text-secondary small ps-3 mb-3">
                {professor.interests.map((interest) => (
                  <li key={interest}>{interest}</li>
                ))}
              </ul>
              <Button
                variant="secondary"
                size="sm"
                href={professor.link}
                target="_blank"
                rel="noreferrer"
              >
                Faculty Profile
              </Button>
            </div>
          </Col>
          <Col md={5}>
            <div className="p-3 bg-dark text-light rounded-3 h-100">
              <div className="text-uppercase text-warning fw-semibold small mb-1">Department</div>
              <div className="fw-bold mb-2">{department.name}</div>
              <p className="small mb-0 text-light opacity-75">{department.description}</p>
            </div>
          </Col>
        </Row>

        <div className="d-flex justify-content-between align-items-center mt-4">
          <div className="text-secondary small">
            {projectName} is a research-driven capstone project guided by {professor.name} and led by {student.name}.
          </div>
          <Button variant="dark" size="sm" onClick={onHide}>Close</Button>
        </div>
      </Modal.Body>
    </Modal>
  );
}

export default CapstoneModal;
