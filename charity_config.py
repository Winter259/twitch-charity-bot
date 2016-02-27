# This Python file uses the following encoding: utf-8
import yarn

STREAMER_LIST = [
    'misfits_enterprises',
    'bubblemapgaminglive'
]

TEAM_NAME = 'sagArace'
BOT_INDEX = 1

PROMPT_TICK_MINUTES = 10
CHARITY_URL = 'https://gameblast16.everydayhero.com/uk/SagARace'
DONATION_CURRENCY = '£'
PLAY_DONATION_SOUND = False
DONATION_SOUND_PATH = 'chewbacca.mp3'


def get_donation_amount(verbose=False):
    print('[+] Attempting to scrape the charity URL')
    try:
        soup = yarn.soup_page(url=CHARITY_URL)
    except Exception as e:
        print('[-] Unable to soup the charity URL: {}'.format(e))
        return 'SCRAPE ERROR'
    else:
        # Here put the specific scraping method required, depending on the website
        container_div = soup.find('div', {'id': 'bar--donation__main'})
        sub_container = container_div.find_all('div', {'class': 'donation-bar__detail'})
        raised_amount = sub_container[2].strong.text.strip('£')
        goal_amount = sub_container[3].strong.text.strip('£')
        raised_amount = raised_amount.replace(',', '')
        goal_amount = goal_amount.replace(',', '')
        percentage_raised = round((float(raised_amount) / float(goal_amount)) * 100, 2)
        if verbose:
            print('[+] Current amount: {}'.format(raised_amount))
            print('[+] Current goal: {}'.format(goal_amount))
            print('[+] Percentage raised: {}%'.format(percentage_raised))
        return [raised_amount, goal_amount, percentage_raised]


if __name__ == '__main__':
    print('[!] Test running the get donation amount method')
    get_donation_amount(verbose=True)
