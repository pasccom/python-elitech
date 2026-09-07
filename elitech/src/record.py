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

from datetime import datetime
from enum import IntFlag
from warnings import warn as warning

class Record:
    Length = 8
    DefaultProtocol = 0x20
    # From this protocol version on, records use the layout of `DataFactory.ParseRecord`
    # in the official software (seen as 0x35 on the Elitech RC-5). The older devices
    # (RC-5+, ...) report lower versions and keep the layout below.
    NewFormatProtocol = 0x30
    # Values the official software uses to mean "no reading" (°C or %RH)
    NoData = (-100., -101., -111., -1001., -1002., -1003.)

    class Flags(IntFlag):
        Zero  = 0b00000000
        Mark  = 0b00000001
        Pause = 0b00000010
        Stop  = 0b00000100
        Sign1 = 0b00001000
        Light = 0b00010000
        Vibr  = 0b00100000
        Sign2 = 0b01000000
        Error = 0b10000000

    def __init__(self, t, temp, flags=0, humi=None):
        self.time = t
        self.temperature = temp
        self.humidity = humi
        self.__flags = flags

    @property
    def pause(self):
        return bool(self.__flags & Record.Flags.Pause)

    @property
    def stop(self):
        return bool(self.__flags & Record.Flags.Stop)

    @property
    def error(self):
        return bool(self.__flags & Record.Flags.Error)

    @property
    def flagStr(self):
        flags = ''
        if (self.__flags & Record.Flags.Mark):
            flags += 'M'
        else:
            flags += '-'
        if (self.__flags & Record.Flags.Light):
            flags += 'L'
        else:
            flags += '-'
        if (self.__flags & Record.Flags.Vibr):
            flags += 'V'
        else:
            flags += '-'
        return flags

    @classmethod
    def parse(cls, frame, protocol=DefaultProtocol):
        if (len(frame) != 8):
            raise ValueError(f"Invalid record length: {len(frame)}")

        q = 0
        s = 0
        for b in frame:
            q |= b << s
            s += 8

        #print('[' + ' '.join([f'{b:02X}' for b in frame]) + f'] -> {q:016X} -> {q:064b}')

        if (q == 0xFFFFFFFFFFFFFFFF):
            return None

        if (protocol >= cls.NewFormatProtocol):
            return cls.__parseNew(frame)

        humidity    = (q >> 54) & 0x3FF
        minute      = (q >> 48) & 0x03F
        temperature = (q >> 37) & 0x7FF
        hour        = (q >> 32) & 0x01F
        day         = (q >> 27) & 0x01F
        month       = (q >> 23) & 0x00F
        year        = (q >> 16) & 0x07F
        second      = (q >> 10) & 0x03F
        flags       = (q >>  0) & 0x0FF

        if (protocol >= 0x23):
            temperature |= ((q >>  9) & 0x01) << 10
        elif ((q >>  9) & 0x01):
            warning('Ignored bit 9 is non zero')
        if ((q >>  8) & 0x01):
            warning('Ignored bit 8 is non zero')

        if (flags & cls.Flags.Sign1):
            temperature = -temperature/10
        else:
            temperature = temperature/10

        if (flags & cls.Flags.Sign2):
            humidity = -humidity/10
        else:
            humidity = humidity/10

        t = datetime(2000 + year, month, day, hour, minute, second)

        if (humidity == 0):
            return cls(t, temperature, flags)
        else:
            return cls(t, temperature, flags, humidity)

    @classmethod
    def __parseNew(cls, frame):
        # Record layout of `DataFactory.ParseRecord` in the official software, used by
        # the recent devices (e.g. the Elitech RC-5, protocol version 0x35). The sign of
        # the temperature is in bit 3 of the first byte, the sign of the humidity in bit 6.
        b = frame
        flags = b[0] & (int(cls.Flags.Mark) | int(cls.Flags.Pause) | int(cls.Flags.Stop)
                        | int(cls.Flags.Light) | int(cls.Flags.Vibr))

        second =  (b[1] >> 2) & 0x3F
        year   = ((b[2]      ) & 0x7F) + 2000
        month  = ((b[3] & 0x07) << 1) | ((b[2] >> 7) & 0x01)
        day    =  (b[3] >> 3) & 0x1F
        hour   =   b[4]        & 0x1F
        minute =   b[6]        & 0x3F

        temperature = (((b[1] >> 1) & 0x01) << 11) | (b[5] << 3) | (b[4] >> 5)
        temperature = -temperature / 10. if (b[0] & 0x08) else temperature / 10.

        humidity = (b[7] << 2) | (b[6] >> 6)
        humidity = -humidity / 10. if (b[0] & 0x40) else humidity / 10.

        if (year > 2099) or (month == 0) or (month > 12) or (day == 0) or (day > 31):
            return None

        t = datetime(year, month, day, hour, minute, second)

        if temperature in cls.NoData:
            flags |= int(cls.Flags.Error)
        if humidity in cls.NoData:
            humidity = None

        if humidity is None:
            return cls(t, temperature, flags)
        else:
            return cls(t, temperature, flags, humidity)



