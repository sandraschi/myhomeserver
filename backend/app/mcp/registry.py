"""
MCP Server Registry and Configuration System.
Manages MCP server configurations and provides auto-discovery.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .client import mcp_manager, MCPClient

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: List[str]
    description: str = ""
    category: str = "general"
    auto_start: bool = False
    environment: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None


class MCPServerRegistry:
    """
    Registry for managing MCP server configurations.

    Supports:
    - Auto-discovery of MCP servers in the workspace
    - Manual server registration
    - Configuration persistence
    - Server categorization
    """

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "mcp_servers.json"
        self.servers: Dict[str, MCPServerConfig] = {}
        self._loaded = False

    async def load_config(self) -> None:
        """Load MCP server configurations from file and auto-discover."""
        if self._loaded:
            return

        # Load from config file if it exists
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    for name, config_data in data.items():
                        config = MCPServerConfig(**config_data)
                        self.servers[name] = config
                        logger.info(f"Loaded MCP server config: {name}")
            except Exception as e:
                logger.error(f"Failed to load MCP server config: {e}")

        # Auto-discover MCP servers in workspace
        await self._auto_discover_servers()

        self._loaded = True

    async def save_config(self) -> None:
        """Save MCP server configurations to file."""
        try:
            data = {}
            for name, config in self.servers.items():
                data[name] = {
                    "name": config.name,
                    "command": config.command,
                    "description": config.description,
                    "category": config.category,
                    "auto_start": config.auto_start,
                    "environment": config.environment,
                    "working_directory": config.working_directory,
                }

            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved MCP server configurations to {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to save MCP server config: {e}")

    async def _auto_discover_servers(self) -> None:
        """Auto-discover MCP servers in the workspace."""
        workspace_root = Path(__file__).parent.parent.parent.parent.parent

        # Common MCP server patterns
        server_patterns = [
            # Python MCP servers
            ("src/*/mcp/server.py", "python", ["-m", "{module}.mcp.server"]),
            ("src/*/server.py", "python", ["-m", "{module}.server"]),
            ("src/*/app.py", "python", ["-m", "{module}.app"]),
            ("main.py", "python", ["main.py"]),
            ("server.py", "python", ["server.py"]),
            ("app.py", "python", ["app.py"]),

            # Node.js MCP servers
            ("dist/index.js", "node", ["dist/index.js"]),
            ("build/index.js", "node", ["build/index.js"]),
            ("index.js", "node", ["index.js"]),
        ]

        discovered = []

        # Look for MCP servers in repos
        repos_dir = workspace_root
        if repos_dir.exists():
            for repo_dir in repos_dir.iterdir():
                if not repo_dir.is_dir() or repo_dir.name.startswith('.'):
                    continue

                repo_name = repo_dir.name

                # Check for MCP server indicators
                if self._is_mcp_server(repo_dir):
                    for pattern, interpreter, command_template in server_patterns:
                        for entry_path in repo_dir.glob(pattern):
                            if entry_path.is_file():
                                # Extract module name from path
                                module_name = self._extract_module_name(repo_dir, entry_path)

                                # Create command
                                command = [interpreter] + [
                                    arg.format(module=module_name)
                                    for arg in command_template
                                ]

                                # Determine category
                                category = self._determine_category(repo_name)

                                config = MCPServerConfig(
                                    name=repo_name,
                                    command=command,
                                    description=f"Auto-discovered MCP server: {repo_name}",
                                    category=category,
                                    working_directory=str(repo_dir),
                                )

                                if repo_name not in self.servers:
                                    self.servers[repo_name] = config
                                    discovered.append(repo_name)
                                    logger.info(f"Auto-discovered MCP server: {repo_name}")
                                break

        if discovered:
            logger.info(f"Auto-discovered {len(discovered)} MCP servers: {', '.join(discovered)}")

    def _is_mcp_server(self, repo_dir: Path) -> bool:
        """Check if a repository contains an MCP server."""
        indicators = [
            # Look for MCP-related files
            "mcp",
            "model-context-protocol",
            # Look for server files
            "server.py",
            "main.py",
            "app.py",
            # Look for MCP imports
            "fastmcp",
            "mcp",
        ]

        # Check for indicator files/directories
        for indicator in indicators:
            if any(repo_dir.rglob(f"*{indicator}*")):
                return True

        # Check for pyproject.toml or setup.py with MCP keywords
        for config_file in ["pyproject.toml", "setup.py", "package.json"]:
            config_path = repo_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        content = f.read().lower()
                        if any(keyword in content for keyword in ["mcp", "fastmcp", "model-context-protocol"]):
                            return True
                except:
                    pass

        return False

    def _extract_module_name(self, repo_dir: Path, entry_path: Path) -> str:
        """Extract module name from repository and entry path."""
        # Try to find setup.py/pyproject.toml to get module name
        for config_file in ["pyproject.toml", "setup.py"]:
            config_path = repo_dir / config_file
            if config_path.exists():
                try:
                    # Simple parsing - look for name field
                    with open(config_path, 'r') as f:
                        content = f.read()
                        if "name =" in content or '"name"' in content:
                            # Very basic parsing
                            lines = content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line.startswith('name =') or line.startswith('"name"'):
                                    name = line.split('=', 1)[1].strip().strip('"\'')
                                    return name.replace('-', '_')
                except:
                    pass

        # Fallback: use repo name
        return repo_dir.name.replace('-', '_')

    def _determine_category(self, repo_name: str) -> str:
        """Determine server category based on name."""
        name_lower = repo_name.lower()

        categories = {
            "camera": ["camera", "video", "surveillance"],
            "energy": ["energy", "power", "electric", "smartplug"],
            "weather": ["weather", "netatmo", "climate"],
            "security": ["security", "ring", "alarm"],
            "home": ["home", "assistant", "hub", "nest"],
            "ai": ["ai", "llm", "gpt", "claude", "language"],
            "database": ["database", "db", "sql", "mongo"],
            "virtualization": ["vm", "virtual", "container", "docker"],
            "network": ["network", "tailscale", "vpn"],
            "media": ["media", "plex", "jellyfin", "emby"],
        }

        for category, keywords in categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category

        return "general"

    def register_server(self, config: MCPServerConfig) -> None:
        """Register an MCP server manually."""
        self.servers[config.name] = config
        # Also register with the MCP manager
        mcp_manager.register_server(
            config.name,
            config.command,
            description=config.description,
            category=config.category,
            working_directory=config.working_directory
        )
        logger.info(f"Registered MCP server: {config.name}")

    def unregister_server(self, name: str) -> None:
        """Unregister an MCP server."""
        if name in self.servers:
            del self.servers[name]
            logger.info(f"Unregistered MCP server: {name}")

    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        """Get server configuration by name."""
        return self.servers.get(name)

    def list_servers(self, category: Optional[str] = None) -> List[MCPServerConfig]:
        """List all registered servers, optionally filtered by category."""
        servers = list(self.servers.values())
        if category:
            servers = [s for s in servers if s.category == category]
        return servers

    def list_categories(self) -> List[str]:
        """List all server categories."""
        categories = set()
        for server in self.servers.values():
            categories.add(server.category)
        return sorted(list(categories))

    async def initialize_all_auto_start(self) -> None:
        """Initialize all servers marked for auto-start."""
        auto_start_servers = [s for s in self.servers.values() if s.auto_start]

        if not auto_start_servers:
            logger.info("No MCP servers configured for auto-start")
            return

        logger.info(f"Auto-starting {len(auto_start_servers)} MCP servers")

        for config in auto_start_servers:
            try:
                logger.info(f"Auto-starting MCP server: {config.name}")
                await mcp_manager.get_client(config.name)
            except Exception as e:
                logger.error(f"Failed to auto-start MCP server {config.name}: {e}")

    async def shutdown_all(self) -> None:
        """Shutdown all MCP server connections."""
        await mcp_manager.close_all()


# Global registry instance
mcp_registry = MCPServerRegistry()


async def initialize_mcp_registry() -> None:
    """Initialize the MCP server registry."""
    await mcp_registry.load_config()

    # Register known MCP servers manually for now
    # In production, this would be loaded from config files

    # Example registrations (these would be auto-discovered)
    workspace_root = Path(__file__).parent.parent.parent.parent.parent

    # MCP servers registered and auto-started with proper configuration
    # Tapo Camera MCP - auto-start with config from tapo-camera-mcp directory
    tapo_path = workspace_root / "tapo-camera-mcp"
    if tapo_path.exists():
        config = MCPServerConfig(
            name="tapo-camera-mcp",
            command=["python", "--version"],
            description="Tapo camera and smart device control",
            category="camera",
            auto_start=True,  # Auto-start with config
            working_directory=str(tapo_path),
        )
        mcp_registry.register_server(config)

    # Ring MCP - auto-start with config from ring-mcp directory
    ring_path = workspace_root / "ring-mcp"
    if ring_path.exists():
        config = MCPServerConfig(
            name="ring-mcp",
            command=["ring-mcp"],
            description="Ring doorbell and security system",
            category="security",
            auto_start=True,  # Auto-start with config
            working_directory=str(ring_path),
        )
        mcp_registry.register_server(config)

    # Home Assistant MCP - not installed in Docker yet
    ha_path = workspace_root / "home-assistant-mcp"
    if ha_path.exists():
        config = MCPServerConfig(
            name="home-assistant-mcp",
            command=["python", "-m", "home_assistant_mcp.cli"],
            description="Home Assistant smart home integration",
            category="home",
            auto_start=False,  # HA not installed yet
            working_directory=str(ha_path),
        )
        mcp_registry.register_server(config)

    # Netatmo MCP - auto-start with .env from netatmo-weather-mcp directory
    netatmo_path = workspace_root / "netatmo-weather-mcp"
    if netatmo_path.exists():
        config = MCPServerConfig(
            name="netatmo-weather-mcp",
            command=["python", "-m", "netatmo_weather_mcp.server"],
            description="Netatmo weather sensors",
            category="weather",
            auto_start=True,  # Enable auto-start
            working_directory=str(netatmo_path),
        )
        mcp_registry.register_server(config)

    # Local LLM MCP - commented out as not needed for smart home devices
    # llm_path = workspace_root / "local-llm-mcp"
    # if llm_path.exists():
    #     config = MCPServerConfig(
    #         name="local-llm-mcp",
    #         command=["python", "-m", "local_llm_mcp.server"],
    #         description="Local language model integration",
    #         category="ai",
    #         working_directory=str(llm_path),
    #     )
    #     mcp_registry.register_server(config)

    logger.info(f"Registered {len(mcp_registry.servers)} MCP servers")