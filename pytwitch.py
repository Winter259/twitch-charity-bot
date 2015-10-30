import socket
from winsound import Beep
from time import sleep
from cfg import *

def pause(prompt='', amount=5):
    ticks = amount
    print(prompt)
    while ticks > 0:
        print('[*] Pause ends in: {}  '.format(ticks), end='\r')
        sleep(1)
        ticks -= 1
    # print('[+] Pause ended, continuing now!')

def print_list(prompt='', list_to_print=[]):
    if len(list_to_print) == 0:
        print('[-] Attempted to print an empty list!')
    else:
        print('[+] {}'.format(prompt))
        for element in list_to_print:
            print('\t\t> {}'.format(element))

HOST = 'irc.twitch.tv'  # the Twitch IRC server
PORT = 6667             # always use port 6667!
DATA_BUFFER_SIZE = 1024
INITIAL_BUFFER_SIZE = 4098
GITHUB_URL = r'https://github.com/Winter259/twitch-charity-bot/tree/charity-stream'
CHECK_TICK = 5
CYCLES_FOR_PROMPT = 15

def get_donation_amount():
    pass

def get_time_left():
    pass

def get_percent_left():
    pass

class Twitch:
    def __init__(self, name='', token='', channel=''):
        self.name = name
        self.token = token
        self.channel = channel
        self.connection = socket.socket()
        self.cycle_count = 0
        print('[!] Purrbot initialised and connected!')
        print('[+] Initial buffer content:')
        self.print_response(INITIAL_BUFFER_SIZE)

    def run(self):
        while True:
            print('[+] Purrbot is on cycle: {}'.format(self.cycle_count))
            # get donation amount
            get_donation_amount()
            # if donation amount has changed, post the prompt
            # if not, check if cycle count has exceeded the amount required for a prompt
            # if not, check for purrbot info command
            # if not, wait for the check tick
            pause('[+] Holding for next cycle', CHECK_TICK)
            self.cycle_count += 1

    def connect(self, channel=''):
        if len(channel) == 0:
            print('[-] No channel passed to Purrbot!')
        else:
            try:
                self.connection.connect((HOST, PORT))
                self.connection.send("PASS {}\r\n".format(PASS).encode("utf-8"))
                self.connection.send("NICK {}\r\n".format(NICK).encode("utf-8"))
                self.connection.send("JOIN {}\r\n".format(channel).encode("utf-8"))
                print('[+] Purrbot has successfully connected to the twitch irc channel: {}'.format(channel))
                return channel
            except Exception as e:
                print('[-] Purrbot did not manage to connect! Exception occurred: {}'.format(e))
                exit(0)

    def receive_data(self, buffer=DATA_BUFFER_SIZE):
        print('[+] Purrbot is waiting for data to come in from the stream')
        response = self.connection.recv(buffer)
        return response.decode('utf-8')

    def print_response(self, buffer=DATA_BUFFER_SIZE):
        decoded_response = self.receive_data(buffer)
        print('Response: {}'.format(decoded_response))

    def post_in_channel(self, chat_string=''):
        if len(chat_string) == 0:
            print('[-] No string passed to be posted to the chat!')
        else:
            print('[?] Attempting to post the string:')
            print('\t', chat_string)
            try:
                self.connection.send('PRIVMSG {} :{}\r\n'.format(self.channel, chat_string).encode('utf-8'))
                print('[!] String posted successfully!')
                return True
            except Exception as e:
                print('[-] Exception occurred: {}'.format(str(e)))
                return False