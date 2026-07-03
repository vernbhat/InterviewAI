import { randomUUID } from "node:crypto";
import { WebSocketServer } from "ws";

const port = Number(process.env.PORT || 8787);
const host = process.env.HOST || "127.0.0.1";
const aiBaseUrl = process.env.FASTAPI_URL || "http://localhost:8000";

const rooms = new Map();
const server = new WebSocketServer({ host, port });

function roomFor(sessionId) {
  if (!rooms.has(sessionId)) {
    rooms.set(sessionId, new Set());
  }

  return rooms.get(sessionId);
}

function send(socket, message) {
  if (socket.readyState === socket.OPEN) {
    socket.send(JSON.stringify(message));
  }
}

function broadcast(sessionId, message, except) {
  const room = roomFor(sessionId);
  for (const peer of room) {
    if (peer !== except) {
      send(peer, message);
    }
  }
}

async function requestHint(payload) {
  const response = await fetch(`${aiBaseUrl}/hint`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`AI hint request failed: ${response.status}`);
  }

  return response.json();
}

server.on("connection", (socket) => {
  const clientId = randomUUID();
  let currentSessionId = "demo-session";

  roomFor(currentSessionId).add(socket);
  send(socket, { type: "connected", clientId, sessionId: currentSessionId });

  socket.on("message", async (raw) => {
    let message;
    try {
      message = JSON.parse(raw.toString());
    } catch {
      send(socket, { type: "error", error: "Invalid JSON message" });
      return;
    }

    if (message.type === "join") {
      roomFor(currentSessionId).delete(socket);
      currentSessionId = message.sessionId || "demo-session";
      roomFor(currentSessionId).add(socket);
      broadcast(currentSessionId, { type: "participant_joined", clientId }, socket);
      send(socket, { type: "joined", clientId, sessionId: currentSessionId });
      return;
    }

    if (message.type === "hint_request") {
      try {
        const hint = await requestHint(message.payload);
        send(socket, { type: "hint", payload: hint });
      } catch (error) {
        send(socket, { type: "error", error: error.message });
      }
      return;
    }

    broadcast(currentSessionId, { ...message, clientId, sentAt: new Date().toISOString() }, socket);
  });

  socket.on("close", () => {
    roomFor(currentSessionId).delete(socket);
    broadcast(currentSessionId, { type: "participant_left", clientId }, socket);
  });
});

console.log(`Realtime gateway listening on ws://${host}:${port}`);
