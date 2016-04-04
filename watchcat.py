from pytwitch import PytwitchReader
from tools import *
from os.path import isfile as file_exists


def read_config_file():
    if not file_exists('config.txt'):
        print('ERROR: Configuration file config.txt does not seem to be in the folder!')
        input('Press any key to exit')
        quit()
    with open('config.txt', 'r') as file:
        values = file.readlines()
        # strip newline characters
        values = [value.replace('\n', '') for value in values]
        if len(values) < 3:
            print('ERROR: Configuration file might be invalid. There should be 3 lines:')
            print('\tBOT TWITCH ACCOUNT NAME')
            print('\tBOT TWITCH API KEY from https://twitchapps.com/tmi/')
            print('\tTWITCH CHANNEL/s TO OBSERVE (just the name of the streamer/s)')
            input('Press any key to exit')
            quit()
        # return list as [bot name, api key, channel]
        return values


def main():
    bot_details = read_config_file()
    choice = input('Start bot with: {} {} pointed at: {}? y/n'.format(
        bot_details[0],
        bot_details[1],
        bot_details[2])
    )
    if choice.lower().startswith('n'):
        quit()
    bot = PytwitchReader(name=bot_details[0], token=bot_details[1], channel=bot_details[2], verbose=True)
    bot.initialise()
    while True:
        bot.print_response()


if __name__ == '__main__':
    main()
