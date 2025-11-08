# PenPot Plugin Implementation Specification

**Component:** PenPot Plugin (JavaScript)  
**Version:** 1.0  
**Date:** 2025-11-08  
**Author:** Designer (Claude Desktop)  
**For:** Engineer (Claude Code)

---

## Overview

This document provides complete implementation instructions for the PenPot Plugin - the component that actually executes design operations inside PenPot. The plugin exposes an HTTP-like interface that the MCP Server calls to perform operations.

**Important:** PenPot plugins run inside the PenPot application and use the PenPot Plugin API. Review the official documentation first: https://help.penpot.app/plugins/

## Implementation Checklist

- [ ] Research PenPot plugin system
- [ ] Create plugin project structure
- [ ] Implement manifest.json
- [ ] Create main plugin.ts file
- [ ] Implement shape creation functions
- [ ] Implement shape modification functions
- [ ] Implement state query functions
- [ ] Create message handler for MCP commands
- [ ] Build and test plugin
- [ ] Deploy to PenPot

## Prerequisites

From audit and documentation review:
- PenPot running on port 9001 ✅
- Node.js 20.19.5 installed ✅
- npm 10.9.2 installed ✅
- Plugin documentation available ✅

## Understanding PenPot Plugins

### Plugin Architecture

```
┌─────────────────────────────────────┐
│     PenPot Application (UI)         │
│                                      │
│  ┌────────────────────────────────┐│
│  │  Plugin (runs in iframe)       ││
│  │                                 ││
│  │  ┌──────────────────────────┐ ││
│  │  │   plugin.ts              │ ││
│  │  │   (Your code)            │ ││
│  │  │                          │ ││
│  │  │   Uses:                  │ ││
│  │  │   - penpot.createRect()  │ ││
│  │  │   - penpot.createText()  │ ││
│  │  │   - penpot.selection     │ ││
│  │  └──────────────────────────┘ ││
│  │                                 ││
│  │  ┌──────────────────────────┐ ││
│  │  │   UI (optional)          │ ││
│  │  │   HTML/CSS/JS            │ ││
│  │  └──────────────────────────┘ ││
│  └────────────────────────────────┘│
└─────────────────────────────────────┘
```

### How Plugins Communicate

**Standard Plugin Pattern:**
```javascript
// Plugin sends message to UI
penpot.ui.sendMessage({ type: "data", payload: {...} });

// UI receives message
window.addEventListener("message", (event) => {
  console.log(event.data);
});
```

**Our Custom Pattern (MCP Integration):**
The plugin will need to expose a way for the MCP server to send commands. Since plugins run in an iframe, we'll use PenPot's messaging system + a proxy approach.

## Project Structure

```
/home/sean/design-tool/penpot-plugin/
├── manifest.json              # Plugin metadata
├── plugin.ts                  # Main plugin code (TypeScript)
├── plugin.js                  # Compiled JavaScript
├── index.html                 # Optional UI
├── styles.css                 # Optional styles
├── icon.png                   # Plugin icon (56x56px)
├── package.json               # npm dependencies
├── tsconfig.json              # TypeScript config
├── vite.config.ts             # Build configuration
└── README.md                  # Installation guide
```

## Step 1: Create Plugin Project

### Initialize Project

```bash
cd /home/sean/design-tool
mkdir -p penpot-plugin
cd penpot-plugin

# Initialize npm
npm init -y

# Install dependencies
npm install --save-dev \
  typescript \
  @penpot/plugin-types \
  vite \
  @types/node
```

### Create package.json

```json
{
  "name": "ai-design-bridge",
  "version": "1.0.0",
  "description": "Enables Claude AI agents to design in PenPot",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "@penpot/plugin-types": "latest",
    "@types/node": "^20.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

### Create tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM"],
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "typeRoots": ["./node_modules/@types", "./node_modules/@penpot"],
    "types": ["plugin-types"]
  },
  "include": ["plugin.ts"]
}
```

### Create vite.config.ts

```typescript
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        plugin: 'plugin.ts',
        index: './index.html',
      },
      output: {
        entryFileNames: '[name].js',
      },
    },
  },
  preview: {
    port: 4400,
  },
});
```

## Step 2: Create Manifest

### Create manifest.json

```json
{
  "name": "AI Design Bridge",
  "description": "Enables Claude AI agents to collaborate on PenPot designs through natural conversation",
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

**Permissions Explained:**
- `content:read`: Read shapes, pages, design elements
- `content:write`: Create and modify design elements
- `library:read`: Access component libraries
- `library:write`: Create reusable components

## Step 3: Create Plugin Icon

### Create icon.png

```bash
# Create a simple 56x56 icon
# You can use ImageMagick or any image editor
# For now, create a placeholder
convert -size 56x56 xc:#FF5733 -gravity center \
  -pointsize 30 -fill white -annotate +0+0 "AI" \
  icon.png
```

Or download/create a proper icon and save as `icon.png` (56x56px).

## Step 4: Main Plugin Implementation

### Create plugin.ts

```typescript
/// <reference types="@penpot/plugin-types" />

/**
 * AI Design Bridge Plugin for PenPot
 * 
 * This plugin enables Claude AI agents to create and modify designs
 * in PenPot through natural conversation.
 */

console.log("AI Design Bridge Plugin initializing...");

// ============================================================================
// COMMAND INTERFACE
// ============================================================================

interface Command {
  operation: string;
  properties?: any;
  element_id?: string;
  query?: any;
}

interface CommandResult {
  success: boolean;
  data?: any;
  error?: string;
}

// ============================================================================
// SHAPE CREATION OPERATIONS
// ============================================================================

function createRectangle(properties: any): CommandResult {
  try {
    const shape = penpot.createRectangle();
    
    // Set properties
    if (properties.name) {
      shape.name = properties.name;
    }
    
    if (properties.width && properties.height) {
      shape.resize(properties.width, properties.height);
    }
    
    if (properties.fills) {
      shape.fills = properties.fills;
    }
    
    if (properties.strokes) {
      shape.strokes = properties.strokes;
    }
    
    if (properties.borderRadius !== undefined) {
      shape.borderRadius = properties.borderRadius;
    }
    
    console.log(`Created rectangle: ${shape.name} (${shape.id})`);
    
    return {
      success: true,
      data: {
        id: shape.id,
        name: shape.name,
        type: 'rectangle'
      }
    };
  } catch (error: any) {
    console.error("Failed to create rectangle:", error);
    return {
      success: false,
      error: error.message
    };
  }
}

function createEllipse(properties: any): CommandResult {
  try {
    const shape = penpot.createEllipse();
    
    if (properties.name) {
      shape.name = properties.name;
    }
    
    if (properties.width && properties.height) {
      shape.resize(properties.width, properties.height);
    }
    
    if (properties.fills) {
      shape.fills = properties.fills;
    }
    
    if (properties.strokes) {
      shape.strokes = properties.strokes;
    }
    
    console.log(`Created ellipse: ${shape.name} (${shape.id})`);
    
    return {
      success: true,
      data: {
        id: shape.id,
        name: shape.name,
        type: 'ellipse'
      }
    };
  } catch (error: any) {
    console.error("Failed to create ellipse:", error);
    return {
      success: false,
      error: error.message
    };
  }
}

function createText(properties: any): CommandResult {
  try {
    const shape = penpot.createText();
    
    if (properties.name) {
      shape.name = properties.name;
    }
    
    if (properties.text) {
      shape.characters = properties.text;
    }
    
    if (properties.fontFamily) {
      // Note: Font must be loaded first
      // For now, we'll use default font
      console.log(`Font ${properties.fontFamily} requested`);
    }
    
    if (properties.fontSize) {
      shape.fontSize = properties.fontSize;
    }
    
    if (properties.fills) {
      shape.fills = properties.fills;
    }
    
    console.log(`Created text: ${shape.name} (${shape.id})`);
    
    return {
      success: true,
      data: {
        id: shape.id,
        name: shape.name,
        type: 'text',
        text: shape.characters
      }
    };
  } catch (error: any) {
    console.error("Failed to create text:", error);
    return {
      success: false,
      error: error.message
    };
  }
}

function createBoard(properties: any): CommandResult {
  try {
    const board = penpot.createBoard();
    
    if (properties.name) {
      board.name = properties.name;
    }
    
    if (properties.width && properties.height) {
      board.resize(properties.width, properties.height);
    }
    
    if (properties.fills) {
      board.fills = properties.fills;
    }
    
    console.log(`Created board: ${board.name} (${board.id})`);
    
    return {
      success: true,
      data: {
        id: board.id,
        name: board.name,
        type: 'board'
      }
    };
  } catch (error: any) {
    console.error("Failed to create board:", error);
    return {
      success: false,
      error: error.message
    };
  }
}

// ============================================================================
// SHAPE MODIFICATION OPERATIONS
// ============================================================================

function modifyElement(elementId: string, properties: any): CommandResult {
  try {
    // Find element by ID
    // Note: This is a simplified version
    // In practice, you'd need to traverse the tree
    const element = findElementById(elementId);
    
    if (!element) {
      return {
        success: false,
        error: `Element not found: ${elementId}`
      };
    }
    
    // Apply properties
    if (properties.name) {
      element.name = properties.name;
    }
    
    if (properties.width && properties.height) {
      element.resize(properties.width, properties.height);
    }
    
    if (properties.fills) {
      element.fills = properties.fills;
    }
    
    if (properties.strokes) {
      element.strokes = properties.strokes;
    }
    
    if (properties.borderRadius !== undefined && 'borderRadius' in element) {
      (element as any).borderRadius = properties.borderRadius;
    }
    
    console.log(`Modified element: ${element.name} (${element.id})`);
    
    return {
      success: true,
      data: {
        id: element.id,
        name: element.name
      }
    };
  } catch (error: any) {
    console.error("Failed to modify element:", error);
    return {
      success: false,
      error: error.message
    };
  }
}

function findElementById(id: string): any {
  // Helper function to find element by ID
  // This is a simplified version - in practice you'd traverse the full tree
  
  if (!penpot.currentPage) {
    return null;
  }
  
  function traverse(node: any): any {
    if (node.id === id) {
      return node;
    }
    
    if ('children' in node && node.children) {
      for (const child of node.children) {
        const found = traverse(child);
        if (found) return found;
      }
    }
    
    return null;
  }
  
  return traverse(penpot.currentPage);
}

// ============================================================================
// STATE QUERY OPERATIONS
// ============================================================================

function getState(query: any = {}): CommandResult {
  try {
    if (!penpot.currentPage) {
      return {
        success: false,
        error: "No active page"
      };
    }
    
    const elements: any[] = [];
    
    function collectElements(node: any) {
      elements.push({
        id: node.id,
        name: node.name,
        type: node.type,
        x: node.x,
        y: node.y,
        width: node.width,
        height: node.height
      });
      
      if ('children' in node && node.children) {
        for (const child of node.children) {
          collectElements(child);
        }
      }
    }
    
    // Collect all elements from current page
    if (penpot.currentPage.children) {
      for (const child of penpot.currentPage.children) {
        collectElements(child);
      }
    }
    
    console.log(`Retrieved state: ${elements.length} elements`);
    
    return {
      success: true,
      data: {
        elements,
        page: {
          id: penpot.currentPage.id,
          name: penpot.currentPage.name
        }
      }
    };
  } catch (error: any) {
    console.error("Failed to get state:", error);
    return {
      success: false,
      error: error.message
    };
  }
}

// ============================================================================
// COMMAND DISPATCHER
// ============================================================================

function executeCommand(command: Command): CommandResult {
  console.log("Executing command:", command.operation);
  
  switch (command.operation) {
    case 'createRectangle':
      return createRectangle(command.properties || {});
      
    case 'createEllipse':
      return createEllipse(command.properties || {});
      
    case 'createText':
      return createText(command.properties || {});
      
    case 'createBoard':
      return createBoard(command.properties || {});
      
    case 'modifyElement':
      if (!command.element_id) {
        return {
          success: false,
          error: "element_id required for modifyElement"
        };
      }
      return modifyElement(command.element_id, command.properties || {});
      
    case 'getState':
      return getState(command.query || {});
      
    default:
      return {
        success: false,
        error: `Unknown operation: ${command.operation}`
      };
  }
}

// ============================================================================
// MESSAGE HANDLING (MCP SERVER INTEGRATION)
// ============================================================================

// This is where we receive commands from the MCP server
// The mechanism depends on how PenPot plugins can be triggered

// Option 1: Via UI messages (if plugin has UI)
penpot.ui.onMessage<Command>((message) => {
  console.log("Received command via UI:", message);
  
  const result = executeCommand(message);
  
  // Send result back to UI
  penpot.ui.sendMessage({
    type: 'commandResult',
    result
  });
});

// Option 2: Register plugin menu actions
// Note: This allows triggering plugin from PenPot UI
// But not from external MCP server directly
// We'll need to find a way to bridge this gap

// ============================================================================
// PLUGIN INITIALIZATION
// ============================================================================

console.log("AI Design Bridge Plugin loaded successfully");
console.log("Current page:", penpot.currentPage?.name);
console.log("Current file:", penpot.currentFile?.name);

// Test: Create a welcome message
const welcomeText = penpot.createText();
welcomeText.name = "AI Design Bridge Active";
welcomeText.characters = "Ready for AI collaboration!";
welcomeText.fontSize = 24;
welcomeText.fills = [{fillColor: "#FF5733"}];

console.log("Plugin ready for commands");
```

## Step 5: Optional UI (For Testing)

### Create index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Design Bridge</title>
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      padding: 20px;
      margin: 0;
    }
    
    h1 {
      font-size: 18px;
      margin-bottom: 20px;
    }
    
    button {
      padding: 10px 20px;
      margin: 5px;
      border: none;
      background: #FF5733;
      color: white;
      border-radius: 4px;
      cursor: pointer;
    }
    
    button:hover {
      background: #E04623;
    }
    
    #status {
      margin-top: 20px;
      padding: 10px;
      background: #f0f0f0;
      border-radius: 4px;
      font-family: monospace;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <h1>AI Design Bridge</h1>
  
  <div>
    <button onclick="testCreateButton()">Test: Create Button</button>
    <button onclick="testGetState()">Test: Get State</button>
  </div>
  
  <div id="status">Status: Ready</div>
  
  <script>
    function setStatus(message) {
      document.getElementById('status').textContent = message;
    }
    
    function testCreateButton() {
      setStatus('Creating button...');
      
      window.parent.postMessage({
        pluginMessage: {
          operation: 'createRectangle',
          properties: {
            name: 'Test Button',
            width: 200,
            height: 50,
            fills: [{fillColor: '#FF5733'}],
            borderRadius: 8
          }
        }
      }, '*');
    }
    
    function testGetState() {
      setStatus('Getting state...');
      
      window.parent.postMessage({
        pluginMessage: {
          operation: 'getState'
        }
      }, '*');
    }
    
    // Listen for results
    window.addEventListener('message', (event) => {
      if (event.data.type === 'commandResult') {
        setStatus('Result: ' + JSON.stringify(event.data.result, null, 2));
      }
    });
  </script>
</body>
</html>
```

## Step 6: Build Plugin

### Build for Development

```bash
cd /home/sean/design-tool/penpot-plugin
npm run build
```

This creates `plugin.js` in the current directory.

### Serve for Local Testing

```bash
npm run dev
```

This starts a development server on port 4400.

## Step 7: Install Plugin in PenPot

### Manual Installation (Development)

1. **Access PenPot:**
   - Open http://192.168.1.205:9001
   - Login with your account

2. **Open Plugin Manager:**
   - Look for "Plugins" in the menu
   - Or check PenPot documentation for exact location

3. **Add Development Plugin:**
   - Provide manifest URL: `http://localhost:4400/manifest.json`
   - Or use the built files directly (depends on PenPot's plugin system)

**Note:** Exact installation steps depend on PenPot's plugin manager. Check official documentation at https://help.penpot.app/plugins/create-a-plugin/

### Production Installation

Once working, you can serve the plugin from a permanent location:

```bash
# Copy built files to a web-accessible location
cp -r /home/sean/design-tool/penpot-plugin/dist/* /var/www/penpot-plugin/

# Or serve via Python
cd /home/sean/design-tool/penpot-plugin
python3 -m http.server 4400
```

Then install via: `http://192.168.1.205:4400/manifest.json`

## Step 8: Bridge Plugin to MCP Server

### The Challenge

PenPot plugins run in an iframe and can't directly receive HTTP requests from the MCP server. We need a bridge.

### Solution A: Long-Polling via UI

**Concept:** Plugin polls MCP server for commands

```typescript
// Add to plugin.ts
async function pollForCommands() {
  try {
    const response = await fetch('http://localhost:3000/plugin/commands');
    const commands = await response.json();
    
    for (const command of commands) {
      const result = executeCommand(command);
      
      // Send result back to MCP server
      await fetch('http://localhost:3000/plugin/results', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(result)
      });
    }
  } catch (error) {
    console.error('Polling failed:', error);
  }
  
  // Poll every 2 seconds
  setTimeout(pollForCommands, 2000);
}

// Start polling
pollForCommands();
```

### Solution B: PenPot's Built-in API

**Check if PenPot has REST API endpoints we can use instead of the plugin:**

According to the audit, PenPot has `backend-api-doc` flag enabled. The MCP server might be able to call PenPot's REST API directly, bypassing the plugin limitation.

**Next Steps:**
1. Research PenPot's REST API documentation
2. If available, use REST API directly from MCP server
3. Plugin becomes optional (just for testing)

## Step 9: Testing

### Test Plugin Locally

1. **Load plugin in PenPot**
2. **Check browser console** (F12) for plugin logs
3. **Use test UI buttons** to create shapes
4. **Verify shapes appear** in PenPot canvas

### Test MCP Integration

Once plugin is working:

1. **Start MCP server** (port 3000)
2. **Send command to MCP server**:
   ```bash
   curl -X POST http://localhost:3000/design/create \
     -H "Content-Type: application/json" \
     -d '{"action":"create","natural_language":"create a button"}'
   ```
3. **Verify shape appears** in PenPot

## Step 10: Troubleshooting

### Plugin Won't Load

```javascript
// Add debug logging to plugin.ts
console.log("Plugin starting...");
console.log("PenPot available:", typeof penpot !== 'undefined');
console.log("Current page:", penpot?.currentPage?.name);
```

### Check Browser Console

- Open PenPot in browser
- Press F12 to open DevTools
- Check Console tab for errors
- Check Network tab for failed requests

### Plugin Permissions

If operations fail, check that manifest.json has correct permissions:
- `content:write` - Required for creating shapes
- `content:read` - Required for reading state

## Alternative Approach: Use PenPot REST API

**If the plugin approach is too complex**, we can check if PenPot's REST API can do everything we need:

1. **Research PenPot REST API** (backend-api-doc is enabled)
2. **Call API directly from MCP server**
3. **Skip plugin entirely** (simpler architecture)

**Check audit results:** PenPot has `enable-prepl-server` and `backend-api-doc` flags enabled, suggesting there may be API access.

## Success Criteria

- [ ] Plugin loads in PenPot without errors
- [ ] Can create rectangle via plugin
- [ ] Can create text via plugin
- [ ] Can query current state
- [ ] Plugin logs appear in browser console
- [ ] Test UI buttons work
- [ ] MCP server can trigger plugin operations
- [ ] Both Claude agents can see changes

## Next Steps

After plugin is working:

1. **Configure MCP clients** (Claude Desktop + Claude Code)
2. **Test end-to-end workflow**
3. **Optimize based on usage**
4. **Add more operations** as needed

---

**Status:** Ready for Implementation  
**Estimated Time:** 8-12 hours (including research and testing)  
**Dependencies:** PenPot running (✅), MCP Server (in progress)  
**Priority:** High (critical path)

**Critical Research Needed:**
- Exact PenPot plugin installation process
- How to trigger plugins from external sources
- Whether PenPot REST API can replace plugin

---

**Engineer:** Start with simple plugin that creates one shape. Verify it works. Then expand functionality. If plugin approach is blocked by technical limitations, pivot to REST API approach.
