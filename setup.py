from setuptools import setup

setup(
    name="pycheckers",
    version="0.0.3",
    install_requires=[
        "graphics.py",
    ],
    packages=["pycheckers"],
    entry_points={
        "console_scripts": [
            "checkers = pycheckers.host:main",
        ],
    },
)
