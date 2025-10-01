# Multi-User Support Documentation

Agent Zero now supports multiple users with isolated resources and role-based access control.

## Overview

The multi-user system provides:
- User authentication and authorization
- Role-based access control (Admin, User, Guest)
- User-specific resources (memory, knowledge base, chat history)
- API key authentication for programmatic access
- Rate limiting per user
- Session management

## Architecture

```
┌─────────────────────────────────────────────┐
│           User Authentication               │
│  (Username/Password or API Key)            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         Session Management                  │
│  - Create user-specific AgentContext       │
│  - Apply user resource limits              │
│  - Track session activity                  │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌──────────┐
│ Memory │  │Knowledge│  │ Settings │
│ (User) │  │ (User)  │  │  (User)  │
└────────┘  └────────┘  └──────────┘
```

## User Roles

### Admin
- Full access to all features
- Can create, modify, and delete users
- Can view all user sessions
- No rate limits

### User (Default)
- Access to personal agent instance
- Isolated memory and knowledge base
- Subject to rate limits
- Can manage own profile

### Guest
- Limited access
- Stricter rate limits
- Temporary sessions only

## Getting Started

### Default Admin User

On first run, a default admin user is created:
- **Username**: `admin`
- **Password**: `admin` (⚠️ Change immediately!)
- **API Key**: Generated automatically

### Creating Users

#### Via API

```bash
curl -X POST http://localhost:50001/api/user_register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "secure_password"
  }'
```

#### Via Admin Interface

1. Log in as admin
2. Navigate to User Management
3. Click "Create User"
4. Fill in user details

### User Authentication

#### Username/Password

```bash
curl -X POST http://localhost:50001/api/user_login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "secure_password"
  }'
```

Response includes session cookie and API key.

#### API Key

Include in request headers:
```bash
curl -X POST http://localhost:50001/api/chat \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Agent Zero"}'
```

## User-Specific Resources

### Memory Isolation

Each user has an isolated memory space:
- Location: `/memory/user_{username}/`
- Vector database per user
- No cross-user memory access

### Knowledge Base Isolation

Each user has a personal knowledge base:
- Location: `/knowledge/user_{username}/`
- Separate RAG indexing
- Can import custom documents

### Chat History

Chat histories are user-specific:
- Stored separately per user
- Exportable by user
- Admin can access all histories

## Rate Limiting

Users are subject to configurable rate limits:

```python
# Default limits
max_requests_per_minute: 60
max_memory_mb: 1000
max_knowledge_items: 10000
```

### Configuring Limits

```bash
# Update user limits (admin only)
curl -X POST http://localhost:50001/api/user_update \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "max_requests_per_minute": 120
  }'
```

## API Endpoints

### Authentication

#### POST /api/user_login
Login with username and password.

**Request:**
```json
{
  "username": "john",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "username": "john",
    "email": "john@example.com",
    "role": "user",
    "api_key": "generated_api_key"
  }
}
```

#### POST /api/user_logout
Logout current user.

#### POST /api/user_register
Register a new user.

**Request:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "secure_password"
}
```

### User Management

#### GET /api/user_info
Get current user information.

#### GET /api/user_list
List all users (admin only).

#### POST /api/user_update
Update user settings.

**Request:**
```json
{
  "username": "john",
  "email": "newemail@example.com",
  "max_requests_per_minute": 120
}
```

#### POST /api/user_delete
Delete a user (admin only).

#### POST /api/user_change_password
Change user password.

**Request:**
```json
{
  "old_password": "current_password",
  "new_password": "new_secure_password"
}
```

## Session Management

### Session Lifecycle

1. **Login**: User authenticates, session created
2. **Activity**: Session updated on each request
3. **Timeout**: Session expires after 60 minutes of inactivity
4. **Logout**: Session explicitly terminated

### Session Data

Each session includes:
- User information
- Agent context (isolated per user)
- Request count and rate limit tracking
- Last activity timestamp

### Cleanup

Expired sessions are automatically cleaned up every 15 minutes.

## Security Best Practices

### 1. Change Default Password

```bash
curl -X POST http://localhost:50001/api/user_change_password \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "admin",
    "new_password": "very_secure_admin_password"
  }'
```

### 2. Use HTTPS in Production

Configure nginx or traefik with SSL certificates.

### 3. Protect API Keys

- Store API keys securely
- Rotate keys regularly
- Never commit keys to version control

### 4. Configure Strong Passwords

Enforce password requirements:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols

### 5. Enable Rate Limiting

Adjust limits based on usage patterns and server capacity.

### 6. Monitor User Activity

Use Grafana dashboards to monitor:
- Active users
- Request rates
- Failed login attempts
- Resource usage per user

## Troubleshooting

### Cannot Login

1. Check credentials are correct
2. Verify user is active: `user.active = true`
3. Check logs for authentication errors

### Rate Limit Exceeded

1. Check user's `max_requests_per_minute` setting
2. Wait 60 seconds for rate limit reset
3. Contact admin to increase limit

### Session Expired

1. Login again to create new session
2. Increase session timeout if needed

### User Not Found

1. Verify username spelling
2. Check user exists in users.json
3. Ensure users directory is readable

## Migration from Single-User

### Step 1: Backup Data

```bash
make backup
```

### Step 2: Create Admin User

Default admin is created automatically on first run.

### Step 3: Migrate Existing Data

Move existing memory/knowledge to admin user:

```bash
mkdir -p memory/user_admin
mkdir -p knowledge/user_admin
cp -r memory/default/* memory/user_admin/
cp -r knowledge/default/* knowledge/user_admin/
```

### Step 4: Create Additional Users

Use API or admin interface to create users.

## Configuration

### Enable/Disable Multi-User

In `.env`:
```bash
# Enable multi-user mode
ENABLE_MULTI_USER=true

# Session timeout (minutes)
SESSION_TIMEOUT=60

# Rate limiting
DEFAULT_RATE_LIMIT=60
```

### User Storage

Users are stored in `users/users.json`:
```json
[
  {
    "username": "admin",
    "email": "admin@agent-zero.local",
    "role": "admin",
    "active": true,
    "api_key": "generated_key",
    "memory_subdir": "user_admin",
    "knowledge_subdir": "user_admin",
    "max_requests_per_minute": 100
  }
]
```

## Advanced Features

### Custom User Settings

Each user can have custom settings:

```python
user.settings = {
    "theme": "dark",
    "language": "en",
    "notifications": true,
    "default_model": "gpt-4"
}
```

### User Groups (Future)

Plan to support user groups for shared resources:
- Shared knowledge bases
- Team memory spaces
- Collaborative agents

### SSO Integration (Future)

Plan to support:
- OAuth2 (Google, GitHub, etc.)
- LDAP/Active Directory
- SAML

## Support

For issues or questions:
- GitHub Issues: https://github.com/agent0ai/agent-zero/issues
- Discord: https://discord.gg/B8KZKNsPpj
- Documentation: /docs/
