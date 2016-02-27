from shutil import copy2 as copy_file
from time import sleep


def pause(initial_prompt='', amount=5, clear_pause_prompt=True):
    print('[+] {}'.format(initial_prompt))
    for tick in range(amount, 0, -1):
        print('[*] Pause ends in: {}    '.format(tick), end='\r')
        sleep(1)
    if clear_pause_prompt:
        print('                                        ', end='\r')  # clear the line completely


# get a float value xy.z from the passed string, used for calculations
def get_float_from_string(amount=''):
    if amount == '':
        print('[-] Empty string passed to the decimal from string converter')
        return ''
    amount_string = ''
    for letter in amount:
        if letter in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            amount_string += letter
        if letter == '.':
            amount_string += letter
    return round(float(amount_string), 2)


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


def write_to_text_file(file_dir=None, file_name='donations', file_format='.txt', donation_amount='', verbose=False):
    if donation_amount == '':
        if verbose:
            print('[-] No amount passed to be written to the text file')
    else:
        # bad hack to quickly remove the decimals
        donation_amount = [float(amount) for amount in donation_amount]
        donation_amount = [round(amount, 0) for amount in donation_amount]
        donation_amount = [int(amount) for amount in donation_amount]
        if verbose:
            print('[+] Attempting to write the amount: {} to the text file: {}'.format(
                donation_amount,
                file_name + file_format))
        try:
            with open(file_name + file_format, 'w') as file:
                file.write('{} {} {}'.format(donation_amount[0], donation_amount[1], donation_amount[2]))
                file.close()
            print('[+] Write successful')
        except Exception as e:
            print('[-] Unable to write to text file: {}'.format(e))
        if file_dir is not None:
            try:
                print('[+] Attempting to copy to the required file directory')
                copy_file(src=file_name + file_format, dst='/home/charitybot/apache-flask/assets/charity/' + file_name + file_format)
                print('[+] Copy successful')
            except Exception as e:
                print('[-] Unable to copy text file: {}'.format(e))