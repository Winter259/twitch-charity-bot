from pytwitch import *
from time import *
from winsound import Beep

"""
Include a file called cfg.py in the same directory as main.py with the following:
NICK = "purrbot359"                 # your Twitch username, lowercase
PASS = "xyzxyyzxyhfdiufjdsoifjospi" # your Twitch OAuth token, get this from here: http://www.twitchapps.com/tmi/
CHAN = "#test"                      # the channel you want to join
STREAMER_NAME = 'test'              # name of the streamer
PROMPT_TICK_TIME = 10 * 60  # interval in seconds between when the bot will post prompts
"""

def pause(prompt='', amount=5):
    ticks = amount
    print(prompt)
    while ticks > 0:
        print('[*] Pause ends in: {}  '.format(ticks), end='\r')
        sleep(1)
        ticks -= 1
    print('[+] Pause ended, continuing now!')


def beep_speaker(ping_amount=2, delay=1.0):
    for tick in range(0, ping_amount):
        Beep(200, 200)
        sleep(delay)

print('--- Starting Purrbot! ---\n')
purrbot = Twitch(NICK, PASS, CHAN)
cycle = 1
while True:
    purrbot.check_connection()
    print('[+] Purrbot is on cycle: {}'.format(cycle))
    print('[+] Waiting for data input from the channel', end='\r')
    purrbot.post_in_channel('I am a bot and I am being tested! Cycle: {}'.format(cycle))
    pause('[+] Waiting for next Cycle', PROMPT_TICK_TIME)
    cycle += 1
