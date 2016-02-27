# This Python file uses the following encoding: utf-8
import yarn

stream_fields = [
    'team_name',
    'streamer_list',
    'prompt_tick',  # Minutes
    'donation_currency',
    'donation_url',
    'bot_name'
]

# TODO: import these from a txt or csv file rather than hard coding them alongside other values
# TODO, write test to check that these actually exist
active_charity_streams = [
    # TEAM WOTSIT
    dict(
        zip(
            stream_fields,
            [
                'wotsit',
                [
                    'kateclick',
                    'natswright',
                    'symyoulater',
                    'pleijpje'
                ],
                5,
                '£',
                'https://gameblast16.everydayhero.com/uk/team-wotsit',
                'default'
            ]
        )
    ),
    # TEAM SAGARACE
    dict(
        zip(
            stream_fields,
            [
                'sagArace',
                [
                    'bubblemapgaminglive',
                    'misfits_enterprises'
                ],
                5,
                '£',
                'https://gameblast16.everydayhero.com/uk/SagARace',
                'default'
            ]
        )
    ),
    # TEAM TIIQ
    dict(
        zip(
            stream_fields,
            [
                'tiiq',
                [
                    'djtruthsayer',
                    'cmdrhughmann'
                ],
                10,
                '£',
                'https://gameblast16.everydayhero.com/uk/tiiq',
                'tiiqhuntergames'
            ]
        )
    )
]


def get_donation_amount(url=None, verbose=False):
    if url is None:
        if verbose:
            print('[-] No URL given, returning error')
            return 'ERROR: NO URL GIVEN'
    if verbose:
        print('[+] Attempting to scrape the charity URL')
    try:
        soup = yarn.soup_page(url=url)
    except Exception as e:
        if verbose:
            print('[-] Unable to soup the charity URL: {}'.format(e))
        return 'ERROR: COULD NOT SCRAPE DONATION AMOUNT'
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
    for charity_stream in active_charity_streams:
        print('[!] Team {} have raised: {}'.format(
            charity_stream['team_name'],
            get_donation_amount(url=charity_stream['donation_url'], verbose=True)
        ))
