from setuptools import setup, find_packages


setup(
    name="agentprofit",
    version="1.0.0",
    description="Agent Profit Coach API",
    author="Afinetrip",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic-settings",
        "redis",
        "pytest"
    ],
)