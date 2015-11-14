import sqlite3
import os


class PysqliteError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Pysqlite:
    def __init__(self, database_name='', database_file=''):
        self.dbname = database_name
        if os.path.isfile(database_file) and os.access(database_file, os.R_OK):
            self.dbcon = sqlite3.connect(database_file)
            self.dbcur = self.dbcon.cursor()
        else:
            raise PysqliteError('Selected database could not be found or cannot be accessed!')

    def get_db_data(self, table):
        try:
            data = self.dbcur.execute('SELECT * FROM {}'.format(table))
        except Exception as e:
            raise PysqliteError('Pysqlite experienced the following exception: {}'.format(e))
        data_list = []
        for row in data:
            data_list.append(row)
        if len(data_list) == 0:
            raise PysqliteError('Pysqlite found no data in the table: {}'.format(table))
        return data_list

    def insert_db_data(self, table, row_string, data):
        try:
            self.dbcur.execute('INSERT INTO {} VALUES {}'.format(table, row_string), data)
            self.dbcon.commit()
        except Exception as e:
            raise PysqliteError('Pysqlite experienced the following exception: {}'.format(e))
