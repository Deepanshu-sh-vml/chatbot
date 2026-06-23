"""FastAPI application for Northwind Support Co-pilot."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.routes import router

load_dotenv()

app = FastAPI(
    title="Northwind Support Co-pilot Backend",
    description="4-stage LLM pipeline for support ticket triage",
    version="1.0.0",
)
frontend_origin = os.getenv(
  "FRONTEND_ORIGIN",
  "http://localhost:5173,http://localhost:3000",
)
allowed_origins = [o.strip() for o in frontend_origin.split(",") if o.strip()]

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Log startup."""
    print("🚀 Northwind Support Co-pilot backend started")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)