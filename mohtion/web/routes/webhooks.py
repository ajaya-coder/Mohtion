"""GitHub webhook handlers."""

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from mohtion.db import crud
from mohtion.db.session import get_db
from mohtion.integrations.github_app import GitHubApp

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Handle incoming GitHub webhooks."""
    # Get raw body for signature verification
    body = await request.body()

    # Verify webhook signature
    github_app = GitHubApp()
    is_valid = await github_app.verify_webhook_signature(body, x_hub_signature_256)
    if not is_valid:
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    payload = await request.json()

    # Handle different event types
    match x_github_event:
        case "installation":
            return await handle_installation(payload, db)
        case "push":
            return await handle_push(payload, db)
        case "ping":
            return {"status": "pong"}
        case _:
            logger.debug(f"Ignoring event type: {x_github_event}")
            return {"status": "ignored", "event": x_github_event}


async def handle_installation(payload: dict, db: AsyncSession) -> dict[str, str]:
    """Handle GitHub App installation events."""
    action = payload.get("action")
    installation_data = payload.get("installation", {})
    installation_id = installation_data.get("id")
    account_data = installation_data.get("account", {})
    account_login = account_data.get("login")
    account_id = account_data.get("id")

    logger.info(f"Installation {action}: {account_login} (ID: {installation_id})")

    match action:
        case "created":
            # Persist installation
            await crud.get_or_create_installation(
                db,
                installation_id=installation_id,
                account_login=account_login,
                account_id=account_id
            )

            # Persist repositories
            repositories = payload.get("repositories", [])
            for repo in repositories:
                await crud.get_or_create_repository(
                    db,
                    repo_id=repo.get("id"),
                    installation_id=installation_id,
                    full_name=repo.get("full_name")
                )

            logger.info(f"New installation from {account_login} with {len(repositories)} repos")
        case "deleted":
            # We could mark as inactive instead of hard deleting
            logger.info(f"Installation removed by {account_login}")
        case _:
            logger.debug(f"Installation action: {action}")

    return {"status": "ok", "action": action}


async def handle_push(payload: dict, db: AsyncSession) -> dict[str, str]:
    """Handle push events - optionally trigger scans."""
    repo = payload.get("repository", {})
    repo_name = repo.get("full_name")
    ref = payload.get("ref", "")
    default_branch = repo.get("default_branch", "main")

    # Only process pushes to default branch
    if ref != f"refs/heads/{default_branch}":
        logger.debug(f"Ignoring push to non-default branch: {ref}")
        return {"status": "ignored", "reason": "not default branch"}

    installation_id = payload.get("installation", {}).get("id")
    logger.info(f"Push to {repo_name} (installation: {installation_id})")

    # TODO: Queue scan job via ARQ
    # For MVP, we'll trigger scans manually or on schedule

    return {"status": "ok", "repo": repo_name}
