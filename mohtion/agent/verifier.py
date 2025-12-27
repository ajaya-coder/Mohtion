"""Verifier - Safety phase of the agent loop."""

import asyncio
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

from mohtion.models.repo_config import RepoConfig

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of running tests."""

    passed: bool
    output: str
    return_code: int


class Verifier:
    """Runs tests to verify refactoring didn't break anything."""

    # Common test commands to try (in order)
    DEFAULT_TEST_COMMANDS = [
        "python -m pytest",  # Prefer this - uses pytest from current Python env
        "pytest",
        "python -m unittest discover",
        "npm test",
        "yarn test",
        "go test ./...",
        "cargo test",
    ]

    def __init__(self, repo_path: Path, config: RepoConfig) -> None:
        self.repo_path = repo_path
        self.config = config
        self._test_command: str | None = config.test_command

    async def detect_test_command(self) -> str | None:
        """Auto-detect the test command for this repository."""
        if self._test_command:
            return self._test_command

        # Check for common test configurations
        if (self.repo_path / "pyproject.toml").exists():
            self._test_command = "python -m pytest"
            return self._test_command

        if (self.repo_path / "setup.py").exists():
            self._test_command = "python -m pytest"
            return self._test_command

        if (self.repo_path / "package.json").exists():
            self._test_command = "npm test"
            return self._test_command

        if (self.repo_path / "go.mod").exists():
            self._test_command = "go test ./..."
            return self._test_command

        if (self.repo_path / "Cargo.toml").exists():
            self._test_command = "cargo test"
            return self._test_command

        # Try each default command
        for cmd in self.DEFAULT_TEST_COMMANDS:
            try:
                result = await self._run_command(cmd, timeout=10)
                if result.return_code != 127:  # 127 = command not found
                    self._test_command = cmd
                    return self._test_command
            except Exception:
                continue

        logger.warning("Could not detect test command")
        return None

    async def install_dependencies(self) -> bool:
        """Install dependencies from requirements.txt if it exists."""
        requirements_file = self.repo_path / "requirements.txt"

        if not requirements_file.exists():
            logger.info("No requirements.txt found, skipping dependency installation")
            return True

        logger.info("Installing dependencies from requirements.txt")
        result = await self._run_command(
            f"pip install -q -r {requirements_file}",
            timeout=180
        )

        if result.passed:
            logger.info("Dependencies installed successfully")
            return True
        else:
            logger.warning(f"Failed to install dependencies: {result.output}")
            return False

    async def run_tests(self, timeout: int = 300) -> TestResult:
        """
        Run the test suite.

        Args:
            timeout: Maximum time to wait for tests (seconds)

        Returns:
            TestResult with pass/fail status and output
        """
        # Install dependencies first
        await self.install_dependencies()

        test_command = await self.detect_test_command()

        if not test_command:
            logger.warning("No test command available, assuming pass")
            return TestResult(
                passed=True,
                output="No test command detected",
                return_code=0,
            )

        logger.info(f"Running tests: {test_command}")
        return await self._run_command(test_command, timeout=timeout)

    async def _run_command(self, command: str, timeout: int = 300) -> TestResult:
        """Run a shell command and capture output."""

        def _run() -> tuple[int, str]:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                output = result.stdout + result.stderr
                return result.returncode, output
            except subprocess.TimeoutExpired:
                return -1, f"Test command timed out after {timeout}s"
            except Exception as e:
                return -1, str(e)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return_code, output = await loop.run_in_executor(None, _run)

        passed = return_code == 0
        if passed:
            logger.info("Tests passed")
        else:
            logger.warning(f"Tests failed with code {return_code}")

        return TestResult(
            passed=passed,
            output=output,
            return_code=return_code,
        )

    async def verify_syntax(self, file_path: Path) -> bool:
        """Quick syntax check for Python files."""
        if file_path.suffix != ".py":
            return True

        full_path = self.repo_path / file_path
        try:
            content = full_path.read_text(encoding="utf-8")
            compile(content, str(file_path), "exec")
            return True
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return False
