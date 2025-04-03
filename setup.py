from setuptools import setup, find_packages

setup(
    name="fellow",
    version="0.0.1",
    description="Fellow CLI tool is a command line development assistant",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Manuel Zierl",
    author_email="manuel.zierl@web.de",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.28.1",
        "openai>=1.69.0",
        "tiktoken>=0.9.0",
        "pexpect>=4.9.0",
        "pydantic~=2.11.0",
        "PyYAML~=6.0.2"
    ],
    entry_points={
        "console_scripts": [
            "fellow = fellow.main:main"
        ]
    },
    package_data={
        "fellow": ["default_fellow_config.yml"]
    }
)

