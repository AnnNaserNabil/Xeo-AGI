from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xeo",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A modular framework for building autonomous agent systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/xeo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        # Core dependencies
        "pydantic>=1.10.0",
        "typing-extensions>=4.0.0",
        "aiohttp>=3.8.0",
        
        # LLM dependencies (optional)
        # "google-generativeai>=0.3.0",  # Uncomment if using Gemini
        # "python-dotenv>=0.19.0",       # For loading environment variables
    ],
    extras_require={
        "llm": [
            "google-generativeai>=0.3.0",
            "python-dotenv>=0.19.0",
        ],
    },
    include_package_data=True,
)
