import React from 'react';
import { Navbar as BsNavbar, Container, Button } from 'react-bootstrap';

function Navbar({ sessionId, onNewSession }) {
  const truncatedSession = sessionId ? `${sessionId.slice(0, 6)}...${sessionId.slice(-4)}` : '';

  return (
    <BsNavbar bg="dark" variant="dark" expand="lg">
      <Container>
        <BsNavbar.Brand href="#home">NL2UML</BsNavbar.Brand>
        <BsNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BsNavbar.Collapse id="basic-navbar-nav">
          <div className="ms-auto d-flex align-items-center gap-3">
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
  );
}

export default Navbar;
