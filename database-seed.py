import sqlite3
import time
import random
from datetime import datetime

table_name = 'testing'
record_count = 50
event_titles = ['EliteEvent', 'Karaoke Night', 'Pankating', 'Mahddogging', 'Fireytoading', 'RheaAyasing']
streamers = ['purrbot359', 'purrcat259', 'purrcat259,purrbot359']

current_time_epoch = time.mktime(datetime.now().timetuple())
print('Current time in epoch seconds: ', current_time_epoch)

dbcon = sqlite3.connect('ggforcharity.db')
dbcur = dbcon.cursor()
print('Current data:')
data = dbcur.execute('SELECT * FROM {}'.format(table_name))
for row in data:
    print('\t', row)
print('Dropping table: ', table_name)
dbcur.execute('DROP TABLE {}'.format(table_name, table_name))
print('Creating table: ', table_name)
dbcur.execute(
    'CREATE TABLE "testing" ('
    '`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,'
    ' `day`	TEXT NOT NULL,'
    ' `start_time`	INTEGER NOT NULL, '
    ' `end_time`	INTEGER NOT NULL, '
    '`title`	TEXT NOT NULL, '
    '`streamers`	TEXT NOT NULL'
    ')'
)
for number in range(1, record_count):
    print('Setting row: {}'.format(number))
    day_string = 'DAY DATE HH:MM - HH:MM'
    end_time = current_time_epoch + 60
    event_title = random.choice(event_titles)
    streamer = random.choice(streamers)
    dbcur.execute('INSERT INTO {} VALUES (NULL, ?, ?, ?, ?, ?)'.format(table_name), (day_string, current_time_epoch, end_time, event_title,  streamer))
    current_time_epoch += random.choice((0, 60, 120))
print('Commiting data')
dbcon.commit()
print('Closing connection')
dbcon.close()
print('All done :)')



