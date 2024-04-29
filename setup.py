from setuptools import setup

setup(
    name="pycheckers",
    version="0.0.1",
    install_requires=[
        "socket",
        "pickle",
        "tkinter",
        "random",
        "time",
        "graphics.py",
    ],
    packages=["pycheckers"],
    entry_points={
        "console_scripts": [
            "checkers = pycheckers.host:main",
        ],
    },
)
