"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routers import chat, databases, config, conversations
from api.services.agent_service import AgentService
from api.services.mcp_service import MCPService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    print("Starting DataLens API...")

    # Initialize MCP Service if enabled
    agent_service = AgentService.get_instance()
    if agent_service.use_mcp:
        print("Initializing MCP Service...")
        await MCPService.startup()

    yield

    # Shutdown
    print("Shutting down DataLens API...")

    # Shutdown MCP Service if enabled
    if agent_service.use_mcp:
        print("Shutting down MCP Service...")
        await MCPService.shutdown()

    AgentService.reset_instance()


app = FastAPI(
    title="DataLens API",
    description="Intelligent Data Analysis Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(databases.router)
app.include_router(config.router)
app.include_router(conversations.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DataLens API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)