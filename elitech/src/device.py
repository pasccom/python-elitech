from pathlib import Path

import sys
import warnings
sys.path.insert(0, str(Path(__file__).parents[2] / 'HIDParser'))

from hid_parser import ReportDescriptor, HIDComplianceWarning


supportedDevices = [
    {'VId': 0x04d8, 'PId':0x0033, 'name': 'Elitech RC-51'               },
    {'VId': 0x04d8, 'PId':0x0133, 'name': 'Elitech RC-51H'              },
    {'VId': 0x04d8, 'PId':0x3005, 'name': 'Elitech RC-5+'               },
    {'VId': 0x04d8, 'PId':0x0037, 'name': 'Elitech RC-55'               },
    {'VId': 0x04d8, 'PId':0x1014, 'name': 'Elitech TemLog 20'           },
    {'VId': 0x04d8, 'PId':0x1114, 'name': 'Elitech TemLog 20H'          },
    {'VId': 0x04d8, 'PId':0x0012, 'name': 'Elitech RC-18'               },
    {'VId': 0x04d8, 'PId':0x0013, 'name': 'Elitech RC-19'               },
    {'VId': 0x04d8, 'PId':0x1005, 'name': 'Elitech ST5'                 },
    {'VId': 0x04d8, 'PId':0x0033, 'name': 'Elitech RC-51'               },
    {'VId': 0x0416, 'PId':0x3006, 'name': 'Elitech LogEt 6'             },
    {'VId': 0x0416, 'PId':0x4008, 'name': 'Elitech LogEt 8'             },
    {'VId': 0x0416, 'PId':0x4308, 'name': 'Elitech LogEt 8 Life Science'},
    {'VId': 0x0416, 'PId':0x3008, 'name': 'Elitech LogEt 8 Food'        },
    {'VId': 0x04d8, 'PId':0x2033, 'name': 'Elitech MSL-51'              },
    {'VId': 0x04d8, 'PId':0x2133, 'name': 'Elitech MSL-51H'             },
    {'VId': 0x0416, 'PId':0x0001, 'name': 'Elitech LogEt 1'             },
    {'VId': 0x0416, 'PId':0x0101, 'name': 'Elitech LogEt 1TH'           },
    {'VId': 0x0416, 'PId':0x0201, 'name': 'Elitech LogEt 1Bio'          },
    {'VId': 0x04d8, 'PId':0xF564, 'name': ''                            },
    {'VId': 0x0416, 'PId':0x3A01, 'name': ''                            },
    {'VId': 0x464d, 'PId':0x0402, 'name': ''                            },
]

class WarningFilter:
    def __init__(self, category=None):
        self.__cls = category
        self.__old = None

    def __enter__(self):
        self.__old = warnings.showwarning
        warnings.showwarning = self.__showWarning
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__old is not None:
            warnings.showwarning = self.__old
        self.__old = None
        return False

    def __showWarning(self, message, category, filename, lineno, file=None, line=None):
        if (self.__cls is not None) and (category is not self.__cls):
            self.__old(message, category, filename, lineno, file=None, line=None)

class Device:
    def __init__(self, devPath):
        self.path = devPath
        if self.path and (type(self.path) is str):
            self.path = Path(self.path)
        if self.path and not self.path.exists():
            raise ValueError(f"Device \"{self.path}\" does not exist")
        self.__dev = None
        self.__vendorId = None
        self.__productId = None
        self.__descriptor = None

    def __enter__(self):
        if self.path:
            self.__dev = open(self.path, 'rb+')
        return self


    def __exit__(self, *args):
        if self.__dev is not None:
            self.__dev.close()
            self.__dev = None
        return False

    @staticmethod
    def enumerate():
        hidClassPath = Path('/sys/class/hidraw')

        for hidSysPath in hidClassPath.iterdir():
            hidDevice = Device(Path('/dev') / hidSysPath.name)
            try:
                hidDevice.__resolve()
            except ValueError:
                continue

            for d in supportedDevices:
                if (d['VId'] == hidDevice.vendorId) and (d['PId'] == hidDevice.productId):
                    yield hidDevice
                    break

    @property
    def vendorId(self):
        if self.__vendorId is None:
            self.__resolve()
        return self.__vendorId

    @property
    def productId(self):
        if self.__productId is None:
            self.__resolve()
        return self.__productId

    @property
    def name(self):
        if not self.path:
            return None

        for d in supportedDevices:
            if (d['VId'] == self.vendorId) and (d['PId'] == self.productId):
                return d['name'] if (len(d['name']) > 0) else 'Unknown'

        raise ValueError(f"Unsupported device: {self.vendorId:04x}:{self.productId:04x}")

    @property
    def outReportSize(self):
        if self.__descriptor is None:
            self.__readDescriptor()
        if self.__descriptor is not None:
            return self.__descriptor.get_output_report_size().byte
        else:
            return 64

    @property
    def inReportSize(self):
        if self.__descriptor is None:
            self.__readDescriptor()
        if self.__descriptor is not None:
            return self.__descriptor.get_input_report_size().byte
        else:
            return 64

    def write(self, frame):
        request = frame + bytes([0] * (self.outReportSize - len(frame)))
        print("Request:  " + ' '.join([f'{b:02X}' for b in request]))
        if self.__dev is not None:
            self.__dev.write(request)
            self.__dev.flush()

    def read(self):
        response = None
        if self.__dev is not None:
            try:
                response = self.__dev.read(self.inReportSize)
            except KeyboardInterrupt:
                pass
        if response is None:
            response = bytes([0]*self.inReportSize)
        print("Response: " + ' '.join([f'{b:02X}' for b in response]))
        return response

    def __resolve(self):
        if not self.path:
            return

        hidSysPath = Path('/sys/class/hidraw') / self.path.name

        for p in hidSysPath.resolve().parents:
            if (p / 'idVendor').is_file() and (p / 'idProduct').is_file():
                with open(p / 'idVendor', 'rt') as f:
                    self.__vendorId = int(f.read().strip(), 16)
                with open(p / 'idProduct', 'rt') as f:
                    self.__productId = int(f.read().strip(), 16)
                break
        else:
            raise ValueError("Device vendor id and product id cannot be obtained")

    def __readDescriptor(self):
        if not self.path:
            return

        with open(Path('/sys/class/hidraw') / self.path.name / 'device' / 'report_descriptor', 'rb') as f:
            report = [int(b) for b in f.read()]

        with WarningFilter(HIDComplianceWarning):
            self.__descriptor = ReportDescriptor(report)

    def __repr__(self): #pragma: no cover
        if not self.path:
            return "Null"
        else:
            return f"Device('{self.path}')"

