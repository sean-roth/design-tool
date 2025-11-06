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
│   ├── AUDIT-REQUEST.md      # Questions for system audit
│   ├── AUDIT-RESULTS.md      # Audit findings
│   ├── ARCHITECTURE.md       # Detailed architecture
│   ├── PLUGIN-SPEC.md        # Plugin implementation spec
│   └── MCP-SERVER-SPEC.md    # MCP server spec
├── penpot-plugin/
│   ├── manifest.json         # Plugin manifest
│   ├── plugin.ts             # Main plugin code
│   ├── api.ts                # HTTP API implementation
│   └── package.json          # Dependencies
├── mcp-server/
│   ├── server.py             # MCP server implementation
│   ├── requirements.txt      # Python dependencies
│   └── config.example.json   # Configuration template
├── mcp-configs/
│   ├── claude-desktop.json   # Windows Claude Desktop config
│   └── claude-code.json      # Linux Claude Code config
├── tests/
│   └── integration/          # Integration tests
├── .gitignore
├── LICENSE
└── README.md
```

## Current Status

🚧 **Initial Setup Phase** 🚧

- [x] Repository created
- [x] Basic structure defined
- [ ] System audit completed
- [ ] Architecture finalized
- [ ] PenPot plugin developed
- [ ] MCP server implemented
- [ ] Agent configurations created
- [ ] Integration testing complete

## Getting Started

### Prerequisites
- PenPot server (self-hosted)
- Linux server for MCP server
- Claude Desktop (Windows/Mac)
- Claude Code (CLI)

### Next Steps

1. **Engineer**: Complete system audit (see `docs/AUDIT-REQUEST.md`)
2. **Designer**: Review audit and write implementation specs
3. **Engineer**: Implement plugin and MCP server
4. **Both**: Test and iterate

## Use Cases

### Web Application Design
Designer creates UI mockups while Engineer validates technical feasibility and responsive behavior.

### Mobile App Prototyping
Rapid iteration on mobile interfaces with real-time feedback on platform constraints.

### Design System Development
Collaborative creation of component libraries with both design and engineering input.

### Client Projects
Quick turnaround on design concepts with immediate implementation assessment.

## Contributing

This is currently a private project for Sean's AI operations infrastructure. May be open-sourced in the future.

## License

TBD

## Contact

Sean Roth - Compel English founder
