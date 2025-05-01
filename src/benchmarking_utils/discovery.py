import os
from pathlib import Path

def discover_tests(self, project_root, pattern="test_*.py"):
    """Discover all test files in a project matching a glob pattern."""
    from pathlib import Path

    root = Path(project_root)
    test_files = [str(p) for p in root.rglob(pattern) if p.is_file()]
    return sorted(test_files)