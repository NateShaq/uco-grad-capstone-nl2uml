import React, { useState } from 'react';
import { Navbar as BsNavbar, Container, Button } from 'react-bootstrap';
import CapstoneModal from './CapstoneModal';

function Navbar({ sessionId, onNewSession }) {
  const truncatedSession = sessionId ? `${sessionId.slice(0, 6)}...${sessionId.slice(-4)}` : '';
  const [showCapstone, setShowCapstone] = useState(false);

  return (
    <>
      <BsNavbar bg="dark" variant="dark" expand="lg">
        <Container>
          <BsNavbar.Brand href="#home" className="d-flex align-items-center gap-2">
            <img
              src={`${process.env.PUBLIC_URL}/UCO_Logo.svg`}
              alt="University of Central Oklahoma logo"
              style={{ height: 28, width: 'auto' }}
            />
            <span className="fw-semibold text-uppercase small">NL2UML</span>
          </BsNavbar.Brand>
          <BsNavbar.Toggle aria-controls="basic-navbar-nav" />
          <BsNavbar.Collapse id="basic-navbar-nav">
            <div className="ms-auto d-flex align-items-center gap-3">
              <Button variant="outline-info" size="sm" onClick={() => setShowCapstone(true)}>
                About capstone
              </Button>
              {sessionId && (
                <span className="text-light small">Session: {truncatedSession}</span>
              )}
              <Button variant="outline-light" size="sm" onClick={onNewSession}>
                New Session
              </Button>
            </div>
          </BsNavbar.Collapse>
        </Container>
      </BsNavbar>
      <CapstoneModal show={showCapstone} onHide={() => setShowCapstone(false)} />
    </>
  );
}

export default Navbar;
