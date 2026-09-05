from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import List
from datetime import datetime

# Import your existing modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.agent_state import AgentState
from nodes.fetch_emails import fetch_all_unread_emails
from nodes.summarize import generate_summary
from nodes.slack import send_slack_message

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.current_state = {
            "unread_emails": [],
            "summary": "",
            "approved": False,
            "status": "idle"
        }

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    with open("frontend/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/api/status")
async def get_status():
    return JSONResponse(manager.current_state)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_json({
            "type": "connected",
            "data": manager.current_state
        })

        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "fetch_emails":
                await handle_fetch_emails(websocket)
            elif action == "generate_summary":
                await handle_generate_summary(websocket)
            elif action == "approve":
                await handle_approve(websocket, data.get("summary"))
            elif action == "reject":
                await handle_reject(websocket)
            elif action == "reset":
                await handle_reset(websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def handle_fetch_emails(websocket: WebSocket):
    try:
        await websocket.send_json({
            "type": "status",
            "data": {"status": "fetching", "message": "Fetching unread emails..."}
        })

        # Run fetch in thread to avoid blocking
        state = {"unread_emails": [], "summary": "", "approved": False}
        result = await asyncio.to_thread(fetch_all_unread_emails, state)
        
        manager.current_state["unread_emails"] = result["unread_emails"]
        manager.current_state["status"] = "fetched"

        await websocket.send_json({
            "type": "emails_fetched",
            "data": {
                "emails": result["unread_emails"],
                "count": len(result["unread_emails"])
            }
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })

async def handle_generate_summary(websocket: WebSocket):
    try:
        await websocket.send_json({
            "type": "status",
            "data": {"status": "summarizing", "message": "Generating summary with AI..."}
        })

        state = {
            "unread_emails": manager.current_state["unread_emails"],
            "summary": "",
            "approved": False
        }
        
        result = await asyncio.to_thread(generate_summary, state)
        
        manager.current_state["summary"] = result["summary"]
        manager.current_state["status"] = "awaiting_approval"

        await websocket.send_json({
            "type": "summary_generated",
            "data": {"summary": result["summary"]}
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })

async def handle_approve(websocket: WebSocket, summary: str):
    try:
        await websocket.send_json({
            "type": "status",
            "data": {"status": "sending", "message": "Sending to Slack..."}
        })

        state = {
            "unread_emails": manager.current_state["unread_emails"],
            "summary": summary or manager.current_state["summary"],
            "approved": True
        }
        
        await asyncio.to_thread(send_slack_message, state)
        
        manager.current_state["approved"] = True
        manager.current_state["status"] = "completed"

        await websocket.send_json({
            "type": "slack_sent",
            "data": {"message": "Summary sent to Slack successfully!"}
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })

async def handle_reject(websocket: WebSocket):
    manager.current_state["status"] = "rejected"
    await websocket.send_json({
        "type": "rejected",
        "data": {"message": "Summary rejected"}
    })

async def handle_reset(websocket: WebSocket):
    manager.current_state = {
        "unread_emails": [],
        "summary": "",
        "approved": False,
        "status": "idle"
    }
    await websocket.send_json({
        "type": "reset",
        "data": manager.current_state
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)