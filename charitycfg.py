import yarn

STREAMER_LIST = [
    'bubblemapgaminglive',
    'misfits_enterprises'
]

PROMPT_TICK_MINUTES = 5
CHARITY_URL = 'http://pmhf3.akaraisin.com/Donation/Event/Home.aspx?seid=11349&mid=8'
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
        td = soup.findAll('td', {'class': 'ThermometerAchived', 'align': 'Right'})  # class is spelt wrongly...
        current_amount = td[0].text  # get just the text
        print('[+] Current amount:', current_amount)
        return current_amount

if __name__ == '__main__':
    print('Test running the get donation amount method')
    print('Current amount: {}'.format(get_donation_amount()))
