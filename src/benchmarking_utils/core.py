import psutil
import platform
from datetime import datetime
from pathlib import Path

from .runner import measure_performance_subprocess
from .serializer import get_summary, save_results


class PerformanceMetrics:
    """Encapsulates performance data collection for a test suite and framework."""

    def __init__(self, framework_name, test_suite_name, output_dir=None):
        self.framework = framework_name
        self.test_suite = test_suite_name

        if output_dir is None:
            base_dir = Path(__file__).resolve().parent.parent
            self.output_dir = base_dir / "results" / "raw_metrics"
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Prepare metadata container
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "platform": platform.platform(),
                "machine_type": platform.machine(),
                "processor": platform.processor(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "total_memory_mb": psutil.virtual_memory().total / 1024 / 1024,
                "python_version": platform.python_version(),
            },
            "framework": framework_name,
            "test_suite": test_suite_name,
            "runs": [],
        }

        # Record test framework version in metadata
        try:
            if framework_name.lower() == 'pytest':
                import pytest
                fw_version = pytest.__version__
            elif framework_name.lower() == 'unittest':
                fw_version = f"stdlib ({platform.python_version()})"
            else:
                from importlib.metadata import version as _md_version
                fw_version = _md_version(framework_name)
        except Exception:
            fw_version = 'unknown'
        self.results['metadata']['test_framework_version'] = fw_version

    # Delegate collected methods
    measure = measure_performance_subprocess
    get_summary = get_summary
    save_results = save_results