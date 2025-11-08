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
