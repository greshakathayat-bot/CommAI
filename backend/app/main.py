import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.api import transcripts, accounts, clients, sales_reps, agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="CommAi API",
    description="Sales intelligence platform — transcript analysis and opportunity matching",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables on startup
@app.on_event("startup")
def on_startup():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready.")

# Register routers
app.include_router(sales_reps.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(transcripts.router, prefix="/api")
app.include_router(agent.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "CommAi API"}
