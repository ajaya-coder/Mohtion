"""Tests for expanded analyzers (Type Hints and Duplicates)."""

import pytest
from pathlib import Path

from mohtion.analyzers.type_checker import TypeHintAnalyzer
from mohtion.analyzers.duplicate import DuplicateAnalyzer
from mohtion.models.repo_config import RepoConfig
from mohtion.models.target import DebtType


@pytest.fixture
def type_analyzer() -> TypeHintAnalyzer:
    config = RepoConfig()
    return TypeHintAnalyzer(config)


@pytest.fixture
def duplicate_analyzer() -> DuplicateAnalyzer:
    config = RepoConfig()
    return DuplicateAnalyzer(config)


# --- Type Hint Tests ---

@pytest.mark.asyncio
async def test_detects_missing_types(type_analyzer: TypeHintAnalyzer) -> None:
    """Functions missing type hints should be detected."""
    code = """
def no_types(a, b):
    return a + b
"""
    targets = await type_analyzer.analyze_file(Path("test.py"), code)
    assert len(targets) == 1
    assert targets[0].debt_type == DebtType.TYPE_HINTS
    assert targets[0].function_name == "no_types"
    assert "Missing type hints" in targets[0].description


@pytest.mark.asyncio
async def test_ignores_typed_functions(type_analyzer: TypeHintAnalyzer) -> None:
    """Functions with type hints should be ignored."""
    code = """
def fully_typed(a: int, b: int) -> int:
    return a + b
"""
    targets = await type_analyzer.analyze_file(Path("test.py"), code)
    assert len(targets) == 0


@pytest.mark.asyncio
async def test_partial_types(type_analyzer: TypeHintAnalyzer) -> None:
    """Functions with partial types should still be flagged."""
    code = """
def partial(a: int, b):
    return a + b
"""
    targets = await type_analyzer.analyze_file(Path("test.py"), code)
    assert len(targets) == 1
    assert targets[0].debt_type == DebtType.TYPE_HINTS
    assert targets[0].function_name == "partial"


@pytest.mark.asyncio
async def test_low_severity_private(type_analyzer: TypeHintAnalyzer) -> None:
    """Private functions should have lower severity."""
    code = """
def _private(x):
    pass
"""
    targets = await type_analyzer.analyze_file(Path("test.py"), code)
    # Severity might be low enough to be filtered out (threshold 0.3)
    # _private: missing 2/2 -> ratio 1.0. Private * 0.5 = 0.5.
    # 0.5 > 0.3, so it should be returned.
    assert len(targets) == 1
    assert targets[0].severity <= 0.5


# --- Duplicate Tests ---

@pytest.mark.asyncio
async def test_detects_structural_duplicates(duplicate_analyzer: DuplicateAnalyzer) -> None:
    """Functions with identical logic but different variable names should be flagged."""
    code = """
def calculate_area(width, height):
    area = width * height
    return area

def get_size(w, h):
    s = w * h
    return s
"""
    targets = await duplicate_analyzer.analyze_file(Path("test.py"), code)
    assert len(targets) == 2
    assert "Structural duplication found" in targets[0].description


@pytest.mark.asyncio
async def test_ignores_unique_code(duplicate_analyzer: DuplicateAnalyzer) -> None:
    """Different functions should not be flagged."""
    code = """
def func_a(x):
    return x * 2

def func_b(x):
    return x + 2
"""
    targets = await duplicate_analyzer.analyze_file(Path("test.py"), code)
    assert len(targets) == 0


@pytest.mark.asyncio
async def test_ignores_trivial_code(duplicate_analyzer: DuplicateAnalyzer) -> None:
    """Too short functions should be ignored even if identical."""
    code = """
def getter_a(self):
    return self.a

def getter_b(self):
    return self.a
"""
    # These 2-line functions should be skipped by the "lines < 3" check
    targets = await duplicate_analyzer.analyze_file(Path("test.py"), code)
    assert len(targets) == 0


@pytest.mark.asyncio
async def test_ignores_docstrings_in_duplicates(duplicate_analyzer: DuplicateAnalyzer) -> None:
    """Functions differing only by docstrings should be flagged as duplicates."""
    # Must be at least 3 lines of logic
    code = """
def func_a(x):
    '''This is function A'''
    y = x * x
    z = y + 1
    return z

def func_b(x):
    '''This is function B with different docstring'''
    y = x * x
    z = y + 1
    return z
"""
    targets = await duplicate_analyzer.analyze_file(Path("test.py"), code)
    assert len(targets) == 2
