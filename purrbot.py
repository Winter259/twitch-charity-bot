import bot_config
import charity_config as charity
from pysqlite import Pysqlite
from pytwitch import Pytwitch, return_kadgar_link, get_online_streamers
from time import strftime
from tools import *

VERSION = '0.3'
DATABASE_NAME = 'charity'
DATABASE_TABLE = 'donations'
CHECK_TICK = 10  # seconds between checks
TESTING_MODE = False


def get_non_default_bot(bot_list=None, requested_bot_id=None):
    if bot_list is None:
        print('[-] No bot list passed')
        return None
    if requested_bot_id is None:
        print('[-] No bot requested')
        return None
    for bot in bot_list:
        if bot.return_identity() == requested_bot_id:
            return bot
    else:
        return None


def get_bot(bot_list=None, bot_id='default'):
    if bot_list is None:
        print('[-] No bot list passed')
        return None
    if bot_id is not 'default':
        return get_non_default_bot(bot_list=bot_list, requested_bot_id=bot_id)
    return bot_list[0]


def main():
    print('[!] Starting Twitch Charity Bot')
    print('[!] More information can be found at: https://github.com/purrcat259/twitch-charity-bot')
    print('[+] Opening database connection')
    database = Pysqlite(DATABASE_NAME, DATABASE_NAME + '.db')
    print('[+] Initialising bots')
    # Determine if any extra bots need to be initialised here and store their instances in a list
    active_bots = []
    # Initialise the default bot
    bot_details = bot_config.purrbots[0]
    purrbot = Pytwitch(
        name=bot_details['name'],
        token=bot_details['token'],
        verbose=True)
    active_bots.append(purrbot)
    # check if the streams will use any non-default bots
    active_streams = charity.active_charity_streams
    for stream in active_streams:
        if not stream['bot_name'] == 'default':
            print('[+] Team {} require bot with ID: {}'.format(stream['team_name'], stream['bot_name']))
            for bot in bot_config.purrbots:
                if bot['name'] == stream['bot_name']:
                    print('[+] Bot found, initialising {}'.format(stream['bot_name']))
                    # Assign the team name as an identifier for easy comparison later on
                    non_default_bot = Pytwitch(
                        name=bot['name'],
                        token=bot['token'],
                        identifier=stream['team_name'],
                        verbose=True)
                    active_bots.append(non_default_bot)
                    break
            else:
                print('[-] Bot could not be found, please check your config then try again')
                input('[?] Please press any key to exit')
                exit()
        else:
            print('[+] Team {} will use the standard purrbot359'.format(stream['team_name']))
    print('[+] Charity bot will start for the following streams:')
    print('[+]\tTeam\t\tBot')
    for stream in active_streams:
        if stream['bot_name'] is 'default':
            print('\t{}\t\t{}'.format(
                stream['team_name'],
                active_bots[0].return_identity()))
        else:
            print('\t{}\t\t{}'.format(
                stream['team_name'],
                get_non_default_bot(active_bots, stream['team_name']).return_identity()))
    continue_value = input('[?] Continue? y/n: ')
    if not continue_value.lower().startswith('y'):
        exit()
    update_timestamp = strftime('%d/%m/%Y %X')
    for stream in active_streams:
        # Print to console first
        print('[!] Purrbot is online at {} for stream team: {}, streamers: {}, watching at {}. Test mode: {}'.format(
            update_timestamp,
            stream['team_name'],
            stream['streamer_list'],
            stream['donation_url'],
            TESTING_MODE))
        # get the default bot
        bot = active_bots[0]
        # override if you need another one
        if stream['bot_name'] is not 'default':
            # Get the bot needed, by getting the index on the name
            bot_names = [obj.return_identity() for obj in active_bots]
            bot_index_needed = bot_names.index(stream['team_name'])
            bot = active_bots[bot_index_needed]
        chat_string = '{} is now online for streamers: {}. Watching for donations at {}'.format(
            bot.name,
            stream['streamer_list'],
            stream['donation_url']
        )
        bot.post_in_streamer_channels(
            streamer_list=get_online_streamers(streamer_list=stream['streamer_list']),
            chat_string=chat_string,
            pause_time=2
        )
    """
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
    """
    # build extra active stream data from what we already have
    for stream in active_streams:
        try:
            donation_amount_data = charity.get_donation_amount(url=stream['donation_url'])
        except Exception as e:
            print('[-] Unable to scrape website: {}'.format(e))
            input('Press any key to exit')
            exit()
        stream['amount_raised'] = donation_amount_data[0]
        stream['amount_goal'] = donation_amount_data[1]
        stream['amount_percentage'] = donation_amount_data[2]
        stream['prompt_index'] = 0
        stream['cycle_count'] = 0
        stream['cycles_for_prompt'] = (stream['prompt_tick'] * 60) / CHECK_TICK
    # Start the main loop
    while True:
        for stream in active_streams:
            stream_bot = get_bot(bot_list=active_bots, bot_id=stream['bot_name'])
            print('[+] {} is on cycle: {} for team: {} and streamers: {}'.format(
                stream_bot.name,
                stream['cycle_count'],
                stream['team_name'],
                stream['streamer_list']))
            try:
                donation_amount_data = charity.get_donation_amount(url=stream['donation_url'])
                new_amount_raised = donation_amount_data[0]
            except Exception as e:
                print('[-] Website scrape error: {}'.format(e))
                # Skip past this current stream cycle if the scrape does not work
                continue
            # When a new donation is present, this will be true
            if not new_amount_raised == stream['amount_raised']:
                # update the timestamp
                update_timestamp = strftime('%d/%m/%Y %X')
                # get a float value of the new donation
                new_donation = get_amount_difference(stream['amount_raised'], new_amount_raised)
                # assign the new, higher value to the stream dictionary
                stream['amount_raised'] = new_amount_raised
                # check that the donation amount is not 0.0, encountered this in the past
                if not new_donation == 0.0:
                    # round up the donation, because of floating point values going .999999
                    new_donation = round(new_donation, 2)
                    print('[!] NEW DONATION DETECTED! {}{} at {}'.format(
                        stream['donation_currency'],
                        new_donation,
                        update_timestamp))
                # insert the donation into the database
                insert_donation_into_db(db=database, amount=new_amount_raised, verbose=True)
                # write the donation amount to a text file for use with OBS via the API
                # name the file according to the team name
                write_and_copy_text_file(
                    file_name=stream['team_name'],
                    donation_amount=donation_amount_data,
                    # fill this in according to the linux directory
                    dest_file_dir='/home/digitalcat/apache-flask/assets/charity/',
                    verbose=True)
                # build the string to post to channels
                chat_string = 'NEW DONATION OF {}{}! {}{} out of {}{} raised! {}% of the goal has been reached. Visit {} to donate!'.format(
                    stream['donation_currency'],
                    new_donation,
                    stream['donation_currency'],
                    stream['amount_raised'],
                    stream['donation_currency'],
                    donation_amount_data[1],
                    donation_amount_data[2],
                    stream['donation_url'])
                # post the chat string to all streamers
                purrbot.post_in_streamer_channels(
                    streamer_list=get_online_streamers(streamer_list=stream['streamer_list'], verbose=True),
                    chat_string=chat_string,
                    pause_time=2)
        else:
            # if a new donation has not been detected, then check if we have to post a prompt
            if stream['cycle_count'] == stream['cycles_for_prompt']:
                # reset the cycle counter
                stream['cycle_count'] = 0
                prompt_string = ''
                # do a round robin between the chat strings available, according to the prompt index of the stream
                if stream['prompt_index'] == 0:  # money raised, schedule and donation link
                    prompt_string = '£{} has been raised by team {} for Gameblast so far! You too can donate at: {}'.format(
                        stream['amount_raised'],
                        stream['team_name'],
                        stream['donation_url'])
                elif stream['prompt_index'] == 1:
                    prompt_string = 'Watch all the current team {} streamers here: {}'.format(
                        stream['team_name'],
                        return_kadgar_link(get_online_streamers(streamer_list=stream['streamer_list'], verbose=True)))
                purrbot.post_in_streamer_channels(
                    streamer_list=get_online_streamers(streamer_list=stream['streamer_list'], verbose=True),
                    chat_string=prompt_string,
                    pause_time=2)
                # iterate the prompt index, reset it if it reaches the limit (depends on amount of prompts)
                stream['prompt_index'] += 1
                if stream['prompt_index'] == 2:  # TODO: Set this value somewhere else rather than manual?
                    stream['prompt_index'] = 0
            else:
                stream['cycle_count'] += 1  # iterate the counter
                # print how much time to the next prompt
                cycles_left = int(stream['cycles_for_prompt'] - stream['cycle_count'] + 1)
                time_left = round((cycles_left / 60) * CHECK_TICK, 1)
                print('[+] Team: {}, Last donation at: {}, Next prompt: {} minutes, Amount raised: {}{}, '.format(
                    stream['team_name'],
                    update_timestamp,
                    time_left,
                    stream['donation_currency'],
                    stream['amount_raised']))


if __name__ == '__main__':
    main()
