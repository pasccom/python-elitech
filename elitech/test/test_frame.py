import unittest

from PythonUtils import testdata

from elitech.src.frames import Frame

class TestFrame(unittest.TestCase):
    def testInvalidOperation(self):
        with self.assertRaises(ValueError) as e:
            Frame(None, 0, 1)

        self.assertEqual(str(e.exception), f"Invalid operation: None")

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter, 'offset':        -1},
        {'op': Frame.Operation.SetParameter, 'offset':        -2},
        {'op': Frame.Operation.GetRecord,    'offset':        -3},
        {'op': Frame.Operation.GetParameter, 'offset': 0x1000000},
        {'op': Frame.Operation.SetParameter, 'offset': 0x1000001},
        {'op': Frame.Operation.GetRecord,    'offset': 0x1000002},
    ])
    def testInvalidOffset(self, op, offset):
        with self.assertRaises(ValueError) as e:
            Frame(op, offset, 1)

        self.assertEqual(str(e.exception), f"Invalid offset: {offset}")

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter, 'length':  0},
        {'op': Frame.Operation.GetParameter, 'length': -1},
        {'op': Frame.Operation.GetRecord,    'length': -2},
        {'op': Frame.Operation.GetParameter, 'length': 52},
        {'op': Frame.Operation.GetRecord,    'length': 53},
        {'op': Frame.Operation.GetRecord,    'length': 54},
    ])
    def testInvalidLength(self, op, length):
        with self.assertRaises(ValueError) as e:
            Frame(op, 0, length)

        self.assertEqual(str(e.exception), f"Invalid length: {length}")

    @testdata.TestData([
        {'op': Frame.Operation.SetParameter, 'length': 52},
        {'op': Frame.Operation.SetParameter, 'length': 53},
        {'op': Frame.Operation.SetParameter, 'length': 54},
    ])
    def testInvalidDataLength(self, op, length):
        with self.assertRaises(ValueError) as e:
            Frame(op, 0, bytes([0x00]*length))

        self.assertEqual(str(e.exception), f"Too much data: {length}")

    @testdata.TestData([
        {'op': Frame.Operation.SetParameter, 'length': 1},
        {'op': Frame.Operation.SetParameter, 'length': 2},
        {'op': Frame.Operation.SetParameter, 'length': 3},
    ])
    def testInvalidData(self, op, length):
        with self.assertRaises(TypeError) as e:
            Frame(op, 0, [0x00]*length)

        self.assertEqual(str(e.exception), "Invalid type for data or length: <class 'list'>")

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter, 'offset':         0, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x10])},
        {'op': Frame.Operation.GetParameter, 'offset':         0, 'length':  2, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x10])},
        {'op': Frame.Operation.GetParameter, 'offset':         0, 'length': 51, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x33, 0x41])},
        {'op': Frame.Operation.GetParameter, 'offset':      0xFF, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0x00, 0xFE, 0x00, 0x02, 0x0E])},
        {'op': Frame.Operation.GetParameter, 'offset':      0xFF, 'length':  2, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x02, 0x0F])},
        {'op': Frame.Operation.GetParameter, 'offset':      0xFF, 'length': 51, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x33, 0x40])},
        {'op': Frame.Operation.GetParameter, 'offset':    0xFFFF, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0xFF, 0xFE, 0x00, 0x02, 0x0D])},
        {'op': Frame.Operation.GetParameter, 'offset':    0xFFFF, 'length':  2, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x02, 0x0E])},
        {'op': Frame.Operation.GetParameter, 'offset':    0xFFFF, 'length': 51, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x33, 0x3F])},
        {'op': Frame.Operation.GetParameter, 'offset':  0xFFFFFF, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0xFF, 0xFE, 0xFF, 0x02, 0x0C])},
        {'op': Frame.Operation.GetParameter, 'offset':  0xFFFFFF, 'length':  2, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x02, 0x0D])},
        {'op': Frame.Operation.GetParameter, 'offset':  0xFFFFFF, 'length': 51, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x03, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x33, 0x3E])},
        {'op': Frame.Operation.GetRecord,    'offset':         0, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x0D])},
        {'op': Frame.Operation.GetRecord,    'offset':         0, 'length':  2, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x0E])},
        {'op': Frame.Operation.GetRecord,    'offset':         0, 'length': 51, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x33, 0x3F])},
        {'op': Frame.Operation.GetRecord,    'offset':      0xFF, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x01, 0x0C])},
        {'op': Frame.Operation.GetRecord,    'offset':      0xFF, 'length':  2, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x02, 0x0D])},
        {'op': Frame.Operation.GetRecord,    'offset':      0xFF, 'length': 51, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x33, 0x3E])},
        {'op': Frame.Operation.GetRecord,    'offset':    0xFFFF, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x01, 0x0B])},
        {'op': Frame.Operation.GetRecord,    'offset':    0xFFFF, 'length':  2, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x02, 0x0C])},
        {'op': Frame.Operation.GetRecord,    'offset':    0xFFFF, 'length': 51, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x33, 0x3D])},
        {'op': Frame.Operation.GetRecord,    'offset':  0xFFFFFF, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x01, 0x0A])},
        {'op': Frame.Operation.GetRecord,    'offset':  0xFFFFFF, 'length':  2, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x02, 0x0B])},
        {'op': Frame.Operation.GetRecord,    'offset':  0xFFFFFF, 'length': 51, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, 0x01, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x33, 0x3C])},
    ])
    def testReadFrame(self, op, offset, length, expected):
        frame = Frame(op, offset, length)
        self.assertEqual(bytes(frame), expected)

    @testdata.TestData([
        {'op': Frame.Operation.SetParameter, 'offset':         0, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0D, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,    0x00,    0x11])},
        {'op': Frame.Operation.SetParameter, 'offset':      0xFF, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0D, 0x04, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x01,    0x00,    0x10])},
        {'op': Frame.Operation.SetParameter, 'offset':    0xFFFF, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0D, 0x04, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x01,    0x00,    0x0F])},
        {'op': Frame.Operation.SetParameter, 'offset':  0xFFFFFF, 'length':  1, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x0D, 0x04, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x01,    0x00,    0x0E])},
        {'op': Frame.Operation.SetParameter, 'offset':         0, 'length': 51, 'expected': bytes([0x00, 0x33, 0xCC, 0x00, 0x3F, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x33] + [0]*51 + [0x75])},
    ])
    def testWriteFrame(self, op, offset, length, expected):
        frame = Frame(op, offset, bytes([0]*length))
        self.assertEqual(bytes(frame), expected)

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter},
        {'op': Frame.Operation.SetParameter},
        {'op': Frame.Operation.GetRecord   },
    ])
    def testParseIncompleteHeader(self, op):
        frame = Frame(op, 0, 2)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, op.value + 0x0D]))
        with self.assertRaises(ValueError) as e:
            frame.parse(bytes([0x33, 0xCC, 0x00, 0x0A, op.value, 0x00, 0x00, 0x00, 0x00, 0x00]))

        self.assertEqual(str(e.exception), f"Anwser does not contain header: len(answer) = 10")

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter},
        {'op': Frame.Operation.SetParameter},
        {'op': Frame.Operation.GetRecord   },
    ])
    def testParseInvalidHeader(self, op):
        frame = Frame(op, 0, 2)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, op.value + 0x0D]))
        with self.assertRaises(ValueError) as e:
            frame.parse(bytes([0x00, 0x33, 0xCC, 0x01, 0x0A, op.value, 0x00, 0x00, 0x00, 0x00, 0x00]))

        self.assertEqual(str(e.exception), f"Invalid answer header: 00 33 CC")

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter},
        {'op': Frame.Operation.SetParameter},
        {'op': Frame.Operation.GetRecord   },
    ])
    def testParseOperationMismatch(self, op):
        frame = Frame(op, 0, 2)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, op.value + 0x0D]))
        with self.assertRaises(ValueError) as e:
            frame.parse(bytes([0x33, 0xCC, 0x00, 0x0E, op.value + 1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, op.value + 0x10]))

        self.assertEqual(str(e.exception), f"Answer operation does not match: {op.value + 1:02X}")

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter},
        {'op': Frame.Operation.GetRecord   },
    ])
    def testParseMissingData(self, op):
        frame = Frame(op, 0, 2)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, op.value + 0x0D]))
        with self.assertRaises(ValueError) as e:
            frame.parse(bytes([0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00]))

        self.assertEqual(str(e.exception), f"Anwser does not contain data: 12 < 13")

    @testdata.TestData([
        {'op': Frame.Operation.SetParameter, 'o': 0x0000, 'l': 1},
        {'op': Frame.Operation.SetParameter, 'o': 0x0001, 'l': 1},
        {'op': Frame.Operation.SetParameter, 'o': 0xFFFF, 'l': 1},
        {'op': Frame.Operation.SetParameter, 'o': 0x0000, 'l': 2},
        {'op': Frame.Operation.SetParameter, 'o': 0x0001, 'l': 2},
        {'op': Frame.Operation.SetParameter, 'o': 0xFFFF, 'l': 2},
        {'op': Frame.Operation.SetParameter, 'o': 0x0000, 'l': 3},
        {'op': Frame.Operation.SetParameter, 'o': 0x0001, 'l': 3},
        {'op': Frame.Operation.SetParameter, 'o': 0xFFFF, 'l': 3},
    ])
    def testParseSetParameterMissingData(self, op, o, l):
        frame = Frame(op, o, bytes(range(1, l + 1)))
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C + l, op.value, 0x00, 0x00, o >> 8, o & 0xFF, 0x00, l] + list(range(1, l + 1)) + [(op.value + (o >> 8) + (o & 0xFF) + 2*l + l*(l + 1)//2 + 0x0B) & 0xFF]))
        with self.assertRaises(ValueError) as e:
            frame.parse(bytes([0x33, 0xCC, 0x00, 0x0D, op.value, 0x00, 0x00, o >> 8, o & 0xFF, 0x00, 0x01]))

        self.assertEqual(str(e.exception), f"Anwser does not contain data: 11 < 12")

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter, 'o1': 0x0000, 'o2': 0x0001},
        {'op': Frame.Operation.GetParameter, 'o1': 0x0001, 'o2': 0x0000},
        {'op': Frame.Operation.GetParameter, 'o1': 0x00FF, 'o2': 0x00FE},
        {'op': Frame.Operation.GetParameter, 'o1': 0x00FE, 'o2': 0x00FF},
        {'op': Frame.Operation.GetParameter, 'o1': 0x0100, 'o2': 0x0000},
        {'op': Frame.Operation.GetParameter, 'o1': 0x0000, 'o2': 0x0100},
        {'op': Frame.Operation.GetParameter, 'o1': 0xFFFF, 'o2': 0x00FF},
        {'op': Frame.Operation.GetParameter, 'o1': 0x00FF, 'o2': 0xFFFF},
    ])
    def testParseGetParameterOffsetMismatch(self, op, o1, o2):
        frame = Frame(op, o1, 2)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, o1 >> 8, o1 & 0xFF, 0x00, 0x02, (op.value + (o1 >> 8) + (o1 & 0xFF) + 0x0D) & 0xFF]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0E, op.value, 0x00, 0x00, o2 >> 8, o2 & 0xFF, 0x00, 0x02, 0x00, 0x00, (op.value + (o2 >> 8) + (o2 & 0xFF) + 0x0F) & 0xFF]))

        self.assertEqual(str(w.warning), f"Answer offset does not match: {o2} != {o1}")

        self.assertEqual(answer.range.start, o2)
        self.assertEqual(answer.range.len, 2)
        self.assertEqual(answer.data, bytes([0x00, 0x00]))

    @testdata.TestData([
        {'op': Frame.Operation.SetParameter, 'o1': 0x0000, 'o2': 0x0001},
        {'op': Frame.Operation.SetParameter, 'o1': 0x0001, 'o2': 0x0000},
        {'op': Frame.Operation.SetParameter, 'o1': 0x00FF, 'o2': 0x00FE},
        {'op': Frame.Operation.SetParameter, 'o1': 0x00FE, 'o2': 0x00FF},
        {'op': Frame.Operation.SetParameter, 'o1': 0x0100, 'o2': 0x0000},
        {'op': Frame.Operation.SetParameter, 'o1': 0x0000, 'o2': 0x0100},
        {'op': Frame.Operation.SetParameter, 'o1': 0xFFFF, 'o2': 0x00FF},
        {'op': Frame.Operation.SetParameter, 'o1': 0x00FF, 'o2': 0xFFFF},
    ])
    def testParseSetParameterOffsetMismatch(self, op, o1, o2):
        frame = Frame(op, o1, b'\0')
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0D, op.value, 0x00, 0x00, o1 >> 8, o1 & 0xFF, 0x00, 0x01, 0x00, (op.value + (o1 >> 8) + (o1 & 0xFF) + 0x0D) & 0xFF]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0D, op.value, 0x00, 0x00, o2 >> 8, o2 & 0xFF, 0x00, 0x01, 0x01, (op.value + (o2 >> 8) + (o2 & 0xFF) + 0x0E) & 0xFF]))

        self.assertEqual(str(w.warning), f"Answer offset does not match: {o2} != {o1}")

        self.assertTrue(answer)

    @testdata.TestData([
        {'op': Frame.Operation.GetRecord,    'o1': 0x0000, 'o2': 0x0001},
        {'op': Frame.Operation.GetRecord,    'o1': 0x0001, 'o2': 0x0000},
        {'op': Frame.Operation.GetRecord,    'o1': 0x00FF, 'o2': 0x00FE},
        {'op': Frame.Operation.GetRecord,    'o1': 0x00FE, 'o2': 0x00FF},
        {'op': Frame.Operation.GetRecord,    'o1': 0x0100, 'o2': 0x0000},
        {'op': Frame.Operation.GetRecord,    'o1': 0x0000, 'o2': 0x0100},
        {'op': Frame.Operation.GetRecord,    'o1': 0xFFFF, 'o2': 0x00FF},
        {'op': Frame.Operation.GetRecord,    'o1': 0x00FF, 'o2': 0xFFFF},
    ])
    def testParseGetRecordOffsetMismatch(self, op, o1, o2):
        frame = Frame(op, o1, 2)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, o1 >> 8, o1 & 0xFF, 0x00, 0x02, (op.value + (o1 >> 8) + (o1 & 0xFF) + 0x0D) & 0xFF]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x1C, op.value, 0x00, 0x00, o2 >> 8, o2 & 0xFF, 0x00, 0x02] + [0x00]*16 + [(op.value + (o2 >> 8) + (o2 & 0xFF) + 0x0F) & 0xFF]))

        self.assertEqual(str(w.warning), f"Answer offset does not match: {o2} != {o1}")

        self.assertEqual(answer.range.start, 8*o2)
        self.assertEqual(answer.range.len, 16)
        self.assertEqual(answer.data, bytes([0x00]*16))

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter, 'l1': 0x02, 'l2': 0x03},
        {'op': Frame.Operation.GetParameter, 'l1': 0x03, 'l2': 0x02},
        {'op': Frame.Operation.GetParameter, 'l1': 0x33, 'l2': 0x32},
        {'op': Frame.Operation.GetParameter, 'l1': 0x32, 'l2': 0x33},
    ])
    def testParseGetParameterLengthMismatch(self, op, l1, l2):
        frame = Frame(op, 0, l1)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l1, (op.value + l1 + 0x0B) & 0xFF]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0C + l2, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l2] + [0x00]*l2 + [(op.value + 2*l2 + 0x0B) & 0xFF]))

        self.assertEqual(str(w.warning), f"Answer length does not match: {l2} != {l1}")

        self.assertEqual(answer.range.start, 0)
        self.assertEqual(answer.range.len, min(l1, l2))
        self.assertEqual(answer.data, bytes([0x00]*min(l1, l2)))

    @testdata.TestData([
        {'op': Frame.Operation.SetParameter, 'l': 0x02},
        {'op': Frame.Operation.SetParameter, 'l': 0x03},
    ])
    def testParseSetParameterLengthMismatch(self, op, l):
        frame = Frame(op, 0, bytes(range(1, l + 1)))
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C + l, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l] + list(range(1, l + 1)) + [(op.value + 2*l + l*(l + 1)//2 + 0x0B) & 0xFF]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0C + l, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l] + list(range(1, l + 1)) + [(op.value + 2*l + l*(l + 1)//2 + 0x0B) & 0xFF]))

        self.assertEqual(str(w.warning), f"Answer length does not match: {l} != 1")

        self.assertTrue(answer)

    @testdata.TestData([
        {'op': Frame.Operation.GetRecord, 'l1': 0x01, 'l2': 0x02},
        {'op': Frame.Operation.GetRecord, 'l1': 0x02, 'l2': 0x01},
        {'op': Frame.Operation.GetRecord, 'l1': 0x03, 'l2': 0x04},
        {'op': Frame.Operation.GetRecord, 'l1': 0x04, 'l2': 0x03},
        {'op': Frame.Operation.GetRecord, 'l1': 0x05, 'l2': 0x06},
        {'op': Frame.Operation.GetRecord, 'l1': 0x06, 'l2': 0x05},
    ])
    def testParseGetRecordLengthMismatch(self, op, l1, l2):
        frame = Frame(op, 0, l1)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l1, (op.value + l1 + 0x0B) & 0xFF]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0C + 8*l2, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l2] + [0x00]*(8*l2) + [(op.value + 9*l2 + 0x0B) & 0xFF]))

        self.assertEqual(str(w.warning), f"Answer length does not match: {l2} != {l1}")

        self.assertEqual(answer.range.start, 0)
        self.assertEqual(answer.range.len, 8*min(l1, l2))
        self.assertEqual(answer.data, bytes([0x00]*(8*min(l1, l2))))


    @testdata.TestData([
        {'op': Frame.Operation.GetParameter, 'l': 0x02},
        {'op': Frame.Operation.GetParameter, 'l': 0x03},
        {'op': Frame.Operation.GetParameter, 'l': 0x33},
        {'op': Frame.Operation.GetParameter, 'l': 0x32},
    ])
    def testParseGetParameterMissingChecksum(self, op, l):
        frame = Frame(op, 0, l)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l, (op.value + l + 0x0B) & 0xFF]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0C + l, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l] + [0x00]*l))

        self.assertEqual(str(w.warning), "Answer does not have a checksum")

        self.assertEqual(answer.range.start, 0)
        self.assertEqual(answer.range.len, l)
        self.assertEqual(answer.data, bytes([0x00]*l))

    def testParseSetParameterMissingChecksum(self):
        op = Frame.Operation.SetParameter
        frame = Frame(op, 0, b'\0')
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0D, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, (op.value + 0x0D) & 0xFF]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0D, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01]))

        self.assertEqual(str(w.warning), "Answer does not have a checksum")

        self.assertTrue(answer)

    @testdata.TestData([
        {'op': Frame.Operation.GetRecord, 'l': 0x01},
        {'op': Frame.Operation.GetRecord, 'l': 0x02},
        {'op': Frame.Operation.GetRecord, 'l': 0x03},
        {'op': Frame.Operation.GetRecord, 'l': 0x04},
        {'op': Frame.Operation.GetRecord, 'l': 0x05},
        {'op': Frame.Operation.GetRecord, 'l': 0x06},
    ])
    def testParseGetRecordMissingChecksum(self, op, l):
        frame = Frame(op, 0, l)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l, (op.value + l + 0x0B) & 0xFF]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0C + 8*l, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l] + [0x00]*(8*l)))

        self.assertEqual(str(w.warning), "Answer does not have a checksum")

        self.assertEqual(answer.range.start, 0)
        self.assertEqual(answer.range.len, 8*l)
        self.assertEqual(answer.data, bytes([0x00]*(8*l)))

    def testParseGetParameterInvalidChecksum(self):
        op = Frame.Operation.GetParameter
        frame = Frame(op, 0, 1)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, op.value + 0x0D]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0E, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, op.value + 0x10]))

        self.assertEqual(str(w.warning), f"Invalid answer checksum: {op.value + 0x10:02X} != {op.value + 0x0F:02X}")

        self.assertEqual(answer.range.start, 0)
        self.assertEqual(answer.range.len, 1)
        self.assertEqual(answer.data, bytes([0x00]))

    def testParseSetParameterInvalidChecksum(self):
        op = Frame.Operation.SetParameter
        frame = Frame(op, 0, b'\0')
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0D, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, op.value + 0x0D]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0D, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, op.value + 0x0F]))

        self.assertEqual(str(w.warning), f"Invalid answer checksum: {op.value + 0x0F:02X} != {op.value + 0x0E:02X}")

        self.assertTrue(answer)

    def testParseGetRecordInvalidChecksum(self):
        op = Frame.Operation.GetRecord
        frame = Frame(op, 0, 1)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, op.value + 0x0C]))
        with self.assertWarns(UserWarning) as w:
            answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x14, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01] + [0x00]*8 + [op.value + 0x15]))

        self.assertEqual(str(w.warning), f"Invalid answer checksum: {op.value + 0x15:02X} != {op.value + 0x14:02X}")

        self.assertEqual(answer.range.start, 0)
        self.assertEqual(answer.range.len, 8)
        self.assertEqual(answer.data, bytes([0x00]*8))

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter, 'l': 0x02},
        {'op': Frame.Operation.GetParameter, 'l': 0x03},
        {'op': Frame.Operation.GetParameter, 'l': 0x33},
        {'op': Frame.Operation.GetParameter, 'l': 0x32},
    ])
    def testParseGetParameterReadResponse(self, op, l):
        frame = Frame(op, 0, l)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l, (op.value + l + 0x0B) & 0xFF]))
        answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0C + l, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l] + [i for i in range(0, l)] + [(op.value + 2*l + ((l - 1)*l) // 2 + 0x0B) & 0xFF]))

        self.assertEqual(answer.range.start, 0)
        self.assertEqual(answer.range.len, l)
        self.assertEqual(answer.data, bytes([i for i in range(0, l)]))

    @testdata.TestData([
        {'op': Frame.Operation.GetParameter, 'offset': 0x0000},
        {'op': Frame.Operation.GetParameter, 'offset': 0x0001},
        {'op': Frame.Operation.GetParameter, 'offset': 0xFFFF},
    ])
    def testParseGetParameterRead1Response(self, op, offset):
        o = max(0, offset - 1)
        frame = Frame(op, offset, 1)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, o >> 8, o & 0xFF, 0x00, 0x02, (op.value + (o >> 8) + (o & 0xFF) + 0x0D) & 0xFF]))
        answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0E, op.value, 0x00, 0x00, o >> 8, o & 0xFF, 0x00, 0x02, 0xD1, 0xD2, (op.value + (o >> 8) + (o & 0xFF) + 0x1A3 + 0x0F) & 0xFF]))

        self.assertEqual(answer.range.start, offset)
        self.assertEqual(answer.range.len, 1)
        self.assertEqual(answer.data, bytes([0xD2 - int(offset == 0)]))

    @testdata.TestData([
        {'op': Frame.Operation.GetRecord, 'l': 0x01},
        {'op': Frame.Operation.GetRecord, 'l': 0x02},
        {'op': Frame.Operation.GetRecord, 'l': 0x03},
        {'op': Frame.Operation.GetRecord, 'l': 0x04},
        {'op': Frame.Operation.GetRecord, 'l': 0x05},
        {'op': Frame.Operation.GetRecord, 'l': 0x06},
    ])
    def testParseGetRecordReadResponse(self, op, l):
        frame = Frame(op, 0, l)
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l, (op.value + l + 0x0B) & 0xFF]))
        answer = frame.parse(bytes([0x33, 0xCC, 0x00, 0x0C + 8*l, op.value, 0x00, 0x00, 0x00, 0x00, 0x00, l] + [i for i in range(0, 8*l)] + [(op.value + 9*l + (8*l - 1)*4*l + 0x0B) & 0xFF]))

        self.assertEqual(answer.range.start, 0)
        self.assertEqual(answer.range.len, 8*l)
        self.assertEqual(answer.data, bytes([i for i in range(0, 8*l)]))

    @testdata.TestData([
        {'op': Frame.Operation.SetParameter, 'o': 0x0000, 'l': 1},
        {'op': Frame.Operation.SetParameter, 'o': 0x0001, 'l': 1},
        {'op': Frame.Operation.SetParameter, 'o': 0xFFFF, 'l': 1},
        {'op': Frame.Operation.SetParameter, 'o': 0x0000, 'l': 2},
        {'op': Frame.Operation.SetParameter, 'o': 0x0001, 'l': 2},
        {'op': Frame.Operation.SetParameter, 'o': 0xFFFF, 'l': 2},
        {'op': Frame.Operation.SetParameter, 'o': 0x0000, 'l': 3},
        {'op': Frame.Operation.SetParameter, 'o': 0x0001, 'l': 3},
        {'op': Frame.Operation.SetParameter, 'o': 0xFFFF, 'l': 3},
    ])
    def testParseSetParameterOK(self, op, o, l):
        frame = Frame(op, o, bytes(range(1, l + 1)))
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C + l, op.value, 0x00, 0x00, o >> 8, o & 0xFF, 0x00, l] + list(range(1, l + 1)) + [(op.value + (o >> 8) + (o & 0xFF) + 2*l + l*(l + 1)//2 + 0x0B) & 0xFF]))
        self.assertTrue(frame.parse(bytes([0x33, 0xCC, 0x00, 0x0D, op.value, 0x00, 0x00, o >> 8, o & 0xFF, 0x00, 0x01, 0x01, (op.value + (o >> 8) + (o & 0xFF) + 0x0E) & 0xFF])))

    @testdata.TestData([
        {'op': Frame.Operation.SetParameter, 'o': 0x0000, 'l': 1},
        {'op': Frame.Operation.SetParameter, 'o': 0x0001, 'l': 1},
        {'op': Frame.Operation.SetParameter, 'o': 0xFFFF, 'l': 1},
        {'op': Frame.Operation.SetParameter, 'o': 0x0000, 'l': 2},
        {'op': Frame.Operation.SetParameter, 'o': 0x0001, 'l': 2},
        {'op': Frame.Operation.SetParameter, 'o': 0xFFFF, 'l': 2},
        {'op': Frame.Operation.SetParameter, 'o': 0x0000, 'l': 3},
        {'op': Frame.Operation.SetParameter, 'o': 0x0001, 'l': 3},
        {'op': Frame.Operation.SetParameter, 'o': 0xFFFF, 'l': 3},
    ])
    def testParseSetParameterKO(self, op, o, l):
        frame = Frame(op, o, bytes(range(1, l + 1)))
        self.assertEqual(bytes(frame), bytes([0x00, 0x33, 0xCC, 0x00, 0x0C + l, op.value, 0x00, 0x00, o >> 8, o & 0xFF, 0x00, l] + list(range(1, l + 1)) + [(op.value + (o >> 8) + (o & 0xFF) + 2*l + l*(l + 1)//2 + 0x0B) & 0xFF]))
        self.assertFalse(frame.parse(bytes([0x33, 0xCC, 0x00, 0x0D, op.value, 0x00, 0x00, o >> 8, o & 0xFF, 0x00, 0x01, 0x00, (op.value + (o >> 8) + (o & 0xFF) + 0x0D) & 0xFF])))

