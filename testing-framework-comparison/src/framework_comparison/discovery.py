from pathlib import Path

class TestDiscovery:
    """Discover and prepare test files for comparison."""

    def discover_migration_pairs(self, dataset_path):
        """Find before/after test pairs in TestMigrationsInPy format."""
        migration_pairs = []

        for project_dir in Path(dataset_path).glob("projects/*"):
            for diff_dir in project_dir.glob("diff"):
                # Find matching before/after files
                before_files = list(diff_dir.glob("*-before-*.py"))
                for before in before_files:
                    after = diff_dir / before.name.replace("-before-", "-after-")
                    if after.exists():
                        migration_pairs.append((before, after))

        return migration_pairs
