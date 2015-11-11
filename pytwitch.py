import socket
import sqlite3
import time
from datetime import datetime
from winsound import Beep
from urllib.request import urlopen
from bs4 import BeautifulSoup
from cfg import *

# for testing:
# kadgar.net/live/purrcat259/purrbot359

# misc functions

def pause(prompt='', amount=5):
    ticks = amount
    print(prompt)
    while ticks > 0:
        print('[*] Pause ends in: {}  '.format(ticks), end='\r')
        time.sleep(1)
        ticks -= 1
    print('                                                            ', end='\r')  # clear line completely
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
CHECK_TICK = 3  # seconds between checks
#CYCLES_FOR_PROMPT = (15 * 60) / 5
CYCLES_FOR_PROMPT = 3
# Stream specific
CHARITY_URL = r'http://pmhf3.akaraisin.com/Donation/Event/Home.aspx?seid=11324&mid=8'
STREAMERS = ['purrcat259']
SCHEDULE_URL = r'http://elitedangerous.events/charity/'
# MISC
testing_mode = True

# return functions

def get_donation_amount():
    print('[+] Purrbot is scraping the url...')
    data = urlopen(CHARITY_URL).read()
    soup = BeautifulSoup(data, 'lxml')
    td = soup.findAll('td', {'class': 'ThermometerAchived', 'align': 'Right'})  # class is spelt wrongly...
    achieved_amount = td[0].text  # get just the text
    return achieved_amount

def get_current_epoch(roundNum=False):
    current_time = time.mktime(datetime.now().timetuple())
    if roundNum:
        current_time = round(current_time, 0)
    return int(current_time)

def get_time_passed():
    old_time = datetime(2015, 10, 14, 1, 00, 00)
    epoch_old = time.mktime(old_time.timetuple())
    # print('Old Times:\n\tdatetime: {}\n\tEpoch seconds: {}'.format(t_old, epoch_old))
    epoch_passed = get_current_epoch() - epoch_old
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

def return_kadgar_link(streamer_list=[]):
    if len(streamer_list) == 0:
        print('[-] No streamers passed to the kadgar link generator!')
        return ''
    if len(streamer_list) == 1:
        print('[+] Only one streamer passed, passing twitch stream link instead')
        twitch_link = 'http://www.twitch.tv/'
        twitch_link += streamer_list[0]
        return twitch_link
    kadgar_link = 'http://kadgar.net/live'
    for streamer in streamer_list:
        kadgar_link += '/'
        kadgar_link += streamer
    return kadgar_link

class Twitch:
    def __init__(self, name='', token='', channel=''):
        self.name = name
        self.token = token
        self.channel = channel
        # self.connection = socket.socket()
        self.cycle_count = 0
        self.prompt_index = 0  # index of prompt posted
        self.prompt_cycles = 0  # increment to by 1 every cycle, when equal to CYCLES_FOR_PROMPT, reset and prompt
        self.dbcon = sqlite3.connect('ggforcharity.db')
        self.dbcur = self.dbcon.cursor()
        if testing_mode:
            self.dbtable = 'testing'
        else:
            self.dbtable = 'events'
        """
        self.connect(channel)
        print('[+] Initial buffer content:')
        self.print_response(INITIAL_BUFFER_SIZE)
        """

    def run(self):
        current_money_raised = get_donation_amount()  # Get the donation amount once before starting the loops, for comparison
        while True:
            self.prompt_cycles += 1
            print('[+] Purrbot is on cycle: {}'.format(self.cycle_count))
            current_event_data = self.get_current_events()  # returns a list of dicts each with the current ongoing events
            for ongoing_event in current_event_data:
                print('[+] Current ongoing event: {}'.format(ongoing_event))
                # figure out if there are one or two

            # change the text string into an iterable list
            if not current_event_data[4] is None:
                event_one_streamers = current_event_data[4].split(',')
            else:
                event_one_streamers = []
            if not current_event_data[6] is None:
                event_two_streamers = current_event_data[6].split(',')
            else:
                event_two_streamers = []
            current_events = [(current_event_data[3], event_one_streamers), (current_event_data[5], event_two_streamers)]
            # get donation amount
            new_money_raised = get_donation_amount()
            # if donation amount has changed, post the prompt
            if not new_money_raised == current_money_raised:
                print('[!] Purrbot has detected a new donation!')
                # create a string to post in channels
                chat_string = 'NEW DONATION! {} has been raised! Visit: {} to donate!'.format(new_money_raised, CHARITY_URL)
                for streamers in (event_one_streamers, event_two_streamers):
                    for streamer in streamers:
                        channel = '#{}'.format(streamer)
                        self.post_in_channel(channel, chat_string)
            # if not, check if cycle count has exceeded the amount required for a prompt
            elif self.prompt_cycles == CYCLES_FOR_PROMPT:
                self.prompt_cycles = 0
                # decide which string to use
                if self.prompt_index == 0:
                    prompt_string = r'GGforCharity has raised: {} so far! Donate at: {} Check out the schedule at: {}'.format(
                        new_money_raised,
                        CHARITY_URL,
                        SCHEDULE_URL
                    )
                elif self.prompt_index == 1:
                    event_one = current_events[0][0]
                    event_two = current_events[1][0]
                    if len(event_two_streamers) == 0:
                        streamers = current_event_data[0][1]
                        prompt_string = r'Current GGforCharity Event: {} Watch the current event streamers at: {} Donate at: {}'.format(
                            event_one,
                            return_kadgar_link(streamers),
                            CHARITY_URL
                        )
                    else:
                        streamers_one = current_event_data[0][1]
                        streamers_two = current_event_data[1][1]
                        prompt_string = r'Current GGforCharity Events: Event 1: {} Watch event 1 here: {} Event 2: {} Watch event 2 here: {} . Donate at: {}'.format(
                            event_one,
                            event_two,
                            return_kadgar_link(streamers_one),
                            return_kadgar_link(streamers_two),
                            CHARITY_URL
                        )
                else:
                    prompt_string = r''  # placeholder for more... TODO: current events, next events staring in XYZ hours?
                # iterate prompt index and if > than limit, reset
                self.prompt_index += 1
                if self.prompt_index == 2:
                    self.prompt_index = 0
                # post per event and streamer
                for subevent in current_events:
                    print('[+] Event: {} Streamers: {}'.format(subevent[0], subevent[1]))
                    for streamer in subevent[1]:
                        channel = '#{}'.format(streamer)
                        self.post_in_channel(channel, prompt_string)
            # if not, wait for the amount of the check tick
            pause('[+] Holding for next cycle', CHECK_TICK)
            self.cycle_count += 1

    def connect(self, channel=''):
        if len(channel) == 0:
            print('[-] No channel passed to Purrbot!')
            return False
        else:
            try:
                self.connection = socket.socket()
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
        pause('[+] Holding for disconnect', 4)

    def receive_data(self, buffer=DATA_BUFFER_SIZE):
        print('[+] Purrbot is waiting for data to come in from the stream')
        response = self.connection.recv(buffer)
        return response.decode('utf-8')

    def print_response(self, buffer=DATA_BUFFER_SIZE):
        decoded_response = self.receive_data(buffer)
        print('[!] Response: {}'.format(decoded_response))

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
                    Beep(200, 100)
                    self.close_connection()
                    return True
                except Exception as e:
                    print('[-] Exception occurred: {}'.format(str(e)))
                    self.close_connection()
                    return False

    # db return functions

    def get_db_data(self):
        try:
            data = self.dbcur.execute('SELECT * FROM {}'.format(self.dbtable))
            return data
        except Exception:
            print('[-] Purrbot was unable to interface with the database: ', Exception)
            return ()

    def get_event_data(self):
        db_events = self.get_db_data()
        current_event = ()
        events = []
        events_left = []
        for row in db_events:  # change from db cursor to iterable format
            events.append(row)
        for event in events:
            if event[2] < get_current_epoch():
                current_event = event  # will grab current event
        # place remaining events in another list
        for event in events:
            if event[2] > get_current_epoch():
                events_left.append(event)
        #print_list('Events:', events_left)
        #print('Current event:', current_event)
        return current_event, events_left

    def get_current_events(self):
        current_time_epoch = get_current_epoch(roundNum=True)
        db_events = self.get_db_data()
        all_event_data = []
        current_events = []
        for row in db_events:
            all_event_data.append(row)
        for event in all_event_data:
            event_start_time = event[2]
            event_end_time = event[3]
            #print('Current: {} Start: {} End: {}'.format(current_time_epoch, event_start_time, event_end_time))
            if (current_time_epoch > event_start_time) and (current_time_epoch < event_end_time):
                #print('It is a current event!')
                current_event = {
                    'RowId': event[0],
                    'Day': event[1],
                    'EndTime': event[3],
                    'EventOne': event[4],
                    'StreamersOne': event[5],
                    'EventTwo': event[6],
                    'StreamersTwo': event[7]
                }
                current_events.append(current_event)
        print_list('Current Events: ', current_events)
        return current_events
