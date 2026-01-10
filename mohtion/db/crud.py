from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from mohtion.models import Bounty, BountyStatus, Installation, Repository, ScanHistory


async def get_or_create_installation(
    session: AsyncSession,
    installation_id: int,
    account_login: str,
    account_id: int
) -> Installation:
    """Get or create installation using UPSERT."""
    stmt = insert(Installation).values(
        id=installation_id,
        account_login=account_login,
        account_id=account_id,
        installed_at=datetime.utcnow()
    )
    # If it exists, update the account info just in case it changed
    stmt = stmt.on_conflict_do_update(
        index_elements=['id'],
        set_=dict(
            account_login=stmt.excluded.account_login,
            account_id=stmt.excluded.account_id
        )
    ).returning(Installation)

    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one()

async def get_or_create_repository(
    session: AsyncSession,
    repo_id: int,
    installation_id: int,
    full_name: str
) -> Repository:
    """Get or create repository using UPSERT."""
    stmt = insert(Repository).values(
        id=repo_id,
        installation_id=installation_id,
        full_name=full_name,
        is_active=True
    )
    # If it exists, just ensure it's linked correctly (or do nothing)
    stmt = stmt.on_conflict_do_update(
        index_elements=['id'],
        set_=dict(
            full_name=stmt.excluded.full_name,
            installation_id=stmt.excluded.installation_id
        )
    ).returning(Repository)

    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one()

async def log_scan(session: AsyncSession, repo_id: int, targets_found: int):
    scan = ScanHistory(repository_id=repo_id, targets_found=targets_found)
    session.add(scan)

    # Update last_scanned_at on repository
    stmt = select(Repository).where(Repository.id == repo_id)
    result = await session.execute(stmt)
    repo = result.scalar_one()
    repo.last_scanned_at = datetime.utcnow()

    await session.commit()

async def get_existing_bounty(
    session: AsyncSession,
    repo_id: int,
    target_file: str,
    target_function: str
) -> Bounty | None:
    stmt = select(Bounty).where(
        Bounty.repository_id == repo_id,
        Bounty.target_file == target_file,
        Bounty.target_function == target_function,
        Bounty.status.in_(BountyStatus.active_statuses())
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_bounty(
    session: AsyncSession,
    repo_id: int,
    target_file: str,
    target_function: str,
    issue_type: str
) -> Bounty:
    bounty = Bounty(
        repository_id=repo_id,
        target_file=target_file,
        target_function=target_function,
        issue_type=issue_type,
        status=BountyStatus.IN_PROGRESS
    )
    session.add(bounty)
    await session.commit()
    await session.refresh(bounty)
    return bounty
