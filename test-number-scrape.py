import sqlite3

table_name = 'donations'

dbcon = sqlite3.connect('ggforcharity.db')
dbcur = dbcon.cursor()
print('Current data:')
data = dbcur.execute('SELECT * FROM {}'.format(table_name))
donation_list = []
for row in data:
    print('\t', row)
    donation_list.append(row[2])
print('Closing DB connection')
dbcon.close()
word_list = []
for amount in donation_list:
    print('Amount: {}'.format(amount))
    word = ''
    for letter in amount:
        if letter in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # print('Found number: {}'.format(letter))
            word += letter
        if letter == '.':
            # print('Found dot')
            word += letter
    print('Word: {}'.format(word))
    print('Float word: {} Int word: {}'.format(float(word), int(float(word))))
    print('Float calc: {}'.format(round(float('179.96') - float('150.00'), 2)))