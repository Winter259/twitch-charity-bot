import socket
from cfg import *

HOST = "irc.twitch.tv"  # the Twitch IRC server
PORT = 6667             # always use port 6667!
DATA_BUFFER_SIZE = 256

class Twitch():
    def __init__(self, name='', token='', channel=''):
        self.name = name
        self.token = token
        self.connection = socket.socket()
        self.channel = self.connect(channel)
        print('[!] Purrbot initialised and connected!')

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

    def ping_pong(self, decoded_data):
        print('[!] Bot responding to the irc ping with a pong!')
        self.connection.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))

    def check_connection(self):
        response = self.connection.recv(DATA_BUFFER_SIZE)
        decoded_response = response.decode('utf-8')
        if decoded_response == 'PING :tmi.twitch.tv\r\n':
            self.ping_pong(decoded_response)
        else:
            pass

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
