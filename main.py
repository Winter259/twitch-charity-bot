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
TICK_TIME = 30  # time in seconds between when the bot checks for new donations

def scrape_data():
    print('Scraping data...')
    data = urlopen(URL).read()
    print('Souping data!')
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
    hours_passed = round(((epoch_passed / 60) / 60), 2)
    # print('\tHours passed: {}'.format(hours_passed))
    return hours_passed


def get_stream_time_left(time_passed):
    time_left = round(24 - (time_passed), 2)
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
    print('Live stats:')
    while ticks > 0:
        donation_amount = get_donation_amount(spans)
        amount_of_donators = get_number_of_donations(spans)
        hours_passed = get_stream_time_elapsed()
        percentage_done = round((hours_passed / 24) * 100, 1)
        print('{}/{} hours, {}%, {} raised by {}, Next tick: {}'.format(hours_passed, 24, percentage_done, donation_amount, amount_of_donators, ticks), end='\r')
        ticks -= 1
        time.sleep(1)
    print('Cycle finished, starting new cycle')

print('Starting bot!')
connected = False
spans = scrape_data()
current_donation_amount = get_donation_amount(spans)
print('Starting donation amount is: {}'.format(current_donation_amount))
while True:
    spans = scrape_data()
    new_donation_amount = get_donation_amount(spans)
    print('Current donation amount is: {}'.format(new_donation_amount))
    if not new_donation_amount == current_donation_amount:  # if it is not the same, then it has increased
        print('There has been a new donation! Calculating data for update...')
        amount_of_donators = get_number_of_donations(spans)
        hours_passed = get_stream_time_elapsed()
        percentage_done = round((hours_passed / 24) * 100, 1)
        hours_left = get_stream_time_left(hours_passed)
        irc = socket.socket()
        try:
            irc = socket.socket()
            irc.connect((cfg.HOST, cfg.PORT))
            irc.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
            irc.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
            irc.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))
            connected = True
            print('Bot connected to twitch!')
        except Exception as e:
            print(str(e))
            connected = False
            print('Bot did not manage to connect!')
            exit(0)
        if connected:
            data = irc.recv(4096) # get output
            received_data = data.decode('utf-8')
            time.sleep(1)
            # do the ping pong check
            if received_data.find('PING') != -1:
                print('Bot responding to the irc ping with a pong!')
                pong_string = bytes(received_data.replace('PING', 'PONG'), 'utf-8')
                irc.send(pong_string)
                pause('Waiting for after the PONG', 5)
            new_donation_string = 'A new donation has come through! {} raised by {} donators!'.format(new_donation_amount, amount_of_donators)
            time_string = 'Selezen has been streaming for {} hours out of 24. The stream is {}% complete with {} hours to go!'.format(hours_passed, percentage_done, hours_left)
            donate_string = 'Visit {} to donate!'.format(URL)
            print('Attempting to post the data...')
            try:
                irc.send(bytes('PRIVMSG #selezen :{}\r\n'.format(new_donation_string), 'utf-8'))
                time.sleep(2)
                irc.send(bytes('PRIVMSG #selezen :{}\r\n'.format(time_string), 'utf-8'))
                time.sleep(2)
                irc.send(bytes('PRIVMSG #selezen :{}\r\n'.format(donate_string), 'utf-8'))
                print('Post success!')
            except Exception as e:
                print(str(e))
                print('Closing the connection...')
                irc.close()
                exit(0)
            print('Closing the connection...')
            irc.close()
            connected = False
    else:
        display_live_info(TICK_TIME, spans)