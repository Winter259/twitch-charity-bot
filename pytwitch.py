import socket
import sqlite3
import time
from datetime import datetime
from winsound import Beep
from urllib.request import urlopen
from bs4 import BeautifulSoup
from cfg import *

def pause(prompt='', amount=5):
    ticks = amount
    print(prompt)
    while ticks > 0:
        print('[*] Pause ends in: {}  '.format(ticks), end='\r')
        time.sleep(1)
        ticks -= 1
    print('                                                            ')  # clear line completely
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
CYCLES_FOR_PROMPT = (15 * 60) / 5
# Stream specific
CHARITY_URL = r'http://pmhf3.akaraisin.com/specialevents/RibbonofHope'  # PLACEHOLDER FOR TESTING
STREAMERS = ['purrcat259']

def get_donation_amount():
    print('[+] Purrbot is scraping the url...')
    data = urlopen(CHARITY_URL).read()
    soup = BeautifulSoup(data, 'lxml')
    td = soup.findAll('td', {'class': 'ThermometerAchived', 'align': 'Right'})  # class is spelt wrongly...
    achieved_amount = td[0].text  # get just the text
    return achieved_amount

def get_time_passed():
    now_time = datetime.now()
    epoch = time.mktime(now_time.timetuple())
    # print('Current Times:\n\tdatetime: {}\n\tEpoch seconds: {}'.format(t, epoch))
    old_time = datetime.datetime(2015, 10, 14, 1, 00, 00)
    epoch_old = time.mktime(old_time.timetuple())
    # print('Old Times:\n\tdatetime: {}\n\tEpoch seconds: {}'.format(t_old, epoch_old))
    epoch_passed = epoch - epoch_old
    hours_passed = round(((epoch_passed / 60) / 60), 1)
    # print('\tHours passed: {}'.format(hours_passed))
    return hours_passed

def get_time_left(time_elapsed):
    time_left = round(72 - (time_elapsed), 1)
    # print('Time left: {}'.format(time_left))
    return time_left

def get_percentage_left():
    hours_passed = get_time_passed()
    percentage_done = round((hours_passed / 72) * 100, 1)
    return percentage_done

class Twitch:
    def __init__(self, name='', token='', channel=''):
        self.name = name
        self.token = token
        self.channel = channel
        self.connection = socket.socket()
        self.cycle_count = 0
        self.prompt_index = 0  # index of prompt posted
        self.prompt_cycles = 0  # increment to by 1 every cycle, when equal to CYCLES_FOR_PROMPT, reset and prompt
        """
        self.connect(channel)
        print('[+] Initial buffer content:')
        self.print_response(INITIAL_BUFFER_SIZE)
        """

    def run(self):
        current_money_raised = get_donation_amount()
        while True:
            self.prompt_cycles += 1
            print('[+] Purrbot is on cycle: {}'.format(self.cycle_count))
            # get donation amount
            new_money_raised = get_donation_amount()
            # if donation amount has changed, post the prompt
            if not new_money_raised == current_money_raised:
                print('[!] Purrbot has detected a new donation!')
                # create a string to post in channels
                chat_string = 'NEW DONATION! {} has been raised! Visit: {} to donate!'.format(new_money_raised, CHARITY_URL)
                for streamer in STREAMERS:
                    channel = '#{}'.format(streamer)
                    self.post_in_channel(channel, chat_string)
                    pause('Holding for disconnect', 3)
            elif self.prompt_cycles == CYCLES_FOR_PROMPT:  # if not, check if cycle count has exceeded the amount required for a prompt
                self.prompt_cycles = 0
                # decide which string to use
                if self.prompt_index == 0:
                    prompt_string = r'Purrbot is written in python by CMDR Purrcat. You can find the source code here: {} Donate at: {}'.format(GITHUB_URL, CHARITY_URL)
                elif self.prompt_index == 1:
                    hours_passed = get_time_passed()
                    hours_left = get_time_left(hours_passed)
                    hours_done_percentage = get_percentage_left()
                    prompt_string = r'Time check! Hours elapsed: {}/72 {} hours to go! Stream progress: {}% Donate at: {}'.format(hours_passed, hours_left, hours_done_percentage, CHARITY_URL)
                elif self.prompt_index == 2:
                    prompt_string = r'GGforCharity has raised: {} so far! Donate at: {}'.format( ,CHARITY_URL)
                else:
                    pass
                for streamer in STREAMERS:
                    channel = '#{}'.format(streamer)
                    self.post_in_channel(channel, prompt_string)
                    pause('Holding for disconnect', 5)
            # if not, wait for the amount of the check tick
            pause('[+] Holding for next cycle', CHECK_TICK)
            self.cycle_count += 1

    def connect(self, channel=''):
        if len(channel) == 0:
            print('[-] No channel passed to Purrbot!')
            return False
        else:
            try:
                self.connection.connect((HOST, PORT))
                self.connection.send("PASS {}\r\n".format(PASS).encode("utf-8"))
                self.connection.send("NICK {}\r\n".format(NICK).encode("utf-8"))
                self.connection.send("JOIN {}\r\n".format(channel).encode("utf-8"))
                print('[+] Purrbot has successfully connected to the twitch irc channel: {}'.format(channel))
                return True
            except Exception as e:
                print('[-] Purrbot did not manage to connect! Exception occurred: {}'.format(e))
                return False

    def close_connection(self):
        self.connection.close()

    def receive_data(self, buffer=DATA_BUFFER_SIZE):
        print('[+] Purrbot is waiting for data to come in from the stream')
        response = self.connection.recv(buffer)
        return response.decode('utf-8')

    def print_response(self, buffer=DATA_BUFFER_SIZE):
        decoded_response = self.receive_data(buffer)
        print('Response: {}'.format(decoded_response))

    def post_in_channel(self, channel='',chat_string=''):
        if len(channel) == 0:
            print('[-] No channel passed to post string!')
            return False
        if self.connect(channel):
            # print('[+] Initial buffer content:')
            # self.print_response(INITIAL_BUFFER_SIZE)
            if len(chat_string) == 0:
                print('[-] No string passed to be posted to the chat!')
                self.close_connection()
                return False
            else:
                print('[?] Attempting to post the string:')
                print('\t', chat_string)
                try:
                    self.connection.send('PRIVMSG {} :{}\r\n'.format(channel, chat_string).encode('utf-8'))
                    print('[!] String posted successfully!')
                    Beep(200, 15)
                    self.close_connection()
                    return True
                except Exception as e:
                    print('[-] Exception occurred: {}'.format(str(e)))
                    self.close_connection()
                    return False
