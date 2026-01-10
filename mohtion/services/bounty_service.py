"""Bounty Service - Encapsulates business logic for managing bounties."""

import logging
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from mohtion.db import crud
from mohtion.models.bounty import Bounty, BountyStatus
from mohtion.models.repository import Repository
from mohtion.models.target import TechDebtTarget

logger = logging.getLogger(__name__)


class BountyService:
    """Service for managing the lifecycle of tech debt bounties."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_repository(
        self, 
        repo_id: int, 
        installation_id: int, 
        full_name: str,
        account_login: str,
        account_id: int
    ) -> Repository:
        """Register installation and repository in one go."""
        await crud.get_or_create_installation(
            self.session,
            installation_id,
            account_login,
            account_id
        )
        return await crud.get_or_create_repository(
            self.session,
            repo_id,
            installation_id,
            full_name
        )

    async def log_scan(self, repo_id: int, targets_found: int) -> None:
        """Log a scan result."""
        await crud.log_scan(self.session, repo_id, targets_found)

    async def claim_next_target(
        self, repo_id: int, targets: list[TechDebtTarget]
    ) -> tuple[TechDebtTarget, Bounty] | tuple[None, None]:
        """
        Find the first target that doesn't have an active bounty and create one.
        
        Returns:
            Tuple of (Target, Bounty) if claimed, else (None, None)
        """
        from datetime import timedelta
        
        for target in targets:
            existing = await crud.get_existing_bounty(
                self.session, 
                repo_id, 
                str(target.file_path), 
                target.function_name or ""
            )
            
            if existing:
                # Zombie Check: If it's IN_PROGRESS but old (>1 hour), assume worker died
                is_stale = (
                    existing.status == BountyStatus.IN_PROGRESS 
                    and existing.created_at < datetime.utcnow() - timedelta(hours=1)
                )

                if is_stale:
                    logger.warning(
                        f"Found stale zombie bounty {existing.id} (created {existing.created_at}). "
                        f"Marking as ABANDONED and reclaiming target."
                    )
                    existing.status = BountyStatus.ABANDONED
                    existing.error_message = "Worker timeout/crash detected (Zombie Bounty)"
                    existing.completed_at = datetime.utcnow()
                    self.session.add(existing)
                    # Don't return, fall through to create NEW bounty for this target
                else:
                    logger.info(
                        f"Skipping target {target.location} - Bounty exists: {existing.id} ({existing.status})"
                    )
                    continue
                
            # Found a free target! Claim it.
            bounty = await crud.create_bounty(
                self.session,
                repo_id,
                str(target.file_path),
                target.function_name or "",
                target.debt_type.value
            )
            bounty.branch_name = f"mohtion/bounty-{uuid.uuid4().hex[:8]}"
            await self.session.commit()
            
            return target, bounty
            
        return None, None

    async def update_bounty_status(
        self, 
        bounty: Bounty, 
        status: BountyStatus, 
        error_message: str | None = None,
        commit: bool = True
    ) -> None:
        """Update bounty status."""
        bounty.status = status
        if error_message:
            bounty.error_message = error_message
        
        if status in [BountyStatus.FAILED, BountyStatus.CLOSED]:
            bounty.completed_at = datetime.utcnow()

        self.session.add(bounty)
        if commit:
            await self.session.commit()

    async def record_refactoring(
        self, 
        bounty: Bounty, 
        original_code: str,
        refactored_code: str, 
        summary: str
    ) -> None:
        """Record the refactoring result."""
        bounty.original_code = original_code
        bounty.refactored_code = refactored_code
        bounty.refactoring_summary = summary
        self.session.add(bounty)
        await self.session.commit()

    async def record_test_result(
        self, 
        bounty: Bounty, 
        output: str, 
        passed: bool,
        retry_count: int
    ) -> None:
        """Record test execution result."""
        bounty.test_output = output
        bounty.retry_count = retry_count
        # Note: Status update handled separately or implied
        self.session.add(bounty)
        await self.session.commit()

    async def record_pr(
        self, 
        bounty: Bounty, 
        pr_url: str, 
        pr_number: int
    ) -> None:
        """Record successful PR creation."""
        bounty.status = BountyStatus.OPEN
        bounty.pr_url = pr_url
        bounty.pr_number = pr_number
        bounty.completed_at = datetime.utcnow()
        self.session.add(bounty)
        await self.session.commit()
