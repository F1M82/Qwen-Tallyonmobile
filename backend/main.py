# FILE: backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import Base, engine
from routers import auth, reconciliation, voice, invoice_scan, message_parser, connectors

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/api/v1/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(reconciliation.router, prefix="/api/v1/reconciliation", tags=["Reconciliation"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice Entry"])
app.include_router(invoice_scan.router, prefix="/api/v1/invoice", tags=["Invoice Scan"])
app.include_router(message_parser.router, prefix="/api/v1/messages", tags=["SMS/Email Parser"])
app.include_router(connectors.router, prefix="/api/v1/connectors", tags=["Connectors"])

@app.get("/")
async def root():
    return {
        "message": "TaxMind Platform API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
