import cfg
import charitycfg as charity
from pysqlite import Pysqlite
from pytwitch import Pytwitch, return_kadgar_link, get_online_streamers
from time import sleep, strftime
from shutil import copy2 as copy_file


DATABASE_NAME = 'charity'
DATABASE_TABLE = 'donations'
CHECK_TICK = 10  # seconds between checks
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
    old_amount_float = get_float_from_string(old_amount)
    new_amount_float = get_float_from_string(new_amount)
    if TESTING_MODE:
        print('[!] WARNING! Purrbot is in testing mode and is attempting to do 4.50 - 0.30!')
        old_amount_float = round(float('0.30'), 2)
        new_amount_float = round(float('4.50'), 2)
    amount_donated = new_amount_float - old_amount_float
    print('[+] New donation of: {} - {} = {}$'.format(
        new_amount_float,
        old_amount_float,
        amount_donated))
    if charity.PLAY_DONATION_SOUND:
        try:
            from os import startfile  # used for playing the audio file
            startfile(charity.DONATION_SOUND_PATH)
        except Exception as e:
            print('[-] Unable to play donation sound: {}'.format(e))
    return amount_donated


def insert_donation_into_db(db, amount=0, verbose=False):
    if amount == 0:
        if verbose:
            print('[-] No amount passed, not writing anything to DB')
    else:
        try:
            db.insert_db_data(DATABASE_TABLE, '(NULL, ?, CURRENT_TIMESTAMP)', (amount, ))
            if verbose:
                print('[+] Donation successfully recorded')
        except Exception as e:
            if verbose:
                print('[-] Donation recording error: {}'.format(e))


def write_to_text_file(file_dir=None, file_name='donations', file_format='.txt', donation_amount='', verbose=False):
    if donation_amount == '':
        if verbose:
            print('[-] No amount passed to be written to the text file')
    else:
        # bad hack to quickly remove the decimals
        donation_amount = [float(amount) for amount in donation_amount]
        donation_amount = [round(amount, 0) for amount in donation_amount]
        donation_amount = [int(amount) for amount in donation_amount]
        if verbose:
            print('[+] Attempting to write the amount: {} to the text file: {}'.format(
                donation_amount,
                file_name + file_format))
        try:
            with open(file_name + file_format, 'w') as file:
                file.write('{} {} {}'.format(donation_amount[0], donation_amount[1], donation_amount[2]))
                file.close()
            print('[+] Write successful')
        except Exception as e:
            print('[-] Unable to write to text file: {}'.format(e))
        if file_dir is not None:
            try:
                print('[+] Attempting to copy to the required file directory')
                copy_file(src=file_name + file_format, dst='/home/charitybot/apache-flask/assets/charity/' + file_name + file_format)
                print('[+] Copy successful')
            except Exception as e:
                print('[-] Unable to copy text file: {}'.format(e))


def main():
    # Decide which purrbot to be used here. This should also reflect whatever is
    # inside of charitycfg.py. Make sure that all your options are properly adjusted
    bot_details = cfg.purrbots[charity.BOT_INDEX]  # 0 for team wotsit, 1 for Sag A race, 2 for huntergames
    bot_name = bot_details['NICK']
    bot_token = bot_details['TOKEN']
    print('[!] Starting {}, twitch stream bot for keeping track of charity streams'.format(bot_name))
    print('[!] You can find more information at: https://github.com/purrcat259/twitch-charity-bot')
    purrbot = Pytwitch(name=bot_name, token=bot_token, channel=None, verbose=True)
    last_update_timestamp = strftime('%d/%m/%Y %X')
    print('{} is now online at {} for endpoint: {}, streamers: {}, watching for new donations at: {}. Test mode: {}'.format(
        bot_name,
        last_update_timestamp,
        charity.TEAM_NAME.upper(),
        charity.STREAMER_LIST,
        charity.CHARITY_URL,
        TESTING_MODE))
    purrbot.post_in_streamer_channels(
        streamer_list=get_online_streamers(streamer_list=charity.STREAMER_LIST, verbose=True),
        chat_string='{} is online at {}, watching for donations.'.format(bot_name, last_update_timestamp),
        pause_time=2)
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
        raised_goal_percentage = charity.get_donation_amount()
        current_amount_raised = raised_goal_percentage[0]
        new_amount_raised = raised_goal_percentage[0]
    except Exception as e:
        print('[-] Website scrape error: {}').format(e)
        input('[?] Click any key to exit')
        exit(-1)
    while True:  # The actual bot loop starts here
        print('[+] {} is on cycle: {} for team: {}'.format(
            bot_name,
            bot_cycles,
            charity.TEAM_NAME))
        try:
            raised_goal_percentage = charity.get_donation_amount()
            new_amount_raised = raised_goal_percentage[0]
        except Exception as e:
            print('[-] Website scrape error: {}'.format(e))
            # Skip past this current cycle
            continue
        if not new_amount_raised == current_amount_raised or TESTING_MODE:  # true when a new donation is present
            # update timestamp
            last_update_timestamp = strftime('%d/%m/%Y %X')
            # get a float value of the amount donated just now (not the total)
            new_donation = get_amount_difference(current_amount_raised, new_amount_raised)
            current_amount_raised = new_amount_raised  # update to the newer amount
            if not new_donation == 0.0:
                # insert the currency to a donation string
                print('[!] NEW DONATION: {} at {}'.format(new_donation, last_update_timestamp))
                if TESTING_MODE:
                    from random import randrange
                    current_amount_raised = str(randrange(1, 5))
                # insert the donation in the Database
                insert_donation_into_db(db=database, amount=current_amount_raised, verbose=True)
                # write the donation amount to a text file for use with OBS
                # name the file according to the team name
                write_to_text_file(
                    file_dir='/home/digitalcat/apache-flask/assets/charity/',  # fill this in according to the linux directory
                    file_name=charity.TEAM_NAME,
                    donation_amount=raised_goal_percentage,
                    verbose=True)
                # build the string to post to channels
                chat_string = 'NEW DONATION OF {}{}! {} out of {} raised! {}% of the goal has been reached. Visit {} to donate!'.format(
                    charity.DONATION_CURRENCY,
                    round(new_donation, 2),
                    current_amount_raised,
                    raised_goal_percentage[1],
                    raised_goal_percentage[2],
                    charity.CHARITY_URL)
                # post the chat string to all streamers
                purrbot.post_in_streamer_channels(
                    streamer_list=get_online_streamers(streamer_list=charity.STREAMER_LIST, verbose=True),
                    chat_string=chat_string,
                    pause_time=2)
        else:  # no new donation, check if we should post a prompt instead
            if prompt_cycles == CYCLES_FOR_PROMPT:  # if we've reached the amount required for a prompt
                prompt_cycles = 0  # reset the counter
                prompt_string = ''
                # do a round robin between the chat strings available, according to the prompt index
                if prompt_index == 0:  # money raised, schedule and donation link
                    prompt_string = '£{} has been raised by team {} for Gameblast so far! You too can donate at: {}'.format(
                        new_amount_raised,
                        charity.TEAM_NAME,
                        charity.CHARITY_URL)
                elif prompt_index == 1:
                    prompt_string = 'Watch all the current team {} streamers here: {}'.format(
                        charity.TEAM_NAME,
                        return_kadgar_link(get_online_streamers(streamer_list=charity.STREAMER_LIST, verbose=True)))
                purrbot.post_in_streamer_channels(
                    streamer_list=get_online_streamers(streamer_list=charity.STREAMER_LIST, verbose=True),
                    chat_string=prompt_string,
                    pause_time=2)
                # iterate the prompt index, reset it if it reaches the limit (depends on amount of prompts)
                prompt_index += 1
                if prompt_index == 2:
                    prompt_index = 0
            else:
                prompt_cycles += 1  # counter used for prompts
        # wait the check tick, regardless of what the bot has done
        prompt_cycles_left = int(CYCLES_FOR_PROMPT - prompt_cycles + 1)
        pause('Holding for next cycle.\n[+] Last donation at: {}\n[+] Amount raised: £{}\n[+] Next prompt in {} minutes.'.format(
            last_update_timestamp,
            current_amount_raised,
            round((prompt_cycles_left / 60) * CHECK_TICK, 1)),
            CHECK_TICK)
        bot_cycles += 1


if __name__ == '__main__':
    main()
