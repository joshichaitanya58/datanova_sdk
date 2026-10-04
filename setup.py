import os
from setuptools import setup, find_packages

readme_path = os.path.join(os.path.dirname(__file__), "README.md")
long_description = open(readme_path, encoding="utf-8").read() if os.path.exists(readme_path) else ""

setup(
    name="datanova-sdk",
    version="1.0.0",
    description="Official Python SDK for DataNova Smart Analytics Platform REST APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DataNova Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0"
    ],
    extras_require={
        "async": ["httpx>=0.20.0"],
        "dev": ["pytest>=7.0.0", "pytest-asyncio>=0.20.0", "responses>=0.20.0", "httpx>=0.20.0"]
    },
    python_requires=">=3.8",
    keywords=["analytics", "machine-learning", "data-science", "datanova", "sdk", "rest-api"],
    project_urls={
        "Homepage": "https://datanova-fude.onrender.com",
        "Documentation": "https://datanova-fude.onrender.com ",
        "Repository": "https://github.com/joshichaitanya58/datanova"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
