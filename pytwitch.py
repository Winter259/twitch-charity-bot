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
QUEUE_CHECK_DELAY = 10
CONNECTION_CHECK_DELAY = 3
GITHUB = r'https://github.com/Winter259/twitch-charity-bot'
LINK_DATA = ['www.', '.com', '.org', '.net', '.int', '.edu', '.gov', '.mil']

class Twitch():
    def __init__(self, name='', token='', channel=''):
        self.name = name
        self.token = token
        self.connection = socket.socket()
        self.connection_checks = 0
        self.channel = self.connect(channel)
        self.prompt_commands = {
            '!info': 'Purrbot is written by Purrcat259, you can find the source code on Github here: {}'.format(GITHUB),
            '!racers': 'Check out the latest events in Elite: Racing at /r/EliteRacers!',
        }
        self.queue = ['Hello', 'I', 'am', 'Purrbot359']
        print('[!] Purrbot initialised and connected!')
        print('[+] Initial buffer content:')
        self.print_response(INITIAL_BUFFER_SIZE)

    def run(self):
        cycle = 1
        while True:
            print('[+] Purrbot is on cycle: {}'.format(cycle))
            decoded_response = self.receive_data()  # get response once
            self.check_connection(decoded_response)  # always check connection first
            # TODO if the response matches something like a command or a link, respond instantly
            command_response = self.check_for_command(decoded_response)
            if command_response or len(self.queue) == 0:
                if len(self.queue) == 0:
                    print('[+] Purrbot\'s queue is empty')
                pause('[+] Holding for next connection check', CONNECTION_CHECK_DELAY)
            else:
                print_list('Current queue:', self.queue)
                current_prompt = self.queue.pop(0)
                print('[+] Purrbot has popped {} from the front of the queue'.format(current_prompt))
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
            print('[?] Attempting to post the string: {}'.format(chat_string))
            try:
                self.connection.send('PRIVMSG {} :{}\r\n'.format(self.channel, chat_string).encode('utf-8'))
                print('[!] String posted successfully!')
                return True
            except Exception as e:
                print('[-] Exception occurred: {}'.format(str(e)))
                return False

    def check_for_command(self, decoded_response):
        # check for links
        for data in LINK_DATA:
            if data in decoded_response:
                print('[!] Link detected with part: {}'.format(data))
                self.post_in_channel('Link detected!')
                return True
        # check for prompts
        for command in self.prompt_commands.keys():
            if command in decoded_response:
                print('[!] Prompt command: {} detected!'.format(command))
                self.post_in_channel(self.prompt_commands[command])
                return True

