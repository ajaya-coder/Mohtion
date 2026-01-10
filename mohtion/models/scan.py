from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mohtion.db.base import Base

if TYPE_CHECKING:
    from mohtion.models.repository import Repository

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("repositories.id"), nullable=False
    )
    scanned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    targets_found: Mapped[int] = mapped_column(Integer, default=0)

    repository: Mapped[Repository] = relationship(back_populates="scans")

    def __repr__(self) -> str:
        return f"<ScanHistory {self.repository_id} at {self.scanned_at}>"
