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
        self.flags = flags

    @classmethod
    def parse(cls, frame, protocol=0x20):
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



