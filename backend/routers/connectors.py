"""Connectors router — manage TallyPrime desktop connector status & sync"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict
import json
from datetime import datetime

from database import get_db
from routers.auth import get_current_user, User

router = APIRouter()

# Active WebSocket connections: company_id → websocket
active_connectors: Dict[str, WebSocket] = {}


@router.get("/status/{company_id}")
def connector_status(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_connected = company_id in active_connectors
    return {
        "company_id": company_id,
        "connected": is_connected,
        "last_seen": datetime.utcnow().isoformat() if is_connected else None,
    }


@router.post("/sync/{company_id}")
async def trigger_sync(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ws = active_connectors.get(company_id)
    if not ws:
        raise HTTPException(status_code=503, detail="Connector not connected for this company")

    try:
        await ws.send_text(json.dumps({"action": "sync_masters", "request_id": "sync-now"}))
        return {"status": "sync_triggered", "company_id": company_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/connector")
async def connector_websocket(websocket: WebSocket):
    """WebSocket endpoint that the desktop Connector Agent connects to"""
    await websocket.accept()
    company_id: str = websocket.headers.get("X-Company-ID", "unknown")
    active_connectors[company_id] = websocket

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            msg_type = data.get("type")
            if msg_type == "register":
                print(f"✅ Connector registered: company={company_id}, tally={data.get('tally_running')}")
    except WebSocketDisconnect:
        pass
    finally:
        active_connectors.pop(company_id, None)
