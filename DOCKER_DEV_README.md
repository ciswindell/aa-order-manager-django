# Docker Development Environment

This document describes the Docker-based development environment for the AA Order Manager application.

## Quick Start

```bash
# 1. Clone the repository (if not already done)
git clone <repository-url>
cd aa-order-manager

# 2. Create .env file with required configuration
# See .env.example for template

# 3. Start all services
docker compose up -d

# 4. Access the application
# Django admin: http://localhost:8000/admin/
# Login: admin / admin
# Flower (Celery monitoring): http://localhost:5555/
```

That's it! The database will initialize automatically on first startup.

## Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher (comes with Docker Desktop)
- **Git**: For cloning the repository

## Architecture

The development environment consists of:

- **web**: Django development server (port 8000)
- **worker**: Celery worker for background tasks (`celery@order-manager-worker`)
- **db**: PostgreSQL 15 database with persistent storage
- **redis**: Redis 7 broker/backend for Celery
- **flower**: Celery monitoring UI (port 5555)

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root with:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/order_manager_dev

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Dropbox OAuth (add your credentials)
DROPBOX_APP_KEY=
DROPBOX_APP_SECRET=
DROPBOX_REDIRECT_URI=http://localhost:8000/integrations/dropbox/callback/
```

### Do NOT Set

- `CELERY_TASK_ALWAYS_EAGER` - This disables async task processing

## Common Commands

### Starting Services

```bash
# Start all services in background
docker compose up -d

# Start and view logs
docker compose up

# Start specific service
docker compose up -d web
```

### Stopping Services

```bash
# Stop all services (keeps data)
docker compose down

# Stop and remove volumes (DELETES ALL DATA)
docker compose down -v
```

### Viewing Logs

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs web
docker compose logs worker

# Follow logs in real-time
docker compose logs -f worker
```

### Database Operations

```bash
# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Access Django shell
docker compose exec web python manage.py shell

# Access PostgreSQL directly
docker compose exec db psql -U postgres -d order_manager_dev
```

### Managing Services

```bash
# Restart a service
docker compose restart web

# Rebuild images after dependency changes
docker compose build
docker compose up -d

# Scale workers (if needed)
docker compose up -d --scale worker=3
```

### Development Workflow

```bash
# Check service status
docker compose ps

# View resource usage
docker stats

# Clean up unused Docker resources
docker system prune
```

## Development Features

### Hot Reload

Code changes are automatically detected and the Django server reloads within seconds. No need to restart containers!

**How it works:**
- The `./web` directory is mounted as a volume
- Django's `StatReloader` watches for file changes
- Changes trigger automatic reload

### Async Background Tasks

Celery worker processes tasks asynchronously:

**Before Docker setup:**
- Lease saves: 10-30+ seconds (blocking)
- Admin interface frozen during tasks

**After Docker setup:**
- Lease saves: <0.1 seconds (instant!)
- Tasks run in background worker
- No admin interface blocking

**Monitor tasks:**
- Open Flower at http://localhost:5555/
- View worker status, task history, and performance

### Data Persistence

Database data persists between container restarts:

```bash
# Data survives these operations:
docker compose down
docker compose up -d
docker compose restart db
```

Database is stored in the `postgres_data` Docker volume.

**To reset database:**
```bash
docker compose down -v  # WARNING: Deletes all data!
docker compose up -d
```

## Troubleshooting

### Services won't start

```bash
# Check if ports are already in use
lsof -i :8000  # Django
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :5555  # Flower

# View detailed error logs
docker compose logs web
docker compose logs db
```

### Database connection errors

```bash
# Check if database is healthy
docker compose ps

# Wait for database to be ready
docker compose logs web | grep "PostgreSQL"

# Restart web service
docker compose restart web
```

### Worker not processing tasks

```bash
# Check worker is running
docker compose ps worker

# View worker logs
docker compose logs worker

# Verify worker is listening to correct queues
docker compose logs worker | grep "queues"
# Should show: .> celery and .> orders
```

### Hot reload not working

```bash
# Verify volume mount is correct
docker compose config | grep volumes

# Restart web service
docker compose restart web
```

### Out of disk space

```bash
# Remove unused images, containers, volumes
docker system prune -a

# View disk usage
docker system df
```

## File Structure

```
aa-order-manager/
├── Dockerfile                    # Main application image
├── docker-compose.yml            # Service orchestration
├── docker-compose.override.yml   # Dev-specific overrides
├── .dockerignore                 # Files excluded from build
├── .env                          # Environment variables (create this)
├── requirements.txt              # Python dependencies
└── web/
    ├── init-db.sh                # Database initialization script
    ├── manage.py                 # Django management
    └── ...
```

## Port Mapping

| Service | Internal Port | External Port | Purpose |
|---------|--------------|---------------|---------|
| web     | 8000         | 8000          | Django admin/API |
| db      | 5432         | 5432          | PostgreSQL |
| redis   | 6379         | 6379          | Redis broker |
| flower  | 5555         | 5555          | Celery monitoring |

## Performance Notes

### Worker Configuration

The worker processes both `celery` and `orders` queues:

```yaml
command: celery -A order_manager_project worker -Q celery,orders -l info
```

**Scaling workers:**
```bash
# Single worker (default, good for dev)
docker compose up -d worker

# Multiple workers (for heavy load)
docker compose up -d --scale worker=3
```

### Resource Limits

By default, no resource limits are set for development. For production, consider adding limits in `docker-compose.yml`:

```yaml
services:
  worker:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Next Steps

1. **Configure Dropbox OAuth** - Add credentials to `.env`
2. **Create Agency Storage Configs** - Via Django admin at `/admin/integrations/agencystorageconfig/`
3. **Test full workflow** - Create a Lease and verify async task processing
4. **Monitor with Flower** - Check worker performance at http://localhost:5555/

## Support

For issues or questions:
1. Check logs: `docker compose logs <service>`
2. Review this documentation
3. Check the main [README.md](./README.md)

