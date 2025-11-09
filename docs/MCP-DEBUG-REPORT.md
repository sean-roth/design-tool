# MCP Server Connection Debug Report

**From:** Designer (Claude Desktop)  
**To:** Engineer (Claude Code)  
**Date:** 2025-11-08  
**Priority:** HIGH - Blocking Issue

---

## Current Status

The MCP server is **almost working** but crashing immediately after receiving the initialize message from Claude Desktop. We're very close - just need to fix the initialize response handler.

## What's Working ✅

1. **SSH Connection:** Claude Desktop successfully connects via SSH to Linux server
2. **Python Execution:** The Python script starts without import errors
3. **Message Reception:** The script receives the MCP initialize message
4. **File Location:** Both `mcp-studio.py` and `mcp-stdio.py` are in the correct location

## What's Broken ❌

**The script exits immediately after receiving the initialize message instead of responding to it.**

---

## Log Analysis

### Connection Flow (From Claude Desktop Logs)

```
[info] Initializing server...
[info] Server started and connected successfully
[info] Message from client: {
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {},
    "clientInfo": {"name": "claude-ai", "version": "0.1.0"}
  },
  "jsonrpc": "2.0",
  "id": 0
}
[info] Server transport closed ← PROBLEM HERE
[info] Server transport closed unexpectedly
[error] Server disconnected
```

### Timeline

1. ✅ **0ms:** SSH connection established
2. ✅ **22ms:** Python script starts
3. ✅ **28ms:** Initialize message sent to script
4. ❌ **52ms:** Script exits/crashes (no response sent)

**Expected:** Script should respond with server capabilities and stay running
**Actual:** Script exits immediately

---

## The Problem

The MCP server is not properly handling the `initialize` method. This is the first message in the MCP protocol handshake, and it's mandatory.

### What Should Happen

```
Client: {"method": "initialize", "id": 0, ...}
  ↓
Server: {
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {...},
    "serverInfo": {...}
  }
}
  ↓
Connection stays open
Server waits for tool calls
```

### What's Actually Happening

```
Client: {"method": "initialize", "id": 0, ...}
  ↓
Server: [exits immediately, no response]
  ↓
Connection closed
Claude Desktop shows error
```

---

## Root Cause Hypotheses

### Hypothesis 1: Missing Initialize Handler (Most Likely)

The script doesn't have a proper handler for the `initialize` method. The MCP SDK requires this to be explicitly implemented.

**Check:** Does `mcp-stdio.py` have something like this?

```python
from mcp.server import Server
import mcp.types as types

server = Server("penpot-design-bridge")

# This is REQUIRED
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    # Tool implementations
    pass

# Must have list_tools
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_design",
            description="Create a design element in PenPot",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "element_type": {"type": "string"}
                }
            }
        )
    ]
```

### Hypothesis 2: Not Running stdio_server (Very Likely)

The script might not be calling `stdio_server()` properly at the end.

**Check:** Does the script end with this?

```python
if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    # This MUST be called and MUST block forever
    asyncio.run(stdio_server(server))
```

**Common mistake:**
```python
# WRONG - this returns immediately
if __name__ == "__main__":
    stdio_server(server)  # Missing asyncio.run!
```

### Hypothesis 3: Exception During Initialize (Possible)

The script might be throwing an exception when processing the initialize message, but we're not seeing it because stderr isn't being captured properly.

---

## Debugging Steps

### Step 1: Run Script Locally (CRITICAL)

**On the Linux server, run this:**

```bash
cd /home/sean/design-tool/mcp-server
source venv/bin/activate

# Run the script directly
python mcp-stdio.py
```

**Expected behavior:**
- Script should NOT exit
- Cursor should just sit there waiting (no prompt)
- Script is listening on stdin

**If script exits immediately:** There's a Python error. Add this to the TOP of the script:

```python
import sys
import traceback

try:
    # ... rest of imports ...
    print("Imports successful", file=sys.stderr, flush=True)
except Exception as e:
    print(f"FATAL ERROR: {e}", file=sys.stderr, flush=True)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
```

### Step 2: Test Initialize Message

**While script is running from Step 1, in another terminal:**

```bash
cd /home/sean/design-tool/mcp-server
source venv/bin/activate

# Send an initialize message
echo '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | python mcp-stdio.py
```

**Expected:** Should print a JSON response with server capabilities
**If nothing prints:** The initialize handler is missing or broken

### Step 3: Check MCP SDK Version

```bash
cd /home/sean/design-tool/mcp-server
source venv/bin/activate
pip list | grep mcp
```

**Required:** Should show `mcp` package installed (latest version)

If missing:
```bash
pip install mcp
```

### Step 4: Add Debug Logging

**Add this to the script (after imports, before server creation):**

```python
import sys
import logging

# Configure logging to stderr (visible in Claude Desktop logs)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

logger.error("=== MCP Server Starting ===")
logger.error(f"Python version: {sys.version}")
logger.error(f"Working directory: {os.getcwd()}")

# ... rest of script ...

logger.error("=== About to start stdio_server ===")
asyncio.run(stdio_server(server))
logger.error("=== stdio_server returned (should never reach here) ===")
```

These `logger.error()` messages will appear in the Claude Desktop logs.

---

## Expected Script Structure

Based on MCP SDK best practices, the script should look like this:

```python
#!/usr/bin/env python3
"""MCP Server for PenPot Design Bridge"""

import sys
import logging
from mcp.server import Server
import mcp.types as types
from mcp.server.stdio import stdio_server

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("penpot-design-bridge")

logger.info("Server instance created")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    logger.info("list_tools called")
    return [
        types.Tool(
            name="create_design",
            description="Create a design element in PenPot",
            inputSchema={
                "type": "object",
                "properties": {
                    "natural_language": {
                        "type": "string",
                        "description": "Natural language description of what to create"
                    }
                },
                "required": ["natural_language"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict
) -> list[types.TextContent]:
    """Handle tool calls."""
    logger.info(f"call_tool: {name} with {arguments}")
    
    if name == "create_design":
        # TODO: Actually call PenPot plugin
        return [
            types.TextContent(
                type="text",
                text=f"Created design element: {arguments.get('natural_language')}"
            )
        ]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main entry point."""
    logger.info("Starting stdio_server...")
    
    # This should block forever
    async with stdio_server(server) as (read_stream, write_stream):
        logger.info("stdio_server started successfully")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    
    logger.info("=== MCP Server Starting ===")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        sys.exit(1)
```

---

## Files to Check

### mcp-stdio.py

**Location:** `/home/sean/design-tool/mcp-server/mcp-stdio.py`

**Must have:**
- Import `from mcp.server.stdio import stdio_server`
- Create `Server("penpot-design-bridge")`
- Define `@server.list_tools()` handler
- Define `@server.call_tool()` handler
- Call `asyncio.run(stdio_server(server))` in main

### requirements.txt

**Location:** `/home/sean/design-tool/mcp-server/requirements.txt`

**Must include:**
```
mcp>=0.1.0
```

---

## Quick Test Commands

Run these on the Linux server to verify setup:

```bash
cd /home/sean/design-tool/mcp-server
source venv/bin/activate

# 1. Check Python version (should be 3.12.3)
python --version

# 2. Check MCP installed
pip show mcp

# 3. Run script (should NOT exit)
python mcp-stdio.py
# Press Ctrl+C to stop

# 4. Check syntax
python -m py_compile mcp-stdio.py

# 5. Check imports work
python -c "from mcp.server import Server; from mcp.server.stdio import stdio_server; print('Imports OK')"
```

---

## Success Criteria

When fixed, you should see this in Claude Desktop logs:

```
[info] Initializing server...
[info] Server started and connected successfully
[info] Message from client: {"method":"initialize",...}
[info] Message from server: {"result":{"protocolVersion":"2025-06-18",...}}
[info] Connection established
```

**Key difference:** Server sends a response and stays connected.

---

## If Still Stuck

### Option 1: Share the Script

Commit `mcp-stdio.py` to the repo so I can review the actual code:

```bash
cd /home/sean/design-tool
git add mcp-server/mcp-stdio.py
git commit -m "WIP: MCP stdio server for debugging"
git push
```

Then I can see exactly what's wrong.

### Option 2: Share Direct Error Output

Run this and paste the output:

```bash
cd /home/sean/design-tool/mcp-server
source venv/bin/activate
python mcp-stdio.py 2>&1 | head -50
```

### Option 3: Use the MCP SDK Example

If the above doesn't work, start from the official MCP SDK example:

```bash
cd /home/sean/design-tool/mcp-server
source venv/bin/activate

# Install MCP with examples
pip install mcp

# Copy the example server
python -c "import mcp.server.stdio as s; print(s.__file__)"
# This shows where the package is installed

# Look at the example in the MCP package directory
```

---

## Next Steps After Fix

Once the connection works:

1. Add actual PenPot plugin integration
2. Implement tool handlers properly
3. Test from Claude Desktop
4. Configure Claude Code on Linux side
5. Test designer/engineer collaboration

---

## Summary for Engineer

**The Problem:** Script receives initialize message but exits without responding.

**Most Likely Cause:** Missing or broken `stdio_server()` call, or missing initialize handler.

**First Debug Step:** Run `python mcp-stdio.py` directly on server - should NOT exit.

**Quick Fix:** Ensure script ends with:
```python
if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(server))
```

**Need Help:** Commit the script or share error output so I can see the exact issue.

We're 95% there - just need this initialize handshake to work!

---

**Status:** Blocking Issue  
**Priority:** High  
**Next Action:** Engineer runs local debug steps and reports findings
