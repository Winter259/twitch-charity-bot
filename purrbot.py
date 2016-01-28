import pysqlite
import pytwitch
import urllib.request
import cfg
from purrtools import print_list, pause
from os import startfile
from winsound import Beep
from bs4 import BeautifulSoup

"""
Include a file called cfg.py in the same directory as main.py with the following:
NICK = "purrbot359"                 # your Twitch username, lowercase
PASS = "xyzxyyzxyhfdiufjdsoifjospi" # your Twitch OAuth token, get this from here: http://www.twitchapps.com/tmi/
CHAN = "#test"                      # the channel you want to join
"""

# Stream specific constants. Adjust these according to the stream
DATABASE_NAME = 'charity'
DATABASE_TABLE = 'donations'
STREAMER_LIST = ['bubblemapgaminglive', 'misfits_enterprises']
CHECK_TICK = 3  # seconds between checks
PROMPT_TICK_MINUTES = 5
CYCLES_FOR_PROMPT = (PROMPT_TICK_MINUTES * 60) / CHECK_TICK
CHARITY_URL = 'http://pmhf3.akaraisin.com/Donation/Event/Home.aspx?seid=11349&mid=8'
DONATION_CURRENCY = '£'
DONATION_SOUND_PATH = 'chewbacca.mp3'
START_TIME_EPOCH = 1447372800
END_TIME_EPOCH = 1447632000
TESTING_MODE = False


def create_url_request():
    request = urllib.request.Request(
        CHARITY_URL,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    return request


def get_donation_amount():
    try:
        print('[+] Purrbot is scraping the charity URL')
        url_request = create_url_request()
        f = urllib.request.urlopen(url_request)
        data = f.read().decode('utf-8')
        soup = BeautifulSoup(data, 'lxml')
        td = soup.findAll('td', {'class': 'ThermometerAchived', 'align': 'Right'})  # class is spelt wrongly...
        achieved_amount = td[0].text  # get just the text
        print('[+] Current amount:', achieved_amount)
    except Exception as e:
        print('[-] Purrbot could not scrape the amount: {}'.format(e))
        raise Exception  # TODO: Add more specific exceptions
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
    if TESTING_MODE:
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
        startfile(DONATION_SOUND_PATH)
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


def insert_donation_into_db(db, amount=0, verbose=False):
    if amount == 0:
        if verbose:
            print('[-] No amount passed, not writing anything to DB')
    else:
        try:
            db.insert_db_data(DATABASE_TABLE, '(NULL, ?, CURRENT_TIMESTAMP)', (amount, ))
            if verbose:
                print('[+] Purrbot has successfully recorded the donation')
        except Exception as e:
            if verbose:
                print('[-] Purrbot did not manage to record the donation: {}'.format(e))


def get_all_current_streamers(current_events=[]):
    if len(current_events) == 0:
        print('[-] No events passed to the get all streamers method')
        return []
    all_current_streamers = set()  # use a set to avoid duplicates
    for ongoing_event in current_events:
        for streamer in ongoing_event['Streamers']:
            all_current_streamers.add(streamer)
    return all_current_streamers


def main():
    print('[!] Starting Purrbot359')
    purrbot = pytwitch.Pytwitch(cfg.NICK, cfg.PASS, cfg.CHAN)
    database = pysqlite.Pysqlite(DATABASE_NAME, DATABASE_NAME + '.db')
    bot_cycles = 0      # Global cycles of the bot
    prompt_cycles = 0   # increment by 1 per cycle, then post a prompt when equal to CYCLES_FOR_PROMPT constant
    prompt_index = 0    # index of the available prompts
    current_amount_raised = ''  # stops Pycharm from complaining
    new_amount_raised = ''
    print('[+] Purrbot is attempting to retrieve the first amount of donations')
    try:
        current_amount_raised = get_donation_amount()  # get the donation amount for comparison
        new_amount_raised = get_donation_amount()  # fill the new raised variable too
    except Exception as e:
        print('[-] Website scrape error: {}').format(e)
        input('[?] Click any key to exit')
        exit(-1)
    while True:  # start the actual loop
        print('[+] Purrbot is on cycle: {}'.format(bot_cycles))
        try:
            new_amount_raised = get_donation_amount()
        except Exception as e:
            print('[-] Website scrape error: {}'.format(e))
        else:
            if not new_amount_raised == current_amount_raised:  # true when a new donation is present
                current_amount_raised = new_amount_raised  # update to the newer amount
                new_donation = get_amount_donated()  # get a float value of the amount donated
                if not new_donation == 0:
                    print('[!] NEW DONATION: {} {}'.format(new_donation, DONATION_CURRENCY))
                    # build the string to post to channels
                    chat_string = 'NEW DONATION OF {} {}! A total of {} has been raised so far! Visit {} to donate!'.format(
                        new_donation,
                        DONATION_CURRENCY,
                        new_amount_raised,
                        CHARITY_URL
                    )
                    # record the donation to the database for future visualisation
                    insert_donation_into_db(database, current_amount_raised)
                    # post the chat string to all streamers
                    for streamer in STREAMER_LIST:
                        channel_name = '#{}'.format(streamer)  # channel name is #<streamer>
                        purrbot.post_in_channel(channel=channel_name, chat_string=chat_string)
            else:  # no new donation, check if we should post a prompt instead
                if prompt_cycles == CYCLES_FOR_PROMPT:  # if we've reached the amount required for a prompt
                    print('[+] Posting prompt')
                    prompt_cycles = 0  # reset the counter
                    prompt_string = ''
                    # do a round robin between the chat strings available, according to the prompt index
                    if prompt_index == 0:  # money raised, schedule and donation link
                        prompt_string = 'Bubble and Jenner have raised {} so far! You too can donate to Gameblast at: {}'.format(
                            new_amount_raised,
                            CHARITY_URL
                        )
                    elif prompt_index == 1:
                        pass  # TO FILL IN
                    for streamer in STREAMER_LIST:
                        channel_name = '#{}'.format(streamer)
                        purrbot.post_in_channel(channel=channel_name, chat_string=prompt_string)
                    # iterate the prompt index, reset it if it reaches the limit (depends on amount of prompts)
                    prompt_index += 1
                    if prompt_index == 2:
                        prompt_index = 0
                else:
                    prompt_cycles += 1  # counter used for prompts
    # wait the check tick, regardless of what the bot has done
    prompt_cycles_left = int(CYCLES_FOR_PROMPT - prompt_cycles + 1)
    print('[+] Next prompt in: {} cycles, {} minutes'.format(
        prompt_cycles_left,
        round((prompt_cycles_left / 60) * CHECK_TICK, 1)
    ))  # +1 as is 0'd
    pause('Purrbot is holding for next cycle', CHECK_TICK)
    bot_cycles += 1


if __name__ == '__main__':
    main()
