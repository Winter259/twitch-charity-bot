import sqlite3
import matplotlib.pyplot as plt

dbcon = sqlite3.connect('ggforcharity.db')
dbcur = dbcon.cursor()
data = dbcur.execute('SELECT * FROM donations')

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

plt.plot(time_list, float_list)
plt.show()
