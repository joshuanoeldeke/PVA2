import os
from pathlib import Path

class TestDiscovery:
    def discover_migration_pairs(self, dataset_path):
        """Discover before/after migration pairs in TestMigrationsInPy dataset."""
        migration_pairs = []
        
        for project_dir in Path(dataset_path).glob("*/diff"):
            before_files = list(project_dir.glob("*-before-*.py"))
            for before_file in before_files:
                after_file = project_dir / before_file.name.replace("-before-", "-after-")
                if after_file.exists():
                    migration_pairs.append((str(before_file), str(after_file)))
        
        return migration_pairs
