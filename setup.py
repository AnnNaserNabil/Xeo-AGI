from setuptools import setup, find_packages
import os

# Read the README for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
install_requires = []
if os.path.exists('requirements.txt'):
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        install_requires = [
            line.strip() 
            for line in f.read().split('\n') 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="xeo",
    version="0.2.0",
    author="Xeo Team",
    author_email="contact@xeo.ai",
    description="A modular framework for building autonomous agent systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xeoai/xeo-framework",
    packages=find_packages(include=['xeo', 'xeo.*']),
    package_data={
        'xeo': ['py.typed'],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Typing :: Typed",
    ],
    python_requires='>=3.8',
    install_requires=install_requires or [
        # Core dependencies
        "pydantic>=2.0.0",
        "typing-extensions>=4.5.0",
        "aiohttp>=3.9.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0.0",
        "tenacity>=8.2.0",
    ],
    extras_require={
        "llm": [
            "google-generativeai>=0.3.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings[python]>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "xeo=xeo.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
