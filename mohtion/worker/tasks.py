"""Background job definitions."""

import logging

from mohtion.agent.orchestrator import Orchestrator
from mohtion.db.session import SessionLocal
from mohtion.integrations.github_api import GitHubAPI
from mohtion.integrations.github_app import GitHubApp

logger = logging.getLogger(__name__)


async def scan_repository(
    ctx: dict,
    owner: str,
    repo: str,
    installation_id: int,
    branch: str = "main",
) -> dict:
    """
    Main background task: scan a repository for tech debt and attempt fixes.
    """
    logger.info(f"Starting scan of {owner}/{repo} (branch: {branch})")

    async with SessionLocal() as db:
        # Set up GitHub API client
        github_app = GitHubApp()
        github_api = GitHubAPI(github_app, installation_id)

        # Run the orchestrator
        orchestrator = Orchestrator(github_api, owner, repo, db_session=db)

        try:
            result = await orchestrator.run(branch)
            logger.info(f"Scan complete for {owner}/{repo}: {result}")
            return {
                "status": "success",
                "owner": owner,
                "repo": repo,
                "result": str(result),
            }
        except Exception as e:
            logger.exception(f"Scan failed for {owner}/{repo}")
            return {
                "status": "error",
                "owner": owner,
                "repo": repo,
                "error": str(e),
            }
