"Duplicate code analyzer using Python AST."

import ast
import hashlib
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from mohtion.analyzers.base import Analyzer
from mohtion.models.target import DebtType, TechDebtTarget

logger = logging.getLogger(__name__)


class VariableNormalizer(ast.NodeTransformer):
    """
    Normalizes variable names in an AST to generic placeholders. 
    
    Converts:
        def add(a, b): return a + b
    To:
        def arg_0(var_0, var_1): return var_0 + var_1
    """

    def __init__(self):
        self.mapping = {}
        self.counter = 0

    def _get_name(self, original_name: str) -> str:
        if original_name not in self.mapping:
            self.mapping[original_name] = f"var_{self.counter}"
            self.counter += 1
        return self.mapping[original_name]

    def visit_arg(self, node: ast.arg) -> ast.arg:
        # Normalize argument names
        node.arg = self._get_name(node.arg)
        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        # Normalize variable usage
        if isinstance(node.ctx, (ast.Load, ast.Store)):
             node.id = self._get_name(node.id)
        return node


class DuplicateVisitor(ast.NodeVisitor):
    """AST visitor that finds duplicate function bodies."""

    def __init__(self) -> None:
        self.blocks: list[dict[str, Any]] = []
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
        # We want to check if the logic (body) is identical
        if not node.body:
            return

        # Create a dummy module to hold the body for normalization
        # We use a copy of the body nodes to avoid modifying the original tree
        import copy
        body_nodes = copy.deepcopy(node.body)
        body_node = ast.Module(body=body_nodes, type_ignores=[])

        # Remove docstring if present
        if (
            len(body_node.body) > 0
            and isinstance(body_node.body[0], ast.Expr)
            and isinstance(body_node.body[0].value, ast.Constant)
            and isinstance(body_node.body[0].value.value, str)
        ):
            body_node.body = body_node.body[1:]

        # Normalize variables for structural comparison
        normalizer = VariableNormalizer()

        # Pre-seed normalizer with arguments so they are mapped consistently (var_0, var_1...)
        # We don't modify the function arguments themselves here, just update the mapping
        for arg in node.args.args:
             normalizer._get_name(arg.arg)

        normalized_tree = normalizer.visit(body_node)

        try:
            # unparse() produces canonical code representation
            normalized_code = ast.unparse(normalized_tree).strip()
        except Exception:
            # Fallback for complex ASTs
            return

        # Skip trivial functions (empty, pass, or too short)
        if not normalized_code or normalized_code == "pass":
            return

        # Heuristic: Skip functions with fewer than 3 lines of logic
        if len(normalized_code.splitlines()) < 3:
            return

        code_hash = hashlib.md5(normalized_code.encode("utf-8")).hexdigest()

        self.blocks.append({
            "name": node.name,
            "class_name": self._current_class,
            "start_line": node.lineno,
            "end_line": node.end_lineno or node.lineno,
            "hash": code_hash,
            # Production Optimization: Don't store full 'normalized_code' string in memory
            # The hash is enough for detection.
            "line_count": len(normalized_code.splitlines())
        })


class DuplicateAnalyzer(Analyzer):
    """Analyzer for identifying duplicate code blocks within a file."""

    @property
    def name(self) -> str:
        return "duplicates"

    async def analyze_file(self, file_path: Path, content: str) -> list[TechDebtTarget]:
        """Analyze a Python file for duplicate code."""
        if file_path.suffix != ".py":
            return []

        if not self.should_analyze(file_path):
            return []

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return []

        visitor = DuplicateVisitor()
        visitor.visit(tree)

        # Group by hash
        hash_groups = defaultdict(list)
        for block in visitor.blocks:
            hash_groups[block["hash"]].append(block)

        targets = []
        lines = content.split("\n")

        for code_hash, group in hash_groups.items():
            if len(group) > 1:
                # Found duplicates!
                group.sort(key=lambda x: x["start_line"])

                for i, block in enumerate(group):
                    other_locations = [
                        f"{b['name']} (line {b['start_line']})"
                        for j, b in enumerate(group) if i != j
                    ]

                    description = (
                        f"Structural duplication found. "
                        f"Logic matches {', '.join(other_locations)}."
                    )

                    # Extract original code for the snippet
                    start = block["start_line"] - 1
                    end = block["end_line"]
                    code_snippet = "\n".join(lines[start:end])

                    # Severity calculation
                    base_severity = min(1.0, block["line_count"] / 20)
                    multiplier = 1.0 + (0.1 * (len(group) - 1))
                    severity = min(1.0, base_severity * multiplier)

                    target = TechDebtTarget(
                        file_path=file_path,
                        start_line=block["start_line"],
                        end_line=block["end_line"],
                        debt_type=DebtType.DUPLICATE,
                        severity=severity,
                        description=description,
                        code_snippet=code_snippet,
                        function_name=block["name"],
                        class_name=block["class_name"],
                        metric_value=float(len(group)),
                    )
                    targets.append(target)

        return targets
