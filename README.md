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
│   ├── AUDIT-RESULTS.md      # ✅ System audit complete
│   ├── ARCHITECTURE.md       # ✅ Detailed architecture
│   ├── PLUGIN-SPEC.md        # ✅ Plugin implementation spec
│   └── MCP-SERVER-SPEC.md    # ✅ MCP server spec
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
├── CONTRIBUTING.md
└── README.md
```

## Current Status

🟢 **Specification Phase Complete** 🟢

- [x] Repository created
- [x] Basic structure defined
- [x] System audit completed ⭐
- [x] Architecture finalized ⭐
- [ ] PenPot plugin developed ← **Engineer: Start here**
- [ ] MCP server implemented ← **Engineer: Then this**
- [ ] Agent configurations created
- [ ] Integration testing complete

## Getting Started for Engineer

### Phase 1: MCP Server (Recommended First)

The MCP server can be built and tested independently before the plugin.

**Location:** `/home/sean/design-tool/mcp-server/`

**Documentation:** [docs/MCP-SERVER-SPEC.md](docs/MCP-SERVER-SPEC.md)

**Estimated Time:** 4-6 hours

**Key Tasks:**
1. Create Python virtual environment
2. Install FastAPI and dependencies
3. Implement core server (main.py)
4. Implement PenPot client (penpot_client.py)
5. Implement command translator (translator.py)
6. Open firewall port 3000
7. Test endpoints with curl

**Success Criteria:**
- Server starts on port 3000
- Health check returns 200 OK
- Natural language parsing works
- Accessible from Windows (http://192.168.1.205:3000)

### Phase 2: PenPot Plugin

The plugin interfaces directly with PenPot's Plugin API.

**Location:** `/home/sean/design-tool/penpot-plugin/`

**Documentation:** [docs/PLUGIN-SPEC.md](docs/PLUGIN-SPEC.md)

**Estimated Time:** 8-12 hours (includes research)

**Key Tasks:**
1. Research PenPot plugin system thoroughly
2. Create TypeScript project
3. Implement plugin.ts with shape operations
4. Build and test plugin locally
5. Install plugin in PenPot
6. Bridge plugin to MCP server

**Success Criteria:**
- Plugin loads in PenPot
- Can create shapes via plugin
- Can query design state
- MCP server can trigger operations

### Phase 3: Integration

Connect all pieces and test end-to-end.

**Key Tasks:**
1. Configure MCP clients (Windows + Linux)
2. Test Designer creates element
3. Test Engineer modifies element
4. Verify both see changes
5. Test natural language commands

## Prerequisites

From [AUDIT-RESULTS.md](docs/AUDIT-RESULTS.md):
- ✅ PenPot running (port 9001)
- ✅ Python 3.12.3
- ✅ Node.js 20.19.5
- ✅ Docker available
- ✅ Port 3000 available
- ✅ Sufficient resources (31GB RAM, 60GB disk)

## Use Cases

### Web Application Design
Designer creates UI mockups while Engineer validates technical feasibility and responsive behavior.

### Mobile App Prototyping
Rapid iteration on mobile interfaces with real-time feedback on platform constraints.

### Design System Development
Collaborative creation of component libraries with both design and engineering input.

### Client Projects
Quick turnaround on design concepts with immediate implementation assessment.

## Documentation

All specifications are complete and ready for implementation:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Complete system design, data flow, and technical decisions
- **[MCP-SERVER-SPEC.md](docs/MCP-SERVER-SPEC.md)** - Step-by-step MCP server implementation
- **[PLUGIN-SPEC.md](docs/PLUGIN-SPEC.md)** - Step-by-step PenPot plugin implementation
- **[AUDIT-RESULTS.md](docs/AUDIT-RESULTS.md)** - Complete server audit and environment details

## Communication

This repository serves as the collaboration space between Designer (Claude Desktop) and Engineer (Claude Code). See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow details.

**Current Workflow:**
1. Designer creates specification documents
2. Engineer implements according to specs
3. Engineer commits code and provides updates
4. Designer reviews and provides feedback
5. Iterate until complete

## Contributing

This is currently a private project for Sean's AI operations infrastructure. May be open-sourced in the future.

## License

TBD

## Contact

Sean Roth - Compel English founder

---

## Quick Start for Sean

### Test MCP Server (After Engineer Builds It)

```bash
# From Windows machine
curl http://192.168.1.205:3000/health

# Test create command
curl -X POST http://192.168.1.205:3000/design/create \
  -H "Content-Type: application/json" \
  -d '{"action":"create","natural_language":"create a primary button"}'
```

### Access PenPot

```
URL: http://192.168.1.205:9001
```

### Monitor Progress

Check this README - status checkboxes update as work completes.

---

**Next Actions:**
1. **Engineer:** Start with MCP-SERVER-SPEC.md
2. **Engineer:** Then move to PLUGIN-SPEC.md  
3. **Sean:** Test endpoints once MCP server is running
4. **Both:** Integrate and test full workflow
