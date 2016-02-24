# This Python file uses the following encoding: utf-8
import yarn

STREAMER_LIST = [
    'kateclick'
]

PROMPT_TICK_MINUTES = 10
CHARITY_URL = 'https://mydonate.bt.com/fundraisers/sloughblast16'
DONATION_CURRENCY = '£'
PLAY_DONATION_SOUND = False
DONATION_SOUND_PATH = 'chewbacca.mp3'


def get_donation_amount():
    print('[+] Attempting to scrape the charity URL')
    try:
        soup = yarn.soup_page(url=CHARITY_URL)
    except Exception as e:
        print('[-] Unable to soup the charity URL: {}'.format(e))
        return ''
    else:
        # Here put the specific scraping method required, depending on the website
        current_amount = soup.find('span', {'class': 'text-primary font-20'}).text
        print('[+] Current amount:', current_amount)
        return current_amount

if __name__ == '__main__':
    print('[!] Test running the get donation amount method')
    get_donation_amount()
