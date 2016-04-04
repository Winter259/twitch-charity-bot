import unittest
import charity_config
from os.path import isfile as file_exists
from os import remove as remove_file
from tools import *


# Test the tools file. TODO: Refactor the tools file and (maybe) put its tests in its own file
class TestFloatDifference(unittest.TestCase):
    def test_float_difference(self):
        self.assertEqual(4.2, round(get_amount_difference('0.30', '4.50'), 1))
        self.assertEqual(6.6, round(get_amount_difference('3.4', '10'), 2))


class TestFloatFromString(unittest.TestCase):
    def test_string_from_float(self):
        self.assertEqual(get_float_from_string(''), float(0))
        self.assertEqual(get_float_from_string(amount_string='5.34293', decimal_places=2), 5.34)
        self.assertNotEqual(get_float_from_string(amount_string='5.34293', decimal_places=4), 5.34)


class TestFileWrite(unittest.TestCase):
    def test_file_write_no_params(self):
        state = write_text_file(
            file_name='test',
            file_format='.txt',
            file_lines=None,
            verbose=True)
        self.assertFalse(state)

    # TODO: Add tests for directory not existing
    def test_file_write(self):
        # Check that the file exists after writing it
        write_text_file(
            file_name='test',
            file_format='.txt',
            file_lines='test string only',
            verbose=True)
        self.assertTrue(file_exists('test.txt'))
        # Check if the one string we passed is written correctly
        with open('test.txt', 'r') as file:
            file_data = file.readline().strip()
        self.assertEqual('test string only', file_data)
        # Pass an empty list and see if it fails as expected
        state = write_text_file(
            file_name='test',
            file_format='.txt',
            file_lines=[],
            verbose=True)
        self.assertFalse(state)
        # Write one line, but passed as a list
        write_text_file(
            file_name='test',
            file_format='.txt',
            file_lines=['One line given'],
            verbose=True)
        with open('test.txt', 'r') as file:
            file_data = file.readline().strip()
        self.assertEqual('One line given', file_data)
        # write a list of strings
        test_lines = ['hello', 'my', 'name', 'is', 'Simon']
        write_text_file(
            file_name='test',
            file_format='.txt',
            file_lines=test_lines,
            verbose=True)
        # Read the lines and compare with the lines written
        with open('test.txt', 'r') as file:
            file_data = file.readlines()
        for line_number in range(len(test_lines)):
            self.assertEqual(test_lines[line_number], file_data[line_number].strip())
        # Clean up after the test
        remove_file('test.txt')


# test the charity config
class TestCharityConfig(unittest.TestCase):
    def test_config_exists(self):
        self.assertTrue(file_exists('charity_config.py'))

    def test_stream_data_import(self):
        self.assertTrue(charity_config.active_charity_streams)
        self.assertTrue(len(charity_config.active_charity_streams) > 0)

    def test_donation_scrape(self):
        failure_cases = [
            'ERROR: NO URL GIVEN',
            'ERROR: COULD NOT SCRAPE DONATION_AMOUNT'
        ]
        return_state = charity_config.get_donation_amount(url='https://gameblast16.everydayhero.com/uk/tiiq', verbose=False)
        self.assertFalse(return_state in failure_cases)


"""

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)
"""

if __name__ == '__main__':
    unittest.main()
