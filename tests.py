import unittest
from os.path import isfile as file_exists
from os import remove as remove_file
from tools import *


# Test the tools file. TODO: Refactor the tools file and put its tests in its own file

# TODO: Rewrite this test depending on the method rewrite
class TestFloatDifference(unittest.TestCase):
    def test_float_difference(self):
        self.assertEqual(4.2, round(get_amount_difference('0.30', '4.50'), 1))
        self.assertEqual(6.6, round(get_amount_difference('3.4', '10'), 2))


class TestFloatFromString(unittest.TestCase):
    def test_string_from_float(self):
        self.assertEqual(get_float_from_string(''), '')
        self.assertEqual(get_float_from_string('5.34'), 5.34)


class TestFileWriteAndCopy(unittest.TestCase):
    def test_file_write_no_params(self):
        state = write_and_copy_text_file(
            file_name='test',
            file_format='.txt',
            donation_amount=''
        )
        self.assertFalse(state)

    # TODO: Add tests for directory not existing
    def test_file_write(self):
        write_and_copy_text_file(
            file_name='test',
            file_format='.txt',
            donation_amount='test',
            dest_file_dir=None
        )
        self.assertTrue(file_exists('test.txt'))
        with open('test.txt', 'r') as file:
            file_data = file.readline()
            print(file_data)
        self.assertEqual('test test', file_data)
        # Clean up after the test
        remove_file('test.txt')


"""
class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)
"""

if __name__ == '__main__':
    unittest.main()
