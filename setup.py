"""
RBAC Python - CodeBuddy Edition
基于角色的访问控制系统
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rbac-python-cbc",
    version="1.0.0",
    author="CodeBuddy",
    description="基于角色的访问控制系统（RBAC）",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rbac-python-cbc",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "sqlalchemy>=2.0.25",
        "psycopg2-binary>=2.9.9",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
        "supabase>=2.3.4",
        "loguru>=0.7.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.23.3",
            "httpx>=0.26.0",
            "black>=24.1.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "isort>=5.13.2",
        ],
        "test": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.23.3",
            "httpx>=0.26.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rbac-server=main:main",
        ],
    },
)
