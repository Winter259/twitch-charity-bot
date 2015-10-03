from pytwitch import *

"""
Include a file called cfg.py in the same directory as main.py with the following:
NICK = "purrbot359"                 # your Twitch username, lowercase
PASS = "xyzxyyzxyhfdiufjdsoifjospi" # your Twitch OAuth token, get this from here: http://www.twitchapps.com/tmi/
CHAN = "#test"                      # the channel you want to join
STREAMER_NAME = 'test'              # name of the streamer
PROMPT_TICK_TIME = 10 * 60  # interval in seconds between when the bot will post prompts
"""

def main():
    print('--- Starting Purrbot! ---\n')
    purrbot = Twitch(NICK, PASS, CHAN)
    purrbot.run()


if __name__ == '__main__':
    main()