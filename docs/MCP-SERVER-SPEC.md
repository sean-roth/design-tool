# MCP Server Implementation Specification

**Component:** MCP Server (FastAPI/Python)  
**Version:** 1.0  
**Date:** 2025-11-08  
**Author:** Designer (Claude Desktop)  
**For:** Engineer (Claude Code)

---

## Overview

This document provides complete implementation instructions for the MCP Server - the bridge between Claude AI agents and PenPot. The server receives natural language commands from Claude agents, translates them to PenPot operations, and returns results.

## Implementation Checklist

- [ ] Setup Python environment
- [ ] Install dependencies
- [ ] Create project structure
- [ ] Implement core server (main.py)
- [ ] Implement PenPot client (penpot_client.py)
- [ ] Implement command translator (translator.py)
- [ ] Add configuration management
- [ ] Create Dockerfile
- [ ] Write tests
- [ ] Document API endpoints
- [ ] Open firewall port 3000

## Prerequisites

From audit, we have:
- Python 3.12.3 ✅
- pip 24.0 ✅
- Docker 28.5.1 ✅
- Port 3000 available ✅
- Sudo access ✅

## Project Structure

```
/home/sean/design-tool/mcp-server/
├── main.py                    # FastAPI application entry point
├── penpot_client.py          # PenPot HTTP client
├── translator.py             # Natural language → PenPot commands
├── models.py                 # Pydantic data models
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container definition
├── docker-compose.yml        # Service orchestration
├── .env.example              # Environment template
├── tests/
│   ├── __init__.py
│   ├── test_translator.py
│   ├── test_penpot_client.py
│   └── test_endpoints.py
├── logs/                     # Runtime logs
└── README.md                 # Setup instructions
```

## Step 1: Environment Setup

### Create Project Directory

```bash
cd /home/sean/design-tool
mkdir -p mcp-server/tests/logs
cd mcp-server
```

### Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Create requirements.txt

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
requests==2.31.0
python-multipart==0.0.6
python-dotenv==1.0.0
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configuration Management

### Create config.py

```python
"""Configuration management for MCP Server."""

from pydantic_settings import BaseSettings
from typing import Dict, Any
import json
from pathlib import Path


class PenPotSettings(BaseSettings):
    """PenPot connection settings."""
    url: str = "http://localhost:9001"
    plugin_endpoint: str = "/plugin/api"
    timeout: int = 30


class ServerSettings(BaseSettings):
    """MCP Server settings."""
    host: str = "0.0.0.0"
    port: int = 3000
    log_level: str = "INFO"
    cors_origins: list[str] = ["*"]


class ProjectConfig:
    """Project-specific configuration (brand colors, typography, etc)."""
    
    def __init__(self, config_path: str = "projects.json"):
        self.config_path = Path(config_path)
        self.projects: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load project configurations from JSON file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.projects = json.load(f)
        else:
            # Default configuration
            self.projects = {
                "compel-english": {
                    "brand_colors": {
                        "primary": "#FF5733",
                        "secondary": "#2e3434",
                        "accent": "#FFC300"
                    },
                    "typography": {
                        "heading": "Inter",
                        "body": "Open Sans"
                    },
                    "spacing": {
                        "unit": 8  # 8px base unit
                    }
                }
            }
            self.save()
    
    def save(self):
        """Save project configurations to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.projects, f, indent=2)
    
    def get_project(self, project_name: str) -> Dict[str, Any]:
        """Get configuration for specific project."""
        return self.projects.get(project_name, {})


class Settings(BaseSettings):
    """Main application settings."""
    penpot: PenPotSettings = PenPotSettings()
    server: ServerSettings = ServerSettings()
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


# Global settings instance
settings = Settings()
project_config = ProjectConfig()
```

### Create .env.example

```bash
# PenPot Configuration
PENPOT__URL=http://localhost:9001
PENPOT__PLUGIN_ENDPOINT=/plugin/api
PENPOT__TIMEOUT=30

# Server Configuration
SERVER__HOST=0.0.0.0
SERVER__PORT=3000
SERVER__LOG_LEVEL=INFO
```

## Step 3: Data Models

### Create models.py

```python
"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class ActionType(str, Enum):
    """Supported design actions."""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    QUERY = "query"


class ElementType(str, Enum):
    """Supported design element types."""
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"
    TEXT = "text"
    BOARD = "board"
    PATH = "path"
    GROUP = "group"


class DesignRequest(BaseModel):
    """Request to create or modify design element."""
    action: ActionType
    element_type: Optional[ElementType] = None
    element_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    project: Optional[str] = "compel-english"
    natural_language: Optional[str] = None  # Original command
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "create",
                "element_type": "rectangle",
                "properties": {
                    "name": "Primary Button",
                    "width": 200,
                    "height": 50
                },
                "natural_language": "Create a primary CTA button"
            }
        }


class DesignResponse(BaseModel):
    """Response from design operation."""
    success: bool
    message: str
    element_id: Optional[str] = None
    preview_url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class StateQuery(BaseModel):
    """Query for current design state."""
    board_name: Optional[str] = None
    element_id: Optional[str] = None
    include_children: bool = True


class StateResponse(BaseModel):
    """Current design state."""
    success: bool
    elements: List[Dict[str, Any]] = Field(default_factory=list)
    total_count: int = 0
    error: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    penpot_connected: bool
    version: str = "1.0.0"
```

## Step 4: PenPot Client

### Create penpot_client.py

```python
"""HTTP client for communicating with PenPot plugin."""

import requests
import logging
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class PenPotClient:
    """Client for PenPot plugin HTTP API."""
    
    def __init__(self):
        self.base_url = settings.penpot.url
        self.plugin_endpoint = settings.penpot.plugin_endpoint
        self.timeout = settings.penpot.timeout
        self.session = requests.Session()
    
    @property
    def plugin_url(self) -> str:
        """Full URL to plugin API."""
        return f"{self.base_url}{self.plugin_endpoint}"
    
    def health_check(self) -> bool:
        """Check if PenPot server is accessible."""
        try:
            response = self.session.get(
                self.base_url,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"PenPot health check failed: {e}")
            return False
    
    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command via PenPot plugin.
        
        Args:
            command: Command dictionary with operation and parameters
            
        Returns:
            Response from plugin
            
        Raises:
            requests.RequestException: If request fails
        """
        try:
            response = self.session.post(
                self.plugin_url,
                json=command,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"PenPot command failed: {e}")
            raise
    
    def create_rectangle(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rectangle shape."""
        command = {
            "operation": "createRectangle",
            "properties": properties
        }
        return self.execute_command(command)
    
    def create_ellipse(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create an ellipse shape."""
        command = {
            "operation": "createEllipse",
            "properties": properties
        }
        return self.execute_command(command)
    
    def create_text(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a text element."""
        command = {
            "operation": "createText",
            "properties": properties
        }
        return self.execute_command(command)
    
    def create_board(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a board (artboard)."""
        command = {
            "operation": "createBoard",
            "properties": properties
        }
        return self.execute_command(command)
    
    def modify_element(self, element_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Modify an existing element."""
        command = {
            "operation": "modifyElement",
            "element_id": element_id,
            "properties": properties
        }
        return self.execute_command(command)
    
    def get_state(self, query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get current design state."""
        command = {
            "operation": "getState",
            "query": query or {}
        }
        return self.execute_command(command)


# Global client instance
penpot_client = PenPotClient()
```

## Step 5: Command Translator

### Create translator.py

```python
"""Translate natural language to PenPot commands."""

import re
from typing import Dict, Any, Optional, Tuple
from config import project_config
import logging

logger = logging.getLogger(__name__)


class CommandTranslator:
    """Translates natural language commands to PenPot operations."""
    
    def __init__(self):
        self.element_keywords = {
            "button": "rectangle",
            "box": "rectangle",
            "card": "rectangle",
            "rectangle": "rectangle",
            "circle": "ellipse",
            "ellipse": "ellipse",
            "text": "text",
            "label": "text",
            "heading": "text",
            "board": "board",
            "frame": "board",
            "artboard": "board"
        }
        
        self.style_keywords = {
            "primary": {"fillColor": None},  # Will be filled from brand colors
            "secondary": {"fillColor": None},
            "cta": {"borderRadius": 8},
            "rounded": {"borderRadius": 12},
            "sharp": {"borderRadius": 0}
        }
    
    def parse_command(self, natural_language: str, project: str = "compel-english") -> Tuple[str, Dict[str, Any]]:
        """
        Parse natural language command into element type and properties.
        
        Args:
            natural_language: Command like "create a primary button"
            project: Project name for brand configuration
            
        Returns:
            Tuple of (element_type, properties_dict)
        """
        nl_lower = natural_language.lower()
        
        # Determine element type
        element_type = self._detect_element_type(nl_lower)
        
        # Extract properties
        properties = self._extract_properties(nl_lower, element_type, project)
        
        logger.info(f"Parsed '{natural_language}' → {element_type} with {properties}")
        
        return element_type, properties
    
    def _detect_element_type(self, text: str) -> str:
        """Detect what type of element to create."""
        for keyword, element_type in self.element_keywords.items():
            if keyword in text:
                return element_type
        
        # Default to rectangle if unclear
        return "rectangle"
    
    def _extract_properties(self, text: str, element_type: str, project: str) -> Dict[str, Any]:
        """Extract properties from natural language."""
        properties = {}
        
        # Get project configuration
        config = project_config.get_project(project)
        
        # Extract name
        properties["name"] = self._extract_name(text)
        
        # Extract dimensions
        width, height = self._extract_dimensions(text, element_type)
        if width:
            properties["width"] = width
        if height:
            properties["height"] = height
        
        # Extract colors (from brand or explicit)
        fill_color = self._extract_color(text, config)
        if fill_color:
            properties["fills"] = [{"fillColor": fill_color}]
        
        # Extract border radius
        border_radius = self._extract_border_radius(text)
        if border_radius is not None:
            properties["borderRadius"] = border_radius
        
        # Extract text content (for text elements)
        if element_type == "text":
            content = self._extract_text_content(text)
            if content:
                properties["text"] = content
            
            # Font from project config
            font = config.get("typography", {}).get("body", "Open Sans")
            properties["fontFamily"] = font
        
        return properties
    
    def _extract_name(self, text: str) -> str:
        """Extract element name from command."""
        # Try to find quoted name
        quoted = re.search(r'"([^"]+)"', text)
        if quoted:
            return quoted.group(1)
        
        # Generate name from key words
        words = text.split()
        name_words = []
        for word in words:
            if word in ["create", "add", "make", "a", "an", "the"]:
                continue
            name_words.append(word.capitalize())
        
        return " ".join(name_words[:3]) if name_words else "New Element"
    
    def _extract_dimensions(self, text: str, element_type: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract width and height."""
        # Look for explicit dimensions like "200x50" or "200 x 50"
        dimension_pattern = r'(\d+)\s*[xX×]\s*(\d+)'
        match = re.search(dimension_pattern, text)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # Look for "width: 200, height: 50"
        width_match = re.search(r'width[:\s]+(\d+)', text)
        height_match = re.search(r'height[:\s]+(\d+)', text)
        
        width = int(width_match.group(1)) if width_match else None
        height = int(height_match.group(1)) if height_match else None
        
        # Defaults if not specified
        if not width and not height:
            defaults = {
                "rectangle": (200, 100),
                "ellipse": (100, 100),
                "text": (200, None),
                "board": (1920, 1080)
            }
            return defaults.get(element_type, (None, None))
        
        return width, height
    
    def _extract_color(self, text: str, config: Dict[str, Any]) -> Optional[str]:
        """Extract color from text or brand config."""
        brand_colors = config.get("brand_colors", {})
        
        # Check for brand color keywords
        if "primary" in text and "primary" in brand_colors:
            return brand_colors["primary"]
        if "secondary" in text and "secondary" in brand_colors:
            return brand_colors["secondary"]
        if "accent" in text and "accent" in brand_colors:
            return brand_colors["accent"]
        
        # Check for hex color
        hex_match = re.search(r'#([0-9A-Fa-f]{6})', text)
        if hex_match:
            return f"#{hex_match.group(1)}"
        
        return None
    
    def _extract_border_radius(self, text: str) -> Optional[int]:
        """Extract border radius."""
        if "rounded" in text:
            # Look for specific value
            radius_match = re.search(r'radius[:\s]+(\d+)', text)
            if radius_match:
                return int(radius_match.group(1))
            return 12  # Default rounded
        
        if "sharp" in text or "square" in text:
            return 0
        
        # CTA buttons are typically rounded
        if "cta" in text or "button" in text:
            return 8
        
        return None
    
    def _extract_text_content(self, text: str) -> Optional[str]:
        """Extract text content for text elements."""
        # Look for quoted text
        quoted = re.search(r'"([^"]+)"', text)
        if quoted:
            return quoted.group(1)
        
        # Look for "text: something"
        content_match = re.search(r'text[:\s]+(.+?)(?:\s+with|\s+at|$)', text)
        if content_match:
            return content_match.group(1).strip()
        
        return "Text"


# Global translator instance
translator = CommandTranslator()
```

## Step 6: Main Application

### Create main.py

```python
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
```

## Step 7: Testing

### Create tests/test_translator.py

```python
"""Tests for command translator."""

import pytest
from translator import CommandTranslator

translator = CommandTranslator()


def test_simple_button():
    element_type, props = translator.parse_command("create a button")
    assert element_type == "rectangle"
    assert "name" in props


def test_primary_button_with_brand():
    element_type, props = translator.parse_command(
        "create a primary CTA button",
        project="compel-english"
    )
    assert element_type == "rectangle"
    assert props.get("fills")[0]["fillColor"] == "#FF5733"
    assert props["borderRadius"] == 8


def test_dimensions():
    element_type, props = translator.parse_command("create a 300x50 button")
    assert props["width"] == 300
    assert props["height"] == 50


def test_text_element():
    element_type, props = translator.parse_command('create text "Hello World"')
    assert element_type == "text"
    assert props["text"] == "Hello World"
```

## Step 8: Deployment

### Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 3000

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    container_name: mcp-server
    ports:
      - "3000:3000"
    environment:
      - PENPOT__URL=http://192.168.1.205:9001
    volumes:
      - ./logs:/app/logs
      - ./projects.json:/app/projects.json
    restart: unless-stopped
    networks:
      - penpot

networks:
  penpot:
    external: true
```

## Step 9: Firewall Configuration

### Open Port 3000

```bash
sudo ufw allow 3000/tcp comment "MCP Server"
sudo ufw reload
sudo ufw status
```

## Step 10: Running the Server

### Development Mode

```bash
cd /home/sean/design-tool/mcp-server
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

### Production Mode (Docker)

```bash
cd /home/sean/design-tool/mcp-server
docker-compose up -d
```

### View Logs

```bash
# Development
tail -f logs/server.log

# Docker
docker-compose logs -f mcp-server
```

## Step 11: Testing the Server

### Health Check

```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "healthy",
  "penpot_connected": true,
  "version": "1.0.0"
}
```

### Test Create Endpoint

```bash
curl -X POST http://localhost:3000/design/create \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "natural_language": "create a primary button",
    "project": "compel-english"
  }'
```

### API Documentation

Visit: http://localhost:3000/docs

FastAPI automatically generates interactive API documentation.

## Success Criteria

- [ ] Server starts without errors
- [ ] Health check returns 200 OK
- [ ] Can connect to PenPot (health check shows penpot_connected: true)
- [ ] Create endpoint accepts requests
- [ ] Natural language parsing works
- [ ] Brand colors applied correctly
- [ ] Accessible from Windows machine (http://192.168.1.205:3000)
- [ ] Logs written to logs/server.log
- [ ] API docs accessible at /docs

## Troubleshooting

### Server Won't Start

```bash
# Check if port is already in use
ss -tulpn | grep 3000

# Check logs
cat logs/server.log

# Verify Python version
python3 --version  # Should be 3.12.3
```

### Can't Connect to PenPot

```bash
# Test PenPot directly
curl http://localhost:9001

# Check if PenPot is running
docker ps | grep penpot

# Check PenPot logs
cd /home/sean/penpot
docker-compose logs
```

### Windows Machine Can't Reach Server

```bash
# Verify firewall
sudo ufw status

# Test from server
curl http://192.168.1.205:3000/health

# Test network
ping 192.168.1.205
```

## Next Steps

After MCP Server is running:

1. **Create PenPot Admin Account**
   - Visit http://192.168.1.205:9001
   - Register: mcp-server@compel.ai
   - Save credentials

2. **Implement PenPot Plugin** (See PLUGIN-SPEC.md)
   - Plugin will provide the actual PenPot API
   - MCP Server will call plugin endpoints

3. **Configure MCP Clients**
   - Windows: Claude Desktop config
   - Linux: Claude Code config

4. **Test End-to-End**
   - Designer creates element
   - Engineer sees and modifies it

---

**Status:** Ready for Implementation  
**Estimated Time:** 4-6 hours  
**Dependencies:** PenPot running (✅), Port 3000 open (pending)  
**Next:** PLUGIN-SPEC.md
