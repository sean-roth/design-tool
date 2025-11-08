# MCP Server - PenPot AI Design Bridge

FastAPI-based server that enables Claude AI agents to create and modify designs in PenPot through natural language commands.

## Quick Start

### Development Mode

```bash
cd /home/sean/design-tool/mcp-server
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

### Production Mode (Docker)

```bash
docker-compose up -d
```

## API Endpoints

- `GET /health` - Health check
- `POST /design/create` - Create design element
- `POST /design/modify` - Modify existing element
- `POST /design/state` - Get current design state
- `GET /docs` - Interactive API documentation

## Testing

```bash
# Health check
curl http://localhost:3000/health

# Create button
curl -X POST http://localhost:3000/design/create \
  -H "Content-Type: application/json" \
  -d '{"action":"create","natural_language":"create a primary button"}'
```

## Configuration

See `.env.example` for environment variables.

Default configuration creates `projects.json` with Compel English brand colors.

## Logs

Development: `logs/server.log`
Docker: `docker-compose logs -f mcp-server`
