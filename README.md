# twitch-charity-bot

A bot written initially for a twitch charity stream which scrapes the amount donated, checks if it has changed and if yes posts a prompt to the twitch chat.
It also does intermittent prompts for donations to the charity. It can be adjusted to show things like how long the stream has been going for.

**Requirements:**

- Python 3.x

Tested against:

* 3.4
* 3.5

**Python modules required:**

- BeautifulSoup4

Use ```pip install BeautifulSoup4```

**Usage:**

- Place a file, "cfg.py", with the contents as described in main.py in the same directory
- Place a file, "charitycfg.py", with the contents as described in main.py in the same directory
- Run ```python main.py```