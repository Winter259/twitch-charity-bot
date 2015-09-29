import socket
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
STREAMER_NAME = 'selezen'  # name of the streamer doing the charity stream.
URL = 'https://www.justgiving.com/selezen/'  # the url you will be scraping the information from
PROMPT_TICK_TIME = 10 * 60  # interval in seconds between when the bot will post prompts
TICK_TIME = 10  # time in seconds between when the bot checks for new donations
"""

def pause(prompt='', amount=5):
    ticks = amount
    print(prompt)
    while ticks > 0:
        print('Pause ends in: {}  '.format(ticks), end='\r')
        sleep(1)
        ticks -= 1
    print('Pause ended, continuing now!')


def connect_to_twitch(channel=CHAN):
    irc = socket.socket()
    try:
        irc.connect((HOST, PORT))
        irc.send("PASS {}\r\n".format(PASS).encode("utf-8"))
        irc.send("NICK {}\r\n".format(NICK).encode("utf-8"))
        irc.send("JOIN {}\r\n".format(channel).encode("utf-8"))
        print('Bot connected to twitch!')
        return irc
    except Exception as e:
        print(str(e))
        print('Bot did not manage to connect!')
        exit(0)


def twitch_ping_pong(decoded_data):
    if decoded_data.find('PING') != -1:
        print('Bot responding to the irc ping with a pong!')
        pong_string = bytes(decoded_data.replace('PING', 'PONG'), 'utf-8')
        irc.send(pong_string)
        pause('Waiting for after the PONG', 5)


def post_to_twitch_chat(chat_string='', channel=CHAN):
    if len(chat_string) == 0:
        print('[-] No string passed to be posted to the chat!')
    print('[*] Attempting to post the string: {}'.format(chat_string))
    try:
        irc.send(bytes('PRIVMSG {} :{}\r\n'.format(channel, chat_string), 'utf-8'))
        print('[+] String posted successfully!')
        return True
    except Exception as e:
        print('[-] Exception occured: {}'.format(str(e)))
        print('[-] Closing the connection...')
        irc.close()
        pause('Waiting for connection to close properly...', 5)
        return False


def beep_speaker(ping_amount=2, delay=1.0):
    for tick in range(0, ping_amount):
        Beep(200, 200)
        sleep(delay)


print('--- Starting bot! ---\n')
connected = False
cycle = 0
streamers = ['mahddogg', 'bubblemapgaminglive', 'kerrashlanding', 'fireytoad']
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
        multitwitch_url = r'http://multitwitch.tv/MahdDogg/BubbleMapGamingLive/FireyToad/KerrashLanding'
        post_string = 'Watch all four of the mayhem all star stream team here!: {}'.format(multitwitch_url)
        connection = post_to_twitch_chat(post_string, '#{}'.format(streamer))
        sleep(2)
        if connection:
            print('[+] Closing the connection...')
            irc.close()
            pause('[+] Waiting for connection to close properly...', 10)
    pause('[+] Waiting for next Cycle', TICK_TIME)
    print('--- Finished cycle: {} ---'.format(cycle))
    cycle += 1
