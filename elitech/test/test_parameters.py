# Copyright 2023 Pascal COMBES <pascom@orange.fr>
#
# This file is part of python-elitech.
#
# python-elitech is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-elitech is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-elitech. If not, see <http://www.gnu.org/licenses/>

import unittest

from PythonUtils import testdata

from enum import Enum
import datetime
import math

from elitech.src.parameters import Range
from elitech.src.parameters import StringParameter
from elitech.src.parameters import DateTimeParameter
from elitech.src.parameters import DWordParameter
from elitech.src.parameters import WordParameter
from elitech.src.parameters import ByteParameter
from elitech.src.parameters import EnumParameter
from elitech.src.parameters import HalfByteParameter
from elitech.src.parameters import BitParameter
from elitech.src.parameters import EnumBitParameter
from elitech.src.parameters import FloatParameter
from elitech.src.parameters import TimeSpanParameter
from elitech.src.parameters import TimeZoneParameter

class TestStringParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'l':  1, 'w':  True},
        {'o': 1, 'l': 12, 'w':  True},
        {'o': 0, 'l':  1, 'w':  True},
        {'o': 1, 'l': 12, 'w':  True},
        {'o': 0, 'l':  1, 'w': False},
        {'o': 1, 'l': 12, 'w': False},
        {'o': 0, 'l':  1, 'w': False},
        {'o': 1, 'l': 12, 'w': False},
    ])
    def testConstructor(self, o, l, w):
        param = StringParameter('test-name', 'Test description', o, l, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, l)
        self.assertEqual(param.range, Range(o, l))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*l))

    @testdata.TestData([
        {'data': b'abcdefghijkl',                                     'expectedValue': 'abcdefghijkl'},
        {'data': b'test\x00\x00\x00\x00\x00\x00\x00\x00',             'expectedValue': 'test'        },
        {'data': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 'expectedValue': '',           },
    ])
    def testParseData(self, data, expectedValue):
        param = StringParameter('test-name', 'Test description', 0, 12, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedValue)
        self.assertEqual(bytes(param), data)


    @testdata.TestData([
        {'value': 'abcdefghijkl', 'expectedBytes': b'abcdefghijkl'                                    },
        {'value': 'test',         'expectedBytes': b'test\x00\x00\x00\x00\x00\x00\x00\x00'            },
        {'value': '',             'expectedBytes': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'},
    ])
    def testParseValue(self, value, expectedBytes):
        param = StringParameter('test-name', 'Test description', 0, 12, True)
        param.parseValue(value)
        self.assertEqual(param.value, value)
        self.assertEqual(str(param), value)
        self.assertEqual(bytes(param), expectedBytes)


class TestDateTimeParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'w':  True},
        {'o': 1, 'w':  True},
        {'o': 0, 'w': False},
        {'o': 1, 'w': False},
    ])
    def testConstructor(self, o, w):
        param = DateTimeParameter('test-name', 'Test description', o, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 7)
        self.assertEqual(param.range, Range(o, 7))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*7))

    @testdata.TestData([
        {'data': bytes([0x01, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00]), 'expectedValue': datetime.datetime(2001, 1, 1, 0, 0, 0), 'expectedStr': '2001-01-01 00:00:00'},
        {'data': bytes([0x01, 0x02, 0x00, 0x03, 0x04, 0x05, 0x06]), 'expectedValue': datetime.datetime(2001, 2, 3, 4, 5, 6), 'expectedStr': '2001-02-03 04:05:06'},
    ])
    def testParseData(self, data, expectedValue, expectedStr):
        param = DateTimeParameter('test-name', 'Test description', 0, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), data)


    @testdata.TestData([
        {'value': '2001-01-01 00:00:00', 'expectedValue': datetime.datetime(2001, 1, 1, 0, 0, 0), 'expectedBytes': bytes([0x01, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00])},
        {'value': '2001-02-03 04:05:06', 'expectedValue': datetime.datetime(2001, 2, 3, 4, 5, 6), 'expectedBytes': bytes([0x01, 0x02, 0x00, 0x03, 0x04, 0x05, 0x06])},
    ])
    def testParseValue(self, value, expectedValue, expectedBytes):
        param = DateTimeParameter('test-name', 'Test description', 0, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), value)
        self.assertEqual(bytes(param), expectedBytes)


    def testNow(self):
        param = DateTimeParameter('test-name', 'Test description', 0, True)
        before = datetime.datetime.now()
        param.now()
        after = datetime.datetime.now()
        self.assertGreaterEqual(param.value, before)
        self.assertLessEqual(param.value, after)


class TestDWordParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'w':  True},
        {'o': 1, 'w':  True},
        {'o': 0, 'w': False},
        {'o': 1, 'w': False},
    ])
    def testConstructor(self, o, w):
        param = DWordParameter('test-name', 'Test description', o, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 4)
        self.assertEqual(param.range, Range(o, 4))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00, 0x00, 0x00, 0x00]))

    @testdata.TestData([
        {'data': bytes([0x00, 0x00, 0x00, 0x00]), 'expectedValue': 0x00000000, 'expectedStr': '0x00000000'},
        {'data': bytes([0x00, 0x00, 0x00, 0x01]), 'expectedValue': 0x00000001, 'expectedStr': '0x00000001'},
        {'data': bytes([0x00, 0x00, 0x00, 0xFF]), 'expectedValue': 0x000000FF, 'expectedStr': '0x000000FF'},
        {'data': bytes([0x00, 0x00, 0x01, 0x00]), 'expectedValue': 0x00000100, 'expectedStr': '0x00000100'},
        {'data': bytes([0x00, 0x00, 0xFF, 0xFF]), 'expectedValue': 0x0000FFFF, 'expectedStr': '0x0000FFFF'},
        {'data': bytes([0x00, 0x01, 0x00, 0x00]), 'expectedValue': 0x00010000, 'expectedStr': '0x00010000'},
        {'data': bytes([0xFF, 0xFF, 0xFF, 0xFF]), 'expectedValue': 0xFFFFFFFF, 'expectedStr': '0xFFFFFFFF'},
    ])
    def testParseData(self, data, expectedValue, expectedStr):
        param = DWordParameter('test-name', 'Test description', 0, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), data)

    @testdata.TestData([
        {'value':                         '0x00000000', 'expectedValue': 0x00000000, 'expectedStr': '0x00000000', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0x00])},
        {'value':                         '0x00000001', 'expectedValue': 0x00000001, 'expectedStr': '0x00000001', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0x01])},
        {'value':                         '0x000000FF', 'expectedValue': 0x000000FF, 'expectedStr': '0x000000FF', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0xFF])},
        {'value':                         '0x00000100', 'expectedValue': 0x00000100, 'expectedStr': '0x00000100', 'expectedBytes': bytes([0x00, 0x00, 0x01, 0x00])},
        {'value':                         '0x0000FFFF', 'expectedValue': 0x0000FFFF, 'expectedStr': '0x0000FFFF', 'expectedBytes': bytes([0x00, 0x00, 0xFF, 0xFF])},
        {'value':                         '0x00010000', 'expectedValue': 0x00010000, 'expectedStr': '0x00010000', 'expectedBytes': bytes([0x00, 0x01, 0x00, 0x00])},
        {'value':                         '0xFFFFFFFF', 'expectedValue': 0xFFFFFFFF, 'expectedStr': '0xFFFFFFFF', 'expectedBytes': bytes([0xFF, 0xFF, 0xFF, 0xFF])},
        {'value': '0b00000000000000000000000000000000', 'expectedValue': 0x00000000, 'expectedStr': '0x00000000', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0x00])},
        {'value': '0b00000000000000000000000000000001', 'expectedValue': 0x00000001, 'expectedStr': '0x00000001', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0x01])},
        {'value': '0b00000000000000000000000011111111', 'expectedValue': 0x000000FF, 'expectedStr': '0x000000FF', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0xFF])},
        {'value': '0b00000000000000000000000100000000', 'expectedValue': 0x00000100, 'expectedStr': '0x00000100', 'expectedBytes': bytes([0x00, 0x00, 0x01, 0x00])},
        {'value': '0b00000000000000001111111111111111', 'expectedValue': 0x0000FFFF, 'expectedStr': '0x0000FFFF', 'expectedBytes': bytes([0x00, 0x00, 0xFF, 0xFF])},
        {'value': '0b00000000000000010000000000000000', 'expectedValue': 0x00010000, 'expectedStr': '0x00010000', 'expectedBytes': bytes([0x00, 0x01, 0x00, 0x00])},
        {'value': '0b11111111111111111111111111111111', 'expectedValue': 0xFFFFFFFF, 'expectedStr': '0xFFFFFFFF', 'expectedBytes': bytes([0xFF, 0xFF, 0xFF, 0xFF])},
        {'value':                       '000000000000', 'expectedValue': 0x00000000, 'expectedStr': '0x00000000', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0x00])},
        {'value':                       '000000000001', 'expectedValue': 0x00000001, 'expectedStr': '0x00000001', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0x01])},
        {'value':                       '000000000377', 'expectedValue': 0x000000FF, 'expectedStr': '0x000000FF', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0xFF])},
        {'value':                       '000000000400', 'expectedValue': 0x00000100, 'expectedStr': '0x00000100', 'expectedBytes': bytes([0x00, 0x00, 0x01, 0x00])},
        {'value':                       '000000177777', 'expectedValue': 0x0000FFFF, 'expectedStr': '0x0000FFFF', 'expectedBytes': bytes([0x00, 0x00, 0xFF, 0xFF])},
        {'value':                       '000000200000', 'expectedValue': 0x00010000, 'expectedStr': '0x00010000', 'expectedBytes': bytes([0x00, 0x01, 0x00, 0x00])},
        {'value':                       '037777777777', 'expectedValue': 0xFFFFFFFF, 'expectedStr': '0xFFFFFFFF', 'expectedBytes': bytes([0xFF, 0xFF, 0xFF, 0xFF])},
        {'value':                                  '0', 'expectedValue': 0x00000000, 'expectedStr': '0x00000000', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0x00])},
        {'value':                                  '1', 'expectedValue': 0x00000001, 'expectedStr': '0x00000001', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0x01])},
        {'value':                                '255', 'expectedValue': 0x000000FF, 'expectedStr': '0x000000FF', 'expectedBytes': bytes([0x00, 0x00, 0x00, 0xFF])},
        {'value':                                '256', 'expectedValue': 0x00000100, 'expectedStr': '0x00000100', 'expectedBytes': bytes([0x00, 0x00, 0x01, 0x00])},
        {'value':                              '65535', 'expectedValue': 0x0000FFFF, 'expectedStr': '0x0000FFFF', 'expectedBytes': bytes([0x00, 0x00, 0xFF, 0xFF])},
        {'value':                              '65536', 'expectedValue': 0x00010000, 'expectedStr': '0x00010000', 'expectedBytes': bytes([0x00, 0x01, 0x00, 0x00])},
        {'value':                         '4294967295', 'expectedValue': 0xFFFFFFFF, 'expectedStr': '0xFFFFFFFF', 'expectedBytes': bytes([0xFF, 0xFF, 0xFF, 0xFF])},
    ])
    def testParseValue(self, value, expectedValue, expectedStr, expectedBytes):
        param = DWordParameter('test-name', 'Test description', 0, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'value':  '0xx00'},
        {'value':   '0b02'},
        {'value':  '0bb01'},
        {'value':  '00009'},
        {'value': 'ABCDEF'},
    ])
    def testParseValueInvalid(self, value):
        param = DWordParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid value for unsigned integer: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*4))

    @testdata.TestData([
        {'value':                         '0x100000000'},
        {'value': '0b100000000000000000000000000000000'},
        {'value':                        '040000000000'},
        {'value':                          '4294967296'},
    ])
    def testParseValueTooLarge(self, value):
        param = DWordParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Value is too large: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*4))


class TestWordParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'w':  True},
        {'o': 1, 'w':  True},
        {'o': 0, 'w': False},
        {'o': 1, 'w': False},
    ])
    def testConstructor(self, o, w):
        param = WordParameter('test-name', 'Test description', o, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 2)
        self.assertEqual(param.range, Range(o, 2))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00, 0x00]))

    @testdata.TestData([
        {'data': bytes([0x00, 0x00]), 'expectedValue': 0x0000, 'expectedStr': '0x0000'},
        {'data': bytes([0x00, 0x01]), 'expectedValue': 0x0001, 'expectedStr': '0x0001'},
        {'data': bytes([0x00, 0xFF]), 'expectedValue': 0x00FF, 'expectedStr': '0x00FF'},
        {'data': bytes([0x01, 0x00]), 'expectedValue': 0x0100, 'expectedStr': '0x0100'},
        {'data': bytes([0xFF, 0xFF]), 'expectedValue': 0xFFFF, 'expectedStr': '0xFFFF'},
    ])
    def testParseData(self, data, expectedValue, expectedStr):
        param = WordParameter('test-name', 'Test description', 0, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), data)

    @testdata.TestData([
        {'value':             '0x0000', 'expectedValue': 0x0000, 'expectedStr': '0x0000', 'expectedBytes': bytes([0x00, 0x00])},
        {'value':             '0x0001', 'expectedValue': 0x0001, 'expectedStr': '0x0001', 'expectedBytes': bytes([0x00, 0x01])},
        {'value':             '0x00FF', 'expectedValue': 0x00FF, 'expectedStr': '0x00FF', 'expectedBytes': bytes([0x00, 0xFF])},
        {'value':             '0x0100', 'expectedValue': 0x0100, 'expectedStr': '0x0100', 'expectedBytes': bytes([0x01, 0x00])},
        {'value':             '0xFFFF', 'expectedValue': 0xFFFF, 'expectedStr': '0xFFFF', 'expectedBytes': bytes([0xFF, 0xFF])},
        {'value': '0b0000000000000000', 'expectedValue': 0x0000, 'expectedStr': '0x0000', 'expectedBytes': bytes([0x00, 0x00])},
        {'value': '0b0000000000000001', 'expectedValue': 0x0001, 'expectedStr': '0x0001', 'expectedBytes': bytes([0x00, 0x01])},
        {'value': '0b0000000011111111', 'expectedValue': 0x00FF, 'expectedStr': '0x00FF', 'expectedBytes': bytes([0x00, 0xFF])},
        {'value': '0b0000000100000000', 'expectedValue': 0x0100, 'expectedStr': '0x0100', 'expectedBytes': bytes([0x01, 0x00])},
        {'value': '0b1111111111111111', 'expectedValue': 0xFFFF, 'expectedStr': '0xFFFF', 'expectedBytes': bytes([0xFF, 0xFF])},
        {'value':            '0000000', 'expectedValue': 0x0000, 'expectedStr': '0x0000', 'expectedBytes': bytes([0x00, 0x00])},
        {'value':            '0000001', 'expectedValue': 0x0001, 'expectedStr': '0x0001', 'expectedBytes': bytes([0x00, 0x01])},
        {'value':            '0000377', 'expectedValue': 0x00FF, 'expectedStr': '0x00FF', 'expectedBytes': bytes([0x00, 0xFF])},
        {'value':            '0000400', 'expectedValue': 0x0100, 'expectedStr': '0x0100', 'expectedBytes': bytes([0x01, 0x00])},
        {'value':            '0177777', 'expectedValue': 0xFFFF, 'expectedStr': '0xFFFF', 'expectedBytes': bytes([0xFF, 0xFF])},
        {'value':                  '0', 'expectedValue': 0x0000, 'expectedStr': '0x0000', 'expectedBytes': bytes([0x00, 0x00])},
        {'value':                  '1', 'expectedValue': 0x0001, 'expectedStr': '0x0001', 'expectedBytes': bytes([0x00, 0x01])},
        {'value':                '255', 'expectedValue': 0x00FF, 'expectedStr': '0x00FF', 'expectedBytes': bytes([0x00, 0xFF])},
        {'value':                '256', 'expectedValue': 0x0100, 'expectedStr': '0x0100', 'expectedBytes': bytes([0x01, 0x00])},
        {'value':              '65535', 'expectedValue': 0xFFFF, 'expectedStr': '0xFFFF', 'expectedBytes': bytes([0xFF, 0xFF])},
    ])
    def testParseValue(self, value, expectedValue, expectedStr, expectedBytes):
        param = WordParameter('test-name', 'Test description', 0, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'value':  '0xx00'},
        {'value':   '0b02'},
        {'value':  '0bb01'},
        {'value':  '00009'},
        {'value': 'ABCDEF'},
    ])
    def testParseValueInvalid(self, value):
        param = WordParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid value for unsigned integer: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*2))

    @testdata.TestData([
        {'value':             '0x10000'},
        {'value': '0b10000000000000000'},
        {'value':            '01000000'},
        {'value':               '65536'},
    ])
    def testParseValueTooLarge(self, value):
        param = WordParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Value is too large: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*2))

class TestByteParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'w':  True},
        {'o': 1, 'w':  True},
        {'o': 0, 'w': False},
        {'o': 1, 'w': False},
    ])
    def testConstructor(self, o, w):
        param = ByteParameter('test-name', 'Test description', o, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 1)
        self.assertEqual(param.range, Range(o, 1))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))

    @testdata.TestData([
        {'data': bytes([0x00]), 'expectedValue': 0x00, 'expectedStr': '0x00'},
        {'data': bytes([0x01]), 'expectedValue': 0x01, 'expectedStr': '0x01'},
        {'data': bytes([0xFF]), 'expectedValue': 0xFF, 'expectedStr': '0xFF'},
    ])
    def testParseData(self, data, expectedValue, expectedStr):
        param = ByteParameter('test-name', 'Test description', 0, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), data)

    @testdata.TestData([
        {'value':       '0x00', 'expectedValue': 0x00, 'expectedStr': '0x00', 'expectedBytes': bytes([0x00])},
        {'value':       '0x01', 'expectedValue': 0x01, 'expectedStr': '0x01', 'expectedBytes': bytes([0x01])},
        {'value':       '0xFF', 'expectedValue': 0xFF, 'expectedStr': '0xFF', 'expectedBytes': bytes([0xFF])},
        {'value': '0b00000000', 'expectedValue': 0x00, 'expectedStr': '0x00', 'expectedBytes': bytes([0x00])},
        {'value': '0b00000001', 'expectedValue': 0x01, 'expectedStr': '0x01', 'expectedBytes': bytes([0x01])},
        {'value': '0b11111111', 'expectedValue': 0xFF, 'expectedStr': '0xFF', 'expectedBytes': bytes([0xFF])},
        {'value':       '0000', 'expectedValue': 0x00, 'expectedStr': '0x00', 'expectedBytes': bytes([0x00])},
        {'value':       '0001', 'expectedValue': 0x01, 'expectedStr': '0x01', 'expectedBytes': bytes([0x01])},
        {'value':       '0377', 'expectedValue': 0xFF, 'expectedStr': '0xFF', 'expectedBytes': bytes([0xFF])},
        {'value':          '0', 'expectedValue': 0x00, 'expectedStr': '0x00', 'expectedBytes': bytes([0x00])},
        {'value':          '1', 'expectedValue': 0x01, 'expectedStr': '0x01', 'expectedBytes': bytes([0x01])},
        {'value':        '255', 'expectedValue': 0xFF, 'expectedStr': '0xFF', 'expectedBytes': bytes([0xFF])},
    ])
    def testParseValue(self, value, expectedValue, expectedStr, expectedBytes):
        param = ByteParameter('test-name', 'Test description', 0, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'value':  '0xx00'},
        {'value':   '0b02'},
        {'value':  '0bb01'},
        {'value':  '00009'},
        {'value': 'ABCDEF'},
    ])
    def testParseValueInvalid(self, value):
        param = ByteParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid value for unsigned integer: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))

    @testdata.TestData([
        {'value':       '0x100'},
        {'value': '0b100000000'},
        {'value':        '0400'},
        {'value':         '256'},
    ])
    def testParseValueTooLarge(self, value):
        param = ByteParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Value is too large: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))


class TestEnum2(Enum):
    ZERO = 0x00
    ONE  = 0x01
    TWO  = 0x02
    MAX  = 0x03

class TestEnum7(Enum):
    ZERO = 0x00
    ONE  = 0x01
    TWO  = 0x02
    MAX  = 0x7F

class TestEnum8(Enum):
    ZERO = 0x00
    ONE  = 0x01
    TWO  = 0x02
    MAX  = 0xFF

class TestEnum16(Enum):
    ZERO = 0x0000
    ONE  = 0x0001
    TWO  = 0x0002
    MAX  = 0xFFFF

class TestEnumParameter(unittest.TestCase):
    @testdata.TestData([
        {'cls':  TestEnum2, 's':  2, 'o': 0, 'bo': 0, 'w':  True},
        {'cls':  TestEnum2, 's':  2, 'o': 1, 'bo': 0, 'w':  True},
        {'cls':  TestEnum2, 's':  2, 'o': 0, 'bo': 0, 'w': False},
        {'cls':  TestEnum2, 's':  2, 'o': 1, 'bo': 0, 'w': False},
        {'cls':  TestEnum7, 's':  7, 'o': 0, 'bo': 0, 'w':  True},
        {'cls':  TestEnum7, 's':  7, 'o': 1, 'bo': 0, 'w':  True},
        {'cls':  TestEnum7, 's':  7, 'o': 0, 'bo': 0, 'w': False},
        {'cls':  TestEnum7, 's':  7, 'o': 1, 'bo': 0, 'w': False},
        {'cls':  TestEnum8, 's':  8, 'o': 0, 'bo': 0, 'w':  True},
        {'cls':  TestEnum8, 's':  8, 'o': 1, 'bo': 0, 'w':  True},
        {'cls':  TestEnum8, 's':  8, 'o': 0, 'bo': 0, 'w': False},
        {'cls':  TestEnum8, 's':  8, 'o': 1, 'bo': 0, 'w': False},
        {'cls': TestEnum16, 's': 16, 'o': 0, 'bo': 0, 'w':  True},
        {'cls': TestEnum16, 's': 16, 'o': 1, 'bo': 0, 'w':  True},
        {'cls': TestEnum16, 's': 16, 'o': 0, 'bo': 0, 'w': False},
        {'cls': TestEnum16, 's': 16, 'o': 1, 'bo': 0, 'w': False},
        {'cls':  TestEnum2, 's':  2, 'o': 0, 'bo': 1, 'w':  True},
        {'cls':  TestEnum2, 's':  2, 'o': 1, 'bo': 1, 'w':  True},
        {'cls':  TestEnum2, 's':  2, 'o': 0, 'bo': 1, 'w': False},
        {'cls':  TestEnum2, 's':  2, 'o': 1, 'bo': 1, 'w': False},
        {'cls':  TestEnum7, 's':  7, 'o': 0, 'bo': 1, 'w':  True},
        {'cls':  TestEnum7, 's':  7, 'o': 1, 'bo': 1, 'w':  True},
        {'cls':  TestEnum7, 's':  7, 'o': 0, 'bo': 1, 'w': False},
        {'cls':  TestEnum7, 's':  7, 'o': 1, 'bo': 1, 'w': False},
        {'cls':  TestEnum8, 's':  8, 'o': 0, 'bo': 1, 'w':  True},
        {'cls':  TestEnum8, 's':  8, 'o': 1, 'bo': 1, 'w':  True},
        {'cls':  TestEnum8, 's':  8, 'o': 0, 'bo': 1, 'w': False},
        {'cls':  TestEnum8, 's':  8, 'o': 1, 'bo': 1, 'w': False},
        {'cls': TestEnum16, 's': 16, 'o': 0, 'bo': 1, 'w':  True},
        {'cls': TestEnum16, 's': 16, 'o': 1, 'bo': 1, 'w':  True},
        {'cls': TestEnum16, 's': 16, 'o': 0, 'bo': 1, 'w': False},
        {'cls': TestEnum16, 's': 16, 'o': 1, 'bo': 1, 'w': False},
        {'cls':  TestEnum2, 's':  2, 'o': 0, 'bo': 7, 'w':  True},
        {'cls':  TestEnum2, 's':  2, 'o': 1, 'bo': 7, 'w':  True},
        {'cls':  TestEnum2, 's':  2, 'o': 0, 'bo': 7, 'w': False},
        {'cls':  TestEnum2, 's':  2, 'o': 1, 'bo': 7, 'w': False},
        {'cls':  TestEnum7, 's':  7, 'o': 0, 'bo': 7, 'w':  True},
        {'cls':  TestEnum7, 's':  7, 'o': 1, 'bo': 7, 'w':  True},
        {'cls':  TestEnum7, 's':  7, 'o': 0, 'bo': 7, 'w': False},
        {'cls':  TestEnum7, 's':  7, 'o': 1, 'bo': 7, 'w': False},
        {'cls':  TestEnum8, 's':  8, 'o': 0, 'bo': 7, 'w':  True},
        {'cls':  TestEnum8, 's':  8, 'o': 1, 'bo': 7, 'w':  True},
        {'cls':  TestEnum8, 's':  8, 'o': 0, 'bo': 7, 'w': False},
        {'cls':  TestEnum8, 's':  8, 'o': 1, 'bo': 7, 'w': False},
        {'cls': TestEnum16, 's': 16, 'o': 0, 'bo': 7, 'w':  True},
        {'cls': TestEnum16, 's': 16, 'o': 1, 'bo': 7, 'w':  True},
        {'cls': TestEnum16, 's': 16, 'o': 0, 'bo': 7, 'w': False},
        {'cls': TestEnum16, 's': 16, 'o': 1, 'bo': 7, 'w': False},
        {'cls':  TestEnum2, 's':  2, 'o': 0, 'bo': 8, 'w':  True},
        {'cls':  TestEnum2, 's':  2, 'o': 1, 'bo': 8, 'w':  True},
        {'cls':  TestEnum2, 's':  2, 'o': 0, 'bo': 8, 'w': False},
        {'cls':  TestEnum2, 's':  2, 'o': 1, 'bo': 8, 'w': False},
        {'cls':  TestEnum7, 's':  7, 'o': 0, 'bo': 8, 'w':  True},
        {'cls':  TestEnum7, 's':  7, 'o': 1, 'bo': 8, 'w':  True},
        {'cls':  TestEnum7, 's':  7, 'o': 0, 'bo': 8, 'w': False},
        {'cls':  TestEnum7, 's':  7, 'o': 1, 'bo': 8, 'w': False},
        {'cls':  TestEnum8, 's':  8, 'o': 0, 'bo': 8, 'w':  True},
        {'cls':  TestEnum8, 's':  8, 'o': 1, 'bo': 8, 'w':  True},
        {'cls':  TestEnum8, 's':  8, 'o': 0, 'bo': 8, 'w': False},
        {'cls':  TestEnum8, 's':  8, 'o': 1, 'bo': 8, 'w': False},
        {'cls': TestEnum16, 's': 16, 'o': 0, 'bo': 8, 'w':  True},
        {'cls': TestEnum16, 's': 16, 'o': 1, 'bo': 8, 'w':  True},
        {'cls': TestEnum16, 's': 16, 'o': 0, 'bo': 8, 'w': False},
        {'cls': TestEnum16, 's': 16, 'o': 1, 'bo': 8, 'w': False},
    ])
    def testConstructor(self, cls, s, o, bo, w):
        param = EnumParameter('test-name', 'Test description', o, cls, bo, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, (s + bo + 7) // 8)
        self.assertEqual(param.range, Range(o, (s + bo + 7) // 8))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*((s + bo + 7) // 8)))

    @testdata.TestData([
        {'cls':  TestEnum2, 'bo': 0, 'data': bytes([0x00            ]), 'expectedValue':  TestEnum2.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 0, 'data': bytes([0x04            ]), 'expectedValue':  TestEnum2.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 0, 'data': bytes([0x01            ]), 'expectedValue':  TestEnum2.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum2, 'bo': 0, 'data': bytes([0x05            ]), 'expectedValue':  TestEnum2.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum2, 'bo': 0, 'data': bytes([0x02            ]), 'expectedValue':  TestEnum2.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 0, 'data': bytes([0x06            ]), 'expectedValue':  TestEnum2.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 0, 'data': bytes([0x03            ]), 'expectedValue':  TestEnum2.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x03            ])},
        {'cls':  TestEnum2, 'bo': 0, 'data': bytes([0x07            ]), 'expectedValue':  TestEnum2.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x03            ])},
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0x00            ]), 'expectedValue':  TestEnum7.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0x80            ]), 'expectedValue':  TestEnum7.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0x01            ]), 'expectedValue':  TestEnum7.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0x81            ]), 'expectedValue':  TestEnum7.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0x02            ]), 'expectedValue':  TestEnum7.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0x82            ]), 'expectedValue':  TestEnum7.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0x7F            ]), 'expectedValue':  TestEnum7.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x7F            ])},
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0xFF            ]), 'expectedValue':  TestEnum7.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x7F            ])},
        {'cls':  TestEnum8, 'bo': 0, 'data': bytes([0x00            ]), 'expectedValue':  TestEnum8.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum8, 'bo': 0, 'data': bytes([0x01            ]), 'expectedValue':  TestEnum8.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum8, 'bo': 0, 'data': bytes([0x02            ]), 'expectedValue':  TestEnum8.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum8, 'bo': 0, 'data': bytes([0xFF            ]), 'expectedValue':  TestEnum8.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0xFF            ])},
        {'cls': TestEnum16, 'bo': 0, 'data': bytes([0x00, 0x00      ]), 'expectedValue': TestEnum16.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls': TestEnum16, 'bo': 0, 'data': bytes([0x00, 0x01      ]), 'expectedValue': TestEnum16.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x01      ])},
        {'cls': TestEnum16, 'bo': 0, 'data': bytes([0x00, 0x02      ]), 'expectedValue': TestEnum16.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x00, 0x02      ])},
        {'cls': TestEnum16, 'bo': 0, 'data': bytes([0xFF, 0xFF      ]), 'expectedValue': TestEnum16.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls':  TestEnum2, 'bo': 1, 'data': bytes([0x00            ]), 'expectedValue':  TestEnum2.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 1, 'data': bytes([0x09            ]), 'expectedValue':  TestEnum2.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 1, 'data': bytes([0x02            ]), 'expectedValue':  TestEnum2.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 1, 'data': bytes([0x0B            ]), 'expectedValue':  TestEnum2.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 1, 'data': bytes([0x04            ]), 'expectedValue':  TestEnum2.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum2, 'bo': 1, 'data': bytes([0x0D            ]), 'expectedValue':  TestEnum2.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum2, 'bo': 1, 'data': bytes([0x06            ]), 'expectedValue':  TestEnum2.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x06            ])},
        {'cls':  TestEnum2, 'bo': 1, 'data': bytes([0x0F            ]), 'expectedValue':  TestEnum2.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x06            ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0x00            ]), 'expectedValue':  TestEnum7.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0x01            ]), 'expectedValue':  TestEnum7.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0x02            ]), 'expectedValue':  TestEnum7.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0x03            ]), 'expectedValue':  TestEnum7.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0x04            ]), 'expectedValue':  TestEnum7.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0x05            ]), 'expectedValue':  TestEnum7.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0xFE            ]), 'expectedValue':  TestEnum7.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0xFE            ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0xFF            ]), 'expectedValue':  TestEnum7.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0xFE            ])},
        {'cls':  TestEnum8, 'bo': 1, 'data': bytes([0x00, 0x00      ]), 'expectedValue':  TestEnum8.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 1, 'data': bytes([0x00, 0x02      ]), 'expectedValue':  TestEnum8.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x02      ])},
        {'cls':  TestEnum8, 'bo': 1, 'data': bytes([0x00, 0x04      ]), 'expectedValue':  TestEnum8.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x00, 0x04      ])},
        {'cls':  TestEnum8, 'bo': 1, 'data': bytes([0x01, 0xFE      ]), 'expectedValue':  TestEnum8.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x01, 0xFE      ])},
        {'cls': TestEnum16, 'bo': 1, 'data': bytes([0x00, 0x00, 0x00]), 'expectedValue': TestEnum16.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00, 0x00])},
        {'cls': TestEnum16, 'bo': 1, 'data': bytes([0x00, 0x00, 0x02]), 'expectedValue': TestEnum16.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x00, 0x02])},
        {'cls': TestEnum16, 'bo': 1, 'data': bytes([0x00, 0x00, 0x04]), 'expectedValue': TestEnum16.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x00, 0x00, 0x04])},
        {'cls': TestEnum16, 'bo': 1, 'data': bytes([0x01, 0xFF, 0xFE]), 'expectedValue': TestEnum16.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x01, 0xFF, 0xFE])},
        {'cls':  TestEnum2, 'bo': 7, 'data': bytes([0x00, 0x00      ]), 'expectedValue':  TestEnum2.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'data': bytes([0xFE, 0x7F      ]), 'expectedValue':  TestEnum2.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'data': bytes([0x00, 0x80      ]), 'expectedValue':  TestEnum2.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum2, 'bo': 7, 'data': bytes([0xFE, 0xFF      ]), 'expectedValue':  TestEnum2.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum2, 'bo': 7, 'data': bytes([0x01, 0x00      ]), 'expectedValue':  TestEnum2.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'data': bytes([0xFF, 0x7F      ]), 'expectedValue':  TestEnum2.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'data': bytes([0x01, 0x80      ]), 'expectedValue':  TestEnum2.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x01, 0x80      ])},
        {'cls':  TestEnum2, 'bo': 7, 'data': bytes([0xFF, 0xFF      ]), 'expectedValue':  TestEnum2.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x01, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0x00, 0x00      ]), 'expectedValue':  TestEnum7.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0xC0, 0x7F      ]), 'expectedValue':  TestEnum7.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0x00, 0x80      ]), 'expectedValue':  TestEnum7.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0xC0, 0xFF      ]), 'expectedValue':  TestEnum7.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0x01, 0x00      ]), 'expectedValue':  TestEnum7.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0xC1, 0x7F      ]), 'expectedValue':  TestEnum7.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0x3F, 0x80      ]), 'expectedValue':  TestEnum7.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x3F, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0xFF, 0xFF      ]), 'expectedValue':  TestEnum7.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x3F, 0x80      ])},
        {'cls':  TestEnum8, 'bo': 7, 'data': bytes([0x00, 0x00      ]), 'expectedValue':  TestEnum8.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 7, 'data': bytes([0x00, 0x80      ]), 'expectedValue':  TestEnum8.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum8, 'bo': 7, 'data': bytes([0x01, 0x00      ]), 'expectedValue':  TestEnum8.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 7, 'data': bytes([0x7F, 0x80      ]), 'expectedValue':  TestEnum8.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x7F, 0x80      ])},
        {'cls': TestEnum16, 'bo': 7, 'data': bytes([0x00, 0x00, 0x00]), 'expectedValue': TestEnum16.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00, 0x00])},
        {'cls': TestEnum16, 'bo': 7, 'data': bytes([0x00, 0x00, 0x80]), 'expectedValue': TestEnum16.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x00, 0x80])},
        {'cls': TestEnum16, 'bo': 7, 'data': bytes([0x00, 0x01, 0x00]), 'expectedValue': TestEnum16.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x00, 0x01, 0x00])},
        {'cls': TestEnum16, 'bo': 7, 'data': bytes([0x7F, 0xFF, 0x80]), 'expectedValue': TestEnum16.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x7F, 0xFF, 0x80])},
        {'cls':  TestEnum2, 'bo': 8, 'data': bytes([0x00, 0x00      ]), 'expectedValue':  TestEnum2.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'data': bytes([0xFC, 0xFF      ]), 'expectedValue':  TestEnum2.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'data': bytes([0x01, 0x00      ]), 'expectedValue':  TestEnum2.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'data': bytes([0xFD, 0xFF      ]), 'expectedValue':  TestEnum2.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'data': bytes([0x02, 0x00      ]), 'expectedValue':  TestEnum2.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'data': bytes([0xFE, 0xFF      ]), 'expectedValue':  TestEnum2.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'data': bytes([0x03, 0x00      ]), 'expectedValue':  TestEnum2.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x03, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'data': bytes([0xFF, 0xFF      ]), 'expectedValue':  TestEnum2.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x03, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x00, 0x00      ]), 'expectedValue':  TestEnum7.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x80, 0xFF      ]), 'expectedValue':  TestEnum7.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x01, 0x00      ]), 'expectedValue':  TestEnum7.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x81, 0xFF      ]), 'expectedValue':  TestEnum7.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x02, 0x00      ]), 'expectedValue':  TestEnum7.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x82, 0xFF      ]), 'expectedValue':  TestEnum7.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x7F, 0x00      ]), 'expectedValue':  TestEnum7.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x7F, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x7F, 0xFF      ]), 'expectedValue':  TestEnum7.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0x7F, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'data': bytes([0x00, 0x00      ]), 'expectedValue':  TestEnum8.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'data': bytes([0x01, 0x00      ]), 'expectedValue':  TestEnum8.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'data': bytes([0x02, 0x00      ]), 'expectedValue':  TestEnum8.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'data': bytes([0xFF, 0x00      ]), 'expectedValue':  TestEnum8.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0xFF, 0x00      ])},
        {'cls': TestEnum16, 'bo': 8, 'data': bytes([0x00, 0x00, 0x00]), 'expectedValue': TestEnum16.ZERO, 'expectedStr': 'ZERO', 'expectedBytes': bytes([0x00, 0x00, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'data': bytes([0x00, 0x01, 0x00]), 'expectedValue': TestEnum16.ONE , 'expectedStr':  'ONE', 'expectedBytes': bytes([0x00, 0x01, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'data': bytes([0x00, 0x02, 0x00]), 'expectedValue': TestEnum16.TWO , 'expectedStr':  'TWO', 'expectedBytes': bytes([0x00, 0x02, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'data': bytes([0xFF, 0xFF, 0x00]), 'expectedValue': TestEnum16.MAX , 'expectedStr':  'MAX', 'expectedBytes': bytes([0xFF, 0xFF, 0x00])},
    ])
    def testParseData(self, cls, bo, data, expectedValue, expectedStr, expectedBytes):
        param = EnumParameter('test-name', 'Test description', 0, cls, bo, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0x03            ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x03            ])},
        {'cls':  TestEnum7, 'bo': 0, 'data': bytes([0x83            ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x03            ])},
        {'cls':  TestEnum8, 'bo': 0, 'data': bytes([0x03            ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x03            ])},
        {'cls': TestEnum16, 'bo': 0, 'data': bytes([0x00, 0x03      ]), 'valueStr': '0x0003', 'expectedBytes': bytes([0x00, 0x03      ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0x06            ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x06            ])},
        {'cls':  TestEnum7, 'bo': 1, 'data': bytes([0x07            ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x06            ])},
        {'cls':  TestEnum8, 'bo': 1, 'data': bytes([0x00, 0x06      ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x00, 0x06      ])},
        {'cls': TestEnum16, 'bo': 1, 'data': bytes([0x00, 0x00, 0x06]), 'valueStr': '0x0003', 'expectedBytes': bytes([0x00, 0x00, 0x06])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0x01, 0x80      ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x01, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'data': bytes([0xC1, 0xFF      ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x01, 0x80      ])},
        {'cls':  TestEnum8, 'bo': 7, 'data': bytes([0x01, 0x80      ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x01, 0x80      ])},
        {'cls': TestEnum16, 'bo': 7, 'data': bytes([0x00, 0x01, 0x80]), 'valueStr': '0x0003', 'expectedBytes': bytes([0x00, 0x01, 0x80])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x03, 0x00      ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x03, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'data': bytes([0x83, 0x00      ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x03, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'data': bytes([0x03, 0x00      ]), 'valueStr':   '0x03', 'expectedBytes': bytes([0x03, 0x00      ])},
        {'cls': TestEnum16, 'bo': 8, 'data': bytes([0x00, 0x03, 0x00]), 'valueStr': '0x0003', 'expectedBytes': bytes([0x00, 0x03, 0x00])},
    ])
    def testParseDataInvalid(self, cls, bo, data, valueStr, expectedBytes):
        param = EnumParameter('test-name', 'Test description', 0, cls, bo, True)
        param.parseData(data)

        with self.assertWarns(UserWarning) as w:
            self.assertIsNone(param.value)
        self.assertEqual(str(w.warning), f"Invalid value for enum parameter: {valueStr}")

        with self.assertWarns(UserWarning) as w:
            self.assertEqual(str(param), '')
        self.assertEqual(str(w.warning), f"Invalid value for enum parameter: {valueStr}")

        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'cls':  TestEnum2, 'bo': 0, 'value': 'ZERO', 'expectedValue':  TestEnum2.ZERO, 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  'ONE', 'expectedValue':  TestEnum2.ONE , 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  'TWO', 'expectedValue':  TestEnum2.TWO , 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  'MAX', 'expectedValue':  TestEnum2.MAX , 'expectedBytes': bytes([0x03            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value': 'ZERO', 'expectedValue':  TestEnum7.ZERO, 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  'ONE', 'expectedValue':  TestEnum7.ONE , 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  'TWO', 'expectedValue':  TestEnum7.TWO , 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  'MAX', 'expectedValue':  TestEnum7.MAX , 'expectedBytes': bytes([0x7F            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value': 'ZERO', 'expectedValue':  TestEnum8.ZERO, 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  'ONE', 'expectedValue':  TestEnum8.ONE , 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  'TWO', 'expectedValue':  TestEnum8.TWO , 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  'MAX', 'expectedValue':  TestEnum8.MAX , 'expectedBytes': bytes([0xFF            ])},
        {'cls': TestEnum16, 'bo': 0, 'value': 'ZERO', 'expectedValue': TestEnum16.ZERO, 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls': TestEnum16, 'bo': 0, 'value':  'ONE', 'expectedValue': TestEnum16.ONE , 'expectedBytes': bytes([0x00, 0x01      ])},
        {'cls': TestEnum16, 'bo': 0, 'value':  'TWO', 'expectedValue': TestEnum16.TWO , 'expectedBytes': bytes([0x00, 0x02      ])},
        {'cls': TestEnum16, 'bo': 0, 'value':  'MAX', 'expectedValue': TestEnum16.MAX , 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls':  TestEnum2, 'bo': 1, 'value': 'ZERO', 'expectedValue':  TestEnum2.ZERO, 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  'ONE', 'expectedValue':  TestEnum2.ONE , 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  'TWO', 'expectedValue':  TestEnum2.TWO , 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  'MAX', 'expectedValue':  TestEnum2.MAX , 'expectedBytes': bytes([0x06            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value': 'ZERO', 'expectedValue':  TestEnum7.ZERO, 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  'ONE', 'expectedValue':  TestEnum7.ONE , 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  'TWO', 'expectedValue':  TestEnum7.TWO , 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  'MAX', 'expectedValue':  TestEnum7.MAX , 'expectedBytes': bytes([0xFE            ])},
        {'cls':  TestEnum8, 'bo': 1, 'value': 'ZERO', 'expectedValue':  TestEnum8.ZERO, 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  'ONE', 'expectedValue':  TestEnum8.ONE , 'expectedBytes': bytes([0x00, 0x02      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  'TWO', 'expectedValue':  TestEnum8.TWO , 'expectedBytes': bytes([0x00, 0x04      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  'MAX', 'expectedValue':  TestEnum8.MAX , 'expectedBytes': bytes([0x01, 0xFE      ])},
        {'cls': TestEnum16, 'bo': 1, 'value': 'ZERO', 'expectedValue': TestEnum16.ZERO, 'expectedBytes': bytes([0x00, 0x00, 0x00])},
        {'cls': TestEnum16, 'bo': 1, 'value':  'ONE', 'expectedValue': TestEnum16.ONE , 'expectedBytes': bytes([0x00, 0x00, 0x02])},
        {'cls': TestEnum16, 'bo': 1, 'value':  'TWO', 'expectedValue': TestEnum16.TWO , 'expectedBytes': bytes([0x00, 0x00, 0x04])},
        {'cls': TestEnum16, 'bo': 1, 'value':  'MAX', 'expectedValue': TestEnum16.MAX , 'expectedBytes': bytes([0x01, 0xFF, 0xFE])},
        {'cls':  TestEnum2, 'bo': 7, 'value': 'ZERO', 'expectedValue':  TestEnum2.ZERO, 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  'ONE', 'expectedValue':  TestEnum2.ONE , 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  'TWO', 'expectedValue':  TestEnum2.TWO , 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  'MAX', 'expectedValue':  TestEnum2.MAX , 'expectedBytes': bytes([0x01, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value': 'ZERO', 'expectedValue':  TestEnum7.ZERO, 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  'ONE', 'expectedValue':  TestEnum7.ONE , 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  'TWO', 'expectedValue':  TestEnum7.TWO , 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  'MAX', 'expectedValue':  TestEnum7.MAX , 'expectedBytes': bytes([0x3F, 0x80      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value': 'ZERO', 'expectedValue':  TestEnum8.ZERO, 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  'ONE', 'expectedValue':  TestEnum8.ONE , 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  'TWO', 'expectedValue':  TestEnum8.TWO , 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  'MAX', 'expectedValue':  TestEnum8.MAX , 'expectedBytes': bytes([0x7F, 0x80      ])},
        {'cls': TestEnum16, 'bo': 7, 'value': 'ZERO', 'expectedValue': TestEnum16.ZERO, 'expectedBytes': bytes([0x00, 0x00, 0x00])},
        {'cls': TestEnum16, 'bo': 7, 'value':  'ONE', 'expectedValue': TestEnum16.ONE , 'expectedBytes': bytes([0x00, 0x00, 0x80])},
        {'cls': TestEnum16, 'bo': 7, 'value':  'TWO', 'expectedValue': TestEnum16.TWO , 'expectedBytes': bytes([0x00, 0x01, 0x00])},
        {'cls': TestEnum16, 'bo': 7, 'value':  'MAX', 'expectedValue': TestEnum16.MAX , 'expectedBytes': bytes([0x7F, 0xFF, 0x80])},
        {'cls':  TestEnum2, 'bo': 8, 'value': 'ZERO', 'expectedValue':  TestEnum2.ZERO, 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  'ONE', 'expectedValue':  TestEnum2.ONE , 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  'TWO', 'expectedValue':  TestEnum2.TWO , 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  'MAX', 'expectedValue':  TestEnum2.MAX , 'expectedBytes': bytes([0x03, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value': 'ZERO', 'expectedValue':  TestEnum7.ZERO, 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  'ONE', 'expectedValue':  TestEnum7.ONE , 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  'TWO', 'expectedValue':  TestEnum7.TWO , 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  'MAX', 'expectedValue':  TestEnum7.MAX , 'expectedBytes': bytes([0x7F, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value': 'ZERO', 'expectedValue':  TestEnum8.ZERO, 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  'ONE', 'expectedValue':  TestEnum8.ONE , 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  'TWO', 'expectedValue':  TestEnum8.TWO , 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  'MAX', 'expectedValue':  TestEnum8.MAX , 'expectedBytes': bytes([0xFF, 0x00      ])},
        {'cls': TestEnum16, 'bo': 8, 'value': 'ZERO', 'expectedValue': TestEnum16.ZERO, 'expectedBytes': bytes([0x00, 0x00, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'value':  'ONE', 'expectedValue': TestEnum16.ONE , 'expectedBytes': bytes([0x00, 0x01, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'value':  'TWO', 'expectedValue': TestEnum16.TWO , 'expectedBytes': bytes([0x00, 0x02, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'value':  'MAX', 'expectedValue': TestEnum16.MAX , 'expectedBytes': bytes([0xFF, 0xFF, 0x00])},
    ])
    def testParseValue(self, cls, bo, value, expectedValue, expectedBytes):
        param = EnumParameter('test-name', 'Test description', 0, cls, bo, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), value)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'cls':  TestEnum2, 'bo': 0, 's': 1, 'value': 'THREE'},
        {'cls':  TestEnum7, 'bo': 0, 's': 1, 'value': 'THREE'},
        {'cls':  TestEnum8, 'bo': 0, 's': 1, 'value': 'THREE'},
        {'cls': TestEnum16, 'bo': 0, 's': 2, 'value': 'THREE'},

        {'cls':  TestEnum2, 'bo': 1, 's': 1, 'value': 'THREE'},
        {'cls':  TestEnum7, 'bo': 1, 's': 1, 'value': 'THREE'},
        {'cls':  TestEnum8, 'bo': 1, 's': 2, 'value': 'THREE'},
        {'cls': TestEnum16, 'bo': 1, 's': 3, 'value': 'THREE'},

        {'cls':  TestEnum2, 'bo': 7, 's': 2, 'value': 'THREE'},
        {'cls':  TestEnum7, 'bo': 7, 's': 2, 'value': 'THREE'},
        {'cls':  TestEnum8, 'bo': 7, 's': 2, 'value': 'THREE'},
        {'cls': TestEnum16, 'bo': 7, 's': 3, 'value': 'THREE'},

        {'cls':  TestEnum2, 'bo': 8, 's': 2, 'value': 'THREE'},
        {'cls':  TestEnum7, 'bo': 8, 's': 2, 'value': 'THREE'},
        {'cls':  TestEnum8, 'bo': 8, 's': 2, 'value': 'THREE'},
        {'cls': TestEnum16, 'bo': 8, 's': 3, 'value': 'THREE'},
    ])
    def testParseValueInvalid(self, cls, bo, s, value):
        param = EnumParameter('test-name', 'Test description', 0, cls, bo, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid value: {value} (accepted values: \"ZERO\", \"ONE\", \"TWO\", \"MAX\")")
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*s))

    @testdata.TestData([
        {'cls':  TestEnum2, 'bo': 0, 'value':            None, 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':            None, 'oldData': bytes([0x01            ]), 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':            None, 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFF            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':            None, 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':            None, 'oldData': bytes([0x01            ]), 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':            None, 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFF            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':            None, 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':            None, 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFF            ])},
        {'cls': TestEnum16, 'bo': 0, 'value':            None, 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls': TestEnum16, 'bo': 0, 'value':            None, 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.ZERO, 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.ZERO, 'oldData': bytes([0x03            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.ZERO, 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFC            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.ONE , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.ONE , 'oldData': bytes([0x03            ]), 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.ONE , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFD            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.TWO , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.TWO , 'oldData': bytes([0x03            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.TWO , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFE            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.MAX , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x03            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.MAX , 'oldData': bytes([0x03            ]), 'expectedBytes': bytes([0x03            ])},
        {'cls':  TestEnum2, 'bo': 0, 'value':  TestEnum2.MAX , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFF            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.ZERO, 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.ZERO, 'oldData': bytes([0x7F            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.ZERO, 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0x80            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.ONE , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.ONE , 'oldData': bytes([0x7F            ]), 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.ONE , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0x81            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.TWO , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.TWO , 'oldData': bytes([0x7F            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.TWO , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0x82            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.MAX , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x7F            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.MAX , 'oldData': bytes([0x7F            ]), 'expectedBytes': bytes([0x7F            ])},
        {'cls':  TestEnum7, 'bo': 0, 'value':  TestEnum7.MAX , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFF            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  TestEnum8.ZERO, 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  TestEnum8.ZERO, 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  TestEnum8.ONE , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  TestEnum8.ONE , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  TestEnum8.TWO , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  TestEnum8.TWO , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  TestEnum8.MAX , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0xFF            ])},
        {'cls':  TestEnum8, 'bo': 0, 'value':  TestEnum8.MAX , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFF            ])},
        {'cls': TestEnum16, 'bo': 0, 'value': TestEnum16.ZERO, 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls': TestEnum16, 'bo': 0, 'value': TestEnum16.ZERO, 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls': TestEnum16, 'bo': 0, 'value': TestEnum16.ONE , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x01      ])},
        {'cls': TestEnum16, 'bo': 0, 'value': TestEnum16.ONE , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x00, 0x01      ])},
        {'cls': TestEnum16, 'bo': 0, 'value': TestEnum16.TWO , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x02      ])},
        {'cls': TestEnum16, 'bo': 0, 'value': TestEnum16.TWO , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x00, 0x02      ])},
        {'cls': TestEnum16, 'bo': 0, 'value': TestEnum16.MAX , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls': TestEnum16, 'bo': 0, 'value': TestEnum16.MAX , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.ZERO, 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.ZERO, 'oldData': bytes([0x06            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.ZERO, 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xF9            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.ONE , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.ONE , 'oldData': bytes([0x06            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.ONE , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFB            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.TWO , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.TWO , 'oldData': bytes([0x06            ]), 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.TWO , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFD            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.MAX , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x06            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.MAX , 'oldData': bytes([0x06            ]), 'expectedBytes': bytes([0x06            ])},
        {'cls':  TestEnum2, 'bo': 1, 'value':  TestEnum2.MAX , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFF            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.ZERO, 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.ZERO, 'oldData': bytes([0xFE            ]), 'expectedBytes': bytes([0x00            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.ZERO, 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0x01            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.ONE , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.ONE , 'oldData': bytes([0xFE            ]), 'expectedBytes': bytes([0x02            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.ONE , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0x03            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.TWO , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.TWO , 'oldData': bytes([0xFE            ]), 'expectedBytes': bytes([0x04            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.TWO , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0x05            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.MAX , 'oldData': bytes([0x00            ]), 'expectedBytes': bytes([0xFE            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.MAX , 'oldData': bytes([0xFE            ]), 'expectedBytes': bytes([0xFE            ])},
        {'cls':  TestEnum7, 'bo': 1, 'value':  TestEnum7.MAX , 'oldData': bytes([0xFF            ]), 'expectedBytes': bytes([0xFF            ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  TestEnum8.ZERO, 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  TestEnum8.ZERO, 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFE, 0x01      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  TestEnum8.ONE , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x02      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  TestEnum8.ONE , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFE, 0x03      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  TestEnum8.TWO , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x04      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  TestEnum8.TWO , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFE, 0x05      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  TestEnum8.MAX , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x01, 0xFE      ])},
        {'cls':  TestEnum8, 'bo': 1, 'value':  TestEnum8.MAX , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls': TestEnum16, 'bo': 1, 'value': TestEnum16.ZERO, 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x00, 0x00, 0x00])},
        {'cls': TestEnum16, 'bo': 1, 'value': TestEnum16.ZERO, 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0xFE, 0x00, 0x01])},
        {'cls': TestEnum16, 'bo': 1, 'value': TestEnum16.ONE , 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x00, 0x00, 0x02])},
        {'cls': TestEnum16, 'bo': 1, 'value': TestEnum16.ONE , 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0xFE, 0x00, 0x03])},
        {'cls': TestEnum16, 'bo': 1, 'value': TestEnum16.TWO , 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x00, 0x00, 0x04])},
        {'cls': TestEnum16, 'bo': 1, 'value': TestEnum16.TWO , 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0xFE, 0x00, 0x05])},
        {'cls': TestEnum16, 'bo': 1, 'value': TestEnum16.MAX , 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x01, 0xFF, 0xFE])},
        {'cls': TestEnum16, 'bo': 1, 'value': TestEnum16.MAX , 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0xFF, 0xFF, 0xFF])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.ZERO, 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.ZERO, 'oldData': bytes([0x01, 0x80      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.ZERO, 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFE, 0x7F      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.ONE , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.ONE , 'oldData': bytes([0x01, 0x80      ]), 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.ONE , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFE, 0xFF      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.TWO , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.TWO , 'oldData': bytes([0x01, 0x80      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.TWO , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0x7F      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.MAX , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x01, 0x80      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.MAX , 'oldData': bytes([0x01, 0x80      ]), 'expectedBytes': bytes([0x01, 0x80      ])},
        {'cls':  TestEnum2, 'bo': 7, 'value':  TestEnum2.MAX , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.ZERO, 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.ZERO, 'oldData': bytes([0x3F, 0x80      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.ZERO, 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xC0, 0x7F      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.ONE , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.ONE , 'oldData': bytes([0x3F, 0x80      ]), 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.ONE , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xC0, 0xFF      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.TWO , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.TWO , 'oldData': bytes([0x3F, 0x80      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.TWO , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xC1, 0x7F      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.MAX , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x3F, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.MAX , 'oldData': bytes([0x3F, 0x80      ]), 'expectedBytes': bytes([0x3F, 0x80      ])},
        {'cls':  TestEnum7, 'bo': 7, 'value':  TestEnum7.MAX , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  TestEnum8.ZERO, 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  TestEnum8.ZERO, 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x80, 0x7F      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  TestEnum8.ONE , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x80      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  TestEnum8.ONE , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x80, 0xFF      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  TestEnum8.TWO , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  TestEnum8.TWO , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x81, 0x7F      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  TestEnum8.MAX , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x7F, 0x80      ])},
        {'cls':  TestEnum8, 'bo': 7, 'value':  TestEnum8.MAX , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls': TestEnum16, 'bo': 7, 'value': TestEnum16.ZERO, 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x00, 0x00, 0x00])},
        {'cls': TestEnum16, 'bo': 7, 'value': TestEnum16.ZERO, 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0x80, 0x00, 0x7F])},
        {'cls': TestEnum16, 'bo': 7, 'value': TestEnum16.ONE , 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x00, 0x00, 0x80])},
        {'cls': TestEnum16, 'bo': 7, 'value': TestEnum16.ONE , 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0x80, 0x00, 0xFF])},
        {'cls': TestEnum16, 'bo': 7, 'value': TestEnum16.TWO , 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x00, 0x01, 0x00])},
        {'cls': TestEnum16, 'bo': 7, 'value': TestEnum16.TWO , 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0x80, 0x01, 0x7F])},
        {'cls': TestEnum16, 'bo': 7, 'value': TestEnum16.MAX , 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x7F, 0xFF, 0x80])},
        {'cls': TestEnum16, 'bo': 7, 'value': TestEnum16.MAX , 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0xFF, 0xFF, 0xFF])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.ZERO, 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.ZERO, 'oldData': bytes([0x03, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.ZERO, 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFC, 0xFF      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.ONE , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.ONE , 'oldData': bytes([0x03, 0x00      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.ONE , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFD, 0xFF      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.TWO , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.TWO , 'oldData': bytes([0x03, 0x00      ]), 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.TWO , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFE, 0xFF      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.MAX , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x03, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.MAX , 'oldData': bytes([0x03, 0x00      ]), 'expectedBytes': bytes([0x03, 0x00      ])},
        {'cls':  TestEnum2, 'bo': 8, 'value':  TestEnum2.MAX , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.ZERO, 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.ZERO, 'oldData': bytes([0x7F, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.ZERO, 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x80, 0xFF      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.ONE , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.ONE , 'oldData': bytes([0x7F, 0x00      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.ONE , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x81, 0xFF      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.TWO , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.TWO , 'oldData': bytes([0x7F, 0x00      ]), 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.TWO , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x82, 0xFF      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.MAX , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x7F, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.MAX , 'oldData': bytes([0x7F, 0x00      ]), 'expectedBytes': bytes([0x7F, 0x00      ])},
        {'cls':  TestEnum7, 'bo': 8, 'value':  TestEnum7.MAX , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  TestEnum8.ZERO, 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x00, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  TestEnum8.ZERO, 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x00, 0xFF      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  TestEnum8.ONE , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x01, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  TestEnum8.ONE , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x01, 0xFF      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  TestEnum8.TWO , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0x02, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  TestEnum8.TWO , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0x02, 0xFF      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  TestEnum8.MAX , 'oldData': bytes([0x00, 0x00      ]), 'expectedBytes': bytes([0xFF, 0x00      ])},
        {'cls':  TestEnum8, 'bo': 8, 'value':  TestEnum8.MAX , 'oldData': bytes([0xFF, 0xFF      ]), 'expectedBytes': bytes([0xFF, 0xFF      ])},
        {'cls': TestEnum16, 'bo': 8, 'value': TestEnum16.ZERO, 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x00, 0x00, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'value': TestEnum16.ZERO, 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0x00, 0x00, 0xFF])},
        {'cls': TestEnum16, 'bo': 8, 'value': TestEnum16.ONE , 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x00, 0x01, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'value': TestEnum16.ONE , 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0x00, 0x01, 0xFF])},
        {'cls': TestEnum16, 'bo': 8, 'value': TestEnum16.TWO , 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0x00, 0x02, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'value': TestEnum16.TWO , 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0x00, 0x02, 0xFF])},
        {'cls': TestEnum16, 'bo': 8, 'value': TestEnum16.MAX , 'oldData': bytes([0x00, 0x00, 0x00]), 'expectedBytes': bytes([0xFF, 0xFF, 0x00])},
        {'cls': TestEnum16, 'bo': 8, 'value': TestEnum16.MAX , 'oldData': bytes([0xFF, 0xFF, 0xFF]), 'expectedBytes': bytes([0xFF, 0xFF, 0xFF])},
    ])
    def testOldData(self, cls, bo, value, oldData, expectedBytes):
        param = EnumParameter('test-name', 'Test description', 0, cls, bo, True)
        param.value = value
        self.assertEqual(bytes(param | oldData), expectedBytes)


class TestHalfByteParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'pos': HalfByteParameter.Position.Lower, 'w':  True},
        {'o': 1, 'pos': HalfByteParameter.Position.Lower, 'w':  True},
        {'o': 0, 'pos': HalfByteParameter.Position.Lower, 'w':  True},
        {'o': 1, 'pos': HalfByteParameter.Position.Lower, 'w':  True},
        {'o': 0, 'pos': HalfByteParameter.Position.Upper, 'w': False},
        {'o': 1, 'pos': HalfByteParameter.Position.Upper, 'w': False},
        {'o': 0, 'pos': HalfByteParameter.Position.Upper, 'w': False},
        {'o': 1, 'pos': HalfByteParameter.Position.Upper, 'w': False},
    ])
    def testConstructor(self, o, pos, w):
        param = HalfByteParameter('test-name', 'Test description', o, pos, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 1)
        self.assertEqual(param.range, Range(o, 1))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))

    @testdata.TestData([
        {'pos': HalfByteParameter.Position.Lower, 'data': bytes([0xF0]), 'expectedValue': 0x00, 'expectedStr': '0x00', 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Lower, 'data': bytes([0xF1]), 'expectedValue': 0x01, 'expectedStr': '0x01', 'expectedBytes': bytes([0x01])},
        {'pos': HalfByteParameter.Position.Lower, 'data': bytes([0xF8]), 'expectedValue': 0x08, 'expectedStr': '0x08', 'expectedBytes': bytes([0x08])},
        {'pos': HalfByteParameter.Position.Lower, 'data': bytes([0xFF]), 'expectedValue': 0x0F, 'expectedStr': '0x0F', 'expectedBytes': bytes([0x0F])},
        {'pos': HalfByteParameter.Position.Lower, 'data': bytes([0x00]), 'expectedValue': 0x00, 'expectedStr': '0x00', 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Lower, 'data': bytes([0x01]), 'expectedValue': 0x01, 'expectedStr': '0x01', 'expectedBytes': bytes([0x01])},
        {'pos': HalfByteParameter.Position.Lower, 'data': bytes([0x08]), 'expectedValue': 0x08, 'expectedStr': '0x08', 'expectedBytes': bytes([0x08])},
        {'pos': HalfByteParameter.Position.Lower, 'data': bytes([0x0F]), 'expectedValue': 0x0F, 'expectedStr': '0x0F', 'expectedBytes': bytes([0x0F])},
        {'pos': HalfByteParameter.Position.Upper, 'data': bytes([0x0F]), 'expectedValue': 0x00, 'expectedStr': '0x00', 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Upper, 'data': bytes([0x1F]), 'expectedValue': 0x01, 'expectedStr': '0x01', 'expectedBytes': bytes([0x10])},
        {'pos': HalfByteParameter.Position.Upper, 'data': bytes([0x8F]), 'expectedValue': 0x08, 'expectedStr': '0x08', 'expectedBytes': bytes([0x80])},
        {'pos': HalfByteParameter.Position.Upper, 'data': bytes([0xFF]), 'expectedValue': 0x0F, 'expectedStr': '0x0F', 'expectedBytes': bytes([0xF0])},
        {'pos': HalfByteParameter.Position.Upper, 'data': bytes([0x00]), 'expectedValue': 0x00, 'expectedStr': '0x00', 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Upper, 'data': bytes([0x10]), 'expectedValue': 0x01, 'expectedStr': '0x01', 'expectedBytes': bytes([0x10])},
        {'pos': HalfByteParameter.Position.Upper, 'data': bytes([0x80]), 'expectedValue': 0x08, 'expectedStr': '0x08', 'expectedBytes': bytes([0x80])},
        {'pos': HalfByteParameter.Position.Upper, 'data': bytes([0xF0]), 'expectedValue': 0x0F, 'expectedStr': '0x0F', 'expectedBytes': bytes([0xF0])},
    ])
    def testParseData(self, pos, data, expectedValue, expectedStr, expectedBytes):
        param = HalfByteParameter('test-name', 'Test description', 0, pos, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'pos': HalfByteParameter.Position.Lower, 'value': '0x00', 'expectedValue': 0x00, 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Lower, 'value': '0x01', 'expectedValue': 0x01, 'expectedBytes': bytes([0x01])},
        {'pos': HalfByteParameter.Position.Lower, 'value': '0x08', 'expectedValue': 0x08, 'expectedBytes': bytes([0x08])},
        {'pos': HalfByteParameter.Position.Lower, 'value': '0x0F', 'expectedValue': 0x0F, 'expectedBytes': bytes([0x0F])},
        {'pos': HalfByteParameter.Position.Lower, 'value': '0x00', 'expectedValue': 0x00, 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Lower, 'value': '0x01', 'expectedValue': 0x01, 'expectedBytes': bytes([0x01])},
        {'pos': HalfByteParameter.Position.Lower, 'value': '0x08', 'expectedValue': 0x08, 'expectedBytes': bytes([0x08])},
        {'pos': HalfByteParameter.Position.Lower, 'value': '0x0F', 'expectedValue': 0x0F, 'expectedBytes': bytes([0x0F])},
        {'pos': HalfByteParameter.Position.Upper, 'value': '0x00', 'expectedValue': 0x00, 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Upper, 'value': '0x01', 'expectedValue': 0x01, 'expectedBytes': bytes([0x10])},
        {'pos': HalfByteParameter.Position.Upper, 'value': '0x08', 'expectedValue': 0x08, 'expectedBytes': bytes([0x80])},
        {'pos': HalfByteParameter.Position.Upper, 'value': '0x0F', 'expectedValue': 0x0F, 'expectedBytes': bytes([0xF0])},
        {'pos': HalfByteParameter.Position.Upper, 'value': '0x00', 'expectedValue': 0x00, 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Upper, 'value': '0x01', 'expectedValue': 0x01, 'expectedBytes': bytes([0x10])},
        {'pos': HalfByteParameter.Position.Upper, 'value': '0x08', 'expectedValue': 0x08, 'expectedBytes': bytes([0x80])},
        {'pos': HalfByteParameter.Position.Upper, 'value': '0x0F', 'expectedValue': 0x0F, 'expectedBytes': bytes([0xF0])},
    ])
    def testParseValue(self, pos, value, expectedValue, expectedBytes):
        param = HalfByteParameter('test-name', 'Test description', 0, pos, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), value)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'pos': HalfByteParameter.Position.Lower, 'value':   '0xx0'},
        {'pos': HalfByteParameter.Position.Lower, 'value':   '0b02'},
        {'pos': HalfByteParameter.Position.Lower, 'value':  '0bb01'},
        {'pos': HalfByteParameter.Position.Lower, 'value':     '09'},
        {'pos': HalfByteParameter.Position.Lower, 'value': 'ABCDEF'},
        {'pos': HalfByteParameter.Position.Upper, 'value':   '0xx0'},
        {'pos': HalfByteParameter.Position.Upper, 'value':   '0b02'},
        {'pos': HalfByteParameter.Position.Upper, 'value':  '0bb01'},
        {'pos': HalfByteParameter.Position.Upper, 'value':     '09'},
        {'pos': HalfByteParameter.Position.Upper, 'value': 'ABCDEF'},
    ])
    def testParseValueInvalid(self, pos, value):
        param = HalfByteParameter('test-name', 'Test description', 0, pos, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid value for unsigned integer: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))

    @testdata.TestData([
        {'pos': HalfByteParameter.Position.Lower, 'value':    '0x10'},
        {'pos': HalfByteParameter.Position.Lower, 'value': '0b10000'},
        {'pos': HalfByteParameter.Position.Lower, 'value':     '020'},
        {'pos': HalfByteParameter.Position.Lower, 'value':      '16'},
        {'pos': HalfByteParameter.Position.Upper, 'value':    '0x10'},
        {'pos': HalfByteParameter.Position.Upper, 'value': '0b10000'},
        {'pos': HalfByteParameter.Position.Upper, 'value':     '020'},
        {'pos': HalfByteParameter.Position.Upper, 'value':      '16'},
    ])
    def testParseValueTooLarge(self, pos, value):
        param = HalfByteParameter('test-name', 'Test description', 0, pos, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Value is too large: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))

    @testdata.TestData([
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x00, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x00, 'oldData': bytes([0x0F]), 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x00, 'oldData': bytes([0xF0]), 'expectedBytes': bytes([0xF0])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x00, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xF0])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x01, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x01])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x01, 'oldData': bytes([0x0F]), 'expectedBytes': bytes([0x01])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x01, 'oldData': bytes([0xF0]), 'expectedBytes': bytes([0xF1])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x01, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xF1])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x08, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x08])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x08, 'oldData': bytes([0x0F]), 'expectedBytes': bytes([0x08])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x08, 'oldData': bytes([0xF0]), 'expectedBytes': bytes([0xF8])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x08, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xF8])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x0F, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x0F])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x0F, 'oldData': bytes([0x0F]), 'expectedBytes': bytes([0x0F])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x0F, 'oldData': bytes([0xF0]), 'expectedBytes': bytes([0xFF])},
        {'pos': HalfByteParameter.Position.Lower, 'value': 0x0F, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x00, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x00, 'oldData': bytes([0xF0]), 'expectedBytes': bytes([0x00])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x00, 'oldData': bytes([0x0F]), 'expectedBytes': bytes([0x0F])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x00, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0x0F])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x01, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x10])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x01, 'oldData': bytes([0xF0]), 'expectedBytes': bytes([0x10])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x01, 'oldData': bytes([0x0F]), 'expectedBytes': bytes([0x1F])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x01, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0x1F])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x08, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x80])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x08, 'oldData': bytes([0xF0]), 'expectedBytes': bytes([0x80])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x08, 'oldData': bytes([0x0F]), 'expectedBytes': bytes([0x8F])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x08, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0x8F])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x0F, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0xF0])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x0F, 'oldData': bytes([0xF0]), 'expectedBytes': bytes([0xF0])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x0F, 'oldData': bytes([0x0F]), 'expectedBytes': bytes([0xFF])},
        {'pos': HalfByteParameter.Position.Upper, 'value': 0x0F, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
    ])
    def testOldData(self, pos, value, oldData, expectedBytes):
        param = HalfByteParameter('test-name', 'Test description', 0, pos, True)
        param.value = value
        self.assertEqual(bytes(param | oldData), expectedBytes)


class TestBitParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'bo': 0, 'w':  True},
        {'o': 1, 'bo': 0, 'w':  True},
        {'o': 0, 'bo': 7, 'w':  True},
        {'o': 1, 'bo': 7, 'w':  True},
        {'o': 0, 'bo': 0, 'w': False},
        {'o': 1, 'bo': 0, 'w': False},
        {'o': 0, 'bo': 7, 'w': False},
        {'o': 1, 'bo': 7, 'w': False},
    ])
    def testConstructor(self, o, bo, w):
        param = BitParameter('test-name', 'Test description', o, bo, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 1)
        self.assertEqual(param.range, Range(o, 1))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))

    @testdata.TestData([
        {'bo': 0, 'data': bytes([0xFE]), 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 1, 'data': bytes([0xFD]), 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 2, 'data': bytes([0xFB]), 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 3, 'data': bytes([0xF7]), 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 4, 'data': bytes([0xEF]), 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 5, 'data': bytes([0xDF]), 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 6, 'data': bytes([0xBF]), 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 7, 'data': bytes([0x7F]), 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 0, 'data': bytes([0x01]), 'expectedValue':  True, 'expectedBytes': bytes([0x01])},
        {'bo': 1, 'data': bytes([0x02]), 'expectedValue':  True, 'expectedBytes': bytes([0x02])},
        {'bo': 2, 'data': bytes([0x04]), 'expectedValue':  True, 'expectedBytes': bytes([0x04])},
        {'bo': 3, 'data': bytes([0x08]), 'expectedValue':  True, 'expectedBytes': bytes([0x08])},
        {'bo': 4, 'data': bytes([0x10]), 'expectedValue':  True, 'expectedBytes': bytes([0x10])},
        {'bo': 5, 'data': bytes([0x20]), 'expectedValue':  True, 'expectedBytes': bytes([0x20])},
        {'bo': 6, 'data': bytes([0x40]), 'expectedValue':  True, 'expectedBytes': bytes([0x40])},
        {'bo': 7, 'data': bytes([0x80]), 'expectedValue':  True, 'expectedBytes': bytes([0x80])},
    ])
    def testParseData(self, bo, data, expectedValue, expectedBytes):
        param = BitParameter('test-name', 'Test description', 0, bo, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), str(expectedValue))
        self.assertEqual(bytes(param), expectedBytes)


    @testdata.TestData([
        {'bo': 0, 'value': 'False', 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 1, 'value': 'False', 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 2, 'value': 'False', 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 3, 'value': 'False', 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 4, 'value': 'False', 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 5, 'value': 'False', 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 6, 'value': 'False', 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 7, 'value': 'False', 'expectedValue': False, 'expectedBytes': bytes([0x00])},
        {'bo': 0, 'value':  'True', 'expectedValue':  True, 'expectedBytes': bytes([0x01])},
        {'bo': 1, 'value':  'True', 'expectedValue':  True, 'expectedBytes': bytes([0x02])},
        {'bo': 2, 'value':  'True', 'expectedValue':  True, 'expectedBytes': bytes([0x04])},
        {'bo': 3, 'value':  'True', 'expectedValue':  True, 'expectedBytes': bytes([0x08])},
        {'bo': 4, 'value':  'True', 'expectedValue':  True, 'expectedBytes': bytes([0x10])},
        {'bo': 5, 'value':  'True', 'expectedValue':  True, 'expectedBytes': bytes([0x20])},
        {'bo': 6, 'value':  'True', 'expectedValue':  True, 'expectedBytes': bytes([0x40])},
        {'bo': 7, 'value':  'True', 'expectedValue':  True, 'expectedBytes': bytes([0x80])},
    ])
    def testParseValue(self, bo, value, expectedValue, expectedBytes):
        param = BitParameter('test-name', 'Test description', 0, bo, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), value)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'value': 'None'},
        {'value':    '2'},
    ])
    def testParseValueInvalid(self, value):
        param = BitParameter('test-name', 'Test description', 0, 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid bit value: {value}")
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))

    @testdata.TestData([
        {'bo': 0, 'value': False, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 1, 'value': False, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 2, 'value': False, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 3, 'value': False, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 4, 'value': False, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 5, 'value': False, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 6, 'value': False, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 7, 'value': False, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 0, 'value': False, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFE])},
        {'bo': 1, 'value': False, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFD])},
        {'bo': 2, 'value': False, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFB])},
        {'bo': 3, 'value': False, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xF7])},
        {'bo': 4, 'value': False, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xEF])},
        {'bo': 5, 'value': False, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xDF])},
        {'bo': 6, 'value': False, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xBF])},
        {'bo': 7, 'value': False, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0x7F])},
        {'bo': 0, 'value':  True, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x01])},
        {'bo': 1, 'value':  True, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x02])},
        {'bo': 2, 'value':  True, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x04])},
        {'bo': 3, 'value':  True, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x08])},
        {'bo': 4, 'value':  True, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x10])},
        {'bo': 5, 'value':  True, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x20])},
        {'bo': 6, 'value':  True, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x40])},
        {'bo': 7, 'value':  True, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x80])},
        {'bo': 0, 'value':  True, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 1, 'value':  True, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 2, 'value':  True, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 3, 'value':  True, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 4, 'value':  True, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 5, 'value':  True, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 6, 'value':  True, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 7, 'value':  True, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
    ])
    def testOldData(self, bo, value, oldData, expectedBytes):
        param = BitParameter('test-name', 'Test description', 0, bo, True)
        param.value = value
        self.assertEqual(bytes(param | oldData), expectedBytes)

class TestEnum1(Enum):
    KO = 0x00
    OK = 0x01

class TestEnumBitParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'bo': 0, 'w':  True},
        {'o': 1, 'bo': 0, 'w':  True},
        {'o': 0, 'bo': 7, 'w':  True},
        {'o': 1, 'bo': 7, 'w':  True},
        {'o': 0, 'bo': 0, 'w': False},
        {'o': 1, 'bo': 0, 'w': False},
        {'o': 0, 'bo': 7, 'w': False},
        {'o': 1, 'bo': 7, 'w': False},
    ])
    def testConstructor(self, o, bo, w):
        param = EnumBitParameter('test-name', 'Test description', o, bo, TestEnum1, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 1)
        self.assertEqual(param.range, Range(o, 1))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))

    @testdata.TestData([
        {'bo': 0, 'data': bytes([0xFE]), 'expectedValue': TestEnum1.KO, 'expectedStr': 'KO', 'expectedBytes': bytes([0x00])},
        {'bo': 1, 'data': bytes([0xFD]), 'expectedValue': TestEnum1.KO, 'expectedStr': 'KO', 'expectedBytes': bytes([0x00])},
        {'bo': 2, 'data': bytes([0xFB]), 'expectedValue': TestEnum1.KO, 'expectedStr': 'KO', 'expectedBytes': bytes([0x00])},
        {'bo': 3, 'data': bytes([0xF7]), 'expectedValue': TestEnum1.KO, 'expectedStr': 'KO', 'expectedBytes': bytes([0x00])},
        {'bo': 4, 'data': bytes([0xEF]), 'expectedValue': TestEnum1.KO, 'expectedStr': 'KO', 'expectedBytes': bytes([0x00])},
        {'bo': 5, 'data': bytes([0xDF]), 'expectedValue': TestEnum1.KO, 'expectedStr': 'KO', 'expectedBytes': bytes([0x00])},
        {'bo': 6, 'data': bytes([0xBF]), 'expectedValue': TestEnum1.KO, 'expectedStr': 'KO', 'expectedBytes': bytes([0x00])},
        {'bo': 7, 'data': bytes([0x7F]), 'expectedValue': TestEnum1.KO, 'expectedStr': 'KO', 'expectedBytes': bytes([0x00])},
        {'bo': 0, 'data': bytes([0x01]), 'expectedValue': TestEnum1.OK, 'expectedStr': 'OK', 'expectedBytes': bytes([0x01])},
        {'bo': 1, 'data': bytes([0x02]), 'expectedValue': TestEnum1.OK, 'expectedStr': 'OK', 'expectedBytes': bytes([0x02])},
        {'bo': 2, 'data': bytes([0x04]), 'expectedValue': TestEnum1.OK, 'expectedStr': 'OK', 'expectedBytes': bytes([0x04])},
        {'bo': 3, 'data': bytes([0x08]), 'expectedValue': TestEnum1.OK, 'expectedStr': 'OK', 'expectedBytes': bytes([0x08])},
        {'bo': 4, 'data': bytes([0x10]), 'expectedValue': TestEnum1.OK, 'expectedStr': 'OK', 'expectedBytes': bytes([0x10])},
        {'bo': 5, 'data': bytes([0x20]), 'expectedValue': TestEnum1.OK, 'expectedStr': 'OK', 'expectedBytes': bytes([0x20])},
        {'bo': 6, 'data': bytes([0x40]), 'expectedValue': TestEnum1.OK, 'expectedStr': 'OK', 'expectedBytes': bytes([0x40])},
        {'bo': 7, 'data': bytes([0x80]), 'expectedValue': TestEnum1.OK, 'expectedStr': 'OK', 'expectedBytes': bytes([0x80])},
    ])
    def testParseData(self, bo, data, expectedValue, expectedStr, expectedBytes):
        param = EnumBitParameter('test-name', 'Test description', 0, bo, TestEnum1, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'bo': 0, 'value': 'KO', 'expectedValue': TestEnum1.KO, 'expectedBytes': bytes([0x00])},
        {'bo': 1, 'value': 'KO', 'expectedValue': TestEnum1.KO, 'expectedBytes': bytes([0x00])},
        {'bo': 2, 'value': 'KO', 'expectedValue': TestEnum1.KO, 'expectedBytes': bytes([0x00])},
        {'bo': 3, 'value': 'KO', 'expectedValue': TestEnum1.KO, 'expectedBytes': bytes([0x00])},
        {'bo': 4, 'value': 'KO', 'expectedValue': TestEnum1.KO, 'expectedBytes': bytes([0x00])},
        {'bo': 5, 'value': 'KO', 'expectedValue': TestEnum1.KO, 'expectedBytes': bytes([0x00])},
        {'bo': 6, 'value': 'KO', 'expectedValue': TestEnum1.KO, 'expectedBytes': bytes([0x00])},
        {'bo': 7, 'value': 'KO', 'expectedValue': TestEnum1.KO, 'expectedBytes': bytes([0x00])},
        {'bo': 0, 'value': 'OK', 'expectedValue': TestEnum1.OK, 'expectedBytes': bytes([0x01])},
        {'bo': 1, 'value': 'OK', 'expectedValue': TestEnum1.OK, 'expectedBytes': bytes([0x02])},
        {'bo': 2, 'value': 'OK', 'expectedValue': TestEnum1.OK, 'expectedBytes': bytes([0x04])},
        {'bo': 3, 'value': 'OK', 'expectedValue': TestEnum1.OK, 'expectedBytes': bytes([0x08])},
        {'bo': 4, 'value': 'OK', 'expectedValue': TestEnum1.OK, 'expectedBytes': bytes([0x10])},
        {'bo': 5, 'value': 'OK', 'expectedValue': TestEnum1.OK, 'expectedBytes': bytes([0x20])},
        {'bo': 6, 'value': 'OK', 'expectedValue': TestEnum1.OK, 'expectedBytes': bytes([0x40])},
        {'bo': 7, 'value': 'OK', 'expectedValue': TestEnum1.OK, 'expectedBytes': bytes([0x80])},
    ])
    def testParseValue(self, bo, value, expectedValue, expectedBytes):
        param = EnumBitParameter('test-name', 'Test description', 0, bo, TestEnum1, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), value)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'value':  'None'},
        {'value': 'False'},
        {'value':  'True'},
        {'value':     '2'},
    ])
    def testParseValueInvalid(self, value):
        param = EnumBitParameter('test-name', 'Test description', 0, 0, TestEnum1, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid value: {value} (accepted values: \"KO\", \"OK\")")
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]))

    @testdata.TestData([
        {'bo': 0, 'value':         None, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 1, 'value':         None, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 2, 'value':         None, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 3, 'value':         None, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 4, 'value':         None, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 5, 'value':         None, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 6, 'value':         None, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 7, 'value':         None, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 0, 'value':         None, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 1, 'value':         None, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 2, 'value':         None, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 3, 'value':         None, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 4, 'value':         None, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 5, 'value':         None, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 6, 'value':         None, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 7, 'value':         None, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 0, 'value': TestEnum1.KO, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 1, 'value': TestEnum1.KO, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 2, 'value': TestEnum1.KO, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 3, 'value': TestEnum1.KO, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 4, 'value': TestEnum1.KO, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 5, 'value': TestEnum1.KO, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 6, 'value': TestEnum1.KO, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 7, 'value': TestEnum1.KO, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x00])},
        {'bo': 0, 'value': TestEnum1.KO, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFE])},
        {'bo': 1, 'value': TestEnum1.KO, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFD])},
        {'bo': 2, 'value': TestEnum1.KO, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFB])},
        {'bo': 3, 'value': TestEnum1.KO, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xF7])},
        {'bo': 4, 'value': TestEnum1.KO, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xEF])},
        {'bo': 5, 'value': TestEnum1.KO, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xDF])},
        {'bo': 6, 'value': TestEnum1.KO, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xBF])},
        {'bo': 7, 'value': TestEnum1.KO, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0x7F])},
        {'bo': 0, 'value': TestEnum1.OK, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x01])},
        {'bo': 1, 'value': TestEnum1.OK, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x02])},
        {'bo': 2, 'value': TestEnum1.OK, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x04])},
        {'bo': 3, 'value': TestEnum1.OK, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x08])},
        {'bo': 4, 'value': TestEnum1.OK, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x10])},
        {'bo': 5, 'value': TestEnum1.OK, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x20])},
        {'bo': 6, 'value': TestEnum1.OK, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x40])},
        {'bo': 7, 'value': TestEnum1.OK, 'oldData': bytes([0x00]), 'expectedBytes': bytes([0x80])},
        {'bo': 0, 'value': TestEnum1.OK, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 1, 'value': TestEnum1.OK, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 2, 'value': TestEnum1.OK, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 3, 'value': TestEnum1.OK, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 4, 'value': TestEnum1.OK, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 5, 'value': TestEnum1.OK, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 6, 'value': TestEnum1.OK, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
        {'bo': 7, 'value': TestEnum1.OK, 'oldData': bytes([0xFF]), 'expectedBytes': bytes([0xFF])},
    ])
    def testOldData(self, bo, value, oldData, expectedBytes):
        param = EnumBitParameter('test-name', 'Test description', 0, bo, TestEnum1, True)
        param.value = value
        self.assertEqual(bytes(param | oldData), expectedBytes)


class TestFloatParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'w':  True},
        {'o': 1, 'w':  True},
        {'o': 0, 'w': False},
        {'o': 1, 'w': False},
    ])
    def testConstructor(self, o, w):
        param = FloatParameter('test-name', 'Test description', o, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 2)
        self.assertEqual(param.range, Range(o, 2))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00, 0x00]))

    @testdata.TestData([
        {'data': bytes([0x00, 0x00]), 'expectedValue':          0.0, 'expectedStr':     '0.0'},
        {'data': bytes([0x00, 0x01]), 'expectedValue':          0.1, 'expectedStr':     '0.1'},
        {'data': bytes([0x7F, 0xFF]), 'expectedValue':       3276.7, 'expectedStr':  '3276.7'},
        {'data': bytes([0x80, 0x00]), 'expectedValue':         -0.0, 'expectedStr':     '0.0'},
        {'data': bytes([0x80, 0x01]), 'expectedValue':         -0.1, 'expectedStr':    '-0.1'},
        {'data': bytes([0xFF, 0xFE]), 'expectedValue':      -3276.6, 'expectedStr': '-3276.6'},
        {'data': bytes([0xFF, 0xFF]), 'expectedValue': float('nan'), 'expectedStr':     'nan'},
    ])
    def testParseData(self, data, expectedValue, expectedStr):
        param = FloatParameter('test-name', 'Test description', 0, True)
        param.parseData(data)
        if math.isnan(expectedValue):
            self.assertTrue(math.isnan(param.value))
        else:
            self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), data)

    @testdata.TestData([
        {'value':      '0.0', 'expectedValue':          0.0, 'expectedStr':     '0.0', 'expectedBytes': bytes([0x00, 0x00])},
        {'value':      '0.1', 'expectedValue':          0.1, 'expectedStr':     '0.1', 'expectedBytes': bytes([0x00, 0x01])},
        {'value':     '0.14', 'expectedValue':          0.1, 'expectedStr':     '0.1', 'expectedBytes': bytes([0x00, 0x01])},
        {'value':     '0.16', 'expectedValue':          0.2, 'expectedStr':     '0.2', 'expectedBytes': bytes([0x00, 0x02])},
        {'value':   '3276.7', 'expectedValue':       3276.7, 'expectedStr':  '3276.7', 'expectedBytes': bytes([0x7F, 0xFF])},
        {'value':  '3276.74', 'expectedValue':       3276.7, 'expectedStr':  '3276.7', 'expectedBytes': bytes([0x7F, 0xFF])},
        {'value':     '-0.0', 'expectedValue':         -0.0, 'expectedStr':     '0.0', 'expectedBytes': bytes([0x00, 0x00])},
        {'value':     '-0.1', 'expectedValue':         -0.1, 'expectedStr':    '-0.1', 'expectedBytes': bytes([0x80, 0x01])},
        {'value':    '-0.14', 'expectedValue':         -0.1, 'expectedStr':    '-0.1', 'expectedBytes': bytes([0x80, 0x01])},
        {'value':    '-0.16', 'expectedValue':         -0.2, 'expectedStr':    '-0.2', 'expectedBytes': bytes([0x80, 0x02])},
        {'value':  '-3276.6', 'expectedValue':      -3276.6, 'expectedStr': '-3276.6', 'expectedBytes': bytes([0xFF, 0xFE])},
        {'value': '-3276.64', 'expectedValue':      -3276.6, 'expectedStr': '-3276.6', 'expectedBytes': bytes([0xFF, 0xFE])},
        {'value':      'nan', 'expectedValue': float('nan'), 'expectedStr':     'nan', 'expectedBytes': bytes([0xFF, 0xFF])},
        {'value':      'inf', 'expectedValue': float('nan'), 'expectedStr':     'nan', 'expectedBytes': bytes([0xFF, 0xFF])},
        {'value':     '-inf', 'expectedValue': float('nan'), 'expectedStr':     'nan', 'expectedBytes': bytes([0xFF, 0xFF])},
    ])
    def testParseValue(self, value, expectedValue, expectedStr, expectedBytes):
        param = FloatParameter('test-name', 'Test description', 0, True)
        param.parseValue(value)
        if math.isnan(expectedValue):
            self.assertTrue(math.isnan(param.value))
        else:
            self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'value':  '0..'},
        {'value': '0..0'},
        {'value': '0.0.'},
        {'value': '.0.0'},
        {'value': '0.0f'},
        {'value': 'snan'},
        {'value': 'qnan'},
    ])
    def testParseValueInvalid(self, value):
        param = FloatParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid value for floating-point number: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*2))

    @testdata.TestData([
        {'value':   '3276.8'},
        {'value':  '3276.76'},
    ])
    def testParseValueTooLarge(self, value):
        param = FloatParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Value is too large: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*2))

    @testdata.TestData([
        {'value':  '-3276.7'},
        {'value': '-3276.66'},
    ])
    def testParseValueTooSmall(self, value):
        param = FloatParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Value is too small: {value}")

        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*2))


class TestTimeSpanParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'w':  True},
        {'o': 1, 'w':  True},
        {'o': 0, 'w': False},
        {'o': 1, 'w': False},
    ])
    def testConstructor(self, o, w):
        param = TimeSpanParameter('test-name', 'Test description', o, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 2)
        self.assertEqual(param.range, Range(o, 2))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00, 0x00]))

    @testdata.TestData([
        {'data': bytes([0x00, 0x00]), 'expectedValue':      0, 'expectedStr':         '0s'},
        {'data': bytes([0x00, 0x01]), 'expectedValue':     10, 'expectedStr':        '10s'},
        {'data': bytes([0x00, 0x06]), 'expectedValue':     60, 'expectedStr':         '1m'},
        {'data': bytes([0x00, 0x07]), 'expectedValue':     70, 'expectedStr':      '1m10s'},
        {'data': bytes([0x01, 0x68]), 'expectedValue':   3600, 'expectedStr':         '1h'},
        {'data': bytes([0x01, 0x6E]), 'expectedValue':   3660, 'expectedStr':       '1h1m'},
        {'data': bytes([0x01, 0x6F]), 'expectedValue':   3670, 'expectedStr':    '1h1m10s'},
        {'data': bytes([0x21, 0xC0]), 'expectedValue':  86400, 'expectedStr':         '1j'},
        {'data': bytes([0x23, 0x28]), 'expectedValue':  90000, 'expectedStr':       '1j1h'},
        {'data': bytes([0x23, 0x2E]), 'expectedValue':  90060, 'expectedStr':     '1j1h1m'},
        {'data': bytes([0x23, 0x2F]), 'expectedValue':  90070, 'expectedStr':  '1j1h1m10s'},
        {'data': bytes([0xFF, 0xFF]), 'expectedValue': 655350, 'expectedStr': '7j14h2m30s'},
    ])
    def testParseData(self, data, expectedValue, expectedStr):
        param = TimeSpanParameter('test-name', 'Test description', 0, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), data)

    @testdata.TestData([
        {'value':         '0s', 'expectedValue':      0, 'expectedBytes': bytes([0x00, 0x00])},
        {'value':        '10s', 'expectedValue':     10, 'expectedBytes': bytes([0x00, 0x01])},
        {'value':         '1m', 'expectedValue':     60, 'expectedBytes': bytes([0x00, 0x06])},
        {'value':      '1m10s', 'expectedValue':     70, 'expectedBytes': bytes([0x00, 0x07])},
        {'value':         '1h', 'expectedValue':   3600, 'expectedBytes': bytes([0x01, 0x68])},
        {'value':       '1h1m', 'expectedValue':   3660, 'expectedBytes': bytes([0x01, 0x6E])},
        {'value':      '1h10s', 'expectedValue':   3610, 'expectedBytes': bytes([0x01, 0x69])},
        {'value':    '1h1m10s', 'expectedValue':   3670, 'expectedBytes': bytes([0x01, 0x6F])},
        {'value':         '1j', 'expectedValue':  86400, 'expectedBytes': bytes([0x21, 0xC0])},
        {'value':       '1j1h', 'expectedValue':  90000, 'expectedBytes': bytes([0x23, 0x28])},
        {'value':       '1j1m', 'expectedValue':  86460, 'expectedBytes': bytes([0x21, 0xC6])},
        {'value':      '1j10s', 'expectedValue':  86410, 'expectedBytes': bytes([0x21, 0xC1])},
        {'value':     '1j1h1m', 'expectedValue':  90060, 'expectedBytes': bytes([0x23, 0x2E])},
        {'value':    '1j1h10s', 'expectedValue':  90010, 'expectedBytes': bytes([0x23, 0x29])},
        {'value':  '1j1h1m10s', 'expectedValue':  90070, 'expectedBytes': bytes([0x23, 0x2F])},
        {'value': '7j14h2m30s', 'expectedValue': 655350, 'expectedBytes': bytes([0xFF, 0xFF])},
    ])
    def testParseValue(self, value, expectedValue, expectedBytes):
        param = TimeSpanParameter('test-name', 'Test description', 0, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), value)
        self.assertEqual(bytes(param), expectedBytes)

    @testdata.TestData([
        {'value':          'j'},
        {'value':       'j10h'},
        {'value':    'j10h10m'},
        {'value': 'j10h10m10s'},
        {'value':       '10jh'},
        {'value':    '10jh10m'},
        {'value': '10jh10m10s'},
        {'value':       '10jm'},
        {'value':    '10jm10s'},
        {'value':       '10js'},
        {'value':          'h'},
        {'value':       'h10m'},
        {'value':    'h10m10s'},
        {'value':       '10hm'},
        {'value':    '10hm10s'},
        {'value':       '10hs'},
        {'value':          'm'},
        {'value':       'm10s'},
        {'value':       '10ms'},
        {'value':          's'},
        {'value':       '10h10j'},
        {'value':    '10h10j10m'},
        {'value': '10h10j10m10s'},
        {'value':    '10h10m10j'},
        {'value': '10h10m10j10s'},
        {'value': '10h10m10s10j'},
        {'value':    '10j10m10h'},
        {'value': '10j10m10h10s'},
        {'value': '10j10m10s10h'},
        {'value':       '10m10h'},
        {'value':    '10m10h10s'},
        {'value':    '10m10s10h'},
        {'value': '10j10h10s10m'},
        {'value':    '10h10s10m'},
        {'value':    '10j10s10m'},
        {'value':       '10s10m'},
    ])
    def testParseValueInvalid(self, value):
        param = TimeSpanParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid timespan: {value}")
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00, 0x00]))

    @testdata.TestData([
        {'value':        '11s', 'expectedValue':    10, 'expectedStr':        '10s', 'expectedBytes': bytes([0x00, 0x01])},
        {'value':     '10m12s', 'expectedValue':   610, 'expectedStr':     '10m10s', 'expectedBytes': bytes([0x00, 0x3D])},
        {'value':      '1h13s', 'expectedValue':  3610, 'expectedStr':      '1h10s', 'expectedBytes': bytes([0x01, 0x69])},
        {'value':      '1j14s', 'expectedValue': 86410, 'expectedStr':      '1j10s', 'expectedBytes': bytes([0x21, 0xC1])},
        {'value':   '1h10m16s', 'expectedValue':  4210, 'expectedStr':   '1h10m10s', 'expectedBytes': bytes([0x01, 0xA5])},
        {'value':   '1j10m17s', 'expectedValue': 87010, 'expectedStr':   '1j10m10s', 'expectedBytes': bytes([0x21, 0xFD])},
        {'value':    '1j1h18s', 'expectedValue': 90010, 'expectedStr':    '1j1h10s', 'expectedBytes': bytes([0x23, 0x29])},
        {'value': '1j1h10m19s', 'expectedValue': 90610, 'expectedStr': '1j1h10m10s', 'expectedBytes': bytes([0x23, 0x65])},
        {'value':        '51s', 'expectedValue':    50, 'expectedStr':        '50s', 'expectedBytes': bytes([0x00, 0x05])},
        {'value':     '10m52s', 'expectedValue':   650, 'expectedStr':     '10m50s', 'expectedBytes': bytes([0x00, 0x41])},
        {'value':      '1h53s', 'expectedValue':  3650, 'expectedStr':      '1h50s', 'expectedBytes': bytes([0x01, 0x6D])},
        {'value':      '1j54s', 'expectedValue': 86450, 'expectedStr':      '1j50s', 'expectedBytes': bytes([0x21, 0xC5])},
        {'value':   '1h10m56s', 'expectedValue':  4250, 'expectedStr':   '1h10m50s', 'expectedBytes': bytes([0x01, 0xA9])},
        {'value':   '1j10m57s', 'expectedValue': 87050, 'expectedStr':   '1j10m50s', 'expectedBytes': bytes([0x22, 0x01])},
        {'value':    '1j1h58s', 'expectedValue': 90050, 'expectedStr':    '1j1h50s', 'expectedBytes': bytes([0x23, 0x2D])},
        {'value': '1j1h10m59s', 'expectedValue': 90650, 'expectedStr': '1j1h10m50s', 'expectedBytes': bytes([0x23, 0x69])},
    ])
    def testParseValueTooAccurate(self, value, expectedValue, expectedStr, expectedBytes):
        param = TimeSpanParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), "Time span precision is 10s. Ignoring extra precision.")
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedStr)
        self.assertEqual(bytes(param), expectedBytes)


class TestTimeZoneParameter(unittest.TestCase):
    @testdata.TestData([
        {'o': 0, 'w':  True},
        {'o': 1, 'w':  True},
        {'o': 0, 'w': False},
        {'o': 1, 'w': False},
    ])
    def testConstructor(self, o, w):
        param = TimeZoneParameter('test-name', 'Test description', o, w)
        self.assertEqual(param.name, 'test-name')
        self.assertEqual(param.description, 'Test description')
        self.assertEqual(param.offset, o)
        self.assertEqual(param.len, 12)
        self.assertEqual(param.range, Range(o, 12))
        self.assertEqual(param.writable, w)
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param), bytes([0x00]*12))

    @testdata.TestData([
        {'data': bytes([0xE0] + [0xFF]*10 + [0x00]), 'expectedValue': '+0000'},
        {'data': bytes([0xE1] + [0xFF]*10 + [0x00]), 'expectedValue': '+0100'},
        {'data': bytes([0xEB] + [0xFF]*10 + [0x00]), 'expectedValue': '+1100'},
        {'data': bytes([0xEC] + [0xFF]*10 + [0x00]), 'expectedValue': '+1200'},
        {'data': bytes([0xED] + [0xFF]*10 + [0x00]), 'expectedValue': '-1100'},
        {'data': bytes([0xEF] + [0xFF]*10 + [0x00]), 'expectedValue': '-0900'},
        {'data': bytes([0xF0] + [0xFF]*10 + [0x00]), 'expectedValue': '-0800'},
        {'data': bytes([0xF7] + [0xFF]*10 + [0x00]), 'expectedValue': '-0100'},
        #{'data': bytes([0xF8] + [0xFF]*10 + [0x00]), 'expectedValue': '+0000'},
        {'data': bytes([0xE0] + [0xFF]*10 + [0x1E]), 'expectedValue': '+0030'},
        {'data': bytes([0xEB] + [0xFF]*10 + [0x1E]), 'expectedValue': '+1130'},
        {'data': bytes([0xF8] + [0xFF]*10 + [0x1E]), 'expectedValue': '-0030'},
        {'data': bytes([0xED] + [0xFF]*10 + [0x1E]), 'expectedValue': '-1130'},
    ])
    def testParseData(self, data, expectedValue):
        param = TimeZoneParameter('test-name', 'Test description', 0, True)
        param.parseData(data)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedValue)
        self.assertEqual(bytes(param | bytes([0xE0] + [0xFF]*10 + [0x00])), data)

    @testdata.TestData([
        {'data': bytes([0xF9] + [0xFF]*10 + [0x00]), 'h': 25, 'm':  0},
        {'data': bytes([0xFF] + [0xFF]*10 + [0x00]), 'h': 31, 'm':  0},
        {'data': bytes([0xE0] + [0xFF]*10 + [0x3C]), 'h':  0, 'm': 60},
        {'data': bytes([0xEB] + [0xFF]*10 + [0x3C]), 'h': 11, 'm': 60},
        {'data': bytes([0xEC] + [0xFF]*10 + [0x01]), 'h': 12, 'm':  1},
        {'data': bytes([0xED] + [0xFF]*10 + [0x3C]), 'h': 13, 'm': 60},
        {'data': bytes([0xF8] + [0xFF]*10 + [0x3C]), 'h': 24, 'm': 60},
    ])
    def testParseDataInvalid(self, data, h, m):
        param = TimeZoneParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseData(data)
        self.assertEqual(str(w.warning), f"Invalid timezone data: h={h}, m={m}")
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param | bytes([0xE0] + [0xFF]*10 + [0x00])), bytes([0xE0] + [0xFF]*10 + [0x00]))

    @testdata.TestData([
        {'value':  '0000', 'expectedValue': '+0000', 'expectedBytes': bytes([0xE0] + [0xFF]*10 + [0x00])},
        {'value': '+0000', 'expectedValue': '+0000', 'expectedBytes': bytes([0xE0] + [0xFF]*10 + [0x00])},
        {'value': '-0000', 'expectedValue': '+0000', 'expectedBytes': bytes([0xE0] + [0xFF]*10 + [0x00])},
        {'value':  '0100', 'expectedValue': '+0100', 'expectedBytes': bytes([0xE1] + [0xFF]*10 + [0x00])},
        {'value':  '1200', 'expectedValue': '+1200', 'expectedBytes': bytes([0xEC] + [0xFF]*10 + [0x00])},
        {'value': '+0100', 'expectedValue': '+0100', 'expectedBytes': bytes([0xE1] + [0xFF]*10 + [0x00])},
        {'value': '+1200', 'expectedValue': '+1200', 'expectedBytes': bytes([0xEC] + [0xFF]*10 + [0x00])},
        {'value': '-0100', 'expectedValue': '-0100', 'expectedBytes': bytes([0xF7] + [0xFF]*10 + [0x00])},
        {'value': '-1200', 'expectedValue': '-1200', 'expectedBytes': bytes([0xEC] + [0xFF]*10 + [0x00])},
        {'value':  '0030', 'expectedValue': '+0030', 'expectedBytes': bytes([0xE0] + [0xFF]*10 + [0x1E])},
        {'value':  '1130', 'expectedValue': '+1130', 'expectedBytes': bytes([0xEB] + [0xFF]*10 + [0x1E])},
        {'value': '+0030', 'expectedValue': '+0030', 'expectedBytes': bytes([0xE0] + [0xFF]*10 + [0x1E])},
        {'value': '+1130', 'expectedValue': '+1130', 'expectedBytes': bytes([0xEB] + [0xFF]*10 + [0x1E])},
        {'value': '-0030', 'expectedValue': '-0030', 'expectedBytes': bytes([0xF8] + [0xFF]*10 + [0x1E])},
        {'value': '-1130', 'expectedValue': '-1130', 'expectedBytes': bytes([0xED] + [0xFF]*10 + [0x1E])},
    ])
    def testParseValue(self, value, expectedValue, expectedBytes):
        param = TimeZoneParameter('test-name', 'Test description', 0, True)
        param.parseValue(value)
        self.assertEqual(param.value, expectedValue)
        self.assertEqual(str(param), expectedValue)
        self.assertEqual(bytes(param | bytes([0xE0] + [0xFF]*10 + [0x00])), expectedBytes)


    @testdata.TestData([
        {'value':   '1300'},
        {'value':  '+1300'},
        {'value':  '-1300'},
        {'value':   '0060'},
        {'value':  '+0060'},
        {'value':  '-0060'},
        {'value':    '115'},
        {'value':   '+115'},
        {'value':   '-115'},
        {'value':  '11500'},
        {'value': '+11500'},
        {'value': '-11500'},
        {'value':    'UTC'},
    ])
    def testParseValueInvalid(self, value):
        param = TimeZoneParameter('test-name', 'Test description', 0, True)
        with self.assertWarns(UserWarning) as w:
            param.parseValue(value)
        self.assertEqual(str(w.warning), f"Invalid timezone: {value}")
        self.assertIsNone(param.value)
        self.assertEqual(str(param), '')
        self.assertEqual(bytes(param | bytes([0xE0] + [0xFF]*10 + [0x00])), bytes([0xE0] + [0xFF]*10 + [0x00]))

