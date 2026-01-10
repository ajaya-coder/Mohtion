"""Code analyzers for tech debt detection."""

from mohtion.analyzers.base import Analyzer
from mohtion.analyzers.complexity import ComplexityAnalyzer
from mohtion.analyzers.duplicate import DuplicateAnalyzer
from mohtion.analyzers.type_checker import TypeHintAnalyzer

__all__ = ["Analyzer", "ComplexityAnalyzer", "DuplicateAnalyzer", "TypeHintAnalyzer"]
