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
GITHUB = r'https://github.com/Winter259/twitch-charity-bot/tree/charity-stream'
PROMPT_DELAY = 60 * 15

class Twitch:
    def __init__(self, name='', token='', channel=''):
        self.name = name
        self.token = token
        self.connection = socket.socket()
        self.cycle = 0
        print('[!] Purrbot initialised and connected!')
        print('[+] Initial buffer content:')
        self.print_response(INITIAL_BUFFER_SIZE)

    def run(self):
        while True:
            print('[+] Purrbot is on cycle: {}'.format(self.cycle))
            decoded_response = self.receive_data()  # get response once
            # TODO if the response matches something like a command or a link, respond instantly
            print_list('Current queue:', self.queue)
            current_prompt = self.queue.pop(0)
            print('[+] Purrbot has popped {} from the front of the queue'.format(current_prompt))
            self.post_in_channel(current_prompt)
            pause('[+] Holding for next cycle', PROMPT_DELAY)
            self.cycle += 1

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
                print('[-] Bot did not manage to connect! Exception occurred: {}'.format(e))
                exit(0)

    def receive_data(self, buffer=DATA_BUFFER_SIZE):
        print('[+] Purrbot is waiting for data to come in from the stream')
        response = self.connection.recv(buffer)
        return response.decode('utf-8')

    def print_response(self, buffer=DATA_BUFFER_SIZE):
        decoded_response = self.receive_data(buffer)
        print('Response: {}'.format(decoded_response))

    def ping_pong(self):
        print('[!] Purrbot has confirmed its connection to the twitch IRC. Checks so far: {}'.format(self.connection_checks))
        self.connection.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))

    def post_in_channel(self, chat_string=''):
        if len(chat_string) == 0:
            print('[-] No string passed to be posted to the chat!')
        else:
            print('[?] Attempting to post the string: {}'.format(chat_string))
            try:
                self.connection.send('PRIVMSG {} :{}\r\n'.format(self.channel, chat_string).encode('utf-8'))
                print('[!] String posted successfully!')
                return True
            except Exception as e:
                print('[-] Exception occurred: {}'.format(str(e)))
                return False