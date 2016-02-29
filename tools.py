from time import sleep


def pause(initial_prompt='', amount=5, clear_pause_prompt=True):
    print('[+] {}'.format(initial_prompt))
    for tick in range(amount, 0, -1):
        print('[*] Pause ends in: {}    '.format(tick), end='\r')
        sleep(1)
    if clear_pause_prompt:
        print('                                        ', end='\r')  # clear the line completely


# get a float value xy.z from the passed string, used for calculations
def get_float_from_string(amount_string='', decimal_places=2, verbose=False):
    if amount_string == '':
        if verbose:
            print('[-] Empty string passed to the decimal from string converter')
        return round(float(0), decimal_places)
    return_string = ''
    for letter in amount_string:
        if letter in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return_string += letter
        if letter == '.':
            return_string += letter
    return round(float(return_string), decimal_places)


# TODO: Rewrite this method, switch the value order and introduce parameter for decimal place count
def get_amount_difference(old_amount='', new_amount='', test_mode=False):
    if old_amount == '' or new_amount == '':
        print('[-] An amount was not passed to the amount donated method')
        return 0
    old_amount_float = get_float_from_string(old_amount)
    new_amount_float = get_float_from_string(new_amount)
    if test_mode:
        print('[!] WARNING! Purrbot is in testing mode and is attempting to do 4.50 - 0.30!')
        old_amount_float = round(float('0.30'), 2)
        new_amount_float = round(float('4.50'), 2)
    amount_donated = new_amount_float - old_amount_float
    print('[+] New donation of: {} - {} = {}$'.format(
        new_amount_float,
        old_amount_float,
        amount_donated))
    return amount_donated


def insert_donation_into_db(db, db_table='', amount=0, verbose=False):
    if amount == 0:
        if verbose:
            print('[-] No amount passed, not writing anything to DB')
    else:
        try:
            db.insert_db_data(db_table, '(NULL, ?, CURRENT_TIMESTAMP)', (amount, ))
            if verbose:
                print('[+] Donation successfully recorded')
        except Exception as e:
            if verbose:
                print('[-] Donation recording error: {}'.format(e))


# TODO: Add check for if file exists and offer to force overwrite
def write_text_file(file_name='default', file_format='.txt', file_lines=None, verbose=False):
    if file_lines is None:
        if verbose:
            print('[-] No data passed to be written to the text file')
        return False
    elif not type(file_lines) is list:
        file_lines = [file_lines]
    if len(file_lines) == 0:
        if verbose:
            print('[-] No data passed to be written to the text file')
        return False
    if verbose:
        print('[+] Writing data to text file: {}'.format(file_name + file_format))
    try:
        with open(file_name + file_format, 'w') as file:
            for line in file_lines:
                file.write(line + '\n')
        if verbose:
            print('[+] Write to {} successful'.format(file_name + file_format))
    except Exception as e:
        if verbose:
            print('[-] Unable to write to file: {}'.format(e))
        return False
    return True
