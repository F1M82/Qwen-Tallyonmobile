"""
TaxMind Desktop Connector
=========================

Lightweight Python agent that runs on client's PC and bridges
TallyPrime (localhost:9000) with TaxMind Cloud Backend.

Installation:
    pip install -r requirements.txt
    pyinstaller --onefile --windowed main.py

Usage:
    python main.py  # Development
    TaxMindConnector.exe  # Production
"""

import asyncio
import httpx
import websockets
import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from tally_client import TallyClient

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "https://api.taxmind.in")
AUTH_TOKEN = os.getenv("CONNECTOR_AUTH_TOKEN", "")
COMPANY_ID = os.getenv("COMPANY_ID", "")
TALLY_HOST = os.getenv("TALLY_HOST", "localhost")
TALLY_PORT = int(os.getenv("TALLY_PORT", "9000"))
RECONNECT_DELAY = 5  # seconds

class ConnectorAgent:
    """
    Desktop connector agent that maintains WebSocket connection
    with backend and executes Tally commands.
    """
    
    def __init__(self):
        self.tally = TallyClient(TALLY_HOST, TALLY_PORT)
        self.backend = BACKEND_URL
        self.ws_url = f"wss://{BACKEND_URL.replace('https', 'wss')}/ws/connector"
        self.company_id = COMPANY_ID
        self.is_running = True
        self.last_heartbeat = datetime.now()
        
    async def run(self):
        """Main connection loop with auto-reconnect"""
        print(f"🔌 TaxMind Connector v1.0.0")
        print(f"📊 TallyPrime: {TALLY_HOST}:{TALLY_PORT}")
        print(f"☁️  Backend: {self.backend}")
        print(f"🏢 Company: {self.company_id}")
        print(f"{'='*50}")
        
        while self.is_running:
            try:
                async with websockets.connect(
                    self.ws_url,
                    extra_headers={
                        "Authorization": f"Bearer {AUTH_TOKEN}",
                        "X-Company-ID": self.company_id
                    },
                    ping_interval=30,
                    ping_timeout=10,
                ) as ws:
                    print(f"✅ Connected to TaxMind backend at {datetime.now().isoformat()}")
                    
                    # Register this connector
                    await self.register_connector(ws)
                    
                    # Main message loop
                    async for message in ws:
                        try:
                            command = json.loads(message)
                            response = await self.handle_command(command)
                            await ws.send(json.dumps(response))
                            self.last_heartbeat = datetime.now()
                        except json.JSONDecodeError:
                            print(f"❌ Invalid JSON received")
                        except Exception as e:
                            print(f"❌ Command error: {e}")
                            await ws.send(json.dumps({
                                "status": "error",
                                "message": str(e)
                            }))
                            
            except websockets.exceptions.ConnectionClosed:
                print(f"⚠️  Connection closed at {datetime.now().isoformat()}")
            except Exception as e:
                print(f"❌ Connection error: {e}")
                print(f"🔄 Reconnecting in {RECONNECT_DELAY} seconds...")
                await asyncio.sleep(RECONNECT_DELAY)
    
    async def register_connector(self, ws: websockets.WebSocketClientProtocol):
        """Register this connector with backend"""
        try:
            # Test Tally connection
            tally_alive = await self.tally.ping()
            
            # Send registration
            await ws.send(json.dumps({
                "type": "register",
                "company_id": self.company_id,
                "tally_running": tally_alive,
                "tally_version": "TallyPrime 7.0",  # Can be detected dynamically
                "connector_version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }))
            
            print(f"📊 Tally Status: {'✅ Running' if tally_alive else '❌ Not Running'}")
            
        except Exception as e:
            print(f"❌ Registration failed: {e}")
    
    async def handle_command(self, cmd: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command from backend and return response"""
        action = cmd.get("action")
        request_id = cmd.get("request_id")
        
        print(f"⚡ Command: {action}")
        
        try:
            if action == "get_ledger":
                data = await self.tally.get_ledger(
                    cmd.get("party_name"),
                    cmd.get("from_date"),
                    cmd.get("to_date")
                )
                return {
                    "status": "ok",
                    "request_id": request_id,
                    "data": data
                }
            
            elif action == "get_all_ledgers":
                ledgers = await self.tally.get_all_ledgers()
                groups = await self.tally.get_all_groups()
                return {
                    "status": "ok",
                    "request_id": request_id,
                    "ledgers": ledgers,
                    "groups": groups
                }
            
            elif action == "post_voucher":
                result = await self.tally.post_voucher(cmd.get("voucher"))
                return {
                    "status": "ok",
                    "request_id": request_id,
                    "result": result
                }
            
            elif action == "get_trial_balance":
                data = await self.tally.get_trial_balance(
                    cmd.get("from_date"),
                    cmd.get("to_date")
                )
                return {
                    "status": "ok",
                    "request_id": request_id,
                    "data": data
                }
            
            elif action == "get_outstanding":
                data = await self.tally.get_outstanding(
                    cmd.get("party_type"),
                    cmd.get("as_of_date")
                )
                return {
                    "status": "ok",
                    "request_id": request_id,
                    "data": data
                }
            
            elif action == "health_check":
                is_alive = await self.tally.ping()
                return {
                    "status": "ok",
                    "request_id": request_id,
                    "tally_running": is_alive,
                    "timestamp": datetime.now().isoformat()
                }
            
            elif action == "sync_masters":
                ledgers = await self.tally.get_all_ledgers()
                groups = await self.tally.get_all_groups()
                return {
                    "status": "ok",
                    "request_id": request_id,
                    "ledgers": ledgers,
                    "groups": groups
                }
            
            else:
                return {
                    "status": "error",
                    "request_id": request_id,
                    "message": f"Unknown action: {action}"
                }
        
        except Exception as e:
            print(f"❌ Command execution error: {e}")
            return {
                "status": "error",
                "request_id": request_id,
                "message": str(e)
            }
    
    def stop(self):
        """Stop the connector"""
        self.is_running = False
        print("👋 Connector stopping...")


def main():
    """Entry point"""
    agent = ConnectorAgent()
    
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        agent.stop()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
