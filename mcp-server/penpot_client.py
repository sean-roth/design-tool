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
