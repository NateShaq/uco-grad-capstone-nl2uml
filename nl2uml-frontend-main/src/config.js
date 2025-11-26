// Centralized frontend configuration for API and WebSocket endpoints.
// Values are injected at build time via CRA's REACT_APP_* variables, with sensible localhost defaults.
export const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8080";
export const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:8080/ws";
export const WS_ENABLED = (process.env.REACT_APP_WS_ENABLED || "").toLowerCase() === "true";
