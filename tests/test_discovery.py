import os
import pytest
from src.framework_comparison.discovery import TestDiscovery

def test_discover_tests(tmp_path):
    # Setup a temporary project with nested test files
    proj = tmp_path / "proj"
    (proj / "subdir").mkdir(parents=True)
    f1 = proj / "test_a.py"
    f2 = proj / "subdir" / "test_b.py"
    f1.write_text("")
    f2.write_text("")
    td = TestDiscovery()
    files = td.discover_tests(str(proj))
    basenames = sorted(os.path.basename(f) for f in files)
    assert basenames == ["test_a.py", "test_b.py"]

def test_discover_migration_pairs(tmp_path):
    # Setup before/after files in a diff folder
    base = tmp_path / "proj" / "diff"
    base.mkdir(parents=True)
    before = base / "module-before-123.py"
    after = base / "module-after-123.py"
    before.write_text("# before")
    after.write_text("# after")
    td = TestDiscovery()
    pairs = td.discover_migration_pairs(str(tmp_path / "proj"))
    assert pairs == [(str(before), str(after))]