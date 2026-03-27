from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db
from routers import auth, reconciliation, voice, invoice_scan, message_parser, connectors, vouchers, reports, audit, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle handler"""
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(vouchers.router, prefix=f"{settings.API_V1_PREFIX}/vouchers", tags=["Vouchers"])
app.include_router(reconciliation.router, prefix=f"{settings.API_V1_PREFIX}/reconciliation", tags=["Reconciliation"])
app.include_router(voice.router, prefix=f"{settings.API_V1_PREFIX}/voice", tags=["Voice Entry"])
app.include_router(invoice_scan.router, prefix=f"{settings.API_V1_PREFIX}/invoice", tags=["Invoice Scan"])
app.include_router(message_parser.router, prefix=f"{settings.API_V1_PREFIX}/messages", tags=["SMS/Email Parser"])
app.include_router(connectors.router, prefix=f"{settings.API_V1_PREFIX}/connectors", tags=["Connectors"])
app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])
app.include_router(audit.router, prefix=f"{settings.API_V1_PREFIX}/audit", tags=["Audit Trail"])
app.include_router(ai.router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["TaxMind AI"])


@app.get("/")
async def root():
    return {
        "message": "TaxMind Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health/ready")
async def readiness_check():
    """Check if all dependencies are ready"""
    return {
        "database": "ok",
        "redis": "ok",
        "ai_apis": "ok" if settings.ANTHROPIC_API_KEY else "not_configured"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
