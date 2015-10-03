from pytwitch import *
from time import *
from winsound import Beep
from cfg import *

"""
Include a file called cfg.py in the same directory as main.py with the following:
HOST = "irc.twitch.tv"              # the Twitch IRC server
PORT = 6667                         # always use port 6667!
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


print('--- Starting bot! ---\n')
connected = False
cycle = 0
#streamers = ['rheaayase', 'kateclick', 'blackmazetv']
streamers = ['kateclick']
while True:
    print('\n--- Starting cycle: {} ---'.format(cycle))
    for streamer in streamers:
        print('[+] Posting multitwitch link to: {}'.format(streamer))
        irc = connect_to_twitch('#{}'.format(streamer))
        data = irc.recv(4096) # get output
        received_data = data.decode('utf-8')
        sleep(1)
        twitch_ping_pong(received_data)
        beep_speaker(1, 0.1) # beep 4 times for donation
        #multitwitch_url = r'http://www.multitwitch.tv/RheaAyase/Kateclick/BlackMazeTV'
        multitwitch_url = r'http://www.multitwitch.tv/RheaAyase/Kateclick'
        # post_string = 'Watch all three of the mayhem open race streamers here!: {}'.format(multitwitch_url)
        post_string = 'Bot url test! {}'.format(multitwitch_url)
        connection = post_to_twitch_chat(post_string, '#{}'.format(streamer))
        sleep(2)
        if connection:
            print('[+] Closing the connection...')
            irc.close()
            pause('[+] Waiting for connection to close properly...', 10)
    pause('[+] Waiting for next Cycle', PROMPT_TICK_TIME)
    print('--- Finished cycle: {} ---'.format(cycle))
    cycle += 1
