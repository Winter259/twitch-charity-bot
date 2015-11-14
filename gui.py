import sqlite3
from tkinter import *

dbcon = sqlite3.connect('ggforcharity.db')
dbcur = dbcon.cursor()
print('Current data:')
db_data = dbcur.execute('SELECT * FROM donations')
data = []
for row in db_data:
    data.append(row)

root = Tk()
title = Label(root, text='Purrbot')
amount_donated = data[-1][2]
donation_string = 'Amount donated: {}'.format(amount_donated)
donation_amount = Label(root, text=donation_string)
title.pack(side=TOP)
donation_amount.pack(side=BOTTOM)
root.mainloop()