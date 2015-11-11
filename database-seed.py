import sqlite3
import time
import random
from datetime import datetime

table_name = 'testing'
record_count = 10
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
dbcur.execute('CREATE TABLE "testing" (`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,'
              ' `day`	TEXT NOT NULL,'
              ' `start_time`	INTEGER NOT NULL, '
              ' `end_time`	INTEGER NOT NULL, '
              '`event_one`	TEXT NOT NULL, '
              '`streamers_one`	TEXT NOT NULL,'
              ' `event_two`	TEXT,'
              ' `streamers_two`	TEXT)')
for number in range(1, record_count):
    day = 'Day String'
    end_time = current_time_epoch + 60
    event_title = random.choice(event_titles)
    streamer = random.choice(streamers)
    if number % 2 == 0:
        print('Setting alternate event', end='\r')
        event_title_two = random.choice(event_titles)
        streamer_two = random.choice(streamers)
        dbcur.execute('INSERT INTO {} VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)'.format(table_name), (day, current_time_epoch, end_time, event_title,  streamer, event_title_two, streamer_two))
    else:
        print('Setting normal event', end='\r')
        dbcur.execute('INSERT INTO {} VALUES (NULL, ?, ?, ?, ?, ?, NULL, NULL)'.format(table_name), (day, current_time_epoch, end_time, event_title,  streamer))
    current_time_epoch += random.choice((20, 30, 40))
print('Commiting data')
dbcon.commit()
print('Closing connection')
dbcon.close()
print('All done :)')



