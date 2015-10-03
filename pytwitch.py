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
    print('[+] Pause ended, continuing now!')

def print_list(prompt='', list_to_print=[]):
    if len(list_to_print) == 0:
        print('[-] Attempted to print an empty list!')
    else:
        print('[+] {}'.format(prompt))
        for element in list_to_print:
            print('\t\t>{}'.format(element))

HOST = 'irc.twitch.tv'  # the Twitch IRC server
PORT = 6667             # always use port 6667!
DATA_BUFFER_SIZE = 1024
QUEUE_CHECK_DELAY = 10
CONNECTION_CHECK_DELAY = 3
GITHUB_URL = r'https://github.com/Winter259/twitch-charity-bot'

class Twitch():
    def __init__(self, name='', token='', channel=''):
        self.name = name
        self.token = token
        self.connection = socket.socket()
        self.connection_checks = 0
        self.channel = self.connect(channel)
        self.commands = {
            '!info': 'Purrbot is written by Purrcat259, you can find the source code on github here: {}'.format(GITHUB_URL)
        }
        self.prompt_cycle_interval = 5  # prompt every 5 cycles
        self.queue = ['Hello', 'my', 'name', 'is', 'Purrbot', '359']
        print('[!] Purrbot initialised and connected!')

    def run(self):
        cycle = 1
        while True:
            print('[+] Purrbot is on cycle: {}'.format(cycle))
            decoded_response = self.receive_data()  # get response once
            self.check_connection(decoded_response)  # always check connection first
            # TODO if the response matches something like a command or a link, respond instantly
            self.check_for_command(decoded_response)
            if len(self.queue) == 0:
                print('[+] Purrbot\'s queue is empty')
                pause('[+] Holding for next connection check', CONNECTION_CHECK_DELAY)
            else:
                print_list('Current queue:', self.queue)
                current_prompt = self.queue.pop(0)
                self.post_in_channel(current_prompt)
                pause('[+] Holding for next queue check', QUEUE_CHECK_DELAY)
            cycle += 1

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

    def receive_data(self):
        print('[+] Purrbot is waiting for data to come in from the stream')
        response = self.connection.recv(DATA_BUFFER_SIZE)
        return response.decode('utf-8')

    def print_response(self):
        decoded_response = self.receive_data()
        print('Response: {}'.format(decoded_response))

    def ping_pong(self):
        print('[!] Purrbot has confirmed its connection to the twitch IRC. Checks so far: {}'.format(self.connection_checks))
        self.connection.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))

    def check_connection(self, decoded_response):
        print('[?] Purrbot is checking if it is still connected')
        self.connection_checks += 1
        if decoded_response == 'PING :tmi.twitch.tv\r\n':
            self.ping_pong()
        else:
            print('[+] Purrbot does not need to respond to a ping')

    def post_in_channel(self, chat_string=''):
        if len(chat_string) == 0:
            print('[-] No string passed to be posted to the chat!')
        else:
            print('[*] Attempting to post the string: {}'.format(chat_string))
            try:
                self.connection.send('PRIVMSG {} :{}\r\n'.format(self.channel, chat_string).encode('utf-8'))
                print('[+] String posted successfully!')
                return True
            except Exception as e:
                print('[-] Exception occurred: {}'.format(str(e)))
                return False

    def check_for_command(self, decoded_response):
        for command in self.commands.keys():
            if command in decoded_response:
                print('[!] Command: {} detected!'.format(command))
                self.post_in_channel(self.commands[command])