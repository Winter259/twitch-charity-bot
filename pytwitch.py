import socket
import cfg
from time import sleep

HOST = 'irc.twitch.tv'  # the Twitch IRC server
PORT = 6667             # always use port 6667!
DATA_BUFFER_SIZE = 1024
INITIAL_BUFFER_SIZE = 4098

# MISC
testing_mode = False


def pause(initial_prompt='', amount=5, clear_pause_prompt=True):
    print('[+] {}'.format(initial_prompt))
    for tick in range(amount, 0, -1):
        print('[*] ', 'Pause ends in: {}    '.format(tick), '\r')
        sleep(1)
    if clear_pause_prompt:
        print('                                        ', end='\r')  # clear the line completely

# set global testing variables
if testing_mode:
    print('[!] PURRBOT IS IN TESTING MODE!')
    CYCLES_FOR_PROMPT = 3


class Pytwitch:
    def __init__(self, name='', token='', channel='', read_chat=False, verbose=False):
        self.name = name
        self.token = token
        self.channel = channel
        self.verbose = verbose
        self.read_chat = read_chat
        self.connection = socket.socket()
        if self.read_chat:
            self.connect(channel)
            if self.verbose:
                print('[+] Initial buffer content:')
            self.print_response(INITIAL_BUFFER_SIZE)

    def connect(self, channel=''):
        if len(channel) == 0:
            if self.verbose:
                print('[-] No channel passed to Purrbot!')
            return False
        else:
            try:
                self.connection = socket.socket()
                self.connection.connect((HOST, PORT))
                self.connection.send("PASS {}\r\n".format(self.token).encode("utf-8"))
                self.connection.send("NICK {}\r\n".format(self.name).encode("utf-8"))
                self.connection.send("JOIN {}\r\n".format(self.channel).encode("utf-8"))
                if self.verbose:
                    print('[+] Purrbot has successfully connected to the twitch irc channel: {}'.format(channel))
                return True
            except Exception as e:
                if self.verbose:
                    print('[-] Purrbot did not manage to connect! Exception occurred: {}'.format(e))
                return False

    def close_connection(self):
        try:
            self.connection.close()
        except Exception as e:
            if self.verbose:
                print('[-] Unable to disconnect: {}'.format(e))

    def receive_data(self, buffer=DATA_BUFFER_SIZE):
        if self.verbose:
            print('[+] Purrbot is waiting for data to come in from the stream')
        response = self.connection.recv(buffer)
        return self.check_for_ping(response.decode('utf-8'))

    def print_response(self, buffer=DATA_BUFFER_SIZE):
        decoded_response = self.receive_data(buffer)
        if self.verbose:
            print('[!] Response: {}'.format(decoded_response))

    def check_for_ping(self, data):
        if data == 'PING :tmi.twitch.tv\r\n':
            self.connection.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))
            return ''
        else:
            return data

    def post_in_channel(self, channel='', chat_string=''):
        if len(channel) == 0:
            if self.verbose:
                print('[-] No channel passed to post string!')
            return False
        if not len(chat_string) == '':
            if self.verbose:
                print('[?] Attempting to post the string:')
                print('\t', chat_string)
            # if the bot is not in reading mode, we need to connect
            if not self.read_chat:
                self.connect(self.channel)
            try:
                self.connection.send('PRIVMSG {} :{}\r\n'.format(channel, chat_string).encode('utf-8'))
                if self.verbose:
                    print('[!] String posted successfully!')
            except Exception as e:
                if self.verbose:
                    print('[-] Exception occurred: {}'.format(str(e)))
            if not self.read_chat:
                self.close_connection()

if __name__ == '__main__':
    bot = Pytwitch(name=cfg.NICK, token=cfg.PASS, channel=cfg.CHAN, verbose=True)
    while True:
        bot.connect('#kateclick')
        bot.post_in_channel('#kateclick', 'test string')
        sleep(5)

