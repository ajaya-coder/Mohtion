"""Type hint analyzer using Python AST."""

import ast
import logging
from pathlib import Path
from typing import Any

from mohtion.analyzers.base import Analyzer
from mohtion.models.target import DebtType, TechDebtTarget

logger = logging.getLogger(__name__)


class TypeHintVisitor(ast.NodeVisitor):
    """AST visitor that finds missing type hints."""

    def __init__(self) -> None:
        self.functions: list[dict[str, Any]] = []
        self._current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track current class context."""
        old_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze a function definition."""
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Analyze an async function definition."""
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # Check arguments
        missing_arg_types = 0
        total_args = 0

        for arg in node.args.args:
            # Skip self/cls for methods
            if arg.arg in ('self', 'cls'):
                continue

            total_args += 1
            if arg.annotation is None:
                missing_arg_types += 1

        # Check keyword-only arguments
        for arg in node.args.kwonlyargs:
            total_args += 1
            if arg.annotation is None:
                missing_arg_types += 1

        # Check return type
        has_return_type = node.returns is not None

        # Calculate score (0.0 to 1.0) of missing types
        # Count return type as 1 "unit" of typing
        total_points = total_args + 1
        missing_points = missing_arg_types + (1 if not has_return_type else 0)

        if missing_points > 0:
            self.functions.append({
                "name": node.name,
                "class_name": self._current_class,
                "start_line": node.lineno,
                "end_line": node.end_lineno or node.lineno,
                "missing_points": missing_points,
                "total_points": total_points,
                "missing_ratio": missing_points / total_points
            })


class TypeHintAnalyzer(Analyzer):
    """Analyzer for missing type hints in Python files."""

    @property
    def name(self) -> str:
        return "type_hints"

    async def analyze_file(self, file_path: Path, content: str) -> list[TechDebtTarget]:
        """Analyze a Python file for missing type hints."""
        # Only analyze Python files
        if file_path.suffix != ".py":
            return []

        if not self.should_analyze(file_path):
            return []

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return []

        visitor = TypeHintVisitor()
        visitor.visit(tree)

        targets = []
        lines = content.split("\n")

        for func in visitor.functions:
            # Extract the function code
            start = func["start_line"] - 1
            end = func["end_line"]
            code_snippet = "\n".join(lines[start:end])

            # Calculate severity
            # Base severity on the ratio of missing types
            severity = func["missing_ratio"]

            # Reduce severity for private functions
            if func["name"].startswith("_") and not func["name"].startswith("__"):
                severity *= 0.5

            # Increase severity if it's a public API (no class, or public class)
            if not func["class_name"] and not func["name"].startswith("_"):
                severity *= 1.2

            # Cap at 1.0
            severity = min(1.0, severity)

            # Only report if severity > 0.3 to avoid noise
            if severity < 0.3:
                continue

            target = TechDebtTarget(
                file_path=file_path,
                start_line=func["start_line"],
                end_line=func["end_line"],
                debt_type=DebtType.TYPE_HINTS,
                severity=severity,
                description=f"Missing type hints ({int(func['missing_ratio']*100)}% missing)",
                code_snippet=code_snippet,
                function_name=func["name"],
                class_name=func["class_name"],
                metric_value=float(func["missing_points"]),
            )
            targets.append(target)

        return targets
