"""
Celery Application Configuration

Configures the Celery application for distributed task processing.

Task Queues:
- detection: High-priority deepfake detection tasks
- analysis: NLP, risk scoring, social engineering analysis
- verification: SMS, voice, push verification tasks
- meeting_bot: Bot management and control tasks
- workflow: Policy evaluation and workflow tasks
- integration: SSO, SIEM sync tasks
"""

import os
from celery import Celery

from src.shared.config.settings import get_settings


# Create Celery application
celery_app = Celery("deepsafe")

# Load settings
settings = get_settings()

# Configure Celery
celery_app.conf.update(
    # Broker settings
    broker_url=settings.celery.broker_url,
    result_backend=settings.celery.result_backend,

    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task routing
    task_routes={
        "detection.*": {"queue": "detection"},
        "analysis.*": {"queue": "analysis"},
        "verification.*": {"queue": "verification"},
        "meeting_bot.*": {"queue": "meeting_bot"},
        "workflow.*": {"queue": "workflow"},
        "integration.*": {"queue": "integration"},
    },

    # Default queue
    task_default_queue="default",

    # Task settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Result settings
    result_expires=3600,  # 1 hour

    # Worker settings
    worker_prefetch_multiplier=4,
    worker_concurrency=8,

    # Beat scheduler
    beat_schedule={
        "cleanup-old-results": {
            "task": "analysis.cleanup_results",
            "schedule": 3600.0,  # Every hour
        },
    },
)

# Configure task queues with priorities
celery_app.conf.task_queues = {
    "detection": {
        "exchange": "detection",
        "routing_key": "detection",
        "queue_arguments": {"x-max-priority": 10},
    },
    "analysis": {
        "exchange": "analysis",
        "routing_key": "analysis",
        "queue_arguments": {"x-max-priority": 5},
    },
    "verification": {
        "exchange": "verification",
        "routing_key": "verification",
        "queue_arguments": {"x-max-priority": 10},
    },
    "meeting_bot": {
        "exchange": "meeting_bot",
        "routing_key": "meeting_bot",
        "queue_arguments": {"x-max-priority": 7},
    },
    "workflow": {
        "exchange": "workflow",
        "routing_key": "workflow",
        "queue_arguments": {"x-max-priority": 3},
    },
    "integration": {
        "exchange": "integration",
        "routing_key": "integration",
        "queue_arguments": {"x-max-priority": 3},
    },
}

# Auto-discover tasks from all services
celery_app.autodiscover_tasks([
    "src.services.stream.tasks",
    "src.services.detection.tasks",
    "src.services.verification.tasks",
    "src.services.analysis.tasks",
    "src.services.workflow.tasks",
    "src.services.integration.tasks",
], force=True)


def get_celery_app() -> Celery:
    """Get the configured Celery application."""
    return celery_app
