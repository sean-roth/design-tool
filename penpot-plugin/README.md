# AI Design Bridge - PenPot Plugin

JavaScript plugin that enables Claude AI agents to create and modify designs in PenPot through the MCP server.

## Quick Start

### Build Plugin

```bash
cd /home/sean/design-tool/penpot-plugin
npm run build
```

### Serve for Development

```bash
npm run dev
```

This starts a development server on http://localhost:4400

### Install in PenPot

1. Open PenPot at http://192.168.1.205:9001
2. Press Ctrl+Alt+P (or ⌘+Alt+P on Mac) to open Plugin Manager
3. Enter manifest URL: `http://localhost:4400/manifest.json`
4. PenPot will load and activate the plugin

## Plugin Operations

The plugin supports these operations via the MCP server:

- `createRectangle` - Create rectangle shapes
- `createEllipse` - Create ellipse/circle shapes
- `createText` - Create text elements
- `createBoard` - Create artboards/frames
- `modifyElement` - Modify existing elements
- `getState` - Query current design state

## Testing

Use the built-in UI to test operations:
- Click "Create Button" to test rectangle creation
- Click "Create Text" to test text creation
- Click "Get Design State" to see all elements

## Integration with MCP Server

The plugin communicates with the MCP server at http://localhost:3000

Flow:
1. Claude agent sends command to MCP server
2. MCP server translates to PenPot operation
3. MCP server sends command to plugin via UI
4. Plugin executes using PenPot API
5. Plugin returns result to MCP server
6. MCP server returns to Claude agent

## Files

- `plugin.ts` - Main plugin code (TypeScript)
- `plugin.js` - Compiled JavaScript (created by build)
- `index.html` - Plugin UI for testing
- `manifest.json` - Plugin metadata
- `icon.png` - Plugin icon (56x56px)
