import cfg
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import socket
import time
import datetime

"""
Include a file called cfg.py in the same directory as main.py with the following:
HOST = "irc.twitch.tv"              # the Twitch IRC server
PORT = 6667                         # always use port 6667!
NICK = "purrbot359"                 # your Twitch username, lowercase
PASS = "xyzxyyzxyhfdiufjdsoifjospi" # your Twitch OAuth token, get this from here: http://www.twitchapps.com/tmi/
CHAN = "#test"                      # the channel you want to join
"""

URL = 'https://www.justgiving.com/selezen/'  # the url you will be scraping the information from
PROMPT_TICK_TIME = 15 * 60
TICK_TIME = 15  # time in seconds between when the bot checks for new donations

def scrape_data():
    # print('Scraping data...')
    data = urlopen(URL).read()
    # print('Souping data...')
    soup = BS(data, 'lxml')
    spans = soup.findAll('span')
    return spans


def get_donation_amount(spans):
    current_amount = spans[12].text  # manually setting these numbers is convenient but dirty, need to find a better way
    # print('\tDonated amount: {}'.format(current_amount))
    return current_amount


def get_number_of_donations(spans):
    amount_of_donations = spans[13].text
    # print('\tAmount of donations: {}'.format(amount_of_donations))
    return amount_of_donations


def get_stream_time_elapsed():
    t = datetime.datetime.now()
    epoch = time.mktime(t.timetuple())
    # print('Current Times:\n\tdatetime: {}\n\tEpoch seconds: {}'.format(t, epoch))
    t_old = datetime.datetime(2015, 9, 12, 13, 00, 00)
    epoch_old = time.mktime(t_old.timetuple())
    # print('Old Times:\n\tdatetime: {}\n\tEpoch seconds: {}'.format(t_old, epoch_old))
    epoch_passed = epoch - epoch_old
    hours_passed = round(((epoch_passed / 60) / 60), 1)
    # print('\tHours passed: {}'.format(hours_passed))
    return hours_passed


def get_stream_time_left(time_passed):
    time_left = round(24 - (time_passed), 1)
    # print('Time left: {}'.format(time_left))
    return time_left


def pause(prompt='', amount=5):
    ticks = amount
    print(prompt)
    while ticks > 0:
        print('Pause ends in: {}  '.format(ticks), end='\r')
        time.sleep(1)
        ticks -= 1
    print('Pause ended, continuing now!')


def display_live_info(wait_time, spans):
    ticks = wait_time
    donation_amount = get_donation_amount(spans)
    amount_of_donators = get_number_of_donations(spans)
    hours_passed = get_stream_time_elapsed()
    percentage_done = round((hours_passed / 24) * 100, 1)
    print('Current stats:')
    print('\t{}/24 hours elapsed'.format(hours_passed))
    print('\t{}% complete'.format(percentage_done))
    print('\t{} raised by {} donators'.format(donation_amount, amount_of_donators))
    while ticks >= 0:
        print('Next tick: {}   '.format(ticks), end='\r')
        ticks -= 1
        time.sleep(1)
    print('\nCycle finished, starting new cycle')


def connect_to_twitch():
    irc = socket.socket()
    try:
        irc.connect((cfg.HOST, cfg.PORT))
        irc.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
        irc.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
        irc.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))
        print('Bot connected to twitch!')
        return irc
    except Exception as e:
        print(str(e))
        print('Bot did not manage to connect!')
        exit(0)


def twitch_ping_pong(decoded_data):
    if decoded_data.find('PING') != -1:
        print('Bot responding to the irc ping with a pong!')
        pong_string = bytes(decoded_data.replace('PING', 'PONG'), 'utf-8')
        irc.send(pong_string)
        pause('Waiting for after the PONG', 5)

print('--- Starting bot! ---\n')
connected = False
cycle = 0
current_prompt_tick = 0
spans = scrape_data()
current_donation_amount = get_donation_amount(spans)
print('Starting donation amount is: {}\n'.format(current_donation_amount))
while True:
    print('\n--- Starting cycle: {} ---'.format(cycle))
    if current_prompt_tick >= PROMPT_TICK_TIME:
        print('Starting time prompt cycle...')
        irc = connect_to_twitch()
        data = irc.recv(4096) # get output
        received_data = data.decode('utf-8')
        time.sleep(1)
        twitch_ping_pong(received_data)
        print('Calculating data')
        hours_passed = get_stream_time_elapsed()
        percentage_done = round((hours_passed / 24) * 100, 1)
        hours_left = get_stream_time_left(hours_passed)
        time_string = 'Selezen has been streaming for {} hours out of 24. The stream is {}% complete with {} hours to go!'.format(hours_passed, percentage_done, hours_left)
        donate_string = 'Visit {} to donate to the Marie Curie Foundation!'.format(URL)
        print('Attempting to post the data...')
        try:
            irc.send(bytes('PRIVMSG #selezen :{}\r\n'.format(time_string), 'utf-8'))
            time.sleep(2)
            irc.send(bytes('PRIVMSG #selezen :{}\r\n'.format(donate_string), 'utf-8'))
            time.sleep(2)
            print('Post success!')
        except Exception as e:
            print(str(e))
            print('Closing the connection...')
            irc.close()
            exit(0)
        print('Closing the connection...')
        irc.close()
        pause('Waiting for connection to close properly...', 5)
        print('Finished prompt cycle')
        current_prompt_tick = 0
    spans = scrape_data()
    print('Old donation amount was: {}'.format(current_donation_amount))
    new_donation_amount = get_donation_amount(spans)
    print('Current donation amount is: {}'.format(new_donation_amount))
    if not new_donation_amount == current_donation_amount:  # if it is not the same, then it has increased
        print('Starting donation prompt cycle...')
        current_donation_amount = new_donation_amount
        print('There has been a new donation! Calculating data for update...')
        amount_of_donators = get_number_of_donations(spans)
        irc = connect_to_twitch()
        data = irc.recv(4096) # get output
        received_data = data.decode('utf-8')
        time.sleep(1)
        twitch_ping_pong(received_data)
        new_donation_string = 'A new donation has come through! Thank you! A total of {} has been raised by {} donators! Visit {} for more information.'.format(new_donation_amount, amount_of_donators, URL)
        print('Attempting to post the data...')
        try:
            irc.send(bytes('PRIVMSG #selezen :{}\r\n'.format(new_donation_string), 'utf-8'))
            time.sleep(2)
            print('Post success!')
        except Exception as e:
            print(str(e))
            print('Closing the connection...')
            irc.close()
            exit(0)
        print('Closing the connection...')
        irc.close()
    else:
        print('No new donation, starting wait tick')
        display_live_info(TICK_TIME - 1, spans)
        current_prompt_tick += TICK_TIME
        print('Prompt tick: {} cycles away'.format(round((PROMPT_TICK_TIME - current_prompt_tick) / TICK_TIME, 0)))
    print('--- Finished cycle: {} ---'.format(cycle))
    cycle += 1
