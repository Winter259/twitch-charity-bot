from time import sleep
from selenium import webdriver
from subprocess import Popen

URL = 'http://www.specialeffect.org.uk/gameblast'


def write_to_text_file(file_name='', amount_to_write=''):
    print('Writing to text file: {}'.format(file_name))
    with open(file_name, 'w') as file:
        file.write(amount_to_write)
        file.close()

if __name__ == '__main__':
    print('Opening Firefox')
    driver = webdriver.Firefox()
    driver.get(URL)
    previous_donation_amount = driver.find_element_by_class_name('FundsRaised__total').text
    print('Caching the current amount: {}'.format(previous_donation_amount))
    write_to_text_file('gameblast.txt', previous_donation_amount)
    # Upload the file by using the batch file, even when it starts to update after it stops for a while
    Popen('send_file.bat')
    while True:
        print('Accessing: {}'.format(URL))
        driver.get(URL)
        print('Waiting for page to load')
        sleep(5)  # Wait for the page to load fully
        if not driver.title == 'gameblast16':
            print('Cycling browser')
            driver.close()
            sleep(60)
            driver = webdriver.Firefox()
            continue
        donation_amount = driver.find_element_by_class_name('FundsRaised__total').text
        print('Current Donation amount: {}'.format(donation_amount))
        if not donation_amount == previous_donation_amount:
            write_to_text_file('gameblast.txt', donation_amount)
            print('Uploading file')
            # Upload the file by using the batch file
            Popen('send_file.bat')
            previous_donation_amount = donation_amount
        else:
            print('Amount unchanged, not writing to file')
        print('Holding for next cycle')
        sleep(50)
