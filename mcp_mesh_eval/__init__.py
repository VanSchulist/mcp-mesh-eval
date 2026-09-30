"""mcp-mesh-eval: Empirical Model Context Protocol Benchmark Suite.

Author: Van Schulist (@VanSchulist / Existential Cloud)
License: MIT
"""

__version__ = "1.0.0"

from .models import FRONTIER_MODELS, ModelProfile
from .engine import BenchmarkHarness, EvalResult
from .reporter import BenchmarkReporter

__all__ = [
    "FRONTIER_MODELS",
    "ModelProfile",
    "BenchmarkHarness",
    "EvalResult",
    "BenchmarkReporter",
]
