"""Add OLLAMA_LLM and WHISPER to indicator_source enum

Revision ID: 002_add_local_sources
Revises: 001_initial
Create Date: 2026-02-23 00:00:01

Adds new enum values for local detection models:
- ollama_llm: Local LLM via Ollama for social engineering analysis
- whisper: Local Whisper transcription model
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_add_local_sources"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to the indicator_source enum
    op.execute("ALTER TYPE indicator_source ADD VALUE IF NOT EXISTS 'ollama_llm'")
    op.execute("ALTER TYPE indicator_source ADD VALUE IF NOT EXISTS 'whisper'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values directly.
    # A full enum rebuild would be needed, but these values are safe to leave in place.
    pass
