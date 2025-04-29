from setuptools import setup, find_packages

setup(
    name="pva2",
    version="0.1.0",
    description="Scientific benchmarking tool for Python test frameworks",
    author="Joshua Nöldeke",
    author_email="youremail@example.com",
    url="https://github.com/joshuanoeldeke/PVA2",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        # Core dependencies
        "iniconfig",
        "numpy",
        "packaging",
        "pluggy",
        "psutil",
        "pytest",
        "scipy",
        # Reporting and visualization
        "pandas",
        "matplotlib",
        "seaborn",
        # GIF animation
        "pillow",
        # CLI
        "click",
    ],
    entry_points={
        "console_scripts": [
            "run-benchmark=framework_comparison.run_benchmark:main",
            "generate-reports=framework_comparison.reporting:generate_reports",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
