from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import UUID, BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mohtion.db.base import Base

if TYPE_CHECKING:
    from mohtion.models.repository import Repository

class BountyStatus(str, Enum):
    """Status of a bounty (refactoring attempt)."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    RETRYING = "retrying"
    OPEN = "open"          # PR is open
    SUCCESS = "success"    # PR was merged
    MERGED = "merged"      # PR was merged
    FAILED = "failed"      # Agent failed
    ABANDONED = "abandoned"
    CLOSED = "closed"      # Closed without merge

    @classmethod
    def active_statuses(cls) -> list["BountyStatus"]:
        """Return statuses that indicate work is ongoing or completed."""
        return [
            cls.OPEN,
            cls.MERGED,
            cls.SUCCESS,
            cls.PENDING,
            cls.IN_PROGRESS,
            cls.TESTING,
            cls.RETRYING,
        ]

class Bounty(Base):
    __tablename__ = "bounties"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("repositories.id"), nullable=False
    )

    # Target details
    target_file: Mapped[str] = mapped_column(String(512), nullable=False)
    target_function: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_type: Mapped[str] = mapped_column(String(50), nullable=False)

    status: Mapped[BountyStatus] = mapped_column(
        SQLEnum(BountyStatus), default=BountyStatus.PENDING, nullable=False
    )

    # PR details
    pr_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pr_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    branch_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Refactoring content
    original_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    refactored_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    refactoring_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Test details
    test_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    repository: Mapped[Repository] = relationship(back_populates="bounties")

    def __repr__(self) -> str:
        return f"<Bounty {self.target_file}:{self.target_function} [{self.status}]>"
