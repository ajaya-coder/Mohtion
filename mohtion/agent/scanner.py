"""Scanner - Reconnaissance phase of the agent loop."""

import logging
from pathlib import Path

from mohtion.analyzers.complexity import ComplexityAnalyzer
from mohtion.analyzers.duplicate import DuplicateAnalyzer
from mohtion.analyzers.type_checker import TypeHintAnalyzer
from mohtion.models.repo_config import RepoConfig
from mohtion.models.target import TechDebtTarget

logger = logging.getLogger(__name__)


class Scanner:
    """Scans a repository for tech debt targets."""

    def __init__(self, repo_path: Path, config: RepoConfig) -> None:
        self.repo_path = repo_path
        self.config = config
        self.analyzers = self._init_analyzers()

    def _init_analyzers(self) -> list:
        """Initialize enabled analyzers based on config."""
        analyzers = []

        if "complexity" in self.config.analyzers:
            analyzers.append(ComplexityAnalyzer(self.config))

        if "type_hints" in self.config.analyzers:
            analyzers.append(TypeHintAnalyzer(self.config))

        if "duplicates" in self.config.analyzers:
            analyzers.append(DuplicateAnalyzer(self.config))

        return analyzers

    async def scan(self) -> list[TechDebtTarget]:
        """
        Scan the repository for tech debt.

        Returns:
            List of tech debt targets, sorted by severity (highest first)
        """
        logger.info(f"Scanning repository at {self.repo_path}")
        targets: list[TechDebtTarget] = []

        # Find all Python files
        python_files = list(self.repo_path.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files")

        for file_path in python_files:
            relative_path = file_path.relative_to(self.repo_path)

            # Skip ignored paths
            if any(
                str(relative_path).startswith(ignore.rstrip("*").rstrip("/"))
                for ignore in self.config.ignore_paths
                if not ignore.startswith("**")
            ):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError) as e:
                logger.warning(f"Failed to read {relative_path}: {e}")
                continue

            # Run all analyzers on this file
            for analyzer in self.analyzers:
                try:
                    file_targets = await analyzer.analyze_file(relative_path, content)
                    targets.extend(file_targets)
                except Exception as e:
                    logger.warning(f"Analyzer {analyzer.name} failed on {relative_path}: {e}")

        # Sort by severity (highest first)
        targets.sort(key=lambda t: t.severity, reverse=True)

        logger.info(f"Found {len(targets)} tech debt targets")
        return targets

    async def get_top_target(self) -> TechDebtTarget | None:
        """Get the highest-priority tech debt target."""
        targets = await self.scan()
        return targets[0] if targets else None
