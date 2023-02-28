import unittest

from PythonUtils import testdata

from elitech.src.parameters import Range
from elitech.src.frames     import Response

class TestResponse(unittest.TestCase):
    @testdata.TestData([
        {'r': Range(0, 0), 'data': bytes([          ])},
        {'r': Range(1, 0), 'data': bytes([          ])},
        {'r': Range(0, 1), 'data': bytes([0x18      ])},
        {'r': Range(1, 1), 'data': bytes([0x18      ])},
        {'r': Range(0, 2), 'data': bytes([0x18, 0x18])},
        {'r': Range(1, 2), 'data': bytes([0x18, 0x18])},
    ])
    def testConstructor(self, r, data):
        response = Response(r, data)
        self.assertEqual(response.range, r)
        self.assertEqual(response.data, data)

    @testdata.TestData([
        {'r': Range(0, 1), 'data': bytes([          ])},
        {'r': Range(1, 1), 'data': bytes([          ])},
        {'r': Range(0, 0), 'data': bytes([0x18      ])},
        {'r': Range(1, 0), 'data': bytes([0x18      ])},
        {'r': Range(0, 2), 'data': bytes([0x18      ])},
        {'r': Range(1, 2), 'data': bytes([0x18      ])},
        {'r': Range(0, 1), 'data': bytes([0x18, 0x18])},
        {'r': Range(1, 1), 'data': bytes([0x18, 0x18])},
    ])
    def testInvalidConstructor(self, r, data):
        with self.assertRaises(ValueError) as e:
            Response(r, data)

        self.assertEqual(str(e.exception), f"Range and data lengths do not match: {len(data)} != {r.len}")

    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([          ])), 'range': Range(0, 0), 'data': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([          ])), 'range': Range(1, 0), 'data': bytes([          ])},
        {'response': Response(Range(1, 0), bytes([          ])), 'range': Range(0, 0), 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(0, 0), 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(1, 0), 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(2, 0), 'data': bytes([          ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(0, 0), 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(0, 1), 'data': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(1, 1), 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range': Range(0, 1), 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range': Range(1, 1), 'data': bytes([0x02      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range': Range(0, 2), 'data': bytes([0x01, 0x02])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range':           0, 'data': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range':           1, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range':           0, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range':           1, 'data': bytes([0x02      ])},
    ])
    def testGetItem(self, response, range, data):
        self.assertEqual(response[range], data)

    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([          ])), 'range': Range(0, 1)},
        {'response': Response(Range(1, 0), bytes([          ])), 'range': Range(1, 1)},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(1, 1)},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(0, 2)},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(0, 1)},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(0, 2)},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(1, 2)},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(0, 3)},
    ])
    def testGetInvalidItem(self, response, range):
        with self.assertRaises(ValueError) as e:
            response[range]

        self.assertEqual(str(e.exception), f"Required range {range} is not in available range {response.range}")

    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([          ])), 'range': Range(0, 0), 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([          ])), 'range': Range(1, 0), 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(1, 0), bytes([          ])), 'range': Range(0, 0), 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(0, 0), 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(1, 0), 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(2, 0), 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(0, 0), 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(0, 1), 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(1, 1), 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range': Range(0, 1), 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF, 0x02])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range': Range(1, 1), 'data': bytes([0xFE      ]), 'expectedData': bytes([0x01, 0xFE])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range': Range(0, 2), 'data': bytes([0xFF, 0xFE]), 'expectedData': bytes([0xFF, 0xFE])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range':           0, 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range':           1, 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range':           0, 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF, 0x02])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range':           1, 'data': bytes([0xFE      ]), 'expectedData': bytes([0x01, 0xFE])},
    ])
    def testSetItem(self, response, range, data, expectedData):
        response[range] = data
        self.assertEqual(response[range], data)
        self.assertEqual(response.data, expectedData)

    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([          ])), 'start': 0, 'end': 0, 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([          ])), 'start': 1, 'end': 1, 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(1, 0), bytes([          ])), 'start': 0, 'end': 0, 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start': 0, 'end': 0, 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start': 1, 'end': 1, 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start': 2, 'end': 2, 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'start': 0, 'end': 0, 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start': 0, 'end': 1, 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'start': 1, 'end': 2, 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'start': 0, 'end': 1, 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF, 0x02])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'start': 1, 'end': 2, 'data': bytes([0xFE      ]), 'expectedData': bytes([0x01, 0xFE])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'start': 0, 'end': 2, 'data': bytes([0xFF, 0xFE]), 'expectedData': bytes([0xFF, 0xFE])},
    ])
    def testSetItemSlice(self, response, start, end, data, expectedData):
        response[start:end] = data
        self.assertEqual(response[start:end], data)
        self.assertEqual(response.data, expectedData)

    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([          ])), 'end': 0, 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(1, 0), bytes([          ])), 'end': 0, 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'end': 0, 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'end': 0, 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'end': 1, 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'end': 1, 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF, 0x02])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'end': 2, 'data': bytes([0xFF, 0xFE]), 'expectedData': bytes([0xFF, 0xFE])},
    ])
    def testSetItemSliceNoStart(self, response, end, data, expectedData):
        response[:end] = data
        self.assertEqual(response[:end], data)
        self.assertEqual(response.data, expectedData)


    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([          ])), 'start': 0, 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([          ])), 'start': 1, 'data': bytes([          ]), 'expectedData': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start': 1, 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start': 2, 'data': bytes([          ]), 'expectedData': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start': 0, 'data': bytes([0xFF      ]), 'expectedData': bytes([0xFF      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'start': 1, 'data': bytes([0xFE      ]), 'expectedData': bytes([0x01, 0xFE])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'start': 0, 'data': bytes([0xFF, 0xFE]), 'expectedData': bytes([0xFF, 0xFE])},
    ])
    def testSetItemSliceNoEnd(self, response, start, data, expectedData):
        response[start:] = data
        self.assertEqual(response[start:], data)
        self.assertEqual(response.data, expectedData)

    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([          ])), 'range': Range(0, 1)},
        {'response': Response(Range(1, 0), bytes([          ])), 'range': Range(1, 1)},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(1, 1)},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(0, 2)},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(0, 1)},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(0, 2)},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(1, 2)},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'range': Range(0, 3)},
    ])
    def testSetInvalidItem(self, response, range):
        with self.assertRaises(ValueError) as e:
            response[range] = [0x0]*range.len

        self.assertEqual(str(e.exception), f"Required range {range} is not in available range {response.range}")

    @testdata.TestData([
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'range': Range(0, 0), 'data': bytes([0xFF      ])},
        {'response': Response(Range(1, 1), bytes([0x02      ])), 'range': Range(1, 1), 'data': bytes([          ])},
        {'response': Response(Range(1, 1), bytes([0x02      ])), 'range': Range(1, 1), 'data': bytes([0xFF, 0xFE])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'range': Range(0, 2), 'data': bytes([0xFF      ])},
    ])
    def testSetInvalidRange(self, response, range, data):
        with self.assertRaises(ValueError) as e:
            response[range] = data

        self.assertEqual(str(e.exception), f"Length of {range} does not match data length: {len(data)}")

    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([                ])), 'start':  0, 'end':  0, 'data': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([                ])), 'start':  1, 'end':  1, 'data': bytes([          ])},
        {'response': Response(Range(1, 0), bytes([                ])), 'start':  0, 'end':  0, 'data': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([                ])), 'start': -1, 'end': -1, 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01            ])), 'start':  0, 'end':  0, 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01            ])), 'start':  0, 'end': -1, 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01            ])), 'start':  1, 'end':  1, 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01            ])), 'start':  2, 'end':  2, 'data': bytes([          ])},
        {'response': Response(Range(1, 1), bytes([0x01            ])), 'start':  0, 'end':  0, 'data': bytes([          ])},
        {'response': Response(Range(1, 1), bytes([0x01            ])), 'start': -1, 'end':  0, 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01            ])), 'start':  0, 'end':  1, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01            ])), 'start': -1, 'end':  1, 'data': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01            ])), 'start':  1, 'end':  2, 'data': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01            ])), 'start': -1, 'end':  2, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'start':  0, 'end':  1, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'start':  0, 'end': -1, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'start': -2, 'end':  1, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'start': -1, 'end':  2, 'data': bytes([0x02      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'start':  1, 'end':  2, 'data': bytes([0x02      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'start':  1, 'end': -1, 'data': bytes([          ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'start':  0, 'end':  2, 'data': bytes([0x01, 0x02])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'start': -2, 'end':  2, 'data': bytes([0x01, 0x02])},
        {'response': Response(Range(0, 3), bytes([0x01, 0x02, 0x03])), 'start':  0, 'end': -1, 'data': bytes([0x01, 0x02])},
    ])
    def testGetSlice(self, response, start, end, data):
        self.assertEqual(response[start:end], data)

    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([                ])), 'end':  0, 'data': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([                ])), 'end':  1, 'data': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([                ])), 'end': -1, 'data': bytes([          ])},
        {'response': Response(Range(1, 0), bytes([                ])), 'end':  0, 'data': bytes([          ])},
        {'response': Response(Range(1, 1), bytes([0x01            ])), 'end':  0, 'data': bytes([          ])},
        {'response': Response(Range(1, 1), bytes([0x01            ])), 'end': -1, 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01            ])), 'end':  1, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01            ])), 'end':  2, 'data': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01            ])), 'end':  2, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'end':  1, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'end': -1, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'end':  2, 'data': bytes([0x01, 0x02])},
        {'response': Response(Range(0, 3), bytes([0x01, 0x02, 0x03])), 'end': -1, 'data': bytes([0x01, 0x02])},
    ])
    def testGetSliceNoStart(self, response, end, data):
        self.assertEqual(response[:end], data)

    @testdata.TestData([
        {'response': Response(Range(0, 0), bytes([          ])), 'start':  0, 'data': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([          ])), 'start':  1, 'data': bytes([          ])},
        {'response': Response(Range(0, 0), bytes([          ])), 'start': -1, 'data': bytes([          ])},
        {'response': Response(Range(1, 0), bytes([          ])), 'start':  0, 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start':  1, 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start':  2, 'data': bytes([          ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start':  0, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 1), bytes([0x01      ])), 'start': -1, 'data': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'start':  0, 'data': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'start':  1, 'data': bytes([0x01      ])},
        {'response': Response(Range(1, 1), bytes([0x01      ])), 'start': -1, 'data': bytes([0x01      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'start':  1, 'data': bytes([0x02      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'start': -1, 'data': bytes([0x02      ])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'start':  0, 'data': bytes([0x01, 0x02])},
        {'response': Response(Range(0, 2), bytes([0x01, 0x02])), 'start': -2, 'data': bytes([0x01, 0x02])},
    ])
    def testGetSliceNoEnd(self, response, start, data):
        self.assertEqual(response[start:], data)

    @testdata.TestData([
        {'r1': Response(Range(0, 0), bytes([    ])), 'r2': Response(Range(1, 0), bytes([    ]))},
        {'r1': Response(Range(1, 0), bytes([    ])), 'r2': Response(Range(0, 0), bytes([    ]))},

        {'r1': Response(Range(0, 1), bytes([0x01])), 'r2': Response(Range(2, 1), bytes([0x01]))},
        {'r1': Response(Range(2, 1), bytes([0x01])), 'r2': Response(Range(0, 1), bytes([0x01]))},
    ])
    def testInvalidMerge(self, r1, r2):
        s1 = r1.range.start
        l1 = r1.range.len
        d1 = r1.data

        s2 = r2.range.start
        l2 = r2.range.len
        d2 = r2.data

        with self.assertRaises(ValueError) as e:
            r1 += r2
        self.assertEqual(str(e.exception), f"Ranges {r1.range} and {r2.range} cannot be merged")

        self.assertEqual(r1.range.start, s1)
        self.assertEqual(r1.range.len, l1)
        self.assertEqual(r1.data, d1)
        self.assertEqual(r2.range.start, s2)
        self.assertEqual(r2.range.len, l2)
        self.assertEqual(r2.data, d2)

    @testdata.TestData([
        {'r1': Response(Range(0, 0), bytes([                ])), 'r2': Response(Range(0, 0), bytes([                ])), 'r': Response(Range(0, 0), bytes([                ]))},
        {'r1': Response(Range(1, 0), bytes([                ])), 'r2': Response(Range(1, 0), bytes([                ])), 'r': Response(Range(1, 0), bytes([                ]))},

        {'r1': Response(Range(0, 1), bytes([0x01            ])), 'r2': Response(Range(0, 1), bytes([0x01            ])), 'r': Response(Range(0, 1), bytes([0x01            ]))},
        {'r1': Response(Range(0, 1), bytes([0x01            ])), 'r2': Response(Range(1, 0), bytes([                ])), 'r': Response(Range(0, 1), bytes([0x01            ]))},
        {'r1': Response(Range(1, 0), bytes([                ])), 'r2': Response(Range(0, 1), bytes([0x01            ])), 'r': Response(Range(0, 1), bytes([0x01            ]))},

        {'r1': Response(Range(0, 1), bytes([0x01            ])), 'r2': Response(Range(1, 1), bytes([0x02            ])), 'r': Response(Range(0, 2), bytes([0x01, 0x02      ]))},
        {'r1': Response(Range(1, 1), bytes([0x02            ])), 'r2': Response(Range(0, 1), bytes([0x01            ])), 'r': Response(Range(0, 2), bytes([0x01, 0x02      ]))},
        {'r1': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'r2': Response(Range(0, 1), bytes([0x01            ])), 'r': Response(Range(0, 2), bytes([0x01, 0x02      ]))},
        {'r1': Response(Range(0, 1), bytes([0x01            ])), 'r2': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'r': Response(Range(0, 2), bytes([0x01, 0x02      ]))},

        {'r1': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'r2': Response(Range(1, 2), bytes([0x02, 0x03      ])), 'r': Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))},
        {'r1': Response(Range(1, 2), bytes([0x02, 0x03      ])), 'r2': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'r': Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))},
        {'r1': Response(Range(0, 3), bytes([0x01, 0x02, 0x03])), 'r2': Response(Range(1, 1), bytes([0x02            ])), 'r': Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))},
        {'r1': Response(Range(1, 1), bytes([0x02            ])), 'r2': Response(Range(0, 3), bytes([0x01, 0x02, 0x03])), 'r': Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))},
    ])
    def testMergeInPlace(self, r1, r2, r):
        s2 = r2.range.start
        l2 = r2.range.len
        d2 = r2.data

        r1 += r2

        self.assertEqual(r1.range, r.range)
        self.assertEqual(r1.data, r.data)
        self.assertEqual(r2.range.start, s2)
        self.assertEqual(r2.range.len, l2)
        self.assertEqual(r2.data, d2)

    @testdata.TestData([
        {'r1': Response(Range(0, 1), bytes([0x01            ])), 'r2': Response(Range(0, 1), bytes([0xFF            ])), 'r': Response(Range(0, 1), bytes([0x01            ]))},

        {'r1': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'r2': Response(Range(0, 1), bytes([0xFF            ])), 'r': Response(Range(0, 2), bytes([0x01, 0x02      ]))},
        {'r1': Response(Range(0, 1), bytes([0x01            ])), 'r2': Response(Range(0, 2), bytes([0xFF, 0x02      ])), 'r': Response(Range(0, 2), bytes([0x01, 0x02      ]))},

        {'r1': Response(Range(0, 2), bytes([0x01, 0x02      ])), 'r2': Response(Range(1, 2), bytes([0xFF, 0x03      ])), 'r': Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))},
        {'r1': Response(Range(1, 2), bytes([0x02, 0x03      ])), 'r2': Response(Range(0, 2), bytes([0x01, 0xFF      ])), 'r': Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))},
        {'r1': Response(Range(0, 3), bytes([0x01, 0x02, 0x03])), 'r2': Response(Range(1, 1), bytes([0xFF            ])), 'r': Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))},
        {'r1': Response(Range(1, 1), bytes([0x02            ])), 'r2': Response(Range(0, 3), bytes([0x01, 0xFF, 0x03])), 'r': Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))},
    ])
    def testMergeInPlaceMismatch(self, r1, r2, r):
        s2 = r2.range.start
        l2 = r2.range.len
        d2 = r2.data

        with self.assertWarns(UserWarning) as w:
            r1 += r2
        self.assertEqual(str(w.warning), "Data mismatch, new overlapping data will be ignored")

        self.assertEqual(r1.range, r.range)
        self.assertEqual(r1.data, r.data)
        self.assertEqual(r2.range.start, s2)
        self.assertEqual(r2.range.len, l2)
        self.assertEqual(r2.data, d2)

    @testdata.TestData([
        {'list': [Response(Range(0, 0), bytes([                ]))                                                  ], 'merged': [Response(Range(0, 0), bytes([                ]))]},
        {'list': [Response(Range(0, 1), bytes([0x01            ])), Response(Range(1, 0), bytes([                ]))], 'merged': [Response(Range(0, 1), bytes([0x01            ]))]},
        {'list': [Response(Range(1, 0), bytes([                ])), Response(Range(0, 1), bytes([0x01            ]))], 'merged': [Response(Range(0, 1), bytes([0x01            ]))]},
        {'list': [Response(Range(0, 1), bytes([0x01            ])), Response(Range(0, 1), bytes([0x01            ]))], 'merged': [Response(Range(0, 1), bytes([0x01            ]))]},
        {'list': [Response(Range(0, 1), bytes([0x01            ])), Response(Range(1, 1), bytes([0x02            ]))], 'merged': [Response(Range(0, 2), bytes([0x01, 0x02      ]))]},
        {'list': [Response(Range(1, 1), bytes([0x02            ])), Response(Range(0, 1), bytes([0x01            ]))], 'merged': [Response(Range(0, 2), bytes([0x01, 0x02      ]))]},
        {'list': [Response(Range(0, 2), bytes([0x01, 0x02      ])), Response(Range(0, 1), bytes([0x01            ]))], 'merged': [Response(Range(0, 2), bytes([0x01, 0x02      ]))]},
        {'list': [Response(Range(0, 2), bytes([0x01, 0x02      ])), Response(Range(1, 1), bytes([0x02            ]))], 'merged': [Response(Range(0, 2), bytes([0x01, 0x02      ]))]},
        {'list': [Response(Range(0, 1), bytes([0x01            ])), Response(Range(0, 2), bytes([0x01, 0x02      ]))], 'merged': [Response(Range(0, 2), bytes([0x01, 0x02      ]))]},
        {'list': [Response(Range(1, 1), bytes([0x02            ])), Response(Range(0, 2), bytes([0x01, 0x02      ]))], 'merged': [Response(Range(0, 2), bytes([0x01, 0x02      ]))]},
        {'list': [Response(Range(0, 3), bytes([0x01, 0x02, 0x03])), Response(Range(1, 1), bytes([0x02            ]))], 'merged': [Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))]},
        {'list': [Response(Range(1, 1), bytes([0x02            ])), Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))], 'merged': [Response(Range(0, 3), bytes([0x01, 0x02, 0x03]))]},

        {'list': [Response(Range(0, 0), bytes([    ])), Response(Range(1, 0), bytes([    ]))], 'merged': [Response(Range(0, 0), bytes([    ])), Response(Range(1, 0), bytes([    ]))]},
        {'list': [Response(Range(1, 0), bytes([    ])), Response(Range(0, 0), bytes([    ]))], 'merged': [Response(Range(0, 0), bytes([    ])), Response(Range(1, 0), bytes([    ]))]},
        {'list': [Response(Range(0, 1), bytes([0x01])), Response(Range(2, 0), bytes([    ]))], 'merged': [Response(Range(0, 1), bytes([0x01])), Response(Range(2, 0), bytes([    ]))]},
        {'list': [Response(Range(2, 0), bytes([    ])), Response(Range(0, 1), bytes([0x01]))], 'merged': [Response(Range(0, 1), bytes([0x01])), Response(Range(2, 0), bytes([    ]))]},
        {'list': [Response(Range(0, 0), bytes([    ])), Response(Range(1, 1), bytes([0x02]))], 'merged': [Response(Range(0, 0), bytes([    ])), Response(Range(1, 1), bytes([0x02]))]},
        {'list': [Response(Range(1, 1), bytes([0x02])), Response(Range(0, 0), bytes([    ]))], 'merged': [Response(Range(0, 0), bytes([    ])), Response(Range(1, 1), bytes([0x02]))]},
        {'list': [Response(Range(0, 1), bytes([0x01])), Response(Range(2, 1), bytes([0x03]))], 'merged': [Response(Range(0, 1), bytes([0x01])), Response(Range(2, 1), bytes([0x03]))]},
        {'list': [Response(Range(2, 1), bytes([0x03])), Response(Range(0, 1), bytes([0x01]))], 'merged': [Response(Range(0, 1), bytes([0x01])), Response(Range(2, 1), bytes([0x03]))]},
    ])
    def testMergeList(self, list, merged):
        self.assertEqual(Response.merge(list), merged)
