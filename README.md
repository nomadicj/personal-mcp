# Team Management MCP Server

A Model Context Protocol (MCP) server for managing your team members, tracking notes, setting goals, and handling reminders.

## Features

- **Staff Management**: Add and track team members with roles, departments, and contact info
- **Notes System**: Keep detailed notes about each team member with categories and tags
- **Goal Tracking**: Set and monitor goals for team members with progress updates
- **Reminders**: Create and manage reminders for staff-related tasks
- **Call Transcript Processing**: Extract action items and insights from meeting transcripts
- **Management Advice**: Get AI-powered suggestions based on staff context

## Installation & Setup

### Option 1: Docker (Recommended)

1. **Quick Start with Docker Compose:**
```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f team-management-mcp

# Stop the container
docker-compose down
```

2. **Using the convenience script:**
```bash
# Build the image
./scripts/run-container.sh build

# Start the container
./scripts/run-container.sh start

# Check status
./scripts/run-container.sh status

# View logs
./scripts/run-container.sh logs

# Stop the container
./scripts/run-container.sh stop
```

3. **Manual Docker commands:**
```bash
# Build image
docker build -t team-management-mcp .

# Run container with data persistence
docker run -d \
  --name team-management-mcp \
  -v $(pwd)/data:/app/data \
  team-management-mcp
```

### Option 2: Local Python Installation

1. Install dependencies:
```bash
pip install -e .
```

2. Run the server:
```bash
python -m src.server
```

## MCP Configuration

### For Docker Setup
Add to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "team-management": {
      "command": "docker",
      "args": ["exec", "-i", "team-management-mcp", "python", "-m", "src.server"],
      "cwd": "/path/to/your/personal-mcp"
    }
  }
}
```

### For Local Python Setup
```json
{
  "mcpServers": {
    "team-management": {
      "command": "python",
      "args": ["/path/to/your/personal-mcp/src/server.py"],
      "cwd": "/path/to/your/personal-mcp"
    }
  }
}
```

## Available Tools

### Staff Management
- `add_staff_member` - Add new team members
- `get_staff_member` - Get details for a specific person
- `list_all_staff` - List all team members

### Notes
- `add_note` - Add notes about team members
- `get_staff_notes` - Retrieve all notes for a person

### Goals
- `add_goal` - Set goals for team members
- `update_goal_progress` - Track progress on goals
- `get_staff_goals` - View all goals for a person

### Reminders
- `add_reminder` - Create reminders for tasks
- `list_reminders` - View pending/completed reminders
- `complete_reminder` - Mark reminders as done

### Advanced Features
- `process_call_transcript` - Extract insights from meeting transcripts
- `get_management_advice` - Get contextual management suggestions

## Data Storage

All data is stored in JSON files in the `data/` directory:
- `staff.json` - Team member profiles
- `notes.json` - All notes
- `goals.json` - Goal tracking
- `reminders.json` - Task reminders
- `transcripts.json` - Processed call transcripts

### Docker Data Persistence
When using Docker, the `data/` directory is mounted as a volume to ensure your team data persists across container restarts. The data files are created automatically when first needed.

## Container Management

### Health Monitoring
The Docker container includes health checks to ensure the MCP server is running properly:
```bash
# Check container health
docker ps

# View detailed health status
docker inspect team-management-mcp | grep -A 10 Health
```

### Resource Usage
The container is configured with reasonable resource limits:
- Memory: 512MB limit, 256MB reserved
- CPU: 0.5 cores limit, 0.25 cores reserved

### Debugging
Use the debug profile to monitor data changes:
```bash
# Start with debug monitoring
docker-compose --profile debug up -d

# View debug logs
docker-compose logs -f mcp-debug
```

## Troubleshooting

### Container Issues
```bash
# Check if container is running
./scripts/run-container.sh status

# View container logs
./scripts/run-container.sh logs

# Restart container
./scripts/run-container.sh stop
./scripts/run-container.sh start

# Clean rebuild
./scripts/run-container.sh clean
./scripts/run-container.sh build
./scripts/run-container.sh start
```

### Data Issues
```bash
# Check data directory
ls -la ./data/

# Backup data
cp -r ./data ./data-backup-$(date +%Y%m%d)

# Reset data (caution: deletes all team data)
rm -rf ./data/*
```