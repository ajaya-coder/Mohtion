"""GitHub API operations - clone, branch, commit, push, create PR."""

import shutil
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

import httpx
from git import Repo

from mohtion.integrations.github_app import GitHubApp
from mohtion.utils import cleanup_path


@dataclass
class PRResult:
    """Result of creating a pull request."""

    url: str
    number: int
    html_url: str


class GitHubAPI:
    """GitHub API client for repository operations."""

    API_BASE = "https://api.github.com"

    def __init__(self, github_app: GitHubApp, installation_id: int) -> None:
        self.github_app = github_app
        self.installation_id = installation_id
        self._token: str | None = None

    async def _get_token(self) -> str:
        """Get installation token (lazy loaded)."""
        if self._token is None:
            self._token = await self.github_app.get_installation_token(
                self.installation_id
            )
        return self._token

    async def _headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        token = await self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def clone_repo(self, owner: str, repo: str) -> Path:
        """Clone a repository to a temporary directory."""
        token = await self._get_token()
        clone_url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"

        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix=f"mohtion_{repo}_"))
        Repo.clone_from(clone_url, temp_dir)
        return temp_dir

    def cleanup_repo(self, repo_path: Path) -> None:
        """Remove cloned repository directory."""
        cleanup_path(repo_path)

    def create_branch(self, repo_path: Path, base_branch: str = "main") -> str:
        """Create a new branch for the bounty."""
        branch_name = f"mohtion/bounty-{uuid.uuid4().hex[:8]}"
        with Repo(repo_path) as repo:
            # Checkout base branch and create new branch
            repo.git.checkout(base_branch)
            repo.git.checkout("-b", branch_name)
        return branch_name

    def commit_changes(
        self, repo_path: Path, file_path: Path, new_content: str, message: str
    ) -> None:
        """Commit changes to a file."""
        # Write the new content
        full_path = repo_path / file_path
        full_path.write_text(new_content)

        with Repo(repo_path) as repo:
            # Stage and commit
            repo.index.add([str(file_path)])
            repo.index.commit(message)

    async def push_branch(
        self, repo_path: Path, owner: str, repo_name: str, branch_name: str
    ) -> None:
        """Push a branch to remote."""
        token = await self._get_token()
        with Repo(repo_path) as repo:
            # Set up authenticated remote URL
            remote_url = f"https://x-access-token:{token}@github.com/{owner}/{repo_name}.git"
            repo.git.remote("set-url", "origin", remote_url)

            # Push the branch
            repo.git.push("--set-upstream", "origin", branch_name)

    async def get_installation_info(self) -> dict:
        """Get details about the current installation."""
        return await self.github_app.get_installation(self.installation_id)

    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        branch_name: str,
        base_branch: str,
        title: str,
        body: str,
    ) -> PRResult:
        """Create a pull request."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/repos/{owner}/{repo}/pulls",
                headers=await self._headers(),
                json={
                    "title": title,
                    "body": body,
                    "head": branch_name,
                    "base": base_branch,
                },
            )
            response.raise_for_status()
            data = response.json()

        return PRResult(
            url=data["url"],
            number=data["number"],
            html_url=data["html_url"],
        )

    async def _get_repo_info(self, owner: str, repo: str) -> dict:
        """Get repository metadata."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/repos/{owner}/{repo}",
                headers=await self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def get_default_branch(self, owner: str, repo: str) -> str:
        """Get the default branch of a repository."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/repos/{owner}/{repo}",
                headers=await self._headers(),
            )
            response.raise_for_status()
            return response.json()["default_branch"]

    async def get_repo_contents(
        self, owner: str, repo: str, path: str = ""
    ) -> list[dict]:
        """Get contents of a repository path."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/repos/{owner}/{repo}/contents/{path}",
                headers=await self._headers(),
            )
            response.raise_for_status()
            return response.json()
