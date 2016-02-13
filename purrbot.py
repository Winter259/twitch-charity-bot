import cfg
import charitycfg as charity
from pysqlite import Pysqlite
from pytwitch import Pytwitch
from time import sleep
from os import startfile  # used for playing the audio file

"""
Include a file called cfg.py in the same directory as main.py with the following:
# your Twitch username in lowercase
NICK = 'purrbot359'
# your Twitch OAuth token
PASS = 'yzxyyzxyhfdiufjdsoifjospi'
# the channel you want to join, starting with '#'
CHAN = '#test'
"""

"""
Include another file callled charitycfg.py in the same directory, with the following:
STREAMER_LIST = ['bubblemapgaminglive', 'misfits_enterprises']
"""

DATABASE_NAME = 'charity'
DATABASE_TABLE = 'donations'
CHECK_TICK = 5  # seconds between checks
CYCLES_FOR_PROMPT = (charity.PROMPT_TICK_MINUTES * 60) / CHECK_TICK
TESTING_MODE = False


def pause(initial_prompt='', amount=5, clear_pause_prompt=True):
    print('[+] {}'.format(initial_prompt))
    for tick in range(amount, 0, -1):
        print('[*] Pause ends in: {}    '.format(tick), end='\r')
        sleep(1)
    if clear_pause_prompt:
        print('                                        ', end='\r')  # clear the line completely


# get a float value xy.z from the passed string, used for calculations
def get_float_from_string(amount=''):
    if amount == '':
        print('[-] Empty string passed to the decimal from string converter')
        return ''
    amount_string = ''
    for letter in amount:
        if letter in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            amount_string += letter
        if letter == '.':
            amount_string += letter
    return round(float(amount_string), 2)


def get_amount_difference(old_amount='', new_amount=''):
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
    if charity.PLAY_DONATION_SOUND:
        try:
            startfile(charity.DONATION_SOUND_PATH)
        except Exception as e:
            print('[-] Unable to play donation sound: {}'.format(e))
    return amount_donated


def return_kadgar_link():
    kadgar_link = 'http://kadgar.net/live'
    # if there is only one streamer in the list, then simply return their twitch channel url
    if len(charity.STREAMER_LIST) == 1:
        twitch_link = 'www.twitch.tv/{}'.format(charity.STREAMER_LIST[0])
        return twitch_link
    for streamer in charity.STREAMER_LIST:
        # append each streamer at the end
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


def write_to_text_file(file_name='donations.txt', donation_amount='', verbose=False):
    if donation_amount == '':
        if verbose:
            print('[-] No amount passed to be written to the text file')
    else:
        if verbose:
            print('[+] Attempting to write: {} to the text file'.format(donation_amount))
        try:
            with open(file_name, 'w') as file:
                file.write(donation_amount)
                file.close()
        except Exception as e:
            print('[-] Unable to write to text file: {}'.format(e))


def main():
    print('[!] Starting purrbot359, twitch stream bot for keeping track of charity streams')
    print('[!] You can find more information at: https://github.com/purrcat259/twitch-charity-bot')
    purrbot = Pytwitch(name=cfg.NICK, token=cfg.PASS, channel=cfg.CHAN, verbose=True)
    purrbot.post_in_channel(cfg.CHAN, 'Purrbot now online and watching for donations at {}'.format(
        charity.CHARITY_URL
    ))
    database = Pysqlite(DATABASE_NAME, DATABASE_NAME + '.db')
    # global cycles of the bot
    bot_cycles = 0
    # increment once per cycle, use this to keep track of cycles up until enough cycles pass for a prompt
    prompt_cycles = 0
    # use to keep track of which index is to be posted
    prompt_index = 0
    # strings to store the amount raised for comparison to determine new donations
    current_amount_raised = ''
    new_amount_raised = ''
    print('[+] Retrieving donation amount for the first time')
    try:
        current_amount_raised = charity.get_donation_amount()
        new_amount_raised = charity.get_donation_amount()
    except Exception as e:
        print('[-] Website scrape error: {}').format(e)
        input('[?] Click any key to exit')
        exit(-1)
    while True:  # start the actual loop
        print('[+] Purrbot is on cycle: {}'.format(bot_cycles))
        try:
            new_amount_raised = charity.get_donation_amount()
        except Exception as e:
            print('[-] Website scrape error: {}'.format(e))
            continue
        if not new_amount_raised == current_amount_raised:  # true when a new donation is present
            new_donation = get_amount_difference(current_amount_raised, new_amount_raised)  # get a float value of the amount donated just now
            current_amount_raised = new_amount_raised  # update to the newer amount
            if not new_donation == 0.0:
                print('[!] NEW DONATION: {}{}'.format(charity.DONATION_CURRENCY, new_donation))
                # record the donation to the database
                insert_donation_into_db(db=database, amount=current_amount_raised, verbose=True)
                # build the string to post to channels
                chat_string = 'NEW DONATION OF {}{}! A total of {} has been raised so far! Visit {} to donate!'.format(
                    charity.DONATION_CURRENCY,
                    new_donation,
                    new_amount_raised,
                    charity.CHARITY_URL
                )
                # post the chat string to all streamers
                for streamer in charity.STREAMER_LIST:
                    channel_name = '#{}'.format(streamer)  # channel name is #<streamer>
                    purrbot.post_in_channel(channel=channel_name, chat_string=chat_string)
                # write the donation amount to a text file for use with OBS
                write_to_text_file(donation_amount=current_amount_raised, verbose=True)
        else:  # no new donation, check if we should post a prompt instead
            if prompt_cycles == CYCLES_FOR_PROMPT:  # if we've reached the amount required for a prompt
                print('[+] Posting prompt')
                prompt_cycles = 0  # reset the counter
                prompt_string = ''
                # do a round robin between the chat strings available, according to the prompt index
                if prompt_index == 0:  # money raised, schedule and donation link
                    prompt_string = '{} has been raised during Sloughblast so far! You too can donate to Gameblast at: {}'.format(
                        new_amount_raised,
                        charity.CHARITY_URL
                    )
                """
                elif prompt_index == 1:
                    prompt_string = 'Watch the twat and the misfit rush to Sag A* at the same time here: {}'.format(
                        return_kadgar_link()
                    )
                """
                for streamer in charity.STREAMER_LIST:
                    channel_name = '#{}'.format(streamer)
                    purrbot.post_in_channel(channel=channel_name, chat_string=prompt_string)
                # iterate the prompt index, reset it if it reaches the limit (depends on amount of prompts)
                prompt_index += 1
                if prompt_index == 1:  # change back to 2 later on
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
