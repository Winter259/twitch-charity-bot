import socket
from purrtools import print_list, get_current_time, pause


HOST = 'irc.twitch.tv'  # the Twitch IRC server
PORT = 6667             # always use port 6667!
DATA_BUFFER_SIZE = 1024
INITIAL_BUFFER_SIZE = 4098

# MISC
testing_mode = False

# set global testing variables
if testing_mode:
    print('[!] PURRBOT IS IN TESTING MODE!')
    CYCLES_FOR_PROMPT = 3


class Pytwitch:
    def __init__(self, name='', token='', channel='', verbose=False):
        self.name = name
        self.token = token
        self.channel = channel
        self.verbose = verbose
        # self.connection = socket.socket()
        """
        self.connect(channel)
        print('[+] Initial buffer content:')
        self.print_response(INITIAL_BUFFER_SIZE)
        """

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
        self.connection.close()
        pause('Holding for disconnect', 3)

    def receive_data(self, buffer=DATA_BUFFER_SIZE):
        if self.verbose:
            print('[+] Purrbot is waiting for data to come in from the stream')
        response = self.connection.recv(buffer)
        return response.decode('utf-8')

    def print_response(self, buffer=DATA_BUFFER_SIZE):
        decoded_response = self.receive_data(buffer)
        if self.verbose:
            print('[!] Response: {}'.format(decoded_response))

    def post_in_channel(self, channel='',chat_string=''):
        if len(channel) == 0:
            if self.verbose:
                print('[-] No channel passed to post string!')
            return False
        if self.connect(channel):
            # print('[+] Initial buffer content:')
            # self.print_response(INITIAL_BUFFER_SIZE)
            if len(chat_string) == 0:
                if self.verbose:
                    print('[-] No string passed to be posted to the chat!')
                self.close_connection()
                return False
            else:
                if self.verbose:
                    print('[?] Attempting to post the string:')
                    print('\t', chat_string)
                try:
                    self.connection.send('PRIVMSG {} :{}\r\n'.format(channel, chat_string).encode('utf-8'))
                    if self.verbose:
                        print('[!] String posted successfully!')
                    self.close_connection()
                    return True
                except Exception as e:
                    if self.verbose:
                        print('[-] Exception occurred: {}'.format(str(e)))
                    self.close_connection()
                    return False
