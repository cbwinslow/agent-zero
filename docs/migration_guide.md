# Migration Guide: Upgrading to Multi-Agent Memory System

This guide helps existing Agent Zero users migrate to the new multi-agent memory system.

## Overview

The multi-agent memory system adds:
- Specialized agent profiles for different tasks
- Centralized memory management via MCP server
- Enhanced knowledge base organization
- Memory compression and optimization
- Multi-agent task coordination

## Migration Steps

### Step 1: Backup Your Data

Before migrating, backup your existing data:

```bash
# Backup memories
cp -r memory memory_backup_$(date +%Y%m%d)

# Backup knowledge
cp -r knowledge knowledge_backup_$(date +%Y%m%d)

# Backup agent configurations
cp -r agents agents_backup_$(date +%Y%m%d)

# Backup settings
cp tmp/settings.json tmp/settings_backup_$(date +%Y%m%d).json
```

### Step 2: Update Repository

Pull the latest changes:

```bash
cd agent-zero
git pull origin main
```

### Step 3: Configure Environment

Create or update your `.env` file:

```bash
# Copy example if you don't have .env yet
cp example.env .env

# Edit with your settings
nano .env
```

Add your API keys and enable new features:

```env
# Your existing API keys
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
# or (recommended)
OPENROUTER_API_KEY=sk-or-v1-...

# Enable new features
MULTI_AGENT_ENABLED=true
MEMORY_MCP_ENABLED=true
```

### Step 4: Run Setup Script

The setup script will configure the memory MCP server:

```bash
python setup_memory_mcp.py
```

This will:
- Add memory MCP server to your settings
- Verify agent profiles are installed
- Check all required files

### Step 5: Migrate Existing Data

#### 5.1 Migrate Memories

Your existing memories in the `memory/` directory will continue to work. No action needed.

To organize them into the new structure:

```python
# Optional: Categorize existing memories
from python.helpers.memory import Memory

async def categorize_memories():
    memory = await Memory.get_by_subdir("default")
    
    # Get all memories
    all_docs = memory.db.get_all_docs()
    
    for doc_id, doc in all_docs.items():
        # Update metadata with categories
        if "area" not in doc.metadata:
            # Determine area based on content
            content = doc.page_content.lower()
            
            if "solution" in content or "solved" in content:
                doc.metadata["area"] = "solutions"
            elif "code" in content or "function" in content:
                doc.metadata["area"] = "fragments"
            else:
                doc.metadata["area"] = "main"
            
            # Update document
            await memory.update_documents([doc])
```

#### 5.2 Migrate Knowledge Base

Your existing knowledge in `knowledge/default/` will continue to work.

To organize into specialized areas:

```bash
# Create area directories if they don't exist
mkdir -p knowledge/default/{main,fragments,solutions,instruments}

# Organize your existing knowledge files
# (Manual step - review and categorize your files)
```

#### 5.3 Migrate Agent Profiles

If you have custom agent profiles in `agents/`:

1. Your existing profiles will continue to work
2. New specialized profiles are added but won't interfere
3. Update your profiles to use new context format if desired

Example update:

```markdown
# Old format (still works)
Custom agent instructions...

# New format (recommended)
# Agent Profile Name

## Core Responsibilities
- List responsibilities

## Approach
- Define approach

## Best Practices
- List practices
```

### Step 6: Update Docker Configuration

If using Docker:

#### 6.1 Update Docker Compose

Your existing `docker/run/docker-compose.yml` has been updated to include the memory MCP server.

To apply changes:

```bash
cd docker/run
docker-compose down
docker-compose pull
docker-compose up -d
```

#### 6.2 Verify Services

Check both services are running:

```bash
docker-compose ps
```

You should see:
- `agent-zero` (main service)
- `agent-zero-memory-mcp` (memory server)

### Step 7: Update Settings in UI

1. Start Agent Zero (or restart if already running)
2. Open Settings UI
3. Navigate to "MCP Servers"
4. Verify "memory-manager" is listed
5. Save settings

### Step 8: Test New Features

#### 8.1 Test Memory MCP Server

```bash
# In Agent Zero conversation
"Save this to memory: Testing the new memory system"
```

Then:
```bash
"Search memories for 'testing'"
```

#### 8.2 Test Multi-Agent System

```bash
# In Agent Zero conversation
"Research the latest Python frameworks and create a comparison report"
```

The system should automatically:
1. Use researcher agent to gather information
2. Use analyst agent to compare options
3. Synthesize results

#### 8.3 Test Agent Profiles

```bash
# In Agent Zero conversation
"Using multiple agents, research REST APIs, plan an implementation, and create a basic example"
```

### Step 9: Optimize Configuration

After testing, optimize your configuration:

```env
# Adjust based on your hardware
MAX_SUB_AGENTS=5  # Reduce if system is slow
MEMORY_MAX_SIZE=10000  # Adjust based on memory usage

# Fine-tune thresholds
MEMORY_COMPRESSION_THRESHOLD=0.9  # Higher = less aggressive
DEFAULT_SEARCH_THRESHOLD=0.7  # Adjust search sensitivity
```

## Compatibility Notes

### What Continues to Work

- ✅ Existing memory database (FAISS)
- ✅ Existing knowledge files
- ✅ Custom agent profiles
- ✅ All existing tools
- ✅ Existing conversations and logs
- ✅ Custom prompts
- ✅ API integrations

### What's New (Optional)

- 🆕 Memory MCP server (can be disabled)
- 🆕 Multi-agent coordination (can be disabled)
- 🆕 Specialized agent profiles (won't interfere with custom ones)
- 🆕 Memory compression (manual operation)
- 🆕 OpenRouter integration (alternative to existing providers)

### Disabling New Features

If you prefer to keep using Agent Zero as before:

```env
# Disable new features
MULTI_AGENT_ENABLED=false
MEMORY_MCP_ENABLED=false
```

Everything will work as it did before the update.

## Common Migration Issues

### Issue 1: Memory MCP Server Won't Start

**Symptom**: Error starting memory-mcp container

**Solution**:
```bash
# Check port availability
lsof -i :3001

# Use different port if needed
echo "MEMORY_MCP_PORT=3002" >> .env

# Update docker-compose.yml accordingly
```

### Issue 2: Agent Profiles Not Found

**Symptom**: Error about missing agent profiles

**Solution**:
```bash
# Re-run setup
python setup_memory_mcp.py

# Or create manually
mkdir -p agents/{researcher,developer,analyst,planner,executor}
```

### Issue 3: Existing Memories Not Searchable

**Symptom**: Memory search returns no results

**Solution**:
```python
# Rebuild memory index
from python.helpers.memory import Memory

async def rebuild_index():
    memory = await Memory.get_by_subdir("default")
    # The index will be automatically rebuilt on next access
    print("Memory index ready")
```

### Issue 4: Docker Compose Version Mismatch

**Symptom**: Docker compose syntax errors

**Solution**:
```bash
# Check docker compose version
docker-compose --version

# If needed, update the compose file format
# Change 'version: "3.8"' to your version
```

## Rolling Back

If you need to roll back:

### Option 1: Disable New Features

```env
MULTI_AGENT_ENABLED=false
MEMORY_MCP_ENABLED=false
```

Restart Agent Zero. All new features will be disabled.

### Option 2: Restore Backups

```bash
# Restore memories
rm -rf memory
mv memory_backup_YYYYMMDD memory

# Restore knowledge
rm -rf knowledge
mv knowledge_backup_YYYYMMDD knowledge

# Restore settings
cp tmp/settings_backup_YYYYMMDD.json tmp/settings.json
```

### Option 3: Git Rollback

```bash
# Find commit before update
git log --oneline

# Rollback to previous version
git checkout <commit-hash>

# Restart services
docker-compose down
docker-compose up -d
```

## Best Practices After Migration

### 1. Regular Backups

Schedule regular backups:

```bash
# Add to crontab
0 2 * * * cd /path/to/agent-zero && ./backup.sh
```

Create `backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf "backup_${DATE}.tar.gz" memory knowledge agents tmp/settings.json
```

### 2. Memory Maintenance

Run periodic memory compression:

```bash
# Weekly memory compression
# In Agent Zero conversation or via script
"Compress memories with threshold 0.9"
```

### 3. Monitor Resources

Keep an eye on resource usage:

```bash
# Check Docker resources
docker stats

# Check disk usage
du -sh memory/ knowledge/
```

### 4. Update Documentation

Document your configuration:

```bash
# Create a notes file
cat > DEPLOYMENT_NOTES.md << 'EOF'
# Agent Zero Deployment Notes

## Configuration
- Multi-agent: Enabled
- Memory MCP: Enabled
- Max agents: 5

## Custom Profiles
- security-expert: For security analysis
- data-engineer: For ETL pipelines

## Maintenance Schedule
- Memory compression: Weekly (Sunday 2 AM)
- Backups: Daily (2 AM)
- Updates: Monthly
EOF
```

## Getting Help

If you encounter issues during migration:

1. **Check Documentation**
   - [Multi-Agent Memory System](multi_agent_memory_system.md)
   - [Integration Guide](integration_guide.md)
   - [Quick Start](../QUICK_START_MULTI_AGENT.md)

2. **Run Validation**
   ```bash
   python tests/test_multi_agent_system.py
   ```

3. **Check Logs**
   ```bash
   # Docker logs
   docker logs agent-zero
   docker logs agent-zero-memory-mcp
   
   # Application logs
   tail -f logs/*.html
   ```

4. **Community Support**
   - GitHub Issues
   - Discord Server
   - Documentation Wiki

## Next Steps

After successful migration:

1. ✅ Review new features documentation
2. ✅ Try example workflows
3. ✅ Customize agent profiles for your use case
4. ✅ Set up monitoring and backups
5. ✅ Share feedback with the community

---

**Congratulations!** You've successfully migrated to the multi-agent memory system. Enjoy the enhanced capabilities! 🚀
