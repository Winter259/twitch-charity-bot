import socket
import sqlite3
import time
from datetime import datetime
from winsound import Beep
from urllib.request import urlopen
from bs4 import BeautifulSoup
from decimal import *  # used for typecasting the raised string
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
            print('\t> {}'.format(element))

HOST = 'irc.twitch.tv'  # the Twitch IRC server
PORT = 6667             # always use port 6667!
DATA_BUFFER_SIZE = 1024
INITIAL_BUFFER_SIZE = 4098
GITHUB_URL = r'https://github.com/Winter259/twitch-charity-bot/tree/charity-stream'
CHECK_TICK = 5  # seconds between checks
PROMPT_TICK_MINUTES = 10
CYCLES_FOR_PROMPT = (PROMPT_TICK_MINUTES * 60) / CHECK_TICK
# Stream specific
CHARITY_URL = r'http://pmhf3.akaraisin.com/Donation/Event/Home.aspx?seid=11349&mid=8'
SCHEDULE_URL = r'http://elitedangerous.events/charity/'
START_TIME_EPOCH = 1447372800
END_TIME_EPOCH = 1447632000
# MISC
testing_mode = False
# set global testing variables
if testing_mode:
    print('[!] PURRBOT IS IN TESTING MODE!')
    CYCLES_FOR_PROMPT = 3
getcontext().prec = 3  # setting decimal places


def beep_loop(number=0, frequency=200, length=100):
    for i in range(0, number):
        Beep(frequency, length)

# global return functions


def scrape_amount_raised():
    try:
        print('[+] Purrbot is scraping the charity URL')
        data = urlopen(CHARITY_URL).read()
        soup = BeautifulSoup(data, 'lxml')
        td = soup.findAll('td', {'class': 'ThermometerAchived', 'align': 'Right'})  # class is spelt wrongly...
        achieved_amount = td[0].text  # get just the text
        print('[+] Current amount:', achieved_amount)
    except Exception:
        print('[-] Purrbout could not scrape the amount: {}'.format(Exception))
        return ''
    return achieved_amount


def get_decimal_from_string(amount=''):
    if amount == '':
        print('[-] Empty string passed to the decimal from string converter')
        return ''
    decimal_req = ''
    for letter in amount:
        if letter == '.':
            # print('Found a dot!')
            decimal_req += '.'
            # continue
        for number in range(0, 9):
            if letter == str(number):
                # print('Found the number: {}!'.format(letter))
                decimal_req += letter
                # break
    # print('Final string: {}'.format(decimal_req))
    return Decimal(decimal_req)


def get_amount_donated(old_amount='', new_amount=''):
    if old_amount == '' or new_amount == '':
        print('[-] An amount was not passed to the amount donated method')
        return 0
    # print('old: {} new: {}'.format(old_amount, new_amount))
    old_amount_decimal = get_decimal_from_string(old_amount)
    new_amount_decimal = get_decimal_from_string(new_amount)
    if testing_mode:
        print('[!] WARNING! Purrbot is in testing mode and is attempting to do 4.00 - 2.03!')
        old_amount_decimal = Decimal('2.03')
        new_amount_decimal = Decimal('4.00')
    amount_donated = new_amount_decimal - old_amount_decimal
    print('[+] New donation of: {} - {} = {}$'.format(
        str(new_amount_decimal),
        str(old_amount_decimal),
        str(amount_donated)
    ))
    beep_loop(4, 500, 100)
    return str(amount_donated)


def get_current_epoch():
    return int(time.mktime(datetime.now().timetuple()))


def get_time_passed():
    old_time = datetime(2015, 10, 14, 1, 00, 00)
    epoch_old = time.mktime(old_time.timetuple())
    # print('Old Times:\n\tdatetime: {}\n\tEpoch seconds: {}'.format(t_old, epoch_old))
    epoch_passed = get_current_epoch() - epoch_old
    hours_passed = round(((epoch_passed / 60) / 60), 1)
    # print('\tHours passed: {}'.format(hours_passed))
    return hours_passed


def get_start_time_remaining():
    time_left = (START_TIME_EPOCH - get_current_epoch())
    time_left = time_left / 60 / 60 # convert to hours
    return round(time_left, 2)


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
        kadgar_link += '/' + streamer
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
        current_money_raised = scrape_amount_raised()  # Get the donation amount once before starting the loops, for comparison
        while True:
            print('[+] Purrbot is on cycle: {}'.format(self.cycle_count))
            current_event_data = self.get_current_events()  # returns a list of dicts each with the current ongoing events
            new_money_raised = scrape_amount_raised()  # get donation amount
            if not new_money_raised == current_money_raised and not new_money_raised == '':  # check if the amount has increased
                # new_donation = get_amount_donated(current_money_raised, new_money_raised) # TODO: typecast to ints
                current_money_raised = new_money_raised  # update the value
                print('[!] Purrbot has detected a new donation!')
                # print('[!] Purrbot has detected a new donation of {}!'.format(new_donation))
                # create the string to post to channels
                """
                chat_string = 'NEW DONATION OF ${} CAD! A total of {} has been raised so far! Visit {} to donate!'.format(
                    new_donation,
                    new_money_raised,
                    CHARITY_URL
                )
                """
                chat_string = 'NEW DONATION! A total of {} has been raised to far! Visit {} to donate!'.format(
                    new_money_raised,
                    CHARITY_URL
                )
                # record the donation in the db for future data visualisation
                self.record_donation('', new_money_raised)
                current_streamers = set()  # use a set to avoid duplicates, just in case!
                for ongoing_event in current_event_data:
                    for streamer in ongoing_event['Streamers']:
                        current_streamers.add(streamer)
                for streamer in current_streamers:
                    channel = '#{}'.format(streamer)  # channel string is #<streamer name>
                    self.post_in_channel(channel, chat_string)
            else:  # if not, check if the amount of cycles has exceeded the amount required for a prompt
                if self.prompt_cycles == CYCLES_FOR_PROMPT:
                    print('[+] Purrbot is going to post a prompt!')
                    self.prompt_cycles = 0  # reset this counter for the cycle to reset
                    # now we decide which chat string to post, round robin between a set number
                    prompt_string = ''
                    print_list('Current ongoing events: {}', current_event_data)
                    for ongoing_event in current_event_data:
                        if self.prompt_index == 0:  # money counter and schedule link
                            prompt_string = r'GGforCharity has raised: {} so far!  Donate at: {}  Check out the stream schedule at: {}'.format(
                                new_money_raised,
                                CHARITY_URL,
                                SCHEDULE_URL
                            )
                        elif self.prompt_index == 1:  # current event prompt with kadgar links
                            prompt_string = r'Current GGforCharity events: '
                            prompt_string += r'Event {}: {}, {} (GMT), watch at: {}  '.format(
                                ongoing_event['RowId'],
                                ongoing_event['Event'],
                                ongoing_event['Day'],
                                return_kadgar_link(ongoing_event['Streamers'])
                            )
                        # if the stream has not started yet, generate a starting soon prompt instead
                        if get_current_epoch() < START_TIME_EPOCH:
                            prompt_string = 'GGforCharity will be starting in {} hours! Find the stream schedule at: {} Donate at: {} !'.format(
                                get_start_time_remaining(),
                                SCHEDULE_URL,
                                CHARITY_URL
                            )
                        for streamer in ongoing_event['Streamers']:
                            channel = '#{}'.format(streamer)
                            self.post_in_channel(channel, prompt_string)
                    # iterate prompt index and if > than limit, reset
                    self.prompt_index += 1
                    if self.prompt_index == 2:
                        self.prompt_index = 0
                if len(current_event_data) == 0:
                    print('[-] No event currently ongoing. Purrbot will not post any prompts')
                    if self.prompt_cycles < 0:
                        self.prompt_cycles = 0  # fix negative cycle count creating a locked loop
                else:
                    self.prompt_cycles += 1  # counter used for prompts, iterate only if there is an event going on
            # wait the check tick regardless of what the bot does
            print('[+] Next prompt in: {} cycles'.format(int(CYCLES_FOR_PROMPT - self.prompt_cycles + 1)))  # +1 as is 0'd
            pause('[+] Purrbot is holding for next cycle', CHECK_TICK)
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
        pause('[+] Holding for disconnect', 3)

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
                    beep_loop(2, 200, 100)
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
            data_list = []
            for row in data:
                data_list.append(row)
            return data_list
        except Exception:
            print('[-] Purrbot was unable to interface with the database: ', Exception)
            return ()

    def get_current_events(self):
        current_time_epoch = get_current_epoch()
        current_events = []
        all_event_data = self.get_db_data()
        for event in all_event_data:
            event_start_time = event[2]
            event_end_time = event[3]
            #print('Current: {} Start: {} End: {}'.format(current_time_epoch, event_start_time, event_end_time))
            if (current_time_epoch > event_start_time) and (current_time_epoch < event_end_time):
                #print('It is a current event!')
                if ',' in event[5]:  # this indicates that it should be a list
                    streamers = event[5].split(',')
                else:
                    streamers = [event[5]]  # encapsulate in a list for easy iteration
                current_event = {
                    'RowId': event[0],
                    'Day': event[1],
                    'StartTime': event[2],
                    'EndTime': event[3],
                    'Event': event[4],
                    'Streamers': streamers
                }
                current_events.append(current_event)
        if len(current_events) > 0:
            print('[+] Current ongoing events:')
        for event_data in current_events:
            print('\t> [{}] {} {}'.format(
                event_data['RowId'],
                event_data['Day'],
                event_data['Event']
            ))
        for event in current_events:
            print_list('Current streamers:', event['Streamers'])
        return current_events

    def record_donation(self, amount_donated='', total_raised=''):
        try:
            current_time_epoch = get_current_epoch()
            self.dbcur.execute('INSERT INTO donations VALUES (NULL, ?, ?, ?)', (amount_donated, total_raised, current_time_epoch))
            self.dbcon.commit()
            print('[+] Purrbot has recorded a donation!')
        except Exception:
            print('[-] Purrbot did not manage to record the donation: {}'.format(Exception))
