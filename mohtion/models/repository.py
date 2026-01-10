from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mohtion.db.base import Base

if TYPE_CHECKING:
    from mohtion.models.bounty import Bounty
    from mohtion.models.scan import ScanHistory

class Installation(Base):
    __tablename__ = "installations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # GitHub Installation ID
    account_login: Mapped[str] = mapped_column(String(255), nullable=False)
    account_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    installed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    repositories: Mapped[list[Repository]] = relationship(
        back_populates="installation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Installation {self.account_login} ({self.id})>"

class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # GitHub Repo ID
    installation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("installations.id"), nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    config_overrides: Mapped[dict] = mapped_column(JSON, default=dict)
    last_scanned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    installation: Mapped[Installation] = relationship(back_populates="repositories")
    bounties: Mapped[list[Bounty]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )
    scans: Mapped[list[ScanHistory]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Repository {self.full_name}>"
