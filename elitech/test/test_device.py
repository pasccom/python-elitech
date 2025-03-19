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
import unittest.mock

from PythonUtils import mockpath

import warnings

from pathlib import Path

from elitech.src.device import Device


class TestDevice(unittest.TestCase):
    def testNone(self):
        dev = Device('')
        self.assertEqual(dev.path, '')
        self.assertFalse(bool(dev))
        self.assertIsNone(dev.vendorId)
        self.assertIsNone(dev.productId)
        self.assertIsNone(dev.name)
        self.assertEqual(dev.outReportSize, 64)
        self.assertEqual(dev.inReportSize, 64)

    def testEmpty(self):
        dev = Device('')
        self.assertEqual(dev.path, '')
        self.assertFalse(bool(dev))
        self.assertIsNone(dev.vendorId)
        self.assertIsNone(dev.productId)
        self.assertIsNone(dev.name)
        self.assertEqual(dev.outReportSize, 64)
        self.assertEqual(dev.inReportSize, 64)

    def testString(self):
        dev = Device('/dev/null')
        self.assertEqual(dev.path, Path('/dev/null'))
        self.assertTrue(bool(dev))

    def testPath(self):
        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.path, Path('/dev/null'))
        self.assertTrue(bool(dev))

    def testNonExistingString(self):
        with self.assertRaises(ValueError) as e:
            dev = Device('/dev/non-existing-device')
        self.assertEqual(str(e.exception), "Device \"/dev/non-existing-device\" does not exist")

    def testNonExistingPath(self):
        with self.assertRaises(ValueError) as e:
            dev = Device(Path('/dev/non-existing-device'))
        self.assertEqual(str(e.exception), "Device \"/dev/non-existing-device\" does not exist")

    @unittest.mock.patch('elitech.src.device.open')
    def testOutReportSize(self, mock_open):
        with open(Path(__file__).parents[0] / 'data' / 'hid_report_descriptor', 'rb') as f:
            unittest.mock.mock_open(mock_open, f.read())

        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.path, Path('/dev/null'))

        with warnings.catch_warnings(record=True) as w:
            outReportSize = dev.outReportSize
        self.assertEqual(len(w), 0)

        self.assertIsNotNone(outReportSize)
        self.assertEqual(outReportSize, 64)

        self.assertEqual(len(mock_open.call_args_list), 1)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/class/hidraw/null/device/report_descriptor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rb')

    @unittest.mock.patch('elitech.src.device.open')
    def testInReportSize(self, mock_open):
        with open(Path(__file__).parents[0] / 'data' / 'hid_report_descriptor', 'rb') as f:
            unittest.mock.mock_open(mock_open, f.read())

        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.path, Path('/dev/null'))

        with warnings.catch_warnings(record=True) as w:
            inReportSize = dev.inReportSize
        self.assertEqual(len(w), 0)

        self.assertIsNotNone(inReportSize)
        self.assertEqual(inReportSize, 64)

        self.assertEqual(len(mock_open.call_args_list), 1)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/class/hidraw/null/device/report_descriptor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rb')

    @unittest.mock.patch('elitech.src.device.print')
    def testWriteEmpty(self, mock_print):
        dev = Device('')
        dev.write(bytes([b for b in range(0, 11)]))

        self.assertEqual(len(mock_print.call_args_list), 1)
        self.assertEqual(mock_print.call_args_list[0][0][0], 'Request:  ' + ' '.join([(f'{b:02X}' if b < 11 else '00') for b in range(0, 64)]))

    @unittest.mock.patch('elitech.src.device.print')
    def testReadEmpty(self, mock_print):
        dev = Device('')
        self.assertEqual(dev.read(), bytes([0]*64))

        self.assertEqual(len(mock_print.call_args_list), 1)
        self.assertEqual(mock_print.call_args_list[0][0][0], 'Response: ' + ' '.join(['00']*64))

    @unittest.mock.patch('elitech.src.device.open')
    def testOpen(self, mock_open):
        mock_file = unittest.mock.Mock()
        mock_open.return_value = mock_file

        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.path, Path('/dev/null'))

        with dev:
            pass

        self.assertEqual(len(mock_open.call_args_list), 1)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/dev/null'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rb+')
        self.assertEqual(len(mock_file.close.call_args_list), 1)

    @unittest.mock.patch('elitech.src.device.print')
    @unittest.mock.patch('elitech.src.device.open')
    def testWrite(self, mock_open, mock_print):
        mock_descriptor = unittest.mock.MagicMock()
        mock_descriptor.__enter__.return_value = mock_descriptor
        with open(Path(__file__).parents[0] / 'data' / 'hid_report_descriptor', 'rb') as f:
            mock_descriptor.read.return_value = f.read()
        mock_file = unittest.mock.Mock()
        mock_open.side_effect = [mock_file, mock_descriptor]

        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.path, Path('/dev/null'))

        with dev:
            dev.write(bytes([b for b in range(0, 11)]))

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/dev/null'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rb+')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/class/hidraw/null/device/report_descriptor'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rb')
        self.assertEqual(len(mock_file.write.call_args_list), 1)
        self.assertEqual(mock_file.write.call_args_list[0][0][0], bytes([b for b in range(0, 11)] + [0]*53))
        self.assertEqual(len(mock_file.flush.call_args_list), 1)
        self.assertEqual(len(mock_file.close.call_args_list), 1)

        self.assertEqual(len(mock_print.call_args_list), 1)
        self.assertEqual(mock_print.call_args_list[0][0][0], 'Request:  ' + ' '.join([(f'{b:02X}' if b < 11 else '00') for b in range(0, 64)]))

    @unittest.mock.patch('elitech.src.device.print')
    @unittest.mock.patch('elitech.src.device.open')
    def testRead(self, mock_open, mock_print):
        mock_descriptor = unittest.mock.MagicMock()
        mock_descriptor.__enter__.return_value = mock_descriptor
        with open(Path(__file__).parents[0] / 'data' / 'hid_report_descriptor', 'rb') as f:
            mock_descriptor.read.return_value = f.read()
        mock_file = unittest.mock.Mock()
        mock_file.__enter__ = mock_file
        mock_file.read.return_value = bytes([b for b in range(0, 64)])
        mock_open.side_effect = [mock_file, mock_descriptor]

        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.path, Path('/dev/null'))

        with dev:
            self.assertEqual(dev.read(), bytes([b for b in range(0, 64)]))

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/dev/null'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rb+')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/class/hidraw/null/device/report_descriptor'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rb')
        self.assertEqual(len(mock_file.read.call_args_list), 1)
        self.assertEqual(mock_file.read.call_args_list[0][0][0], 64)
        self.assertEqual(len(mock_file.close.call_args_list), 1)

        self.assertEqual(len(mock_print.call_args_list), 1)
        self.assertEqual(mock_print.call_args_list[0][0][0], 'Response: ' + ' '.join([f'{b:02X}' for b in range(0, 64)]))

    @unittest.mock.patch('elitech.src.device.print')
    @unittest.mock.patch('elitech.src.device.open')
    def testReadKeyboardInterrupt(self, mock_open, mock_print):
        mock_descriptor = unittest.mock.MagicMock()
        mock_descriptor.__enter__.return_value = mock_descriptor
        with open(Path(__file__).parents[0] / 'data' / 'hid_report_descriptor', 'rb') as f:
            mock_descriptor.read.return_value = f.read()
        mock_file = unittest.mock.Mock()
        mock_file.__enter__ = mock_file
        mock_file.read.side_effect = KeyboardInterrupt
        mock_open.side_effect = [mock_file, mock_descriptor]

        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.path, Path('/dev/null'))

        with dev:
            self.assertEqual(dev.read(), bytes([0x00]*64))

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/dev/null'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rb+')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/class/hidraw/null/device/report_descriptor'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rb')
        self.assertEqual(len(mock_file.read.call_args_list), 1)
        self.assertEqual(mock_file.read.call_args_list[0][0][0], 64)
        self.assertEqual(len(mock_file.close.call_args_list), 1)

        self.assertEqual(len(mock_print.call_args_list), 1)
        self.assertEqual(mock_print.call_args_list[0][0][0], 'Response: ' + ' '.join(['00' for b in range(0, 64)]))

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'}},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}},
                'idVendor': b'1234',
                'idProduct': b'6789',
            }}}}},
        },
    }))
    def testResolveSingle(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.vendorId, 0x1234)
        self.assertEqual(dev.productId, 0x6789)

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idVendor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rt')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idProduct'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rt')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {
                'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'},
                'hidraw0': b'',
            },
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}},
                'idVendor': b'1234',
                'idProduct': b'6789',
            }}}}},
        },
    }))
    def testResolveFirst(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.vendorId, 0x1234)
        self.assertEqual(dev.productId, 0x6789)

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idVendor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rt')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idProduct'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rt')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {
                'hidraw0': b'',
                'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'},
            },
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}},
                'idVendor': b'1234',
                'idProduct': b'6789',
            }}}}},
        },
    }))
    def testResolveSecond(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.vendorId, 0x1234)
        self.assertEqual(dev.productId, 0x6789)

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idVendor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rt')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idProduct'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rt')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'}},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}}
            }}}}},
        },
    }))
    def testResolveNone1(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))

        with self.assertRaises(ValueError) as e:
            dev.vendorId
        self.assertEqual(str(e.exception), f"Device vendor id and product id cannot be obtained")

        with self.assertRaises(ValueError) as e:
            dev.productId
        self.assertEqual(str(e.exception), f"Device vendor id and product id cannot be obtained")

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {
                'hidraw0': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/hidraw0',
                'null': b''},
            },
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'hidraw0'}}},
                'idVendor': b'1234',
                'idProduct': b'6789',
            }}}}},
        },
    }))
    def testResolveNone2(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))

        with self.assertRaises(ValueError) as e:
            dev.vendorId
        self.assertEqual(str(e.exception), f"Device vendor id and product id cannot be obtained")

        with self.assertRaises(ValueError) as e:
            dev.productId
        self.assertEqual(str(e.exception), f"Device vendor id and product id cannot be obtained")

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'}},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}},
                'idVendor': b'04d8',
                'idProduct': b'3005',
            }}}}},
        },
    }))
    def testNameSingle(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.name, 'Elitech RC-5+')

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idVendor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rt')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idProduct'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rt')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {
                'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'},
                'hidraw0': b'',
            },
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}},
                'idVendor': b'04d8',
                'idProduct': b'3005',
            }}}}},
        },
    }))
    def testNameFirst(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.name, 'Elitech RC-5+')

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idVendor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rt')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idProduct'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rt')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {
                'hidraw0': b'',
                'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'},
            },
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}},
                'idVendor': b'04d8',
                'idProduct': b'3005',
            }}}}},
        },
    }))
    def testNameSecond(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))
        self.assertEqual(dev.name, 'Elitech RC-5+')

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idVendor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rt')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idProduct'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rt')


    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'}},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}},
                'idVendor': b'04d8',
                'idProduct': b'1234',
            }}}}},
        },
    }))
    def testNameSingleUnsupported(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))

        with self.assertRaises(ValueError) as e:
            dev.name
        self.assertEqual(str(e.exception), "Unsupported device: 04d8:1234")

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idVendor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rt')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idProduct'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rt')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {
                'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'},
                'hidraw0': b'',
            },
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}},
                'idVendor': b'04d8',
                'idProduct': b'1234',
            }}}}},
        },
    }))
    def testNameFirstUnsupported(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))

        with self.assertRaises(ValueError) as e:
            dev.name
        self.assertEqual(str(e.exception), "Unsupported device: 04d8:1234")

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idVendor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rt')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idProduct'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rt')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'sys' : {
            'class': {'hidraw': {
                'hidraw0': b'',
                'null': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/null'},
            },
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'null'}}},
                'idVendor': b'04d8',
                'idProduct': b'1234',
            }}}}},
        },
    }))
    def testNameSecondUnsupported(self, mock_path, mock_open):
        dev = Device(Path('/dev/null'))

        with self.assertRaises(ValueError) as e:
            dev.name
        self.assertEqual(str(e.exception), "Unsupported device: 04d8:1234")

        self.assertEqual(len(mock_open.call_args_list), 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idVendor'))
        self.assertEqual(mock_open.call_args_list[0][0][1], 'rt')
        self.assertEqual(mock_open.call_args_list[1][0][0], Path('/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/idProduct'))
        self.assertEqual(mock_open.call_args_list[1][0][1], 'rt')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'dev': {'hidraw0': b''},
        'sys': {
            'class': {'hidraw': {'hidraw0': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/hidraw0'}},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'hidraw0'}}}
            }}}}},
        },
    }))
    def testEnumerateError(self, mock_path, mock_open):
        self.assertEqual(len([d for d in Device.enumerate()]), 0)

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'dev': {'hidraw0': b''},
        'sys': {
            'class': {'hidraw': {'hidraw0': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/hidraw0'}},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'hidraw0'}}},
                'idVendor': b'1234',
                'idProduct': b'6789',
            }}}}},
        },
    }))
    def testEnumerateNone(self, mock_path, mock_open):
        self.assertEqual(len([d for d in Device.enumerate()]), 0)

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'dev': {'hidraw0': b''},
        'sys': {
            'class': {'hidraw': {'hidraw0': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/hidraw0'}},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {'3-2': {
                '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'hidraw0'}}},
                'idVendor': b'04d8',
                'idProduct': b'3005',
            }}}}},
        },
    }))
    def testEnumerateSingle(self, mock_path, mock_open):
        devices = [d for d in Device.enumerate()]
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].path, Path('/dev/hidraw0'))
        self.assertEqual(devices[0].vendorId, 0x04d8)
        self.assertEqual(devices[0].productId, 0x3005)
        self.assertEqual(devices[0].name, 'Elitech RC-5+')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'dev': {
            'hidraw0': b'',
            'hidraw1': b'',
        },
        'sys': {
            'class': {'hidraw': {
                'hidraw0': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/hidraw0',
                'hidraw1': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-1/3-1:1.1/0003:04D8:3005.0005/hidraw/hidraw1',
            }},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {
                '3-1': {
                    '3-1:1.1': {'0003:04D8:3005.0005': {'hidraw': {'hidraw1'}}},
                    'idVendor': b'1234',
                    'idProduct': b'6789'
                },
                '3-2': {
                    '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'hidraw0'}}},
                    'idVendor': b'04d8',
                    'idProduct': b'3005',
                },
            }}}},
        },
    }))
    def testEnumerateFirst(self, mock_path, mock_open):
        devices = [d for d in Device.enumerate()]
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].path, Path('/dev/hidraw0'))
        self.assertEqual(devices[0].vendorId, 0x04d8)
        self.assertEqual(devices[0].productId, 0x3005)
        self.assertEqual(devices[0].name, 'Elitech RC-5+')

    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'dev': {
            'hidraw0': b'',
            'hidraw1': b'',
        },
        'sys': {
            'class': {'hidraw': {
                'hidraw0': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/hidraw0',
                'hidraw1': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-1/3-1:1.1/0003:04D8:3005.0005/hidraw/hidraw1',
            }},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {
                '3-1': {
                    '3-1:1.1': {'0003:04D8:3005.0005': {'hidraw': {'hidraw1'}}},
                    'idVendor': b'04d8',
                    'idProduct': b'3005',
                },
                '3-2': {
                    '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'hidraw0'}}},
                    'idVendor': b'1234',
                    'idProduct': b'6789'
                },
            }}}},
        },
    }))
    def testEnumerateSecond(self, mock_path, mock_open):
        devices = [d for d in Device.enumerate()]
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].path, Path('/dev/hidraw1'))
        self.assertEqual(devices[0].vendorId, 0x04d8)
        self.assertEqual(devices[0].productId, 0x3005)
        self.assertEqual(devices[0].name, 'Elitech RC-5+')


    @unittest.mock.patch('elitech.src.device.open', new_callable=mockpath.MockPath.mock_open)
    @unittest.mock.patch('elitech.src.device.Path', new_callable=mockpath.MockPath({
        'dev': {
            'hidraw0': b'',
            'hidraw1': b'',
        },
        'sys': {
            'class': {'hidraw': {
                'hidraw0': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:046D:C069.0002/hidraw/hidraw0',
                'hidraw1': '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-1/3-1:1.1/0003:04D8:3005.0005/hidraw/hidraw1',
            }},
            'devices': {'pci0000:00': {'0000:00:14.0': {'usb3': {
                '3-1': {
                    '3-1:1.1': {'0003:04D8:3005.0005': {'hidraw': {'hidraw1'}}},
                    'idVendor': b'0416',
                    'idProduct': b'0001',
                },
                '3-2': {
                    '3-2:1.0': {'0003:046D:C069.0002': {'hidraw': {'hidraw0'}}},
                    'idVendor': b'04d8',
                    'idProduct': b'3005',
                },
            }}}},
        },
    }))
    def testEnumerateBoth(self, mock_path, mock_open):
        devices = [d for d in Device.enumerate()]
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0].path, Path('/dev/hidraw0'))
        self.assertEqual(devices[0].vendorId, 0x04d8)
        self.assertEqual(devices[0].productId, 0x3005)
        self.assertEqual(devices[0].name, 'Elitech RC-5+')
        self.assertEqual(devices[1].path, Path('/dev/hidraw1'))
        self.assertEqual(devices[1].vendorId, 0x0416)
        self.assertEqual(devices[1].productId, 0x0001)
        self.assertEqual(devices[1].name, 'Elitech LogEt 1')
