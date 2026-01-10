"""Orchestrator - Main agent loop coordinator."""

import logging
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from mohtion.agent.refactor import Refactor
from mohtion.agent.scanner import Scanner
from mohtion.agent.verifier import Verifier
from mohtion.config import get_settings
from mohtion.integrations.github_api import GitHubAPI
from mohtion.models.bounty import Bounty, BountyStatus
from mohtion.models.repo_config import RepoConfig
from mohtion.services.bounty_service import BountyService

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main agent loop: Scan → Refactor → Verify → PR

    This is the core of Mohtion - it coordinates the entire
    tech debt hunting and fixing process.
    """

    def __init__(
        self,
        github_api: GitHubAPI,
        owner: str,
        repo: str,
        db_session: AsyncSession | None = None,
        config_override: RepoConfig | None = None,
    ) -> None:
        self.github_api = github_api
        self.owner = owner
        self.repo = repo
        self.settings = get_settings()
        self.db = db_session
        self.config_override = config_override
        self.bounty_service = BountyService(db_session) if db_session else None
        self._repo_id: int | None = None

    async def run(self, base_branch: str = "main") -> Bounty | None:
        """
        Execute the full agent loop.

        Args:
            base_branch: The base branch to work from

        Returns:
            Bounty if a PR was opened, None if no targets found
        """
        repo_path: Path | None = None

        try:
            # Clone the repository
            logger.info(f"Cloning {self.owner}/{self.repo}...")
            repo_path = await self.github_api.clone_repo(self.owner, self.repo)
            logger.info(f"Cloned to {repo_path}")

            # Sync Repository Metadata
            if self.bounty_service:
                inst_info = await self.github_api.get_installation_info()
                repo_info = await self.github_api._get_repo_info(self.owner, self.repo)
                self._repo_id = repo_info["id"]

                await self.bounty_service.register_repository(
                    repo_id=self._repo_id,
                    installation_id=self.github_api.installation_id,
                    full_name=f"{self.owner}/{self.repo}",
                    account_login=inst_info["account"]["login"],
                    account_id=inst_info["account"]["id"]
                )

            # Load repo config or use override
            if self.config_override:
                config = self.config_override
            else:
                config = RepoConfig.from_file(repo_path / ".mohtion.yaml")

            # Phase 1: RECONNAISSANCE
            logger.info("Phase 1: Reconnaissance")
            scanner = Scanner(repo_path, config)
            targets = await scanner.scan()

            if self.bounty_service and self._repo_id:
                await self.bounty_service.log_scan(self._repo_id, len(targets))

            if not targets:
                logger.info("No tech debt targets found")
                return None

            # Claim a target
            target = None
            bounty = None

            if self.bounty_service and self._repo_id:
                target, bounty = await self.bounty_service.claim_next_target(
                    self._repo_id, targets
                )
            else:
                # Fallback for testing without DB
                target = targets[0]
                bounty = Bounty(
                    target_file=str(target.file_path),
                    target_function=target.function_name or "",
                    issue_type=target.debt_type.value,
                    status=BountyStatus.IN_PROGRESS,
                    branch_name=f"mohtion/bounty-{uuid.uuid4().hex[:8]}"
                )

            if not target:
                logger.info("All targets already have active bounties")
                return None

            logger.info(f"Target acquired: {target}")

            # Create feature branch
            actual_branch = self.github_api.create_branch(repo_path, base_branch)
            bounty.branch_name = actual_branch
            if self.bounty_service:
                await self.bounty_service.update_bounty_status(bounty, BountyStatus.IN_PROGRESS)

            # Phase 2: REFACTORING
            logger.info("Phase 2: Refactoring")
            refactor = Refactor(repo_path)
            result = await refactor.refactor_target(target)

            if not result.success:
                if self.bounty_service:
                    await self.bounty_service.update_bounty_status(
                        bounty, 
                        BountyStatus.FAILED, 
                        error_message=f"Refactoring failed: {result.error}"
                    )
                else:
                    bounty.status = BountyStatus.FAILED
                    bounty.error_message = f"Refactoring failed: {result.error}"
                return bounty

            if self.bounty_service:
                await self.bounty_service.record_refactoring(
                    bounty, 
                    result.original_code,
                    result.refactored_code,
                    result.summary
                )
            else:
                bounty.original_code = result.original_code
                bounty.refactored_code = result.refactored_code
                bounty.refactoring_summary = result.summary

            # Apply the refactoring
            if not await refactor.apply_refactoring(target, result.refactored_code):
                msg = "Failed to apply refactoring"
                if self.bounty_service:
                    await self.bounty_service.update_bounty_status(bounty, BountyStatus.FAILED, msg)
                else:
                    bounty.status = BountyStatus.FAILED
                    bounty.error_message = msg
                return bounty

            # Phase 3: VERIFICATION
            logger.info("Phase 3: Verification")
            verifier = Verifier(repo_path, config)
            
            if self.bounty_service:
                await self.bounty_service.update_bounty_status(bounty, BountyStatus.TESTING)
            else:
                bounty.status = BountyStatus.TESTING

            test_passed = False
            for attempt in range(self.settings.max_retries + 1):
                test_result = await verifier.run_tests()
                
                if self.bounty_service:
                    await self.bounty_service.record_test_result(
                        bounty, 
                        test_result.output, 
                        test_result.passed,
                        attempt
                    )
                else:
                    bounty.test_output = test_result.output

                if test_result.passed:
                    test_passed = True
                    break

                # Self-healing attempt
                if attempt < self.settings.max_retries:
                    logger.info(f"Tests failed, attempting self-heal (attempt {attempt + 1})")
                    
                    if self.bounty_service:
                        await self.bounty_service.update_bounty_status(bounty, BountyStatus.RETRYING)
                    else:
                        bounty.status = BountyStatus.RETRYING

                    heal_result = await refactor.attempt_self_heal(
                        target,
                        bounty.refactored_code,
                        test_result.output,
                    )

                    if heal_result.success:
                        # Update the code with the healed version
                        if self.bounty_service:
                            await self.bounty_service.record_refactoring(
                                bounty,
                                bounty.original_code,
                                heal_result.refactored_code,
                                bounty.refactoring_summary + f"\n\n{heal_result.summary}"
                            )
                        else:
                            bounty.refactored_code = heal_result.refactored_code
                            bounty.refactoring_summary += f"\n\n{heal_result.summary}"

                        # Apply the healed code
                        await refactor.apply_refactoring(target, heal_result.refactored_code)
                    else:
                        msg = f"Self-heal failed: {heal_result.error}"
                        if self.bounty_service:
                            await self.bounty_service.update_bounty_status(bounty, BountyStatus.FAILED, msg)
                        else:
                            bounty.status = BountyStatus.FAILED
                            bounty.error_message = msg
                        return bounty

            if not test_passed:
                msg = "Tests failed after max retries"
                if self.bounty_service:
                    await self.bounty_service.update_bounty_status(bounty, BountyStatus.FAILED, msg)
                else:
                    bounty.status = BountyStatus.FAILED
                    bounty.error_message = msg
                return bounty

            # Phase 4: BOUNTY CLAIM
            logger.info("Phase 4: Opening PR")

            # Commit the changes
            commit_message = (
                f"refactor: {target.description}\n\n"
                f"Mohtion Bounty: {bounty.branch_name}"
            )
            self.github_api.commit_changes(
                repo_path,
                target.file_path,
                (repo_path / target.file_path).read_text(),
                commit_message,
            )

            # Push the branch
            await self.github_api.push_branch(
                repo_path, self.owner, self.repo, bounty.branch_name
            )

            # Create the PR
            pr_title = (
                f"[Mohtion] {target.debt_type.value}: "
                f"{target.function_name or target.file_path.name}"
            )
            pr_body = self._generate_pr_body(bounty, target)

            pr_result = await self.github_api.create_pull_request(
                owner=self.owner,
                repo=self.repo,
                branch_name=bounty.branch_name,
                base_branch=base_branch,
                title=pr_title,
                body=pr_body,
            )

            # Update bounty with success details
            if self.bounty_service:
                await self.bounty_service.record_pr(
                    bounty, 
                    pr_result.html_url, 
                    pr_result.number
                )
            else:
                bounty.status = BountyStatus.OPEN
                bounty.pr_url = pr_result.html_url
                bounty.pr_number = pr_result.number

            logger.info(f"PR opened: {pr_result.html_url}")

            return bounty

        except Exception:
            logger.info("Orchestrator failed")
            if self.db:
                await self.db.rollback()
            raise

        finally:
            # Cleanup cloned repo
            if repo_path:
                self.github_api.cleanup_repo(repo_path)

    def _generate_pr_body(self, bounty: Bounty, target: any) -> str:
        """Generate the PR description."""
        return f"""## Mohtion Bounty Claim

### Tech Debt Identified
**Type:** {target.debt_type.value}
**Location:** `{target.location}`
**Severity:** {target.severity:.2f}

{target.description}

### Refactoring Summary
{bounty.refactoring_summary}

### Verification
- Tests: Passed
- Retries: {bounty.retry_count}

---
*This PR was automatically generated by [Mohtion](https://github.com/your-org/mohtion)*
"""
