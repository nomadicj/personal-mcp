# Team Management Platform - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- 2GB+ available disk space

### Deploy in 3 Commands
```bash
git clone <this-repo> team-management
cd team-management
docker-compose up -d
```

## 🐳 Docker Deployment

### Production Deployment
```bash
# 1. Download/clone the project
git clone <repo-url> team-management
cd team-management

# 2. Set user permissions (important for file access)
export UID=$(id -u) GID=$(id -g)

# 3. Start the platform
docker-compose up -d

# 4. Verify it's running
docker-compose ps
docker-compose logs team-management
```

### Development Deployment
```bash
# Start with logs visible
docker-compose up

# Or start in background
docker-compose up -d

# View logs
docker-compose logs -f team-management

# Stop
docker-compose down
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:
```bash
# MCP Server Configuration
MCP_SERVER_NAME=team-management-platform
LOG_LEVEL=INFO

# Container Resources
MEMORY_LIMIT=256M
CPU_LIMIT=0.5
```

### Data Persistence
Your team data is stored in `./data/` directory:
```
data/
├── staff/           # Individual staff markdown files
├── reminders.md     # Centralized task management
└── transcripts/     # Meeting transcripts
```

**Backup Strategy:**
```bash
# Simple backup
cp -r data/ backup-$(date +%Y%m%d)/

# Git-based backup (recommended)
cd data/
git init
git add .
git commit -m "Team data backup $(date)"
```

## 🔌 Claude Integration

### For Claude Desktop
Add to `~/.config/claude-desktop/config.json`:
```json
{
  "mcpServers": {
    "team-management": {
      "command": "docker",
      "args": ["exec", "-i", "team-management-mcp", "python", "-m", "src.server"],
      "cwd": "/path/to/team-management"
    }
  }
}
```

### For Claude Code
Add the same configuration to your Claude Code MCP settings.

## 📊 Usage Examples

See the main README.md for detailed usage examples and natural language commands you can use with Claude.

### View Generated Files
```bash
# Check staff files
ls -la data/staff/
cat data/staff/john-doe.md

# Check reminders
cat data/reminders.md

# Monitor in real-time
watch -n 5 "ls -la data/staff/"
```

## 🔍 Monitoring & Maintenance

### Health Checks
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs team-management

# Container health
docker inspect team-management-mcp | grep Health -A 10
```

### Updates
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Troubleshooting
```bash
# Reset everything (keeps data)
docker-compose down
docker-compose up --build -d

# Complete reset (DELETES DATA)
docker-compose down -v
rm -rf data/
docker-compose up -d
```

## 🔒 Security Considerations

### Data Protection
- Data stored locally in `./data/` directory
- No external network connections required
- All team data stays on your infrastructure

### Access Control
- Container runs as non-root user
- Read-only configuration mounts
- Resource limits prevent resource exhaustion

### Backup Security
```bash
# Encrypt backups
tar czf - data/ | gpg -c > backup-$(date +%Y%m%d).tar.gz.gpg

# Decrypt backup
gpg -d backup-20240526.tar.gz.gpg | tar xzf -
```

## 📈 Scaling

### Single Machine
- Handles 100+ staff members easily
- Memory usage: ~128MB baseline + ~1MB per 50 staff
- CPU usage: Very low (event-driven)

### Multiple Teams
Deploy separate instances:
```bash
# Team A
cd team-a/
docker-compose -p team-a up -d

# Team B  
cd team-b/
docker-compose -p team-b up -d
```

### Production Hardening
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Set resource limits
echo "deploy:
  resources:
    limits:
      memory: 512M
      cpus: '1.0'" >> docker-compose.override.yml
```

## 🔧 Customization

### Add Custom Tools
1. Edit `src/server.py`
2. Add new MCP tools
3. Rebuild container: `docker-compose build`

### Custom Data Fields
1. Edit `src/models.py`
2. Update `src/markdown_storage.py`
3. Rebuild and restart

### Branding
1. Edit `src/server.py` - change server name
2. Update `docker-compose.yml` - change container names
3. Customize markdown templates in storage.py

## 📞 Support

### Common Issues
1. **Port conflicts**: Change port in docker-compose.yml
2. **Permission errors**: Check `data/` directory permissions
3. **Memory issues**: Increase Docker memory limits
4. **MCP not connecting**: Verify container is running

### Logs Location
- Container logs: `docker-compose logs team-management`
- Application logs: `./logs/` (if mounted)
- Data files: `./data/`

### Getting Help
1. Check container health: `docker-compose ps`
2. Review logs: `docker-compose logs`
3. Validate data files: `ls -la data/staff/`
4. Test MCP connection: Try basic Claude commands

---

**Next Steps:**
1. Deploy the platform
2. Add your first staff member
3. Start using Claude to manage your team!

*For advanced configuration, see ADVANCED.md*