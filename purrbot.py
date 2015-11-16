from pytwitch import *

"""
Include a file called cfg.py in the same directory as main.py with the following:
NICK = "purrbot359"                 # your Twitch username, lowercase
PASS = "xyzxyyzxyhfdiufjdsoifjospi" # your Twitch OAuth token, get this from here: http://www.twitchapps.com/tmi/
CHAN = "#test"                      # the channel you want to join
PROMPT_TICK_TIME = 10 * 60  # interval in seconds between when the bot will post prompts
"""


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
    if testing_mode:
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


def main():
    print('--- Starting Purrbot! ---')
    purrbot = Twitch(NICK, PASS, CHAN)
    purrbot.run()


if __name__ == '__main__':
    main()
