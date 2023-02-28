import unittest

from PythonUtils import testdata

from elitech.src.commands import RecordRead

class TestSliceFromString(unittest.TestCase):
    @testdata.TestData([
        {'s': '::'},
        {'s': '0::'},
        {'s': '::1'},
        {'s': '0::1'},
        {'s': '0:1:2:3'},
    ])
    def testInvalidColon(self, s):
        with self.assertRaises(ValueError) as e:
            RecordRead.sliceFromString(s)

        self.assertEqual(str(e.exception), f"Invalid record selection: {s}")

    @testdata.TestData([
        {'s': 'a', 'l': 'a'},
        {'s': 'a:b', 'l': 'a'},
        {'s': '1:b', 'l': 'b'},
        {'s': 'a:2', 'l': 'a'},
        {'s': 'a:', 'l': 'a'},
        {'s': ':b', 'l': 'b'},
        {'s': 'a:b:c', 'l': 'a'},
        {'s': '1:b:c', 'l': 'c'},
        {'s': 'a:2:c', 'l': 'a'},
        {'s': 'a:b:3', 'l': 'a'},
        {'s': '1:2:c', 'l': 'c'},
        {'s': 'a:2:3', 'l': 'a'},
        {'s': '1:b:3', 'l': 'b'},
        {'s': ':b:c', 'l': 'c'},
        {'s': ':2:c', 'l': 'c'},
        {'s': ':b:3', 'l': 'b'},
        {'s': 'a:b:', 'l': 'a'},
        {'s': '1:b:', 'l': 'b'},
        {'s': 'a:2:', 'l': 'a'},
        {'s': ':b:', 'l': 'b'},
    ])
    def testInvalidLiteral(self, s, l):
        with self.assertRaises(ValueError) as e:
            RecordRead.sliceFromString(s)

        self.assertEqual(str(e.exception), f"invalid literal for int() with base 10: '{l}'")

    @testdata.TestData([
        {'s': '',      'start': None, 'stop': None, 'step': None},
        {'s': ':',     'start': None, 'stop': None, 'step': None},
        {'s': '1',     'start':    0, 'stop':    1, 'step': None},
        {'s': '1:2',   'start':    0, 'stop':    2, 'step': None},
        {'s': '1:',    'start':    0, 'stop': None, 'step': None},
        {'s': ':2',    'start': None, 'stop':    2, 'step': None},
        {'s': '1:2:3', 'start':    0, 'stop':    3, 'step':    2},
        {'s': '1:2:',  'start':    0, 'stop': None, 'step':    2},
        {'s': ':2:3',  'start': None, 'stop':    3, 'step':    2},
        {'s': ':2:',   'start': None, 'stop': None, 'step':    2},
    ])
    def testNormal(self, s, start, stop, step):
        s = RecordRead.sliceFromString(s)
        self.assertEqual(s.start, start)
        self.assertEqual(s.stop, stop)
        self.assertEqual(s.step, step)
