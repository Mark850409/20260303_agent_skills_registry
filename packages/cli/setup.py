from setuptools import setup, find_packages

setup(
    name="agentskills",
    version="1.0.1",
    description="CLI for AI Skills & Apps Registry — install, push & manage AI Skills & Apps",
    author="AgentSkills Team",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "click>=8.1",
        "rich>=13.0",
        "httpx>=0.27",
        "PyYAML>=6.0",
        "GitPython>=3.1",
    ],
    entry_points={
        "console_scripts": [
            "agentskills=agentskills.main:cli",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
