# System Architecture

**Project:** PenPot AI Design Bridge  
**Version:** 1.0  
**Date:** 2025-11-08  
**Author:** Designer (Claude Desktop)

---

## Overview

This document defines the complete architecture for enabling multiple Claude AI agents to collaborate on PenPot designs through natural conversation. The system creates a bridge between Claude's Model Context Protocol (MCP) and PenPot's Plugin API.

## Design Goals

1. **Multi-Agent Collaboration**: Designer (Windows) and Engineer (Linux) work on same designs
2. **Natural Interface**: Agents use conversational commands, not raw API calls
3. **Real-Time Updates**: Changes visible immediately to both agents
4. **Project Agnostic**: Works for any design project, not just Compel English
5. **HTTP-Based**: Avoids SSH complexity that caused Windows connectivity issues
6. **Self-Contained**: No external dependencies beyond PenPot server

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLAUDE AGENTS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────┐              ┌────────────────────┐    │
│  │  Designer Agent    │              │  Engineer Agent    │    │
│  │  (Claude Desktop)  │              │  (Claude Code)     │    │
│  │  Windows Machine   │              │  Linux Server      │    │
│  └─────────┬──────────┘              └─────────┬──────────┘    │
│            │                                    │                │
│            │ MCP Tool                           │ MCP Tool       │
│            │ (HTTP Client)                      │ (HTTP Client)  │
└────────────┼────────────────────────────────────┼────────────────┘
             │                                    │
             │ http://192.168.1.205:3000          │ http://localhost:3000
             │                                    │
        ┌────┴────────────────────────────────────┴──────┐
        │                                                 │
        │         MCP SERVER (FastAPI/Python)            │
        │         Port: 3000                              │
        │         Location: Linux Server                  │
        │                                                 │
        │  - Receives natural language commands          │
        │  - Translates to PenPot operations             │
        │  - Manages agent coordination                  │
        │  - Returns design state                        │
        │                                                 │
        └────────────────────┬───────────────────────────┘
                             │
                             │ HTTP (Internal)
                             │
                ┌────────────▼────────────┐
                │                         │
                │   PENPOT PLUGIN         │
                │   (JavaScript)          │
                │                         │
                │  - Executes PenPot API  │
                │  - Creates shapes       │
                │  - Modifies designs     │
                │  - Captures state       │
                │                         │
                └────────────┬────────────┘
                             │
                             │ PenPot Plugin API
                             │
                ┌────────────▼────────────┐
                │                         │
                │   PENPOT SERVER         │
                │   (Docker Containers)   │
                │   Port: 9001            │
                │                         │
                │  - Frontend             │
                │  - Backend              │
                │  - PostgreSQL           │
                │  - Redis                │
                │  - Exporter             │
                │                         │
                └─────────────────────────┘
```

## Data Flow

### Example: Designer Creates a Button

```
1. Designer (Windows):
   "Create a primary CTA button with our brand colors"
   
2. Claude Desktop → MCP Tool:
   POST http://192.168.1.205:3000/design/create
   {
     "action": "create",
     "element": "button",
     "properties": {
       "type": "primary",
       "style": "cta",
       "brand": "compel-english"
     }
   }
   
3. MCP Server:
   - Parses natural language intent
   - Looks up Compel English brand colors (#FF5733)
   - Translates to PenPot commands
   
4. MCP Server → PenPot Plugin:
   POST http://localhost:9001/plugin/execute
   {
     "operation": "createRectangle",
     "properties": {
       "name": "Primary CTA Button",
       "fills": [{"fillColor": "#FF5733"}],
       "strokes": [{"strokeColor": "#2e3434", "strokeWidth": 2}],
       "size": {"width": 200, "height": 50},
       "borderRadius": 8
     }
   }
   
5. PenPot Plugin:
   - Executes: penpot.createRectangle()
   - Sets properties
   - Returns shape ID and state
   
6. MCP Server → Designer:
   {
     "success": true,
     "element_id": "shape-abc123",
     "message": "Created primary CTA button",
     "preview_url": "http://192.168.1.205:9001/preview/abc123"
   }
   
7. Engineer (Linux) observes same change:
   "I can see the button. The size looks good for desktop but we 
    should add a mobile variant at 160x40."
```

## Component Details

### 1. MCP Server (FastAPI/Python)

**Purpose:** Bridge between Claude agents and PenPot

**Location:** `/home/sean/design-tool/mcp-server/`

**Port:** 3000

**Technology Stack:**
- Python 3.12.3
- FastAPI (async HTTP framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- Requests (HTTP client to PenPot)

**Key Features:**
- RESTful API for Claude agents
- Natural language → PenPot command translation
- Project/brand configuration management
- Design state caching
- Multi-agent coordination
- Error handling and validation

**Endpoints:**
```
POST   /design/create       - Create new design elements
POST   /design/modify       - Modify existing elements
GET    /design/state        - Get current design state
POST   /design/feedback     - Add feedback/comments
GET    /design/preview      - Get design preview URL
POST   /project/config      - Set project configuration
GET    /health              - Health check
```

**Configuration:**
```json
{
  "penpot": {
    "url": "http://localhost:9001",
    "plugin_endpoint": "/plugin/api",
    "admin_account": "mcp-server@compel.ai"
  },
  "projects": {
    "compel-english": {
      "brand_colors": {
        "primary": "#FF5733",
        "secondary": "#2e3434"
      },
      "typography": {
        "heading": "Inter",
        "body": "Open Sans"
      }
    }
  },
  "server": {
    "host": "0.0.0.0",
    "port": 3000
  }
}
```

### 2. PenPot Plugin (JavaScript)

**Purpose:** Execute PenPot operations from MCP commands

**Location:** TBD (PenPot plugin directory)

**Technology Stack:**
- JavaScript (ES6+)
- PenPot Plugin API
- HTTP server (for receiving commands)

**Key Features:**
- Exposes HTTP endpoints for MCP server
- Executes PenPot Plugin API operations
- Shape creation and manipulation
- State capture and reporting
- Screenshot generation (if supported)

**PenPot Plugin API Operations:**
```javascript
// Shape Creation
penpot.createRectangle()
penpot.createEllipse()
penpot.createText()
penpot.createBoard()
penpot.createPath()

// Shape Manipulation
shape.name = "..."
shape.fills = [...]
shape.strokes = [...]
shape.borderRadius = 8
shape.resize(width, height)

// Layout
board.addFlexLayout()
board.addGridLayout()
board.appendChild(shape)

// State
penpot.currentPage
penpot.selection
penpot.root
```

**Plugin Manifest:**
```json
{
  "name": "AI Design Bridge",
  "description": "Enables Claude AI agents to design in PenPot",
  "code": "plugin.js",
  "icon": "icon.png",
  "permissions": [
    "content:read",
    "content:write",
    "library:read",
    "library:write"
  ]
}
```

### 3. MCP Tool Configuration

**Purpose:** Connect Claude agents to MCP server

**Designer (Windows - Claude Desktop):**
```json
{
  "mcpServers": {
    "penpot-design": {
      "command": "node",
      "args": [
        "/path/to/mcp-client.js"
      ],
      "env": {
        "MCP_SERVER_URL": "http://192.168.1.205:3000"
      }
    }
  }
}
```

**Engineer (Linux - Claude Code):**
```json
{
  "mcpServers": {
    "penpot-design": {
      "command": "python",
      "args": [
        "-m", "mcp_client"
      ],
      "env": {
        "MCP_SERVER_URL": "http://localhost:3000"
      }
    }
  }
}
```

## Agent Collaboration Patterns

### Pattern 1: Sequential Creation

```
Designer: "Create hero section with 3 columns"
  → Creates board and column layout
  
Engineer: "I see the layout. Add content placeholders to each column"
  → Adds text boxes and image frames
  
Designer: "Style the text with brand typography"
  → Applies fonts and colors
```

### Pattern 2: Review and Modify

```
Designer: "Create mobile nav menu"
  → Creates hamburger icon and slide-out menu
  
Engineer: "The menu should be 280px wide for thumb reach, not 320px"
  → Resizes menu width
  
Designer: "Good catch, adjusting"
  → Updates width
```

### Pattern 3: Parallel Work

```
Designer: "Working on hero section"
  → Creates elements in hero board
  
Engineer: "Working on footer section" 
  → Creates elements in footer board
  
(Both work simultaneously on different boards)
```

## Technical Decisions

### Why HTTP MCP Server (Not SSH)?

**Problem:** Windows → Linux SSH MCP tools had authentication issues

**Solution:** HTTP-based MCP server accessible on local network
- Designer uses: http://192.168.1.205:3000
- Engineer uses: http://localhost:3000
- No SSH complexity
- Standard HTTP error handling
- Easy to debug with curl/Postman

### Why FastAPI (Not Flask)?

**Reasons:**
1. Async support (better for I/O-bound operations)
2. Auto-generated OpenAPI docs
3. Pydantic validation (type safety)
4. Modern Python (3.7+) best practices
5. Better performance for concurrent requests
6. Built-in WebSocket support (future enhancement)

### Why Single MCP Server (Not Direct Plugin Access)?

**Reasons:**
1. Centralized coordination (both agents talk to one server)
2. Natural language translation layer
3. Project configuration management
4. Easier to add features (brand guidelines, templates)
5. Caching and optimization
6. Agent activity logging

### Design State Management

**Challenge:** How do both agents see the same current state?

**Solution:** 
1. PenPot is source of truth (stores all design data)
2. MCP server queries PenPot for current state
3. Agents can request state at any time
4. No local caching needed (PenPot API is fast)

**State Query Flow:**
```
Agent: "What's the current state of the hero section?"
  → GET /design/state?board=hero-section
  → MCP server queries PenPot plugin
  → Plugin reads penpot.currentPage.children
  → Returns structured data to agent
```

## Network Security

### Firewall Configuration

**Required Rule:**
```bash
sudo ufw allow 3000/tcp comment "MCP Server"
```

**Justification:**
- Port 3000 needed for Designer (Windows) to access MCP server
- Engineer uses localhost (no firewall needed)
- Local network only (192.168.1.x)
- No external exposure

### Authentication

**Phase 1 (MVP):** No authentication
- Local network only
- Trusted agents only
- Focus on functionality

**Phase 2 (Future):** API Key authentication
```
Authorization: Bearer sk_penpot_design_key_abc123
```

**Phase 3 (Production):** JWT tokens
- Time-limited tokens
- Agent-specific permissions
- Audit logging

## Error Handling

### Error Flow

```
Agent → MCP Server → PenPot Plugin → PenPot Server
         ↓              ↓              ↓
      Error          Error          Error
         ↓              ↓              ↓
      Catch          Catch          Catch
         ↓              ↓              ↓
      Format         Format         Format
         ↓              ↓              ↓
      Return ← Return ← Return
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "INVALID_DIMENSIONS",
    "message": "Width must be positive number",
    "details": {
      "received": -100,
      "expected": "> 0"
    },
    "suggestion": "Try: width: 200, height: 50"
  }
}
```

### Error Categories

1. **Validation Errors** (400)
   - Invalid parameters
   - Missing required fields
   - Type mismatches

2. **PenPot Errors** (502)
   - Plugin execution failed
   - PenPot API returned error
   - Connection to PenPot lost

3. **Server Errors** (500)
   - Unexpected exceptions
   - Configuration errors
   - Resource exhaustion

## Performance Considerations

### Response Times (Target)

- Simple operations (create shape): < 200ms
- Complex operations (create board with layout): < 1s
- State queries: < 100ms
- Preview generation: < 2s

### Optimization Strategies

1. **Connection Pooling**: Reuse HTTP connections to PenPot
2. **Async Operations**: Don't block on I/O
3. **Parallel Execution**: Create multiple shapes simultaneously
4. **Minimal Data Transfer**: Only send changed properties
5. **Smart Defaults**: Reduce parameter verbosity

## Deployment

### Development Setup

```bash
# MCP Server
cd /home/sean/design-tool/mcp-server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 3000

# PenPot Plugin
# (Install via PenPot UI - see PLUGIN-SPEC.md)
```

### Production Setup (Docker)

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build: ./mcp-server
    ports:
      - "3000:3000"
    environment:
      - PENPOT_URL=http://penpot-penpot-frontend-1:8080
    networks:
      - penpot
    restart: unless-stopped

networks:
  penpot:
    external: true
```

### Monitoring

**Health Checks:**
```bash
# MCP Server
curl http://localhost:3000/health

# PenPot
curl http://localhost:9001

# End-to-End
curl -X POST http://localhost:3000/design/create \
  -H "Content-Type: application/json" \
  -d '{"action":"test"}'
```

**Logs:**
```bash
# MCP Server logs
tail -f /home/sean/design-tool/mcp-server/logs/server.log

# Docker logs
docker-compose -f /home/sean/penpot/docker-compose.yml logs -f

# System logs
journalctl -u mcp-server -f
```

## Future Enhancements

### Phase 2 Features

1. **Design Templates**
   - Pre-built layouts for common patterns
   - Brand-specific component library
   - One-command template instantiation

2. **Screenshot Generation**
   - Automatic preview images
   - Shareable design links
   - Email notifications with preview

3. **Version Control**
   - Design history tracking
   - Rollback capability
   - Branch/merge for designs

4. **Mattermost Integration**
   - Post design updates to chat
   - Screenshot attachments
   - @mention notifications

5. **AI Design Suggestions**
   - "This button is too small for mobile"
   - "Color contrast fails WCAG AA"
   - "Similar to component X in library"

### Phase 3 Features

1. **Real-Time Sync**
   - WebSocket connections
   - Live cursor positions
   - Instant updates

2. **Advanced Collaboration**
   - Design locks (prevent conflicts)
   - Comment threads on elements
   - Approval workflows

3. **Multi-Project Support**
   - Project templates
   - Cross-project components
   - Team libraries

## Success Criteria

### MVP Success (Phase 1)

- ✅ Designer (Windows) can create shapes in PenPot
- ✅ Engineer (Linux) can see and modify same shapes
- ✅ Both agents can query design state
- ✅ Natural language commands work (90%+ success rate)
- ✅ Response times under 1 second
- ✅ Zero downtime for PenPot during operation

### Production Success (Phase 2)

- ✅ Used for real Compel English designs
- ✅ Reduces design-to-implementation time by 50%+
- ✅ Both agents actively collaborate on projects
- ✅ Sean approves designs created this way
- ✅ System runs reliably for 30 days+

## Risks and Mitigations

### Risk: PenPot Plugin API Limitations

**Impact:** High (could block entire project)

**Mitigation:**
- Thoroughly review PenPot plugin docs before implementation
- Start with simple operations (create rectangle)
- Build incrementally, test frequently
- Fallback: If plugin API insufficient, use PenPot's REST API

### Risk: Network Connectivity Issues

**Impact:** Medium (Designer can't access MCP server)

**Mitigation:**
- Test Windows → Linux connectivity early
- Document firewall requirements
- Provide troubleshooting guide
- Fallback: Engineer can relay commands manually

### Risk: Performance Degradation

**Impact:** Low (slower but functional)

**Mitigation:**
- Profile operations during development
- Set performance budgets
- Optimize bottlenecks
- Fallback: Async operations, user sees "working..."

## Glossary

**MCP (Model Context Protocol):** Standard for Claude to interact with external tools

**PenPot Plugin API:** JavaScript API for creating/modifying designs in PenPot

**FastAPI:** Modern Python web framework with async support

**Agent:** A Claude instance (Designer or Engineer)

**Board:** PenPot's term for an artboard/canvas

**Shape:** Any design element (rectangle, text, etc.)

**Natural Language Command:** Conversational instruction from agent

**State:** Current snapshot of design elements and properties

---

**Document Status:** ✅ Complete  
**Next Steps:** Implement MCP-SERVER-SPEC.md and PLUGIN-SPEC.md  
**Review Required:** After implementation begins
