import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { WS_ENABLED, WS_URL as WS_URL_BASE } from "../config";

// Create a context for WebSocket messages
const WebSocketContext = createContext();

export function WebSocketProvider({ sessionId, children }) {
  const [wsStatus, setWsStatus] = useState("disconnected");
  const wsRef = useRef(null);
  const listeners = useRef([]); // [{action, handler}]

  // Respect build-time flag to disable WebSockets (default off for local).
  const WS_URL = WS_ENABLED && sessionId
    ? `${WS_URL_BASE}?token=${encodeURIComponent(sessionId)}`
    : null;
  
  useEffect(() => {
    if (!WS_URL) return;

    let ws;
    let heartbeat;
    let reconnectTimeout;

    function connect() {
      console.log("[WebSocket] Connecting to:", WS_URL);
      ws = new window.WebSocket(WS_URL);

      wsRef.current = ws;
      setWsStatus("connecting");

      ws.onopen = () => {
        setWsStatus("connected");
        console.log("[WebSocket] Connected!");
        heartbeat = setInterval(() => {
          if (ws.readyState === 1) {
            ws.send(JSON.stringify({ action: "ping" }));
            console.log("[WebSocket] Sent ping");
          }
        }, 40000);
      };

      ws.onmessage = (event) => {
        console.log("[WebSocket] Message event.data:", event.data);
        try {
          const msg = JSON.parse(event.data);
          if (!msg.action) {
            console.warn("[WebSocket] Received message without action:", msg);
            return;
          }
          listeners.current.forEach(({ action, handler }) => {
            if (msg.action === action) {
              try {
                handler(msg);
              } catch (e) {
                console.error("[WebSocket] Handler error for action:", action, e);
              }
            }
          });
        } catch (err) {
          console.error("[WebSocket] Failed to parse message:", event.data, err);
        }
      };

      ws.onclose = (event) => {
        setWsStatus("disconnected");
        console.warn("[WebSocket] Connection closed. Code:", event.code, "Reason:", event.reason);
        clearInterval(heartbeat);
        reconnectTimeout = setTimeout(connect, 3000); // try to reconnect
      };

      ws.onerror = (err) => {
        console.error("[WebSocket] Error:", err);
        ws.close();
      };
    }

    connect();

    return () => {
      clearInterval(heartbeat);
      clearTimeout(reconnectTimeout);
      wsRef.current?.close();
      setWsStatus("disconnected");
    };
  }, [WS_URL, sessionId]);

  // Allow components to register handlers for actions
  function on(action, handler) {
    listeners.current.push({ action, handler });
    return () => {
      listeners.current = listeners.current.filter(l => l.handler !== handler);
    };
  }

  // Optionally: function to send a message
  function send(message) {
    if (wsRef.current && wsRef.current.readyState === 1) {
      wsRef.current.send(JSON.stringify(message));
      console.log("[WebSocket] Sent message:", message);
    } else {
      console.warn("[WebSocket] Tried to send message but socket not ready:", message);
    }
  }

  return (
    <WebSocketContext.Provider value={{ wsStatus, on, send }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  // Provide no-op defaults when WS is disabled.
  const ctx = useContext(WebSocketContext);
  return ctx || { wsStatus: "disabled", on: () => () => {}, send: () => {} };
}
