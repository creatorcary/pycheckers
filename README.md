# Pycheckers
A simple 2D checkers game with multiplayer functionality built with graphics.py by John Zelle.

Find his library here: https://pypi.org/project/graphics.py/


## Installation
For system-wide installation: `sudo pip install pycheckers`

User installation: `pip install pycheckers`

You will need Tkinter, the low-level Python GUI package and dependency of graphics.py. If it's not already installed, run `sudo apt-get install python3-tk` (or the equivalent for your package manager).


## Usage
1. In a Linux terminal, run the command `checkers`.
2. Enter 0 to spectate a simulation, 1 to play against the AI, or 2 for a multiplayer match.
3. For a multiplayer match, either select to host or join. Someone must first host in order for someone else to join.
4. The person who selects join must enter either the IP address or the hostname of the host. These are both displayed in the host's terminal.
5. Upon connecting, black player (the host) goes first. Play continues until someone wins, and the connection closes.


The rules of the game can be found here: https://gamerules.com/rules/checkers-rules/
