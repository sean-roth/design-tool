# Design Tool

AI-powered design collaboration bridge for PenPot. Enables Claude agents (Designer, Engineer, and others) to create, modify, and review designs through natural conversation.

## Overview

This tool creates a bridge between Claude AI agents and PenPot design software, enabling real-time design collaboration between AI assistants with different specializations. A Designer agent can create mockups while an Engineer agent provides technical feedback on implementation feasibility—all through natural language.

## Project Goals

- **Project-Agnostic**: Works with any web app, mobile app, or design project
- **Multi-Agent Collaboration**: Multiple Claude instances can work together on designs
- **Natural Interface**: Agents interact through conversation, not complex APIs
- **Self-Hosted**: Runs on your infrastructure, full control over data
- **Extensible**: Easy to add new design operations and agent capabilities

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Agents                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Designer   │  │   Engineer   │  │    Other     │     │
│  │ (Claude      │  │ (Claude      │  │   Agents     │     │
│  │  Desktop)    │  │   Code)      │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   MCP Server    │
                    │  (HTTP/Local)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  PenPot Plugin  │
                    │  (JavaScript)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  PenPot Server  │
                    │   (Self-Hosted) │
                    └─────────────────┘
```

## Components

### 1. PenPot Plugin
JavaScript plugin that runs inside PenPot and:
- Exposes HTTP API for design operations
- Executes commands using PenPot Plugin API
- Manages shape creation, modification, and inspection
- Returns design state and screenshots

### 2. MCP Server
Model Context Protocol server that:
- Translates natural language to PenPot commands
- Handles authentication and routing
- Provides Claude-friendly tool interface
- Manages multi-agent coordination

### 3. MCP Configurations
JSON configs for each Claude agent:
- Connection details to MCP server
- Available operations and permissions
- Agent-specific settings

## Repository Structure

```
design-tool/
├── docs/
│   ├── ARCHITECTURE.md       # Detailed architecture
│   ├── PLUGIN-SPEC.md        # Plugin implementation spec
│   ├── MCP-SERVER-SPEC.md    # MCP server spec
│   ├── AUDIT-REQUEST.md      # System audit questions
│   └── AUDIT-RESULTS.md      # System audit results
├── penpot-plugin/
│   ├── manifest.json         # Plugin manifest
│   ├── plugin.ts             # Main plugin code
│   ├── api.ts                # HTTP API implementation
│   └── package.json
├── mcp-server/
│   ├── server.py             # MCP server implementation
│   ├── requirements.txt
│   └── config.example.json
├── mcp-configs/
│   ├── claude-desktop.json
│   └── claude-code.json
└── tests/
    └── integration/
```

## Status

Specification phase complete. Architecture finalized, all specs written and ready for implementation.

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — System design, data flow, and technical decisions
- **[MCP-SERVER-SPEC.md](docs/MCP-SERVER-SPEC.md)** — MCP server implementation spec
- **[PLUGIN-SPEC.md](docs/PLUGIN-SPEC.md)** — PenPot plugin implementation spec
- **[AUDIT-RESULTS.md](docs/AUDIT-RESULTS.md)** — Server environment audit

## Stack

Python · TypeScript · FastAPI · PenPot Plugin API · MCP · Docker

## License

TBD
