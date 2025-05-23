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

from abc import abstractmethod
from enum import Enum
from warnings import warn as warning

import datetime
import math

class Range:
    def __init__(self, s, l):
        if (l < 0):
            raise ValueError(f"Invalid range length: {l}")
        self.start = s
        self.len = l

    @property
    def end(self):
        return self.start + self.len - 1

    def __bool__(self):
        return (self.len == 0)

    def __eq__(self, other):
        return ((self.len == 0) and (other.len == 0)) or ((self.start == other.start) and (self.len == other.len))

    def __contains__(self, other):
        return (other.len == 0) or ((self.len != 0) and (self.start <= other.start) and (self.end >= other.start) and (self.end >= other.end))

    def __and__(self, other):
        end = min(self.end, other.end)
        start = max(self.start, other.start)

        if (end + 1 < start):
            return Range(0, 0)
        return Range(start, end - start + 1)

    def __or__(self, other):
        if (self.start > other.end + 1) or (other.start > self.end + 1):
            raise ValueError(f"Ranges {self} and {other} cannot be merged")

        end = max(self.end, other.end)
        start = min(self.start, other.start)
        return Range(start, end - start + 1)

    def __sub__(self, other):
        ranges = []
        if (self.start < other.start):
            ranges.append(Range(self.start, min(self.len, other.start - self.start)))
        if (self.end > other.end):
            ranges.append(Range(max(self.start, other.end + 1), self.end - max(self.start, other.end + 1) + 1))
        return ranges

    def __repr__(self):
        return f'[{self.start}, {self.start + self.len})'

    @classmethod
    def fromString(cls, s):
        parts = s.split('-')
        try:
            parts = [int(p) for p in parts]
        except:
            raise ValueError(f"Invalid range: \"{s}\"")
        if (len(parts) == 1):
            return cls(parts[0] - 1, 1)
        elif (len(parts) != 2):
            raise ValueError(f"Invalid range: \"{s}\"")
        elif (parts[1] < parts[0]):
            raise ValueError(f"Invalid range: \"{s}\"")
        return cls(int(parts[0]) - 1, int(parts[1]) - int(parts[0]) + 1)

    @staticmethod
    def optimize(ranges):
        # Sort ranges in incresing start order
        ranges = sorted(ranges, key=lambda r: r.start)

        # Merge adjacent ranges
        merged = []
        r1 = 0
        while (r1 < len(ranges)):
            m = ranges[r1]
            r2 = r1 + 1
            while (r2 < len(ranges)):
                if (ranges[r2].start <= m.end + 1):
                    m |= ranges[r2]
                    r2 = r2 + 1
                else:
                    break
            merged.append(m)
            r1 = r2

        return merged


class Parameter:
    def __init__(self, name, description, offset, writable, immutable):
        self.name = name
        self.description = description
        self.offset = offset
        self.writable = writable
        self.immutable = immutable
        self._value = None
        self._oldData = None

    def __or__(self, data):
        self._oldData = data
        return self

    @property
    def len(self):
        return self._len

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    @property
    def range(self):
        return Range(self.offset, self.len)

    @abstractmethod
    def parseData(self, data):
        pass #pragma: no cover

    @abstractmethod
    def parseValue(self, _value):
        pass #pragma: no cover

    def __str__(self):
        if self._value is None:
            return ''
        return str(self.value)

    @abstractmethod
    def __bytes__(self):
        pass #pragma: no cover

    def __repr__(self): #pragma: no cover
        if self._value is None:
            return f"{self.__class__.__name__}({self.name})"
        return f"{self.__class__.__name__}({self.name}, {self._value})"


class StringParameter(Parameter):
    def __init__(self, name, description, offset, length, writable, immutable):
        super().__init__(name, description, offset, writable, immutable)
        self._len = length

    def parseData(self, data):
        self._value = data.decode().replace('\x00', '')
        return self

    def parseValue(self, value):
        self._value = value
        return self

    def __bytes__(self):
        if self._value is None:
            return bytes([0x00]*self._len)
        b = self._value.encode()
        return b + bytes([0x00]*(self._len - len(b)))


class DateTimeParameter(Parameter):
    def __init__(self, *args, **kwArgs):
        super().__init__(*args, **kwArgs)
        self._len = 7

    def parseData(self, data):
        self._value = datetime.datetime(2000 + data[0], data[1], data[3], data[4], data[5], data[6])
        return self

    def parseValue(self, value):
        self._value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return self

    def now(self):
        self._value = datetime.datetime.now()
        return self

    def __str__(self):
        if self._value is None:
            return ''
        return self._value.strftime('%Y-%m-%d %H:%M:%S')

    def __bytes__(self):
        if self._value is None:
            return bytes([0x00]*self._len)
        return bytes([self._value.year - 2000, self._value.month, 0x00, self._value.day, self._value.hour, self._value.minute, self._value.second])

class UnsignedIntegerParameter(Parameter):
    def parseData(self, data):
        self._value = 0
        for b in range(0, self._len):
            self._value = (self._value << 8) | data[b]
        return self

    def parseValue(self, value):
        try:
            if (len(value) > 2) and value.startswith('0x'):
                self._value = int(value[2:], 16)
            elif (len(value) > 2) and value.startswith('0b'):
                self._value = int(value[2:], 2)
            elif (len(value) > 1) and value.startswith('0'):
                self._value = int(value[1:], 8)
            elif (len(value) > 0):
                self._value = int(value)
        except (ValueError):
            warning(f"Invalid value for unsigned integer: {value}")
        if (self._value is not None) and (self._value >= math.pow(2, 8*self._len)):
            warning(f"Value is too large: {value}")
            self._value = None
        return self

    def __str__(self):
        if self._value is None:
            return ''
        s = f'{self._value:X}'
        s = '0'*(2*self._len - len(s)) + s
        return f'0x{s}'


    def __bytes__(self):
        ba = [0x00]*self._len
        if self._value is not None:
            v = self._value
            for b in range(0, self._len):
                ba[self._len - 1 - b] = v & 0xFF
                v >>= 8
        return bytes(ba)


class ByteParameter(UnsignedIntegerParameter):
    def __init__(self, *args, **kwArgs):
        super().__init__(*args, **kwArgs)
        self._len = 1


class WordParameter(UnsignedIntegerParameter):
    def __init__(self, *args, **kwArgs):
        super().__init__(*args, **kwArgs)
        self._len = 2


class DWordParameter(UnsignedIntegerParameter):
    def __init__(self, *args, **kwArgs):
        super().__init__(*args, **kwArgs)
        self._len = 4


class EnumParameter(Parameter):
    def __init__(self, name, description, offset, enumCls, bitOffset, writable, immutable):
        super().__init__(name, description, offset, writable, immutable)
        self.__cls = enumCls
        self._len = math.ceil(math.log2(1 + max([i.value for i in self.__cls])))
        self.__bitOffset = bitOffset

    @property
    def value(self):
        for i in self.__cls:
            if (i.value == self._value):
                return i
        if self._value is not None:
            s = f'{self._value:X}'
            s = '0'*(2*((self._len + 7) // 8) - len(s)) + s
            warning(f"Invalid value for enum parameter: 0x{s}")
        return None

    @value.setter
    def value(self, v):
        if v is None:
            self._value = v
        else:
            self._value = v.value

    @property
    def len(self):
        return (self._len + self.__bitOffset + 7) // 8

    def parseData(self, data):
        self._value = 0
        for b in range(0, self.len):
            if (b == 0) and (b == self.len - 1):
                m = ((1 << self._len) - 1) << self.__bitOffset
            elif (b == 0):
                m = (1 << (((self._len + self.__bitOffset - 1) % 8) + 1)) - 1
            elif (b == self.len - 1):
                m = (0xFF << self.__bitOffset) & 0xFF
            else:
                m = 0xFF
            self._value = (self._value << 8) | (data[b] & m)
        self._value >>= self.__bitOffset
        return self

    def parseValue(self, value):
        for i in self.__cls:
            if (i.name == value):
                self._value = i.value
                return self
        values = '", "'.join([i.name for i in self.__cls])
        warning(f"Invalid value: {value} (accepted values: \"{values}\")")
        self._value = None
        return self

    def __str__(self):
        if self.value is not None:
            return self.value.name
        return ''

    def __bytes__(self):
        ba = [b for b in self._oldData] if self._oldData is not None else [0x00]*self.len
        if self._value is not None:
            v = self._value << self.__bitOffset
            for b in range(self.len, 0, -1):
                if (b == 1) and (b == self.len):
                    m = ((1 << self._len) - 1) << self.__bitOffset
                elif (b == 1):
                    m = (1 << (((self._len + self.__bitOffset - 1) % 8) + 1)) - 1
                elif (b == self.len):
                    m = (0xFF << self.__bitOffset) & 0xFF
                else:
                    m = 0xFF
                ba[b - 1] = v & m | ba[b - 1] & (0xFF - m)
                v >>= 8
        return bytes(ba)


class HalfByteParameter(Parameter):
    class Position(Enum):
        Lower = (0x0F, 0)
        Upper = (0xF0, 4)

        def __init__(self, m, o):
            self.mask = m
            self.offset = o

    def __init__(self, name, description, offset, position, writable, immutable):
        super().__init__(name, description, offset, writable, immutable)
        self.__pos = position
        self._len = 1

    def parseData(self, data):
        self._value = (data[0] & self.__pos.mask) >> self.__pos.offset
        return self

    def parseValue(self, value):
        try:
            if (len(value) > 2) and value.startswith('0x'):
                self._value = int(value[2:], 16)
            elif (len(value) > 2) and value.startswith('0b'):
                self._value = int(value[2:], 2)
            elif (len(value) > 1) and value.startswith('0'):
                self._value = int(value[1:], 8)
            elif (len(value) > 0):
                self._value = int(value)
        except (ValueError):
            warning(f"Invalid value for unsigned integer: {value}")
        if (self._value is not None) and (self._value >= 0x10):
            warning(f"Value is too large: {value}")
            self._value = None
        return self

    def __str__(self):
        if self._value is None:
            return ''
        return f'0x0{self._value:X}'

    def __bytes__(self):
        oldData = self._oldData[0] if self._oldData is not None else 0x00
        if self._value is None:
            return bytes([oldData])
        return bytes([(self._value & 0x0F) << self.__pos.offset | (oldData & (0xFF - self.__pos.mask))])


class BitParameter(Parameter):
    def __init__(self, name, description, offset, bitOffset, writable, immutable):
        super().__init__(name, description, offset, writable, immutable)
        self.__offset = bitOffset
        self._len = 1

    def parseData(self, data):
        m = 1 << self.__offset
        self._value = bool(data[0] & m)
        return self

    def parseValue(self, value):
        if (value == 'True') or (value == '1'):
            self._value = True
        elif (value == 'False') or (value == '0'):
            self._value = False
        else:
            warning(f"Invalid bit value: {value}")
            self._value = None
        return self

    def __bytes__(self):
        m = 1 << self.__offset
        oldData = self._oldData[0] if self._oldData is not None else 0x00
        if self._value is None:
            return bytes([oldData])
        return bytes([int(self._value) << self.__offset | (oldData & (0xFF - m))])


class EnumBitParameter(BitParameter):
    def __init__(self, name, description, offset, bitOffset, cls, writable, immutable):
        super().__init__(name, description, offset, bitOffset, writable, immutable)
        self.__cls = cls

    @property
    def value(self):
        for i in self.__cls:
            if (i.value == self._value):
                return i
        return None

    @value.setter
    def value(self, v):
        if v is None:
            self._value = v
        else:
            self._value = v.value

    def parseValue(self, value):
        for i in self.__cls:
            if (i.name == value):
                self._value = i.value
                return self
        values = '", "'.join([i.name for i in self.__cls])
        warning(f"Invalid value: {value} (accepted values: \"{values}\")")
        self._value = None
        return self

    def __str__(self):
        if self.value is not None:
            return self.value.name
        return ''


class FloatParameter(WordParameter):
    @property
    def value(self):
        if self._value is None:
            return None
        elif (self._value == 0xFFFF):
            return float('nan')
        elif (self._value < 0x8000):
            return self._value / 10.
        else:
            return -(self._value - 0x8000) / 10.

    @value.setter
    def value(self, v):
        if math.isnan(v) or math.isinf(v):
            self._value = 0xFFFF
        elif (round(10. * v) > 32767):
            warning(f"Value is too large: {v}")
        elif (v >= 0):
            self._value = round(10. * v)
        elif (round(10. * v) < -32766):
            warning(f"Value is too small: {v}")
        else:
            self._value = 0x8000 - round(10. * v)

    def parseValue(self, value):
        try:
            self.value = float(value)
        except ValueError:
            warning(f"Invalid value for floating-point number: {value}")
            self._value = None
        return self

    def __str__(self):
        if self.value is None:
            return ''
        return str(self.value)


class TimeSpanParameter(WordParameter):
    @property
    def value(self):
        return self._value*10 if self._value is not None else None

    @value.setter
    def value(self, v):
        if (v % 10 != 0):
            warning("Time span precision is 10s. Ignoring extra precision.")

        self._value = v // 10

    def parseValue(self, value):
        try:
            self.__parseValue(value)
        except ValueError:
            warning(f"Invalid timespan: {value}")
            self._value = None
        return self

    def __parseValue(self, value):
        d = value.find('j')
        if (d == -1):
            days = 0
        elif (d == 0):
            raise ValueError(f"Invalid timespan: {value}")
        else:
            days = int(value[0:d])

        h = value.find('h', max([0, d]))
        if (h == -1):
            hours = 0
        elif (h == max([0, d])):
            raise ValueError(f"Invalid timespan: {value}")
        else:
            hours = int(value[(max([-1, d]) + 1):h])

        m = value.find('m', max([0, d, h]))
        if (m == -1):
            minutes = 0
        elif (m == max([0, d, h])):
            raise ValueError(f"Invalid timespan: {value}")
        else:
            minutes = int(value[(max([-1, d, h]) + 1):m])

        s = value.find('s', max([0, d, h, m]))
        if (s == -1):
            seconds = 0
        elif (s == max([0, d, h, m])):
            raise ValueError(f"Invalid timespan: {value}")
        else:
            seconds = int(value[(max([-1, d, h, m]) + 1):s])

        self.value = (((days * 24) + hours) * 60 + minutes) * 60 + seconds

    def __str__(self):
        if self.value is None:
            return ''

        r = ''
        v = self.value
        if (v >= 24*60*60):
            r += f'{v // (24*60*60)}j'
            v %= 24*60*60
        if (v >= 60*60):
            r += f'{v // (60*60)}h'
            v %= 60*60
        if (v >= 60):
            r += f'{v // 60}m'
            v %= 60
        if (v > 0) or (self.value == 0):
            r += f'{v}s'
        return r


class TimeZoneParameter(Parameter):
    def __init__(self, name, description, offset, writable, immutable):
        super().__init__(name, description, offset, writable, immutable)
        self._len = 12

    @property
    def value(self):
        if self._value is None:
            return None
        elif (self._value < 0):
            return f'-{-self._value // 60:02d}{-self._value % 60:02d}'
        else:
            return f'+{self._value // 60:02d}{self._value % 60:02d}'

    @value.setter
    def value(self, v):
        if v.startswith('+'):
            if (len(v) != 5):
                raise ValueError(f'Invalid timezone: {v}')
            h = int(v[1:3])
            m = int(v[3:5])
        elif v.startswith('-'):
            if (len(v) != 5):
                raise ValueError(f'Invalid timezone: {v}')
            h = -int(v[1:3])
            m = -int(v[3:5])
        else:
            if (len(v) != 4):
                raise ValueError(f'Invalid timezone: {v}')
            h = int(v[0:2])
            m = int(v[2:4])
        if (h < -12) or (h > 12) or (m < -59) or (m > 59):
            raise ValueError(f'Invalid timezone: {v}')
        self._value = h * 60 + m

    def parseData(self, data):
        h = data[0] & 0x1F
        m = data[11]
        if (h > 24) or (m >= 60) or ((h == 12) and (m != 0)):
            warning(f'Invalid timezone data: h={h}, m={m}')
        elif (h > 12):
            self._value = -((24 - h) * 60 + m)
        else:
            self._value = h * 60 + m
        return self

        # s = bool(data[0] & 0x10)
        # h = data[0] & 0x0F
        # m = data[11]
        # if (h > 12) or (m >= 60):
        #     warning(f'Invalid timezone data: h={h}, m={m}')
        # else:
        #     self._value = (1 - 2 * s)*(h * 60 + m)
        # return self

    def parseValue(self, value):
        try:
            self.value = value
        except ValueError:
            warning(f"Invalid timezone: {value}")
            self._value = None
        return self

    def __bytes__(self):
        data = [b for b in self._oldData] if self._oldData is not None else [0x00]*12
        if self._value is None:
            pass
        elif (self._value < 0):
            data[0] = (data[0] & 0xE0) | ((24 - (-self._value // 60)) & 0x1F)
            data[11] = -self._value % 60
        else:
            data[0] = (data[0] & 0xE0) | ((self._value // 60) & 0x0F)
            data[11] = self._value % 60
        return bytes(data)


class PdfLanguages(Enum):
    en  = 0x00
    zh  = 0x01 # NOTE PDF does not work with Okular
    es  = 0x02 # NOTE Not available in official software
    MAX = 0xFF

class StartModes(Enum):
    Immediate = 0b000
    Manual    = 0b001
    Timer     = 0b010
    MAX       = 0b111

class TemperatureUnits(Enum):
    Celsius   = False
    Farenheit = True

class SensorLocations(Enum):
    Internal = False
    External = True

class SensorTypes(Enum):
    NoInformation = 0b00
    GlycolBottle  = 0b01
    MAX           = 0b11

class AlarmModes(Enum):
    NoAlarm  = 0b00
    Single   = 0b01
    Multiple = 0b10
    MAX      = 0b11

class DeviceStates(Enum):
    MAX = 0b1111111

class StopModes(Enum):
    Manual    = 0b000
    Temporary = 0b011
    MAX = 0b111

parameters = [
    WordParameter(    'model',                        "Product id of the device from its memory",                                 0x00,                                   False, False),
    StringParameter(  'serial-number',                "Serial number of the device",                                              0x02, 12,                               False, False),
    # Bytes 0x0E and 0x0F are ignored [0x00, 0x00]                                                                                                                             ),
    StringParameter(  'travel-number',                "Travel number",                                                            0x10, 13,                                True, False),
    EnumParameter(    'pdf-language',                 "Language to be used in the PDF",                                           0x1D, PdfLanguages, 0,                   True, False),
    HalfByteParameter('product-properties',           "Properties of the product",                                                0x1E, HalfByteParameter.Position.Lower, False, False),
    BitParameter(     'light-on',                     "Control device light (if available)",                                      0x1E, 4,                                 True, False),
    BitParameter(     'allow-cycle',                  "Allow to overwrite old data when the memory is full",                      0x1E, 7,                                 True, False), # NOTE Does not work on RC-5+
    ByteParameter(    'firmware-version',             "Version number of the firmware",                                           0x1F,                                   False,  True),
    EnumParameter(    'start-mode',                   "Recording start mode",                                                     0x20, StartModes, 0,                     True, False),
    BitParameter(     'button-stop',                  "The device can be stopped by button",                                      0x20, 3,                                 True, False), # TODO test
    BitParameter(     'software-stop',                "The device can be stopped by software",                                    0x20, 4,                                 True, False), # TODO test
    # Bit 5 of byte 0x20 is ignored [0]                                                                                                                                        ),
    BitParameter(     'repeat',                       "Allow a new recording to be started without having read the previous one", 0x20, 6,                                 True, False),
    BitParameter(     'pause-allowed',                "Authorize the recording to be paused (by double clicking the left key)",   0x20, 7,                                 True, False),
    BitParameter(     'pdf-password-protected',       "Protect PDF file with a password",                                         0x21, 0,                                 True, False),
    EnumBitParameter( 'temperature-sensor-location',  "Temperature sensor to be used",                                            0x21, 1, SensorLocations,                True, False),
    EnumBitParameter( 'humidity-sensor-location',     "Humidity sensor to be used",                                               0x21, 2, SensorLocations,                True, False),
    EnumBitParameter( 'temperature-sensor-unit',      "Unit for the temperature record",                                          0x21, 3, TemperatureUnits,               True, False),
    BitParameter(     'temperature-alarm-mode',       "Operation mode of temperature alarm",                                      0x21, 4,                                 True, False), # TODO two bits
    BitParameter(     'humidity-alarm-mode',          "Operation mode of humidity alarm",                                         0x21, 6,                                 True, False), # TODO two bits
    # Bit 6 and 7 of byte 0x21 are ignored [0, 0]                                                                                                                              ),
    BitParameter(     'high-temperature-alarm3-type', "TODO",                                                                     0x22, 0,                                 True, False), # TODO test
    BitParameter(     'high-temperature-alarm1-type', "TODO",                                                                     0x22, 2,                                 True, False), # TODO test
    BitParameter(     'low-temperature-alarm1-type',  "TODO",                                                                     0x22, 3,                                 True, False), # TODO test
    BitParameter(     'high-temperature-alarm2-type', "TODO",                                                                     0x22, 1,                                 True, False), # TODO test
    BitParameter(     'low-temperature-alarm2-type',  "TODO",                                                                     0x22, 4,                                 True, False), # TODO test
    BitParameter(     'low-temperature-alarm3-type',  "TODO",                                                                     0x22, 5,                                 True, False), # TODO test
    BitParameter(     'high-humidity-alarm-type',     "TODO",                                                                     0x22, 6,                                 True, False), # TODO test
    BitParameter(     'low-humidity-alarm-type',      "TODO",                                                                     0x22, 7,                                 True, False), # TODO test
    EnumParameter(    'exact-sensor-type',            "Additional information on the temperature sensor type",                    0x23, SensorTypes, 0,                    True, False),
    # Bit 2 and 3 of byte 0x23 are ignored [0, 0]                                                                                                                              ),
    HalfByteParameter('light-intensity',              "Intensity of the light of the device",                                     0x23, HalfByteParameter.Position.Upper,  True, False),
    TimeZoneParameter('timezone',                     "Timezone for the time parameters",                                         0x24,                                    True, False),
    # Bit 6 and 7 of byte 0x24 are ignored [0, 0]                                                                                                                              ),
    EnumParameter(    'device-state',                 "Current state of the device",                                              0x25, DeviceStates, 0,                  False,  True), # TODO check
    # Bit 7 of byte 0x25 is ignored [0]                                                                                                                                        ),
    EnumParameter(    'actual-stop-mode',             "How the device actually stopped",                                          0x26, StopModes, 0,                     False,  True), # TODO check
    BitParameter(     'temporary-pdf',                "Generate a PDF file even if the device is temporarily stopped",            0x26, 3,                                 True, False),
    BitParameter(     'display-time',                 "TODO",                                                                     0x26, 4,                                 True, False), # NOTE No effect
    # Bit 5, 6 and 7 of byte 0x26 are ignored [0, 0, 0]                                                                                                                        ),
    HalfByteParameter('battery-level',                "Current charging level of the battery",                                    0x27, HalfByteParameter.Position.Lower, False,  True),
    BitParameter(     'csv',                          "Encode measurement data in PDF file",                                      0x27, 4,                                 True, False), # NOTE Does not work on RC-5+
    # Bit 5, 6 and 7 of byte 0x27 are ignored [0, 0, 0]                                                                                                                        ),
    DateTimeParameter('configuration-time',           "Time at which the device was last configured",                             0x28,                                    True, False),
    #ByteParameter(   'timezone-minutes',             "Minute part of the timezone offset",                                       0x2F,                                    True, False),
    DateTimeParameter('start-time',                   "TODO",                                                                     0x30,                                   False, False),
    # Byte 0x37 is ignored [0x00]                                                                                                                                              ),
    DateTimeParameter('stop-time',                    "TODO",                                                                     0x38,                                   False, False),
    # Byte 0x3F is ignored [0x00]                                                                                                                                              ),
    WordParameter(    'start-delay',                  "Delay to wait before starting in \"Timer\" start mode",                    0x40,                                    True, False), # TODO test
    DWordParameter(   'device-capacity',              "Device capacity (in records)",                                             0x42,                                   False, False),
    #DWordParameter(  'record-number',                "Number of record currently in memory",                                     0x46,                                   False), # TODO !TLOG and protocol-version >= 0x24
    WordParameter(    'record-number',                "Number of record currently in memory",                                     0x48,                                   False, False), # TODO !TLOG and protocol-version <  0x24
    # Bytes 0x4A and 0x4B are ignored [0x00, 0x00]                                                                                                                             ),
    TimeSpanParameter('interval',                     "Time span between samples",                                                0x4C,                                    True, False),

    StringParameter(  'password',                     "Password used to protect PDF files",                                       0x80, 6,                                 True, False),
    DateTimeParameter('device-time',                  "Current device time",                                                      0x88,                                   False,  True),
    ByteParameter(    'protocol-version',             "Version number of the protocol",                                           0x95,                                   False, False),
]

class Parameters:
    def __iter__(self):
        for param in parameters:
            yield param

    def __getitem__(self, key):
        for param in parameters:
            if (param.name == key):
                return param
        raise KeyError(f"Unknown parameter: {key}")



