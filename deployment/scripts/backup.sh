#!/bin/bash
# Agent Zero Backup Script
# Creates backups of data volumes and configurations

set -e

AGENT_ZERO_PATH="${AGENT_ZERO_PATH:-/opt/agent-zero}"
BACKUP_DIR="${BACKUP_DIR:-$AGENT_ZERO_PATH/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="agent-zero-backup-$TIMESTAMP"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# log writes a timestamped message to stdout, prefixing the provided text with "[YYYY-MM-DD HH:MM:SS]".
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# backup_volumes backs up Docker volumes and the PostgreSQL database into timestamped archives in BACKUP_DIR.
# Creates compressed tar.gz archives for the memory, knowledge, logs, and redis volumes and a gzipped SQL dump for PostgreSQL.
backup_volumes() {
    log "Starting backup of Docker volumes..."
    
    # Backup memory volume
    log "Backing up memory volume..."
    docker run --rm \
        -v agent-zero-memory:/data/memory:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/${BACKUP_NAME}-memory.tar.gz" -C /data memory
    
    # Backup knowledge volume
    log "Backing up knowledge volume..."
    docker run --rm \
        -v agent-zero-knowledge:/data/knowledge:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/${BACKUP_NAME}-knowledge.tar.gz" -C /data knowledge
    
    # Backup logs volume
    log "Backing up logs volume..."
    docker run --rm \
        -v agent-zero-logs:/data/logs:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/${BACKUP_NAME}-logs.tar.gz" -C /data logs
    
    # Backup PostgreSQL database
    log "Backing up PostgreSQL databases..."
    docker exec agent-zero-postgres pg_dumpall -U postgres | gzip > "$BACKUP_DIR/${BACKUP_NAME}-postgres.sql.gz"
    
    # Backup Redis data
    log "Backing up Redis data..."
    docker run --rm \
        -v redis-data:/data/redis:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/${BACKUP_NAME}-redis.tar.gz" -C /data redis
    
    log "Volume backups completed"
}

# backup_configs creates a compressed tarball of Agent Zero configuration files (.env, config/, docker-compose.production.yml) in the backup directory and ignores missing files.
backup_configs() {
    log "Backing up configuration files..."
    
    tar czf "$BACKUP_DIR/${BACKUP_NAME}-configs.tar.gz" \
        -C "$AGENT_ZERO_PATH" \
        .env \
        config/ \
        docker-compose.production.yml \
        2>/dev/null || true
    
    log "Configuration backup completed"
}

# create_manifest creates a manifest file at "$BACKUP_DIR/${BACKUP_NAME}-manifest.txt" summarizing the backup (date, backup name, agent path), the list of files matching the backup name, total size, known Docker volumes, databases, and current services as reported by docker-compose.
# If no backup files match, the manifest will contain "No files found"; docker-compose errors are suppressed when listing services.
create_manifest() {
    log "Creating backup manifest..."
    
    cat > "$BACKUP_DIR/${BACKUP_NAME}-manifest.txt" <<EOF
Agent Zero Backup Manifest
==========================
Backup Date: $(date)
Backup Name: $BACKUP_NAME
Agent Zero Path: $AGENT_ZERO_PATH

Files:
$(ls -lh "$BACKUP_DIR/${BACKUP_NAME}"* 2>/dev/null || echo "No files found")

Total Size: $(du -sh "$BACKUP_DIR/${BACKUP_NAME}"* 2>/dev/null | awk '{total+=$1} END {print total}')

Docker Volumes:
- agent-zero-memory
- agent-zero-knowledge
- agent-zero-logs
- postgres-data
- redis-data

Databases:
- PostgreSQL (litellm, langfuse)
- Redis

Services Running:
$(docker-compose -f "$AGENT_ZERO_PATH/docker-compose.production.yml" ps 2>/dev/null)
EOF
    
    log "Manifest created"
}

# cleanup_old_backups deletes files in "$BACKUP_DIR" named "agent-zero-backup-*" that are older than "$RETENTION_DAYS" days.
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find "$BACKUP_DIR" -name "agent-zero-backup-*" -type f -mtime +$RETENTION_DAYS -delete
    
    log "Cleanup completed"
}

# main orchestrates the backup workflow by switching to AGENT_ZERO_PATH, running volume and config backups, creating a manifest, cleaning old backups, and logging completion details including backup location, name, and total size.
main() {
    log "Starting Agent Zero backup process..."
    
    cd "$AGENT_ZERO_PATH" || exit 1
    
    backup_volumes
    backup_configs
    create_manifest
    cleanup_old_backups
    
    log "Backup process completed successfully"
    log "Backup location: $BACKUP_DIR"
    log "Backup name: $BACKUP_NAME"
    
    # Calculate total backup size
    TOTAL_SIZE=$(du -sh "$BACKUP_DIR/${BACKUP_NAME}"* 2>/dev/null | awk '{sum+=$1} END {print sum}')
    log "Total backup size: $TOTAL_SIZE"
}

main "$@"
