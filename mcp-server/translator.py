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
