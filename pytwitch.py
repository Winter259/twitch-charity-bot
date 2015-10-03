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

HOST = "irc.twitch.tv"  # the Twitch IRC server
PORT = 6667             # always use port 6667!
DATA_BUFFER_SIZE = 1024
CONNECTION_CHECK_DELAY = 3

class Twitch():
    def __init__(self, name='', token='', channel=''):
        self.name = name
        self.token = token
        self.connection = socket.socket()
        self.connection_checks = 0
        self.channel = self.connect(channel)
        print('[!] Purrbot initialised and connected!')

    def run(self):
        cycle = 1
        while True:
            print('[+] Purrbot is on cycle: {}'.format(cycle))
            self.check_connection()
            self.post_in_channel('I am a bot and I am being tested! Cycle: {}'.format(cycle))
            pause()
            print('[+] Holding {} seconds for next prompt'.format(PROMPT_TICK_TIME))
            sleep(PROMPT_TICK_TIME)
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
        response = self.connection.recv(DATA_BUFFER_SIZE)
        return response.decode('utf-8')

    def print_response(self):
        decoded_response = self.receive_data()
        print('Response: {}'.format(decoded_response))

    def ping_pong(self):
        print('[!] Purrbot has confirmed its connection to the twitch IRC. Checks so far: {}'.format(self.connection_checks))
        self.connection.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))

    def check_connection(self):
        print('[?] Purrbot is checking if it is still connected')
        self.connection_checks += 1
        decoded_response = self.receive_data()
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
