"""Setup configuration for Temporal Worker SDK."""

from setuptools import setup, find_packages

setup(
    name="temporal-worker-sdk",
    version="0.1.0",
    description="Production-grade Python SDK for running Temporal workers with zero boilerplate",
    author="Finubit",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "temporalio>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "prometheus-client>=0.17.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
)
