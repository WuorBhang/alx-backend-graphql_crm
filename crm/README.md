# CRM Celery Setup Guide

This guide explains how to set up and run Celery with Celery Beat for automated CRM report generation.

## Prerequisites

- Python 3.8+
- Django 4.2+
- Redis server

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Redis

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS:
```bash
brew install redis
brew services start redis
```

#### Windows:
Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)

### 3. Verify Redis Installation

```bash
redis-cli ping
# Should return: PONG
```

## Configuration

The Celery configuration is already set up in the Django settings:

- **Broker**: Redis at `redis://localhost:6379/0`
- **Result Backend**: Redis at `redis://localhost:6379/0`
- **Task Serializer**: JSON
- **Schedule**: Weekly CRM report generation (every 7 days)

## Running Celery

### 1. Start Celery Worker

In one terminal:
```bash
cd /path/to/alx-backend-graphql_crm
celery -A crm worker -l info
```

### 2. Start Celery Beat Scheduler

In another terminal:
```bash
cd /path/to/alx-backend-graphql_crm
celery -A crm beat -l info
```

### 3. Run Django Migrations

```bash
python manage.py migrate
```

## Monitoring

### Task Status

Check task status in the Celery worker terminal. You should see:
- Task discovery messages
- Task execution logs
- Any errors or exceptions

### Logs

The CRM report task logs to:
- **File**: `/tmp/crm_report_log.txt`
- **Format**: `YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, $Z revenue`

### Redis Monitoring

Monitor Redis activity:
```bash
redis-cli monitor
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis is running: `sudo systemctl status redis-server`
   - Check Redis port: `redis-cli -p 6379 ping`

2. **Task Not Executing**
   - Verify Celery Beat is running
   - Check task registration in worker logs
   - Verify task function exists in `crm/tasks.py`

3. **GraphQL Connection Error**
   - Ensure Django server is running on port 8000
   - Check GraphQL endpoint: `http://localhost:8000/graphql`

### Debug Mode

For debugging, run with verbose logging:
```bash
celery -A crm worker -l debug
celery -A crm beat -l debug
```

## Task Details

### generate_crm_report

- **Schedule**: Every 7 days (604800 seconds)
- **Purpose**: Generate CRM summary report
- **Data Collected**:
  - Total customer count
  - Total order count
  - Total revenue from orders
- **Output**: Logged to `/tmp/crm_report_log.txt`

### Manual Execution

Run the task manually for testing:
```bash
python manage.py shell
```

```python
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(f"Task ID: {result.id}")
```

## Production Considerations

- Use supervisor or systemd to manage Celery processes
- Configure Redis persistence and backup
- Set up monitoring and alerting
- Use environment variables for configuration
- Implement proper error handling and retries
