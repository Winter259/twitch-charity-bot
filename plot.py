import pysqlite
import time
import matplotlib.pyplot as plt
from datetime import datetime

database = pysqlite.Pysqlite('GGforCharity DB', 'ggforcharity.db')
data = database.get_db_data('donations')

data_list = []
for row in data:
    data_list.append(row)
    #print(row)

time_list = []
for data in data_list:
    time_list.append(data[3])
    #print(data[3])

money_list = []
for data in data_list:
    money_list.append(data[2])
    #print(data[2])

float_list = []
for money in money_list:
    float_str = ''
    for letter in money:
        if letter in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            float_str += letter
        if letter == '.':
            float_str += letter
    if float_str == '110':
        float_str += '.00'
    float_list.append(float(float_str))
    #print(float_str)

plt.title('GGforCharity Donations over Time')
plt.xlabel('time: 12/11/15 22:23 to 16/11/15 00:00')
plt.ylabel('donations ($CAD)')
current_time_epoch = int(time.mktime(datetime.now().timetuple()))
plt.plot(time_list, float_list)
plt.xlim(1447367000, 1447632000)
plt.ylim(0, 5000)
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.show()
