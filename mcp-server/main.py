"""FastAPI application for MCP Server."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from models import (
    DesignRequest,
    DesignResponse,
    StateQuery,
    StateResponse,
    HealthResponse
)
from penpot_client import penpot_client
from translator import translator

# Configure logging
logging.basicConfig(
    level=settings.server.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting MCP Server...")
    logger.info(f"PenPot URL: {settings.penpot.url}")
    logger.info(f"Server: {settings.server.host}:{settings.server.port}")

    # Check PenPot connectivity
    if not penpot_client.health_check():
        logger.warning("PenPot server not accessible at startup")

    yield

    logger.info("Shutting down MCP Server...")


# Create FastAPI app
app = FastAPI(
    title="PenPot AI Design Bridge",
    description="MCP Server for Claude AI agents to collaborate on PenPot designs",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    penpot_status = penpot_client.health_check()

    return HealthResponse(
        status="healthy" if penpot_status else "degraded",
        penpot_connected=penpot_status
    )


@app.post("/design/create", response_model=DesignResponse)
async def create_design(request: DesignRequest):
    """
    Create a new design element.

    This endpoint accepts natural language commands and translates them
    to PenPot operations.
    """
    try:
        logger.info(f"Create request: {request.dict()}")

        # If natural language provided, parse it
        if request.natural_language:
            element_type, properties = translator.parse_command(
                request.natural_language,
                request.project or "compel-english"
            )
            # Merge with explicit properties
            properties.update(request.properties)
        else:
            element_type = request.element_type
            properties = request.properties

        # Execute via PenPot client
        if element_type == "rectangle":
            result = penpot_client.create_rectangle(properties)
        elif element_type == "ellipse":
            result = penpot_client.create_ellipse(properties)
        elif element_type == "text":
            result = penpot_client.create_text(properties)
        elif element_type == "board":
            result = penpot_client.create_board(properties)
        else:
            raise ValueError(f"Unsupported element type: {element_type}")

        return DesignResponse(
            success=True,
            message=f"Created {element_type}: {properties.get('name', 'unnamed')}",
            element_id=result.get("id"),
            preview_url=f"{settings.penpot.url}/view/{result.get('id')}"
        )

    except Exception as e:
        logger.error(f"Create failed: {e}", exc_info=True)
        return DesignResponse(
            success=False,
            message="Failed to create element",
            error={
                "code": "CREATE_FAILED",
                "message": str(e)
            }
        )


@app.post("/design/modify", response_model=DesignResponse)
async def modify_design(request: DesignRequest):
    """Modify an existing design element."""
    try:
        if not request.element_id:
            raise ValueError("element_id required for modify")

        logger.info(f"Modify request: {request.dict()}")

        result = penpot_client.modify_element(
            request.element_id,
            request.properties
        )

        return DesignResponse(
            success=True,
            message=f"Modified element: {request.element_id}",
            element_id=request.element_id,
            data=result
        )

    except Exception as e:
        logger.error(f"Modify failed: {e}", exc_info=True)
        return DesignResponse(
            success=False,
            message="Failed to modify element",
            error={
                "code": "MODIFY_FAILED",
                "message": str(e)
            }
        )


@app.post("/design/state", response_model=StateResponse)
async def get_state(query: StateQuery):
    """Get current design state."""
    try:
        logger.info(f"State query: {query.dict()}")

        result = penpot_client.get_state(query.dict())

        return StateResponse(
            success=True,
            elements=result.get("elements", []),
            total_count=len(result.get("elements", []))
        )

    except Exception as e:
        logger.error(f"State query failed: {e}", exc_info=True)
        return StateResponse(
            success=False,
            error={
                "code": "STATE_QUERY_FAILED",
                "message": str(e)
            }
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "PenPot AI Design Bridge",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.server.host,
        port=settings.server.port,
        log_level=settings.server.log_level.lower()
    )
