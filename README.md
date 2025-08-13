# AA Order Manager — Dev Setup

## Quick start

1) Run Django (in web/):

```bash
python3 manage.py runserver
```

## Optional: real background tasks

To use Redis + Celery worker instead of eager mode, configure a broker and run a worker.
Eager mode can be enabled by environment variable:

```bash
export CELERY_TASK_ALWAYS_EAGER=1
```

This runs tasks inline (no Redis/worker needed). Unset to return to real background processing.


