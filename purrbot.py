import pysqlite
import pytwitch
import urllib.request
from purrtools import get_current_time, print_list, pause
from os import startfile
from winsound import Beep
from bs4 import BeautifulSoup
from cfg import *

"""
Include a file called cfg.py in the same directory as main.py with the following:
NICK = "purrbot359"                 # your Twitch username, lowercase
PASS = "xyzxyyzxyhfdiufjdsoifjospi" # your Twitch OAuth token, get this from here: http://www.twitchapps.com/tmi/
CHAN = "#test"                      # the channel you want to join
"""

# Stream specific constants. Adjust these according to the stream
DATABASE_TABLE = 'ggforcharity'
GITHUB_URL = r'https://github.com/Winter259/twitch-charity-bot/tree/charity-stream'
CHECK_TICK = 3  # seconds between checks
PROMPT_TICK_MINUTES = 5
CYCLES_FOR_PROMPT = (PROMPT_TICK_MINUTES * 60) / CHECK_TICK
CHARITY_URL = r'http://pmhf3.akaraisin.com/Donation/Event/Home.aspx?seid=11349&mid=8'
SCHEDULE_URL = r'http://elitedangerous.events/charity/'
START_TIME_EPOCH = 1447372800
END_TIME_EPOCH = 1447632000


def beep_loop(number=0, frequency=200, length=100):
    for i in range(0, number):
        Beep(frequency, length)


def create_url_request():
    request = urllib.request.Request(
        CHARITY_URL,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    return request


def scrape_amount_raised():
    try:
        print('[+] Purrbot is scraping the charity URL')
        url_request = create_url_request()
        f = urllib.request.urlopen(url_request)
        data = f.read().decode('utf-8')
        soup = BeautifulSoup(data, 'lxml')
        td = soup.findAll('td', {'class': 'ThermometerAchived', 'align': 'Right'})  # class is spelt wrongly...
        achieved_amount = td[0].text  # get just the text
        print('[+] Current amount:', achieved_amount)
    except Exception:
        print('[-] Purrbot could not scrape the amount: {}'.format(Exception))
        return ''
    return achieved_amount


def get_float_from_string(amount=''):
    if amount == '':
        print('[-] Empty string passed to the decimal from string converter')
        return ''
    float_str = ''
    for letter in amount:
        if letter in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            float_str += letter
        if letter == '.':
            float_str += letter
    return round(float(float_str), 2)


def get_amount_donated(old_amount='', new_amount=''):
    if old_amount == '' or new_amount == '':
        print('[-] An amount was not passed to the amount donated method')
        return 0
    # print('old: {} new: {}'.format(old_amount, new_amount))
    old_amount_float = get_float_from_string(old_amount)
    new_amount_float = get_float_from_string(new_amount)
    if testing_mode:  # adjust this
        print('[!] WARNING! Purrbot is in testing mode and is attempting to do 4.00 - 2.03!')
        old_amount_float = round(float('2.03'), 2)
        new_amount_float = round(float('4.00'), 2)
    amount_donated = new_amount_float - old_amount_float
    print('[+] New donation of: {} - {} = {}$'.format(
        new_amount_float,
        old_amount_float,
        amount_donated
    ))
    try:
        startfile('chewbacca.mp3')
    except Exception as e:
        print('[-] Purrbot was unable to play the donation sound: {}'.format(e))
    return amount_donated


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


def get_current_events(db, verbose=False):
    current_events = []
    current_time = get_current_time('epoch')
    db_event_data = db.get_db_data(DATABASE_TABLE)
    for event_data in db_event_data:
        start_time = event_data[2]  # be sure that these are stored in epoch form
        end_time = event_data[3]
        if (current_time > start_time) and (current_time < end_time):  # this means that the event is ongoing
            # split up the streamers into a list if a , is present
            streamers = event_data[5].strip(' ')  # untested feature
            if ',' in streamers:
                streamers = streamers.split(',')
            else:
                streamers = [streamers]  # put in a list for easy iteration later on
            # store all this data in a dict for easy reference
            current_event = {
                    'ID': event_data[0],
                    'Day': event_data[1],
                    'StartTime': event_data[2],
                    'EndTime': event_data[3],
                    'Event': event_data[4],
                    'Streamers': streamers
                }
            current_events.append(current_event)
    if len(current_events) > 0 and verbose:
        print('[+] Current ongoing events:')
        for event in current_events:
            event_string = '\t> ID: {} Event: {} Day: {} Streamers: '.format(event['ID'], event['Event'], event['Day'])
            for streamer in event['Streamers']:
                event_string += '{} '.format(streamer)
            print(event_string)
    return current_events



def main():
    print('--- Initialising Purrbot! ---')
    purrbot = pytwitch.Pytwitch(NICK, PASS, CHAN)
    database = pysqlite.Pysqlite('GGforCharity', 'ggforcharity.db')
    bot_cycles = 0      # Global cycles of the bot
    prompt_cycles = 0   # increment by 1 per cycle, then post a prompt when equal to CYCLES_FOR_PROMPT constant
    prompt_index = 0    # index of the available prompts
    print('--- Starting Purrbot! ---')
    current_money_raised = scrape_amount_raised()  # get the donation amount for comparison
    while True:  # start the actual loop
        print('[+] Purrbot is on cycle: {}'.format(bot_cycles))
        current_events_list = get_current_events(database, True)  # get a list of current event dicts




if __name__ == '__main__':
    main()
