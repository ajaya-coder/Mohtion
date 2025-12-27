#!/usr/bin/env python3
"""Full agent loop test - will create a real PR!"""
import asyncio
import logging
from pathlib import Path

from mohtion.agent.orchestrator import Orchestrator
from mohtion.integrations.github_api import GitHubAPI
from mohtion.integrations.github_app import GitHubApp
from mohtion.models.repo_config import RepoConfig, Thresholds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CustomOrchestrator(Orchestrator):
    """Orchestrator with custom config."""

    async def run(self, base_branch: str = "main") -> any:
        """Run with custom low threshold config."""
        repo_path: Path | None = None

        try:
            # Clone the repository
            logger.info(f"Cloning {self.owner}/{self.repo}...")
            repo_path = await self.github_api.clone_repo(self.owner, self.repo)
            logger.info(f"Cloned to {repo_path}")

            # Use LOW threshold config
            config = RepoConfig(
                thresholds=Thresholds(
                    cyclomatic_complexity=5,  # Low threshold to catch the targets
                    function_length=50,
                    nesting_depth=4
                )
            )

            # Now run the normal orchestrator flow with this config
            from mohtion.agent.scanner import Scanner
            from mohtion.agent.refactor import Refactor
            from mohtion.agent.verifier import Verifier
            from mohtion.models.bounty import BountyResult, BountyStatus
            import uuid

            # Phase 1: RECONNAISSANCE
            logger.info("Phase 1: Reconnaissance")
            scanner = Scanner(repo_path, config)
            target = await scanner.get_top_target()

            if not target:
                logger.info("No tech debt targets found")
                return None

            logger.info(f"Target acquired: {target}")

            # Create bounty tracking
            branch_name = f"mohtion/bounty-{uuid.uuid4().hex[:8]}"
            bounty = BountyResult(
                target=target,
                status=BountyStatus.IN_PROGRESS,
                branch_name=branch_name,
            )

            # Create feature branch
            actual_branch = self.github_api.create_branch(repo_path, base_branch)
            bounty.branch_name = actual_branch

            # Phase 2: REFACTORING
            logger.info("Phase 2: Refactoring")
            refactor = Refactor(repo_path)
            result = await refactor.refactor_target(target)

            if not result.success:
                bounty.mark_failed(f"Refactoring failed: {result.error}")
                return bounty

            bounty.original_code = result.original_code
            bounty.refactored_code = result.refactored_code
            bounty.refactoring_summary = result.summary

            # Apply the refactoring
            if not await refactor.apply_refactoring(target, result.refactored_code):
                bounty.mark_failed("Failed to apply refactoring")
                return bounty

            # Phase 3: VERIFICATION
            logger.info("Phase 3: Verification")
            verifier = Verifier(repo_path, config)
            bounty.status = BountyStatus.TESTING

            for attempt in range(self.settings.max_retries + 1):
                test_result = await verifier.run_tests()
                bounty.test_output = test_result.output

                if test_result.passed:
                    bounty.test_passed = True
                    break

                # Log test output for debugging
                logger.error(f"Test output (attempt {attempt + 1}):\n{test_result.output}")

                # Self-healing attempt
                if attempt < self.settings.max_retries:
                    logger.info(f"Tests failed, attempting self-heal (attempt {attempt + 1})")
                    bounty.status = BountyStatus.RETRYING
                    bounty.retry_count = attempt + 1

                    heal_result = await refactor.attempt_self_heal(
                        target,
                        bounty.refactored_code,
                        test_result.output,
                    )

                    if heal_result.success:
                        bounty.refactored_code = heal_result.refactored_code
                        bounty.refactoring_summary += f"\n\n{heal_result.summary}"
                        await refactor.apply_refactoring(target, heal_result.refactored_code)
                    else:
                        bounty.mark_failed(f"Self-heal failed: {heal_result.error}")
                        return bounty

            if not bounty.test_passed:
                bounty.mark_failed("Tests failed after max retries")
                return bounty

            # Phase 4: BOUNTY CLAIM (Create PR)
            logger.info("Phase 4: Opening PR")

            # Commit the changes
            commit_message = f"refactor: {target.description}\n\nMohtion Bounty: {bounty.branch_name}"
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
            pr_title = f"[Mohtion] {target.debt_type.value}: {target.function_name or target.file_path.name}"
            pr_body = self._generate_pr_body(bounty)

            pr_result = await self.github_api.create_pull_request(
                owner=self.owner,
                repo=self.repo,
                branch_name=bounty.branch_name,
                base_branch=base_branch,
                title=pr_title,
                body=pr_body,
            )

            bounty.mark_success(pr_result.html_url, pr_result.number)
            logger.info(f"PR opened: {pr_result.html_url}")

            return bounty

        except Exception as e:
            logger.exception("Orchestrator failed")
            raise

        finally:
            # Don't cleanup on Windows to avoid permission errors
            if repo_path:
                logger.info(f"Temp directory: {repo_path}")


async def main():
    """Run the full test."""
    OWNER = "JulianCruzet"
    REPO = "test-for-mohtion"
    INSTALLATION_ID = 101273572

    logger.info("=" * 60)
    logger.info("FULL MOHTION AGENT LOOP TEST")
    logger.info("This will create a REAL pull request!")
    logger.info("=" * 60)

    github_app = GitHubApp()
    github_api = GitHubAPI(github_app, INSTALLATION_ID)

    orchestrator = CustomOrchestrator(github_api, OWNER, REPO)

    try:
        result = await orchestrator.run()

        if result:
            logger.info("=" * 60)
            logger.info("SUCCESS! Check your PR:")
            logger.info(f"  {result.pr_url}")
            logger.info("=" * 60)
        else:
            logger.info("No targets found to fix")

    except Exception as e:
        logger.exception("Test failed")


if __name__ == "__main__":
    asyncio.run(main())
