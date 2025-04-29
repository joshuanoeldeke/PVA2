# Use official Python runtime as a parent image
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy dependency declarations
COPY pyproject.toml setup.py requirements.txt ./

# Install OS-level build dependencies and clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies and the pva2 package
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install .

# Copy the rest of the application
COPY src/ /app/src/
COPY test_cases/ /app/test_cases/
COPY tests/ /app/tests/
COPY docs/ /app/docs/

# Default entrypoint: run the benchmark CLI
ENTRYPOINT ["run-benchmark"]
# Example default cmd; override as needed
CMD ["--help"]