from time import sleep, mktime, gmtime, strftime
from datetime import datetime


def print_with_prepend(print_prepend='[+] ', print_string='', print_end='\n'):
    print('{}{}'.format(print_prepend, print_string), end=print_end)


def pause(initial_prompt='', amount=5, clear_pause_prompt=True):
    print_with_prepend('[+] ', initial_prompt)
    for tick in range(amount, 0, -1):
        print_with_prepend('[*] ', 'Pause ends in: {}    '.format(tick), '\r')
        sleep(1)
    if clear_pause_prompt:
        print('                                        ', end='\r')  # clear the line completely


def print_list(prompt='', list_to_print=[]):
    if len(list_to_print) == 0:
        print_with_prepend('[-] ', 'No list passed to be printed')
    else:
        print('[+] ', prompt)
        for element in list_to_print:
            print_with_prepend('\t', '> {}'.format(element))


def get_current_time(return_type='epoch'):
    current_time = datetime.now()
    current_time_epoch = int(mktime(current_time.timetuple()))
    if return_type == 'epoch':
        return current_time_epoch
    elif return_type == 'timestamp':
        current_time = strftime('%d/%m/%Y %H:%M:%S', gmtime(current_time_epoch))
        return current_time
    else:
        print_with_prepend('[-] ', 'No time return type requested')


if __name__ == '__main__':
    pause('Testing pause', 2)
    test_list = ['hello', 'my', 'name', 'is', 'simon']
    print_list('Testing list printing:', test_list)
    print('Current time epoch: {} Current timestamp: {}'.format(get_current_time('epoch'), get_current_time('timestamp')))
