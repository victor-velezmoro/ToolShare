import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Request
from database import init_db
from routers import auth, items, users
from config import settings

# Configure logging
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# File handler: Logs to a file with rotation
file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=1000000, backupCount=3
)
file_handler.setFormatter(log_formatter)

# Stream handler: Logs to stdout for Docker logs
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Add handlers to logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler],
)

logger = logging.getLogger(__name__)
logger.info("Test log message to verify file and console output")



app = FastAPI(
    title="ToolShare",
    description="A simple tool sharing application",
    version="0.3",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    print(f"Middleware triggered for {request.method} {request.url}")
    return response


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(items.router, prefix="/items", tags=["Items"])


@app.on_event("startup")
def on_startup():
    logger.info("Initializing database")
    init_db()
