import unittest

from PythonUtils import testdata

from elitech.src.record import Record

from datetime import datetime

class TestRecord(unittest.TestCase):
    @testdata.TestData([
        {'frame': '00 E8 96 D0 D5 19 23 00', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature':  20.6, 'humidity':  None, 'flags': Record.Flags.Zero                                           },
        {'frame': '01 20 96 D0 B5 19 24 00', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature':  20.5, 'humidity':  None, 'flags': Record.Flags.Mark                                           },
        {'frame': '02 48 96 D0 95 19 24 00', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature':  20.4, 'humidity':  None, 'flags': Record.Flags.Pause                                          },
        {'frame': '04 70 96 D0 55 19 24 00', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature':  20.2, 'humidity':  None, 'flags': Record.Flags.Stop                                           },
        {'frame': '10 98 96 D0 35 19 24 00', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature':  20.1, 'humidity':  None, 'flags': Record.Flags.Light                                          },
        {'frame': '20 C0 96 D0 F5 18 24 00', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature':  19.9, 'humidity':  None, 'flags': Record.Flags.Vibr                                           },
        {'frame': '80 E8 96 D0 D5 18 24 00', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature':  19.8, 'humidity':  None, 'flags': Record.Flags.Error                                          },

        {'frame': '00 E8 96 D0 D5 19 E3 31', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature':  20.6, 'humidity':  19.9, 'flags': Record.Flags.Zero                                           },
        {'frame': '01 20 96 D0 B5 19 64 32', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature':  20.5, 'humidity':  20.1, 'flags': Record.Flags.Mark                                           },
        {'frame': '02 48 96 D0 95 19 A4 32', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature':  20.4, 'humidity':  20.2, 'flags': Record.Flags.Pause                                          },
        {'frame': '04 70 96 D0 55 19 24 33', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature':  20.2, 'humidity':  20.4, 'flags': Record.Flags.Stop                                           },
        {'frame': '10 98 96 D0 35 19 64 33', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature':  20.1, 'humidity':  20.5, 'flags': Record.Flags.Light                                          },
        {'frame': '20 C0 96 D0 F5 18 A4 33', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature':  19.9, 'humidity':  20.6, 'flags': Record.Flags.Vibr                                           },
        {'frame': '80 E8 96 D0 D5 18 E4 33', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature':  19.8, 'humidity':  20.7, 'flags': Record.Flags.Error                                          },

        {'frame': '08 E8 96 D0 D5 19 E3 31', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': -20.6, 'humidity':  19.9, 'flags': Record.Flags.Sign1                                          },
        {'frame': '09 20 96 D0 B5 19 64 32', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature': -20.5, 'humidity':  20.1, 'flags': Record.Flags.Sign1 | Record.Flags.Mark                      },
        {'frame': '0A 48 96 D0 95 19 A4 32', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature': -20.4, 'humidity':  20.2, 'flags': Record.Flags.Sign1 | Record.Flags.Pause                     },
        {'frame': '0C 70 96 D0 55 19 24 33', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature': -20.2, 'humidity':  20.4, 'flags': Record.Flags.Sign1 | Record.Flags.Stop                      },
        {'frame': '18 98 96 D0 35 19 64 33', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature': -20.1, 'humidity':  20.5, 'flags': Record.Flags.Sign1 | Record.Flags.Light                     },
        {'frame': '28 C0 96 D0 F5 18 A4 33', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature': -19.9, 'humidity':  20.6, 'flags': Record.Flags.Sign1 | Record.Flags.Vibr                      },
        {'frame': '88 E8 96 D0 D5 18 E4 33', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature': -19.8, 'humidity':  20.7, 'flags': Record.Flags.Sign1 | Record.Flags.Error                     },

        {'frame': '48 E8 96 D0 D5 19 E3 31', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': -20.6, 'humidity': -19.9, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2                     },
        {'frame': '49 20 96 D0 B5 19 64 32', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature': -20.5, 'humidity': -20.1, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Mark },
        {'frame': '4A 48 96 D0 95 19 A4 32', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature': -20.4, 'humidity': -20.2, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Pause},
        {'frame': '4C 70 96 D0 55 19 24 33', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature': -20.2, 'humidity': -20.4, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Stop },
        {'frame': '58 98 96 D0 35 19 64 33', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature': -20.1, 'humidity': -20.5, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Light},
        {'frame': '68 C0 96 D0 F5 18 A4 33', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature': -19.9, 'humidity': -20.6, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Vibr },
        {'frame': 'C8 E8 96 D0 D5 18 E4 33', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature': -19.8, 'humidity': -20.7, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Error},

        {'frame': '40 E8 96 D0 D5 19 E3 31', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature':  20.6, 'humidity': -19.9, 'flags': Record.Flags.Sign2                                          },
        {'frame': '41 20 96 D0 B5 19 64 32', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature':  20.5, 'humidity': -20.1, 'flags': Record.Flags.Sign2 | Record.Flags.Mark                      },
        {'frame': '42 48 96 D0 95 19 A4 32', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature':  20.4, 'humidity': -20.2, 'flags': Record.Flags.Sign2 | Record.Flags.Pause                     },
        {'frame': '44 70 96 D0 55 19 24 33', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature':  20.2, 'humidity': -20.4, 'flags': Record.Flags.Sign2 | Record.Flags.Stop                      },
        {'frame': '50 98 96 D0 35 19 64 33', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature':  20.1, 'humidity': -20.5, 'flags': Record.Flags.Sign2 | Record.Flags.Light                     },
        {'frame': '60 C0 96 D0 F5 18 A4 33', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature':  19.9, 'humidity': -20.6, 'flags': Record.Flags.Sign2 | Record.Flags.Vibr                      },
        {'frame': 'C0 E8 96 D0 D5 18 E4 33', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature':  19.8, 'humidity': -20.7, 'flags': Record.Flags.Sign2 | Record.Flags.Error                     },
    ])
    def testParse(self, frame, t, temperature, humidity, flags):
        r = Record.parse(bytes([int(b, 16) for b in frame.split(' ')]))
        self.assertEqual(r.time, t)
        self.assertEqual(r.temperature, temperature)
        self.assertEqual(r.humidity, humidity)
        self.assertEqual(r.flags, flags)

    @testdata.TestData([
        {'frame': '00 EA 96 D0 D5 19 23 00', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature':  123.0, 'humidity':  None, 'flags': Record.Flags.Zero                                           },
        {'frame': '01 22 96 D0 B5 19 24 00', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature':  122.9, 'humidity':  None, 'flags': Record.Flags.Mark                                           },
        {'frame': '02 4A 96 D0 95 19 24 00', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature':  122.8, 'humidity':  None, 'flags': Record.Flags.Pause                                          },
        {'frame': '04 72 96 D0 55 19 24 00', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature':  122.6, 'humidity':  None, 'flags': Record.Flags.Stop                                           },
        {'frame': '10 9A 96 D0 35 19 24 00', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature':  122.5, 'humidity':  None, 'flags': Record.Flags.Light                                          },
        {'frame': '20 C2 96 D0 F5 18 24 00', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature':  122.3, 'humidity':  None, 'flags': Record.Flags.Vibr                                           },
        {'frame': '80 EA 96 D0 D5 18 24 00', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature':  122.2, 'humidity':  None, 'flags': Record.Flags.Error                                          },

        {'frame': '00 EA 96 D0 D5 19 E3 31', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature':  123.0, 'humidity':  19.9, 'flags': Record.Flags.Zero                                           },
        {'frame': '01 22 96 D0 B5 19 64 32', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature':  122.9, 'humidity':  20.1, 'flags': Record.Flags.Mark                                           },
        {'frame': '02 4A 96 D0 95 19 A4 32', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature':  122.8, 'humidity':  20.2, 'flags': Record.Flags.Pause                                          },
        {'frame': '04 72 96 D0 55 19 24 33', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature':  122.6, 'humidity':  20.4, 'flags': Record.Flags.Stop                                           },
        {'frame': '10 9A 96 D0 35 19 64 33', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature':  122.5, 'humidity':  20.5, 'flags': Record.Flags.Light                                          },
        {'frame': '20 C2 96 D0 F5 18 A4 33', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature':  122.3, 'humidity':  20.6, 'flags': Record.Flags.Vibr                                           },
        {'frame': '80 EA 96 D0 D5 18 E4 33', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature':  122.2, 'humidity':  20.7, 'flags': Record.Flags.Error                                          },

        {'frame': '08 EA 96 D0 D5 19 E3 31', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': -123.0, 'humidity':  19.9, 'flags': Record.Flags.Sign1                                          },
        {'frame': '09 22 96 D0 B5 19 64 32', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature': -122.9, 'humidity':  20.1, 'flags': Record.Flags.Sign1 | Record.Flags.Mark                      },
        {'frame': '0A 4A 96 D0 95 19 A4 32', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature': -122.8, 'humidity':  20.2, 'flags': Record.Flags.Sign1 | Record.Flags.Pause                     },
        {'frame': '0C 72 96 D0 55 19 24 33', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature': -122.6, 'humidity':  20.4, 'flags': Record.Flags.Sign1 | Record.Flags.Stop                      },
        {'frame': '18 9A 96 D0 35 19 64 33', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature': -122.5, 'humidity':  20.5, 'flags': Record.Flags.Sign1 | Record.Flags.Light                     },
        {'frame': '28 C2 96 D0 F5 18 A4 33', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature': -122.3, 'humidity':  20.6, 'flags': Record.Flags.Sign1 | Record.Flags.Vibr                      },
        {'frame': '88 EA 96 D0 D5 18 E4 33', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature': -122.2, 'humidity':  20.7, 'flags': Record.Flags.Sign1 | Record.Flags.Error                     },

        {'frame': '48 EA 96 D0 D5 19 E3 31', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': -123.0, 'humidity': -19.9, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2                     },
        {'frame': '49 22 96 D0 B5 19 64 32', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature': -122.9, 'humidity': -20.1, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Mark },
        {'frame': '4A 4A 96 D0 95 19 A4 32', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature': -122.8, 'humidity': -20.2, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Pause},
        {'frame': '4C 72 96 D0 55 19 24 33', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature': -122.6, 'humidity': -20.4, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Stop },
        {'frame': '58 9A 96 D0 35 19 64 33', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature': -122.5, 'humidity': -20.5, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Light},
        {'frame': '68 C2 96 D0 F5 18 A4 33', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature': -122.3, 'humidity': -20.6, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Vibr },
        {'frame': 'C8 EA 96 D0 D5 18 E4 33', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature': -122.2, 'humidity': -20.7, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2 | Record.Flags.Error},

        {'frame': '40 EA 96 D0 D5 19 E3 31', 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature':  123.0, 'humidity': -19.9, 'flags': Record.Flags.Sign2                                          },
        {'frame': '41 22 96 D0 B5 19 64 32', 't': datetime(2022, 1, 26, 21, 36,  8), 'temperature':  122.9, 'humidity': -20.1, 'flags': Record.Flags.Sign2 | Record.Flags.Mark                      },
        {'frame': '42 4A 96 D0 95 19 A4 32', 't': datetime(2022, 1, 26, 21, 36, 18), 'temperature':  122.8, 'humidity': -20.2, 'flags': Record.Flags.Sign2 | Record.Flags.Pause                     },
        {'frame': '44 72 96 D0 55 19 24 33', 't': datetime(2022, 1, 26, 21, 36, 28), 'temperature':  122.6, 'humidity': -20.4, 'flags': Record.Flags.Sign2 | Record.Flags.Stop                      },
        {'frame': '50 9A 96 D0 35 19 64 33', 't': datetime(2022, 1, 26, 21, 36, 38), 'temperature':  122.5, 'humidity': -20.5, 'flags': Record.Flags.Sign2 | Record.Flags.Light                     },
        {'frame': '60 C2 96 D0 F5 18 A4 33', 't': datetime(2022, 1, 26, 21, 36, 48), 'temperature':  122.3, 'humidity': -20.6, 'flags': Record.Flags.Sign2 | Record.Flags.Vibr                      },
        {'frame': 'C0 EA 96 D0 D5 18 E4 33', 't': datetime(2022, 1, 26, 21, 36, 58), 'temperature':  122.2, 'humidity': -20.7, 'flags': Record.Flags.Sign2 | Record.Flags.Error                     },
    ])
    def testParse0x23(self, frame, t, temperature, humidity, flags):
        r = Record.parse(bytes([int(b, 16) for b in frame.split(' ')]), 0x23)
        self.assertEqual(r.time, t)
        self.assertEqual(r.temperature, temperature)
        self.assertEqual(r.humidity, humidity)
        self.assertEqual(r.flags, flags)


    def testParseNone(self):
        self.assertIsNone(Record.parse(bytes([0xFF]*8)))

    @testdata.TestData([
        {'frame': '00 E9 96 D0 D5 19 23 00', 'b': 8, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': 20.6, 'humidity': None, 'flags': 0},
        {'frame': '00 EA 96 D0 D5 19 23 00', 'b': 9, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': 20.6, 'humidity': None, 'flags': 0},
        {'frame': '00 E9 96 D0 D5 19 E3 31', 'b': 8, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': 20.6, 'humidity': 19.9, 'flags': 0},
        {'frame': '00 EA 96 D0 D5 19 E3 31', 'b': 9, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': 20.6, 'humidity': 19.9, 'flags': 0},
        {'frame': '08 E9 96 D0 D5 19 E3 31', 'b': 8, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': -20.6, 'humidity': 19.9, 'flags': Record.Flags.Sign1},
        {'frame': '08 EA 96 D0 D5 19 E3 31', 'b': 9, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': -20.6, 'humidity': 19.9, 'flags': Record.Flags.Sign1},
        {'frame': '48 E9 96 D0 D5 19 E3 31', 'b': 8, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': -20.6, 'humidity': -19.9, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2},
        {'frame': '48 EA 96 D0 D5 19 E3 31', 'b': 9, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': -20.6, 'humidity': -19.9, 'flags': Record.Flags.Sign1 | Record.Flags.Sign2},
        {'frame': '40 E9 96 D0 D5 19 E3 31', 'b': 8, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': 20.6, 'humidity': -19.9, 'flags': Record.Flags.Sign2},
        {'frame': '40 EA 96 D0 D5 19 E3 31', 'b': 9, 't': datetime(2022, 1, 26, 21, 35, 58), 'temperature': 20.6, 'humidity': -19.9, 'flags': Record.Flags.Sign2},
    ])
    def testParseWarning(self, frame, b, t, temperature, humidity, flags):
        with self.assertWarns(UserWarning) as w:
            r = Record.parse(bytes([int(b, 16) for b in frame.split(' ')]))
        self.assertEqual(str(w.warning), f"Ignored bit {b} is non zero")

        self.assertEqual(r.time, t)
        self.assertEqual(r.temperature, temperature)
        self.assertEqual(r.humidity, humidity)
        self.assertEqual(r.flags, flags)



    @testdata.TestData([
        {'frame': '00 E8 96 D0 D5 19 23 00 00', 'l': 9},
        {'frame': '00 E8 96 D0 D5 19 23',       'l': 7},
        {'frame': 'FF FF FF FF FF FF FF FF FF', 'l': 9},
        {'frame': 'FF FF FF FF FF FF FF',       'l': 7},
    ])
    def testParseInvalid(self, frame, l):
        with self.assertRaises(ValueError) as e:
            Record.parse(bytes([int(b, 16) for b in frame.split(' ')]))
        self.assertEqual(str(e.exception), f"Invalid record length: {l}")

