import unittest

from PythonUtils import testdata

from elitech.src.parameters import Range

class TestRange(unittest.TestCase):
    @testdata.TestData([
        {'s':      0, 'l':  0, 'e':      -1},
        {'s':      0, 'l':  1, 'e':       0},
        {'s':      0, 'l': 51, 'e':      50},
        {'s': 0xFFFF, 'l':  0, 'e':  0xFFFE},
        {'s': 0xFFFF, 'l':  1, 'e':  0xFFFF},
        {'s': 0xFFFF, 'l': 51, 'e': 0x10031},
    ])
    def testConstructor(self, s, l, e):
        range = Range(s, l)
        self.assertEqual(range.start, s)
        self.assertEqual(range.len, l)
        self.assertEqual(range.end, e)

    @testdata.TestData([
        {'s':      0},
        {'s': 0xFFFF},
    ])
    def testInvalidLength(self, s):
        with self.assertRaises(ValueError) as e:
            Range(s, -1)

        self.assertEqual(str(e.exception), f"Invalid range length: -1")

    @testdata.TestData([
        {'r1': Range(0, 0), 'r2': Range(0, 0), 'equals':  True},
        {'r1': Range(1, 0), 'r2': Range(0, 0), 'equals':  True},
        {'r1': Range(0, 0), 'r2': Range(1, 0), 'equals':  True},

        {'r1': Range(0, 1), 'r2': Range(0, 1), 'equals':  True},
        {'r1': Range(1, 1), 'r2': Range(1, 1), 'equals':  True},

        {'r1': Range(0, 0), 'r2': Range(0, 1), 'equals': False},
        {'r1': Range(0, 1), 'r2': Range(0, 0), 'equals': False},
        {'r1': Range(0, 2), 'r2': Range(0, 1), 'equals': False},
        {'r1': Range(0, 1), 'r2': Range(0, 2), 'equals': False},
        {'r1': Range(0, 2), 'r2': Range(1, 1), 'equals': False},
        {'r1': Range(1, 1), 'r2': Range(0, 2), 'equals': False},
        {'r1': Range(0, 3), 'r2': Range(1, 1), 'equals': False},
        {'r1': Range(1, 1), 'r2': Range(0, 3), 'equals': False},
    ])
    def testEquals(self, r1, r2, equals):
        self.assertEqual(r1 == r2, equals)

    @testdata.TestData([
        {'r': Range(0, 0), 'empty':  True},
        {'r': Range(1, 0), 'empty':  True},
        {'r': Range(0, 1), 'empty': False},
        {'r': Range(1, 1), 'empty': False},
    ])
    def testEmpty(self, r, empty):
        self.assertEqual(bool(r), empty)

    @testdata.TestData([
        {'r1': Range(0, 0), 'r2': Range(0, 0), 'contains':  True},
        {'r1': Range(1, 0), 'r2': Range(0, 0), 'contains':  True},
        {'r1': Range(0, 0), 'r2': Range(1, 0), 'contains':  True},

        {'r1': Range(0, 0), 'r2': Range(0, 1), 'contains': False},
        {'r1': Range(0, 0), 'r2': Range(1, 1), 'contains': False},

        {'r1': Range(0, 1), 'r2': Range(0, 0), 'contains':  True},
        {'r1': Range(0, 1), 'r2': Range(1, 0), 'contains':  True},

        {'r1': Range(0, 1), 'r2': Range(0, 1), 'contains':  True},
        {'r1': Range(0, 1), 'r2': Range(1, 1), 'contains': False},
        {'r1': Range(1, 1), 'r2': Range(0, 1), 'contains': False},

        {'r1': Range(0, 2), 'r2': Range(0, 2), 'contains':  True},
        {'r1': Range(0, 2), 'r2': Range(0, 1), 'contains':  True},
        {'r1': Range(0, 2), 'r2': Range(1, 1), 'contains':  True},
        {'r1': Range(0, 2), 'r2': Range(1, 2), 'contains': False},
        {'r1': Range(1, 2), 'r2': Range(0, 2), 'contains': False},
        {'r1': Range(1, 2), 'r2': Range(0, 3), 'contains': False},

        {'r1': Range(0, 3), 'r2': Range(0, 2), 'contains':  True},
        {'r1': Range(0, 3), 'r2': Range(1, 2), 'contains':  True},
        {'r1': Range(0, 3), 'r2': Range(1, 1), 'contains':  True},
    ])
    def testContains(self, r1, r2, contains):
        self.assertEqual(r2 in r1, contains)

    @testdata.TestData([
        {'r1': Range(0, 0), 'r2': Range(1, 0)},
        {'r1': Range(1, 0), 'r2': Range(0, 0)},

        {'r1': Range(0, 1), 'r2': Range(2, 1)},
        {'r1': Range(2, 1), 'r2': Range(0, 1)},
    ])
    def testInvalidMerge(self, r1, r2):
        with self.assertRaises(ValueError) as e:
            r1 | r2
        self.assertEqual(str(e.exception), f"Ranges {r1} and {r2} cannot be merged")

        with self.assertRaises(ValueError) as e:
            r1 |= r2
        self.assertEqual(str(e.exception), f"Ranges {r1} and {r2} cannot be merged")

    @testdata.TestData([
        {'r1': Range(0, 0), 'r2': Range(0, 0), 'r': Range(0, 0)},
        {'r1': Range(1, 0), 'r2': Range(1, 0), 'r': Range(1, 0)},

        {'r1': Range(0, 1), 'r2': Range(0, 1), 'r': Range(0, 1)},
        {'r1': Range(0, 1), 'r2': Range(1, 0), 'r': Range(0, 1)},
        {'r1': Range(1, 0), 'r2': Range(0, 1), 'r': Range(0, 1)},

        {'r1': Range(0, 1), 'r2': Range(1, 1), 'r': Range(0, 2)},
        {'r1': Range(1, 1), 'r2': Range(0, 1), 'r': Range(0, 2)},
        {'r1': Range(0, 2), 'r2': Range(0, 1), 'r': Range(0, 2)},
        {'r1': Range(0, 1), 'r2': Range(0, 2), 'r': Range(0, 2)},

        {'r1': Range(0, 2), 'r2': Range(1, 2), 'r': Range(0, 3)},
        {'r1': Range(1, 2), 'r2': Range(0, 2), 'r': Range(0, 3)},
        {'r1': Range(0, 3), 'r2': Range(1, 1), 'r': Range(0, 3)},
        {'r1': Range(1, 1), 'r2': Range(0, 3), 'r': Range(0, 3)},
    ])
    def testMerge(self, r1, r2, r):
        s1 = r1.start
        l1 = r1.len
        s2 = r2.start
        l2 = r2.len

        rm = r1 | r2

        self.assertEqual(rm.start, r.start)
        self.assertEqual(rm.len, r.len)
        self.assertEqual(r1.start, s1)
        self.assertEqual(r1.len, l1)
        self.assertEqual(r2.start, s2)
        self.assertEqual(r2.len, l2)

    @testdata.TestData([
        {'r1': Range(0, 0), 'r2': Range(0, 0), 'r': Range(0, 0)},
        {'r1': Range(1, 0), 'r2': Range(1, 0), 'r': Range(1, 0)},

        {'r1': Range(0, 1), 'r2': Range(0, 1), 'r': Range(0, 1)},
        {'r1': Range(0, 1), 'r2': Range(1, 0), 'r': Range(0, 1)},
        {'r1': Range(1, 0), 'r2': Range(0, 1), 'r': Range(0, 1)},

        {'r1': Range(0, 1), 'r2': Range(1, 1), 'r': Range(0, 2)},
        {'r1': Range(1, 1), 'r2': Range(0, 1), 'r': Range(0, 2)},
        {'r1': Range(0, 2), 'r2': Range(0, 1), 'r': Range(0, 2)},
        {'r1': Range(0, 1), 'r2': Range(0, 2), 'r': Range(0, 2)},

        {'r1': Range(0, 2), 'r2': Range(1, 2), 'r': Range(0, 3)},
        {'r1': Range(1, 2), 'r2': Range(0, 2), 'r': Range(0, 3)},
        {'r1': Range(0, 3), 'r2': Range(1, 1), 'r': Range(0, 3)},
        {'r1': Range(1, 1), 'r2': Range(0, 3), 'r': Range(0, 3)},
    ])
    def testMergeInPlace(self, r1, r2, r):
        s2 = r2.start
        l2 = r2.len

        r1 |= r2

        self.assertEqual(r1.start, r.start)
        self.assertEqual(r1.len, r.len)
        self.assertEqual(r2.start, s2)
        self.assertEqual(r2.len, l2)

    @testdata.TestData([
        {'r1': Range(0, 0), 'r2': Range(1, 0), 'r': Range(0, 0)},
        {'r1': Range(1, 0), 'r2': Range(0, 0), 'r': Range(0, 0)},

        {'r1': Range(0, 1), 'r2': Range(2, 1), 'r': Range(0, 0)},
        {'r1': Range(2, 1), 'r2': Range(0, 1), 'r': Range(0, 0)},

        {'r1': Range(0, 0), 'r2': Range(0, 0), 'r': Range(0, 0)},
        {'r1': Range(1, 0), 'r2': Range(1, 0), 'r': Range(1, 0)},

        {'r1': Range(0, 1), 'r2': Range(0, 1), 'r': Range(0, 1)},
        {'r1': Range(0, 1), 'r2': Range(1, 0), 'r': Range(1, 0)},
        {'r1': Range(1, 0), 'r2': Range(0, 1), 'r': Range(1, 0)},

        {'r1': Range(0, 1), 'r2': Range(1, 1), 'r': Range(1, 0)},
        {'r1': Range(1, 1), 'r2': Range(0, 1), 'r': Range(1, 0)},
        {'r1': Range(0, 2), 'r2': Range(0, 1), 'r': Range(0, 1)},
        {'r1': Range(0, 1), 'r2': Range(0, 2), 'r': Range(0, 1)},

        {'r1': Range(0, 2), 'r2': Range(1, 2), 'r': Range(1, 1)},
        {'r1': Range(1, 2), 'r2': Range(0, 2), 'r': Range(1, 1)},
        {'r1': Range(0, 3), 'r2': Range(1, 1), 'r': Range(1, 1)},
        {'r1': Range(1, 1), 'r2': Range(0, 3), 'r': Range(1, 1)},
    ])
    def testIntersect(self, r1, r2, r):
        s1 = r1.start
        l1 = r1.len
        s2 = r2.start
        l2 = r2.len

        ri = r1 & r2

        self.assertEqual(ri.start, r.start)
        self.assertEqual(ri.len, r.len)
        self.assertEqual(r1.start, s1)
        self.assertEqual(r1.len, l1)
        self.assertEqual(r2.start, s2)
        self.assertEqual(r2.len, l2)

    @testdata.TestData([
        {'r1': Range(0, 0), 'r2': Range(1, 0), 'r': Range(0, 0)},
        {'r1': Range(1, 0), 'r2': Range(0, 0), 'r': Range(0, 0)},

        {'r1': Range(0, 1), 'r2': Range(2, 1), 'r': Range(0, 0)},
        {'r1': Range(2, 1), 'r2': Range(0, 1), 'r': Range(0, 0)},

        {'r1': Range(0, 0), 'r2': Range(0, 0), 'r': Range(0, 0)},
        {'r1': Range(1, 0), 'r2': Range(1, 0), 'r': Range(1, 0)},

        {'r1': Range(0, 1), 'r2': Range(0, 1), 'r': Range(0, 1)},
        {'r1': Range(0, 1), 'r2': Range(1, 0), 'r': Range(1, 0)},
        {'r1': Range(1, 0), 'r2': Range(0, 1), 'r': Range(1, 0)},

        {'r1': Range(0, 1), 'r2': Range(1, 1), 'r': Range(1, 0)},
        {'r1': Range(1, 1), 'r2': Range(0, 1), 'r': Range(1, 0)},
        {'r1': Range(0, 2), 'r2': Range(0, 1), 'r': Range(0, 1)},
        {'r1': Range(0, 1), 'r2': Range(0, 2), 'r': Range(0, 1)},

        {'r1': Range(0, 2), 'r2': Range(1, 2), 'r': Range(1, 1)},
        {'r1': Range(1, 2), 'r2': Range(0, 2), 'r': Range(1, 1)},
        {'r1': Range(0, 3), 'r2': Range(1, 1), 'r': Range(1, 1)},
        {'r1': Range(1, 1), 'r2': Range(0, 3), 'r': Range(1, 1)},
    ])
    def testIntersectInPlace(self, r1, r2, r):
        s2 = r2.start
        l2 = r2.len

        r1 &= r2

        self.assertEqual(r1.start, r.start)
        self.assertEqual(r1.len, r.len)
        self.assertEqual(r2.start, s2)
        self.assertEqual(r2.len, l2)

    @testdata.TestData([
        {'r1': Range(0, 0), 'r2': Range(0, 0), 'ranges': [                        ]},
        {'r1': Range(1, 0), 'r2': Range(1, 0), 'ranges': [                        ]},
        {'r1': Range(0, 0), 'r2': Range(1, 0), 'ranges': [Range(0, 0)             ]},
        {'r1': Range(1, 0), 'r2': Range(0, 0), 'ranges': [Range(1, 0)             ]},
        {'r1': Range(0, 1), 'r2': Range(0, 0), 'ranges': [Range(0, 1)             ]},
        {'r1': Range(0, 1), 'r2': Range(1, 0), 'ranges': [Range(0, 1)             ]},
        {'r1': Range(0, 1), 'r2': Range(1, 1), 'ranges': [Range(0, 1)             ]},
        {'r1': Range(1, 1), 'r2': Range(0, 1), 'ranges': [Range(1, 1)             ]},
        {'r1': Range(0, 1), 'r2': Range(0, 1), 'ranges': [                        ]},
        {'r1': Range(0, 2), 'r2': Range(0, 0), 'ranges': [Range(0, 2)             ]},
        {'r1': Range(0, 2), 'r2': Range(1, 0), 'ranges': [Range(0, 1), Range(1, 1)]},
        {'r1': Range(0, 2), 'r2': Range(2, 0), 'ranges': [Range(0, 2)             ]},
        {'r1': Range(0, 2), 'r2': Range(0, 1), 'ranges': [Range(1, 1)             ]},
        {'r1': Range(0, 2), 'r2': Range(1, 1), 'ranges': [Range(0, 1)             ]},
        {'r1': Range(0, 2), 'r2': Range(1, 2), 'ranges': [Range(0, 1)             ]},
        {'r1': Range(1, 2), 'r2': Range(0, 2), 'ranges': [Range(2, 1)             ]},
        {'r1': Range(0, 2), 'r2': Range(0, 2), 'ranges': [                        ]},
        {'r1': Range(0, 3), 'r2': Range(1, 0), 'ranges': [Range(0, 1), Range(1, 2)]},
        {'r1': Range(0, 3), 'r2': Range(2, 0), 'ranges': [Range(0, 2), Range(2, 1)]},
        {'r1': Range(0, 3), 'r2': Range(1, 1), 'ranges': [Range(0, 1), Range(2, 1)]},
    ])
    def testSub(self, r1, r2, ranges):
        s1 = r1.start
        l1 = r1.len
        s2 = r2.start
        l2 = r2.len

        dr = r1 - r2

        self.assertEqual(len(dr), len(ranges))
        self.assertEqual([r.start for r in dr], [r.start for r in ranges])
        self.assertEqual([r.len for r in dr], [r.len for r in ranges])
        self.assertEqual(r1.start, s1)
        self.assertEqual(r1.len, l1)
        self.assertEqual(r2.start, s2)
        self.assertEqual(r2.len, l2)

    @testdata.TestData([
        {'s': '1',   'expectedRange': Range(0, 1)},
        {'s': '2',   'expectedRange': Range(1, 1)},
        {'s': '1-2', 'expectedRange': Range(0, 2)},
        {'s': '2-3', 'expectedRange': Range(1, 2)},
        {'s': '1-3', 'expectedRange': Range(0, 3)},
    ])
    def testFromString(self, s, expectedRange):
        self.assertEqual(Range.fromString(s), expectedRange)

    @testdata.TestData([
        {'s': '-1'   },
        {'s': '1-'   },
        {'s': '1-2-3'},
        {'s': '1-2-' },
        {'s': '-2-3' },
        {'s': '2-1'  },
    ])
    def testFromStringInvalid(self, s):
        with self.assertRaises(ValueError) as e:
            Range.fromString(s)

        self.assertEqual(str(e.exception), f"Invalid range: \"{s}\"")

    @testdata.TestData([
        {'ranges': [                        ], 'optimized': [                        ]},
        {'ranges': [Range(0, 1)             ], 'optimized': [Range(0, 1)             ]},
        {'ranges': [Range(0, 1), Range(2, 1)], 'optimized': [Range(0, 1), Range(2, 1)]},
        {'ranges': [Range(2, 1), Range(0, 1)], 'optimized': [Range(0, 1), Range(2, 1)]},
        {'ranges': [Range(0, 1), Range(1, 1)], 'optimized': [Range(0, 2)             ]},
        {'ranges': [Range(1, 1), Range(0, 1)], 'optimized': [Range(0, 2)             ]},
        {'ranges': [Range(0, 2), Range(1, 2)], 'optimized': [Range(0, 3)             ]},
        {'ranges': [Range(1, 2), Range(0, 2)], 'optimized': [Range(0, 3)             ]},
        {'ranges': [Range(0, 3), Range(1, 1)], 'optimized': [Range(0, 3)             ]},
        {'ranges': [Range(1, 1), Range(0, 3)], 'optimized': [Range(0, 3)             ]},
    ])
    def testOptimize(self, ranges, optimized):
        original = [r for r in ranges]
        self.assertEqual(Range.optimize(ranges), optimized)
        self.assertEqual(ranges, original)

