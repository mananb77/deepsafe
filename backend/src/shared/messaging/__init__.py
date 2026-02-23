"""Messaging configuration for Celery task queues."""

from src.shared.messaging.celery_app import celery_app

__all__ = ["celery_app"]
