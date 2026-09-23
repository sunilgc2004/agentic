import json
from typing import Dict, List, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.logging import logger

router = APIRouter()


class WebSocketConnectionManager:
    """Manages active WebSocket subscribers per test run."""

    def __init__(self):
        # Maps run_id -> set of active WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, run_id: str, websocket: WebSocket):
        await websocket.accept()
        if run_id not in self.active_connections:
            self.active_connections[run_id] = set()
        self.active_connections[run_id].add(websocket)
        logger.info(f"WebSocket client connected to run: {run_id}")

    def disconnect(self, run_id: str, websocket: WebSocket):
        if run_id in self.active_connections:
            self.active_connections[run_id].discard(websocket)
            if not self.active_connections[run_id]:
                del self.active_connections[run_id]
        logger.info(f"WebSocket client disconnected from run: {run_id}")

    async def broadcast_to_run(self, run_id: str, message: dict):
        if run_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[run_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.add(connection)
            for dead in dead_connections:
                self.active_connections[run_id].discard(dead)


ws_manager = WebSocketConnectionManager()


@router.websocket("/ws/execution/{run_id}")
async def execution_websocket(websocket: WebSocket, run_id: str):
    """Real-time live streaming of test execution logs, steps, and human-in-the-loop commands."""
    await ws_manager.connect(run_id, websocket)
    try:
        while True:
            # Handle incoming client commands (e.g. pause, resume, stop, approve)
            data = await websocket.receive_text()
            try:
                cmd = json.loads(data)
                action = cmd.get("action")
                from app.agents.orchestrator import QAOrchestrator
                orch = QAOrchestrator.active_runs.get(run_id)
                if orch and action:
                    if action == "pause":
                        orch.pause()
                        await ws_manager.broadcast_to_run(run_id, {"event": "paused", "run_id": run_id})
                    elif action == "resume":
                        orch.resume()
                        await ws_manager.broadcast_to_run(run_id, {"event": "resumed", "run_id": run_id})
                    elif action == "stop":
                        orch.stop()
                        await ws_manager.broadcast_to_run(run_id, {"event": "stopped", "run_id": run_id})
            except Exception as e:
                logger.error(f"Error handling websocket command: {e}")
    except WebSocketDisconnect:
        ws_manager.disconnect(run_id, websocket)
