# apps/api/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes.repositories import router as repo_router
from routes.snapshots import router as snapshot_router

app = FastAPI(title="CodeAtlas API", version="1.0.0")

# Enable CORS so Next.js frontend on port 3000 can communicate with FastAPI on port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(repo_router)
app.include_router(snapshot_router)

@app.get("/health")
def health_check():
    """Simple health check endpoint to confirm API service status."""
    return {"status": "ok"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global fallback exception handler to return structured JSON errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "details": str(exc)}
    )