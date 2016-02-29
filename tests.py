import unittest
from tools import *


class TestFloatDifference(unittest.TestCase):
    def test_float_difference(self):
        self.assertEqual(4.2, round(get_amount_difference('0.30', '4.50'), 1))

"""
class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)
"""

if __name__ == '__main__':
    unittest.main()
