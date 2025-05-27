"""Setup configuration for Pharmaceutical Digital Twin Factory"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pharmaceutical-digital-twin",
    version="0.1.0",
    author="PDTF Team",
    author_email="team@pdtf.ai",
    description="AI + Quantum-powered digital twin platform for pharmaceutical manufacturing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JustGoingViral/Pharmaceutical-Digital-Twin",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
            "pre-commit>=3.3.0",
        ],
        "quantum": [
            "qiskit>=0.43.0",
            "qiskit-aer>=0.12.0",
            "amazon-braket-sdk>=1.50.0",
        ],
        "chemistry": [
            # "rdkit>=2023.3.1",  # Requires conda
            "mordred>=1.2.0",
            "pubchempy>=1.0.4",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdtf=core.cli:main",
            "pdtf-server=core.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.xml", "templates/*"],
    },
)