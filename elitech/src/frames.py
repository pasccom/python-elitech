from enum import Enum
from warnings import warn as warning

from .parameters import Range

class Response:
    def __init__(self, range, data):
        if (len(data) != range.len):
            raise ValueError(f"Range and data lengths do not match: {len(data)} != {range.len}")
        self.range = range
        self.data = data

    def __eq__(self, other):
        return (self.range == other.range) and (self.data == other.data)

    def __getitem__(self, arg):
        if type(arg) is int:
            arg = Range(arg, 1)
        elif type(arg) is slice:
            start = None
            if (arg.start is not None):
                start = arg.start - self.range.start
            stop = None
            if  (arg.stop is not None):
                stop = arg.stop - self.range.start
            return self.data[slice(start, stop, arg.step)]
        if arg not in self.range:
            raise ValueError(f"Required range {arg} is not in available range {self.range}")
        return self.data[(arg.start - self.range.start):(arg.start + arg.len - self.range.start)]

    def __setitem__(self, arg, d):
        data = [b for b in self.data]
        if type(arg) is int:
            arg = Range(arg, 1)
        if type(arg) is slice:
            start = None
            if (arg.start is not None):
                start = arg.start - self.range.start
            stop = None
            if  (arg.stop is not None):
                stop = arg.stop - self.range.start
            data[slice(start, stop, arg.step)] = d
        elif (len(d) != arg.len):
            raise ValueError(f"Length of {arg} does not match data length: {len(d)}")
        elif arg not in self.range:
            raise ValueError(f"Required range {arg} is not in available range {self.range}")
        else:
            data[(arg.start - self.range.start):(arg.start + arg.len - self.range.start)] = d
        self.data = bytes(data)

    def __iadd__(self, other):
        r = self.range | other.range
        if (self[self.range & other.range] != other[self.range & other.range]):
            warning("Data mismatch, new overlapping data will be ignored")

        if other.range in self.range:
            pass
        elif self.range in other.range:
            self.data = other.data[:(self.range.start - other.range.start)] + self.data + other.data[(self.range.end + 1 - other.range.start):]
        elif (self.range.start < other.range.start):
            self.data = self.data + other.data[(self.range.end + 1 - other.range.start):]
        elif (self.range.end > other.range.end):
            self.data = other.data[:(self.range.start - other.range.start)] + self.data
        else: #pragma: no cover
            raise RuntimeError(f'Could not merge {self.range} and {other.range}')
        self.range = r
        return self

    def __repr__(self): #pragma: no cover
        return f'Response{self.range!r}'

    @staticmethod
    def merge(answers):
        answers.sort(key=lambda a: a.range.start)

        a = 0
        while (a + 1 < len(answers)):
            try:
                answers[a] += answers[a + 1]
                del(answers[a + 1])
            except ValueError:
                a = a + 1

        return answers


class Frame:
    class Operation(Enum):
        GetRecord = 0x01
        GetParameter = 0x03
        SetParameter = 0x04

    def __init__(self, op, offset, *args):
        if type(op) is not Frame.Operation:
            raise ValueError(f"Invalid operation: {op}")
        self.__op = op

        if (offset < 0) or (offset > 0xFFFFFF):
            raise ValueError(f"Invalid offset: {offset}")
        self.__offset = offset

        if type(args[0]) is bytes:
            if (len(args[0]) > 51):
                raise ValueError(f"Too much data: {len(args[0])}")
            self.__len = len(args[0])
            self.__data = args[0]
        elif type(args[0]) is int:
            if (args[0] <= 0) or (args[0] > 51):
                raise ValueError(f"Invalid length: {args[0]}")
            self.__len = args[0]
            self.__data = []
        else:
            raise TypeError(f"Invalid type for data or length: {type(args[0])}")

    def __bytes__(self):
        o, l = self.__correctRange()
        frame = [0x33, 0xCC, 0x00, None, self.__op.value, 0x00, 0x00, (o >> 8) & 0xFF, o & 0xFF, o >> 16, l & 0xFF] + [b for b in self.__data]
        frame[3] = len(frame) + 1
        return bytes([0] + frame + [sum(frame) & 0xFF])

    def __repr__(self): #pragma: no cover
        if self.__data:
            data = ' '.join([f'{b:02X}' for b in self.__data])
            return f"Frame({self.__op}, {self.__offset}, [{data}])"
        else:
            return f"Frame({self.__op}, {self.__offset}, {self.__len})"

    def parse(self, answer):
        if (len(answer) < 11):
            raise ValueError(f"Anwser does not contain header: len(answer) = {len(answer)}")
        if (answer[0:3] != bytes([0x33, 0xCC, 0x00])):
            header = ' '.join([f'{b:02X}' for b in answer[0:3]])
            raise ValueError(f"Invalid answer header: {header}")
        if (answer[4] != self.__op.value):
            raise ValueError(f"Answer operation does not match: {answer[4]:02X}")

        o, l = self.__correctRange()
        if (self.__op == Frame.Operation.SetParameter):
            l = 1

        if ((answer[9] << 16) + (answer[7] << 8) + answer[8] != o):
            warning(f"Answer offset does not match: {(answer[9] << 16) + (answer[7] << 8) + answer[8]} != {o}")
            o = (answer[9] << 16) + (answer[7] << 8) + answer[8]
        if (answer[10] != l):
            warning(f"Answer length does not match: {answer[10]} != {l}")
            l = answer[10]

        if (len(answer) < 11 + l):
            raise ValueError(f"Anwser does not contain data: {len(answer)} < {11 + l}")

        if (len(answer) >= answer[3]):
            if (answer[answer[3] - 1] != sum(answer[:(answer[3] - 1)]) & 0xFF):
                warning(f"Invalid answer checksum: {answer[answer[3] - 1]:02X} != {sum(answer[:(answer[3] - 1)]) & 0xFF:02X}")
        else:
            warning("Answer does not have a checksum")

        if (self.__op == Frame.Operation.SetParameter):
            return (answer[11] == 1)
        elif (self.__op == Frame.Operation.GetRecord):
            if Range(self.__offset, self.__len) in Range(o, l):
                return Response(Range(8*self.__offset, 8*self.__len), answer[(11 + 8*(self.__offset - o)):(11 + 8*(self.__offset - o + self.__len))])
            else:
                return Response(Range(8*o, 8*l), answer[11:(11 + 8*l)])
        else:
            if Range(self.__offset, self.__len) in Range(o, l):
                return Response(Range(self.__offset, self.__len), answer[(11 + self.__offset - o):(11 + self.__offset - o + self.__len)])
            else:
                return Response(Range(o, l), answer[11:(11 + l)])

    def __correctRange(self):
        if (self.__op == Frame.Operation.GetParameter) and (self.__len == 1):
            return max(0, self.__offset - 1), 2
        return self.__offset, self.__len



