from pytwitch import PytwitchReader
from tools import *
from os.path import isfile as file_exists


def read_config_file():
    if not file_exists('config.txt'):
        print('ERROR: Configuration file config.txt is missing!')
        input('Press any key to exit')
        quit()
    with open('config.txt', 'r') as file:
        # strip newline characters
        values = [value.replace('\n', '') for value in file.readlines()]
        if len(values) < 3:
            print('ERROR: Configuration file might be invalid. There should be 3 lines:')
            print('\tBOT TWITCH ACCOUNT NAME')
            print('\tBOT TWITCH API KEY from https://twitchapps.com/tmi/')
            print('\tTWITCH CHANNEL/s TO OBSERVE (just the name of the streamer/s)')
            input('Press any key to exit')
            quit()
        # return list as [bot name, api key, channel]
        return values


def read_commands_file():
    if not file_exists('commands.txt'):
        print('ERROR: Commands file commands.txt is missing!')
        input('Press any key to exit')
        quit()
    with open('commands.txt', 'r') as file:
        commands = [command.replace('\n', '') for command in file.readlines()]
        if len(commands) < 2:
            print('ERROR: Commands file is invalid. There should be at least 2 lines:')
            print('\tCommand name (what people will do to invoke it, ie: !command)')
            print('\tReturn text (what the bot will post to the channel')
            input('Press any key to exit')
            quit()
        command_data = []
        for i, command in enumerate(commands):
            if i == 0 or i % 2 == 0:
                command_data.append([command, commands[i + 1]])
            else:
                continue
        return command_data


def main():
    bot_config = read_config_file()
    commands = read_commands_file()
    print(commands)
    choice = input('Start bot with: {} {} pointed at: {}? (y/n): '.format(
        bot_config[0],
        bot_config[1],
        bot_config[2])
    )
    if choice.lower().startswith('n'):
        quit()
    bot = PytwitchReader(name=bot_config[0], token=bot_config[1], channel=bot_config[2], verbose=True)
    bot.initialise()
    while True:
        bot.increment_cycles()
        print('[+] Cycle: {}'.format(bot.return_cycles()))
        data = bot.receive_data(verbose_disable=True)
        data = bot.get_author_and_message(data)
        if len(data) == 1:
            continue  # skip if it is only one field
        print(data)
        for command in commands:
            if data[1] == command[0]:
                print(command[1])
                break
        sleep(1)


if __name__ == '__main__':
    main()
