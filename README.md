# Personal Team Management MCP Server

A **Model Context Protocol (MCP) server** that helps managers track their team members, notes, goals, and reminders using **human-readable markdown files**. Works with Claude AI to provide natural language team management.

## What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) allows AI assistants like Claude to connect to external tools and data sources. This server gives Claude the ability to manage your team data through simple conversational commands.

## ✨ Features

- **👥 Staff Management** - Track team members with roles, departments, and contact info
- **📝 Smart Notes** - Add categorized notes with timestamps and context
- **🎯 Goal Tracking** - Set and monitor progress on team member goals  
- **⏰ Reminders** - Create priority-based reminders for management tasks
- **🗣️ Meeting Processing** - Extract action items from call transcripts
- **🧠 AI Advice** - Get management suggestions based on team data
- **📁 Human-Readable Storage** - All data stored as markdown files you can edit directly

## 🚀 Quick Start

### 1. Deploy with Docker

```bash
# Clone and start
git clone <this-repo> team-management
cd team-management
docker-compose up -d

# Verify it's running
docker-compose ps
```

### 2. Connect to Claude

Add this to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux:** `~/.config/claude-desktop/config.json`

```json
{
  "mcpServers": {
    "team-management": {
      "command": "docker",
      "args": ["exec", "-i", "team-management-mcp", "python", "-m", "src.server"],
      "cwd": "/path/to/your/team-management"
    }
  }
}
```

**Important:** Replace `/path/to/your/team-management` with the actual path to your cloned directory.

### 3. Restart Claude Desktop

Close and reopen Claude Desktop. You should see the team management tools available.

## 💬 How to Use with Claude

Once connected, you can manage your team through natural conversation with Claude:

### Adding Team Members
```
"Add a new team member: John Smith, email john@company.com, 
role Senior Developer, department Engineering, reports to Sarah Johnson"
```

### Taking Notes
```
"Add a note for John Smith: Excellent performance on the API project. 
Delivered 2 weeks early and helped mentor junior developers. 
Category this as performance feedback."
```

### Setting Goals
```
"Set a goal for John Smith: Complete AWS certification by end of Q2. 
This will help with our cloud migration project."
```

### Creating Reminders
```
"Remind me to schedule John's performance review in 2 weeks. 
Mark this as high priority."
```

### Getting Insights
```
"Give me management advice for John Smith based on his recent notes and goals."
```

### Viewing Team Data
```
"Show me all my team members"
"What are John Smith's current goals?"
"List all my pending reminders"
```

## 📁 Data Structure

Your team data is stored as readable markdown files in the `data/` directory:

```
data/
├── staff/
│   ├── john-smith.md          # Individual staff profiles
│   ├── sarah-johnson.md       # Goals, notes, achievements
│   └── alex-wong.md           # Human-readable format
├── reminders.md               # Centralized task management  
└── transcripts/               # Processed meeting notes
    ├── 2024-01-15-team-standup.md
    └── 2024-01-20-john-1on1.md
```

### Example Staff File (`data/staff/john-smith.md`)

```markdown
---
id: "550e8400-e29b-41d4-a716-446655440000"
name: "John Smith"
email: "john@company.com"
role: "Senior Developer"
department: "Engineering"
manager: "Sarah Johnson"
created_at: "2024-01-15T10:00:00"
updated_at: "2024-01-20T15:30:00"
---

# John Smith

## Overview
- **Role:** Senior Developer
- **Department:** Engineering  
- **Email:** john@company.com
- **Manager:** Sarah Johnson

## Current Goals
- Complete AWS Solutions Architect certification by Q2 2024
- Mentor 2 junior developers on best practices

## Notes
- Excellent performance on API project *(performance, 2024-01-15)*
- Interested in cloud architecture training *(development, one_on_one, 2024-01-20)*
- Led successful code review process improvements *(leadership, 2024-01-18)*

## Achievements
- Delivered API project 2 weeks early
- Mentored 3 junior developers
- Reduced deployment time by 40%

---
*Last updated: 2024-01-20 15:30*
```

## 🛠️ Installation Options

### Docker (Recommended)

**Prerequisites:** Docker and Docker Compose

```bash
git clone <repo-url> team-management
cd team-management
docker-compose up -d
```

### Local Python Installation

**Prerequisites:** Python 3.11+

```bash
# Install dependencies
pip install -e .

# Run the server
python -m src.server
```

**Local MCP Config:**
```json
{
  "mcpServers": {
    "team-management": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/team-management"
    }
  }
}
```

## 🔧 Management & Maintenance

### View Your Data
```bash
# Check generated files
ls -la data/staff/
cat data/reminders.md

# Watch for changes
watch -n 5 "ls -la data/staff/"
```

### Backup Your Data
```bash
# Simple backup
cp -r data/ backup-$(date +%Y%m%d)/

# Git-based backup (recommended)
cd data/
git init
git add .
git commit -m "Team data backup $(date)"
```

### Container Management
```bash
# Check status
docker-compose ps

# View logs  
docker-compose logs -f team-management

# Restart
docker-compose restart

# Update
docker-compose down
docker-compose pull
docker-compose up -d
```

## 🔒 Security & Privacy

- **Local data storage** - All team information stays on your system
- **No external connections** - Data never leaves your infrastructure
- **Human-readable files** - Easy to audit and backup
- **Git-friendly** - Version control your team data history
- **Encrypted backups** - Standard tools work with the markdown files

## 🎯 Use Cases

### For Engineering Managers
- Track team member skills and career progression
- Set and monitor quarterly goals
- Keep detailed 1:1 meeting notes
- Manage performance review preparation

### For HR Teams  
- Maintain comprehensive employee profiles
- Track goal completion across departments
- Generate development plan reports
- Coordinate cross-team initiatives

### For Small Business Owners
- Simple team member database
- Task and reminder management
- Employee development tracking
- Meeting notes and action items

## 🔧 Troubleshooting

### MCP Connection Issues
1. **Check Docker container:** `docker-compose ps`
2. **Verify Claude config:** Path must be absolute, not relative
3. **Restart Claude Desktop:** Close completely and reopen
4. **Check logs:** `docker-compose logs team-management`

### Data Issues
```bash
# Reset data (caution: deletes everything)
rm -rf data/*
docker-compose restart

# Fix permissions
sudo chown -R $USER:$USER data/
```

### Common Problems
- **"No tools available"** → Check MCP config path and restart Claude
- **Permission errors** → Run `export UID=$(id -u) GID=$(id -g)` before docker-compose
- **Files not updating** → Check container logs for errors

## 📚 Advanced Usage

### Bulk Operations
```
"Import these team members: Alice (engineer), Bob (designer), Carol (manager)"
"Set the same goal for all engineers: Complete security training by March"
"Add performance review reminders for my entire team in 2 weeks"
```

### Meeting Transcripts
```
"Process this transcript from today's standup: [paste transcript]"
"Extract action items from yesterday's planning meeting"
```

### Reporting
```
"Generate a summary of all team goals and their current status"
"What are the main concerns noted for my team members?"
"Show me all high-priority reminders"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with your local Claude setup
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues:** Open a GitHub issue
- **Documentation:** Check this README and DEPLOYMENT.md
- **MCP Protocol:** https://modelcontextprotocol.io/

---

**Ready to get started?** Deploy with Docker and start managing your team with Claude! 🚀