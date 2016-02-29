import socket
import bot_config
from time import sleep
from requests import get as req_get

HOST = 'irc.twitch.tv'  # the Twitch IRC server
PORT = 6667             # always use port 6667!
DATA_BUFFER_SIZE = 1024
INITIAL_BUFFER_SIZE = 4098

# MISC
testing_mode = False


def pause(initial_prompt='', amount=5, clear_pause_prompt=True):
    print('[+] {}'.format(initial_prompt))
    for tick in range(amount, 0, -1):
        print('[*] ', 'Pause ends in: {}    '.format(tick), end='\r')
        sleep(1)
    if clear_pause_prompt:
        print('                                        ', end='\r')  # clear the line completely

# set global testing variables
if testing_mode:
    print('[!] PURRBOT IS IN TESTING MODE!')
    CYCLES_FOR_PROMPT = 3


# Method to return kadgar links, given a tuple of streamers
def return_kadgar_link(streamers=None):
    kadgar_link = 'http://kadgar.net/live'
    if streamers is None:
        return 'N/A'
    # if there is only one streamer in the list, then simply return their twitch channel url
    if len(streamers) == 1:
        twitch_link = 'www.twitch.tv/{}'.format(streamers[0])
        return twitch_link
    for streamer in streamers:
        # append each streamer at the end
        kadgar_link += '/' + streamer
    return kadgar_link


def get_online_streamers(streamer_list=None, full_verbose=False, verbose=True):
    if verbose:
        print('[+] Getting list of online streamers')
    if streamer_list is None:
        if full_verbose:
            print('[-] No streamer list passed')
    else:
        online_streamers = []
        for streamer in streamer_list:
            try:
                data = req_get('https://api.twitch.tv/kraken/streams/' + streamer).json()
            except Exception as e:
                if full_verbose:
                    print('[-] JSON error: {}'.format(e))
            else:
                try:
                    stream_data = data['stream']
                except KeyError:
                    print('[-] Unable to get streamer data from API')
                else:
                    if stream_data is not None:
                        if full_verbose:
                            print('[+] {} is online!'.format(streamer))
                        online_streamers.append(streamer)
                    else:
                        if full_verbose:
                            print('[-] {} is offline!'.format(streamer))
        if len(online_streamers) > 0:
            if verbose:
                print('[+] Current online streamers: {}'.format(online_streamers))
        else:
            if verbose:
                print('[-] None of the passed streamers are currently online.')
        return online_streamers


class Pytwitch:
    def __init__(self, name='', token='', channel=None, read_chat=False, identifier='default', verbose=False):
        self.name = name
        self.token = token
        self.channel = channel
        self.read_chat = read_chat
        self.verbose = verbose
        self.identifier = identifier
        self.connection = socket.socket()
        self.cycles = 0
        if self.read_chat:
            self.connect(channel)
            if self.verbose:
                print('[+] Initial buffer content:')
            self.print_response(INITIAL_BUFFER_SIZE)

    def return_identity(self):
        return self.identifier

    def increment_cycles(self):
        self.cycles += 1

    def reset_cycles(self):
        self.cycles = 0

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
                if self.channel is not None:
                    self.connection.send("JOIN {}\r\n".format(self.channel).encode("utf-8"))
                if self.verbose:
                    print('[+] Purrbot successfully connected to the twitch channel: {}'.format(channel))
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

    def post_in_channel(self, channel=None, chat_string=''):
        if channel is None:
            if self.verbose:
                print('[-] No channel passed to post string!')
            return False
        if not len(chat_string) == '':
            if self.verbose:
                print('[?] Attempting to post the string:')
                print('\t', chat_string)
            # if the bot is not in reading mode, we need to connect
            if not self.read_chat or self.channel is None:
                self.connect(channel=channel)
            else:
                # if the bot is in read_chat mode, then it is tied to only one
                # channel at a time, so assign the channel to the instance assigned one
                channel = self.channel
            try:
                self.connection.send('PRIVMSG {} :{}\r\n'.format(channel, chat_string).encode('utf-8'))
                if self.verbose:
                    print('[!] String posted successfully!')
            except Exception as e:
                if self.verbose:
                    print('[-] Exception occurred: {}'.format(str(e)))
            if not self.read_chat:
                self.close_connection()

    def post_in_streamer_channels(self, streamer_list=None, chat_string='', pause_time=3):
        channels = ['#' + streamer for streamer in streamer_list]
        for channel in channels:
            self.post_in_channel(channel=channel, chat_string=chat_string)
            pause(initial_prompt='Holding between channels', amount=pause_time)

if __name__ == '__main__':
    bot_details = bot_config.purrbots[0]
    bot = Pytwitch(name=bot_details['NICK'], token=bot_details['TOKEN'], verbose=True)
    while True:
        bot.connect('#purrcat259')
        bot.post_in_channel('#purrcat259', 'test string')
        sleep(2)
        bot.close_connection()
        sleep(5)

