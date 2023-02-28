from .device import Device
from .parameters import Parameters
from .parameters import Range
from .frames import Frame
from .frames import Response
from .record import Record

from warnings import warn as warning

import sys
import textwrap

class UnknownCommandError(ValueError):
    def __init__(self, cmd):
        super().__init__(f"Unknown command '{' '.join(cmd)}'")

class MetaCommand(type):
    def __call__(cls, *args):
        try:
            return super().__call__(*args)
        except UnknownCommandError:
            pass

        assert len(args) == 1
        args = args[0]

        for subClass in cls.__subclasses__():
            try:
                subClassCmd = subClass.cmdName
            except AttributeError: #pragma: no cover
                continue
            if type(subClassCmd) is str:
                subClassCmd = (subClassCmd,)
            if all([cmd == subCmd for cmd, subCmd in zip(args.cmds, subClassCmd)]):
                params = args.cmds[len(subClassCmd):]
                delattr(args, 'cmds')
                return subClass.__call__(args, *params)
                #return cls.__create(subClass, args, len(subClassCmd))

        return super().__call__(args)

    # def __create(cls, subClass, args, skip):
    #     try:
    #         subClassUsesDev = subClass.usesDevice
    #     except AttributeError:
    #         subClassUsesDev = False
    #
    #     params = args.cmds[skip:]
    #     return subClass.__call__(Device(args.dev), *params)
    #     if subClassUsesDev:
    #         if not args.dev:
    #             warning(f"A device is required to really run '{' '.join(args.cmds[0:skip])}'")
    #         return subClass.__call__(Device(args.dev), *params)
    #     else:
    #         if args.dev:
    #             warning(f"A device is not needed to run '{' '.join(args.cmds[0:skip])}'")
    #         return subClass.__call__(*params)

class Command(metaclass=MetaCommand):
    def __init__(self, args):
        raise UnknownCommandError(args.cmds)

class Help(Command):
    '''Give help on command 'command'.'''

    cmdName = 'help'
    cmdArgs = 'command'

    def __init__(self, args, *params):
        self.__params = params

    @staticmethod
    def __cmdName(cmd):
        if type(cmd.cmdName) is str:
            return cmd.cmdName
        elif type(cmd.cmdName) is tuple:
            return ' '.join(cmd.cmdName)

    @staticmethod
    def __cmdArgs(cmd):
        try:
            return cmd.cmdArgs
        except AttributeError:
            return ''

    def execute(self):
        class Namespace:
            pass

        cmd = None
        if (len(self.__params) > 0):
            args = Namespace()
            setattr(args, 'cmds', self.__params)
            setattr(args, 'dev', '')
            try:
                cmd = Command(args)
            except ValueError:
                #try:
                #    setattr(args, 'dev', '_')
                #    cmd = Command(args)
                #except ValueError:
                params = ' '.join(self.__params)
                print(f"{sys.argv[0]} does not have a command named \"{params}\"\n")

        if cmd is None:
            print("Available commands:")
            for cmd in Command.__subclasses__():
                print(f'  - {Help.__cmdName(cmd)} {Help.__cmdArgs(cmd)} ({cmd.__doc__.strip().splitlines()[0]})')
        else:
            print(textwrap.dedent(f'''
                {sys.argv[0]} {Help.__cmdName(cmd)} {Help.__cmdArgs(cmd)}
                    {textwrap.dedent(cmd.__doc__)}
            ''').strip())

    def __repr__(self):
        params = '", "'.join(self.__params)
        return f'HelpCommand("{params}")'


class DeviceList(Command):
    '''
        List available Elitech devices

        Prints a table with the following columns:
          - Path in '/dev/' tree
          - Name of the device
    '''

    cmdName = ('device', 'list')

    def __init__(self, args, *params):
        if (len(params) > 0):
            params = '", "'.join(params)
            warning(f"Ignored parameters: \"{params}\"")

    def execute(self):
        print('Available devices:')
        for device in Device.enumerate():
            print(f'{device.path}: {device.name} ({device.vendorId:04x}:{device.productId:04x})')

    def __repr__(self):
        return 'DeviceListCommand'


class ParameterList(Command):
    '''
        List available parameters and their meanings
    '''

    cmdName = ('parameter', 'list')

    def __init__(self, args, *params):
        if (len(params) > 0):
            params = '", "'.join(params)
            warning(f"Ignored parameters: \"{params}\"")

    def execute(self):
        print('Available parameters:')
        for param in Parameters():
            print(f'  - {param.name}: {param.description}')

    def __repr__(self):
        return 'ParameterListCommand'


class ConfigRead(Command):
    '''
        Read configuration parameters from an Elitech device

        The implementation will send the minimum number of commands to get the parameters
    '''

    cmdName = ('parameter', 'get')
    cmdArgs = 'parameter ...'

    def __init__(self, args, *params):
        self.__dev = Device(args.dev)
        self.__params = []
        parameters = Parameters()
        for p in params:
            try:
                self.__params.append(parameters[p])
            except KeyError:
                warning(f"Ignoring unknown parameter: {p}")

        if (len(self.__params) == 0) and (len(params) != 0):
            raise ValueError(f"All parameters have been ignored")

    def execute(self):
        ranges = Range.optimize([p.range for p in self.__params])
        print(ranges)

        answers = []
        for r in ranges:
            frame = Frame(Frame.Operation.GetParameter, r.start, r.len)
            with self.__dev:
                self.__dev.write(bytes(frame))
                try:
                    answers.append(frame.parse(self.__dev.read()))
                except ValueError as e:
                    warning(f"Got invalid response ({str(e)})")
        answers = Response.merge(answers)
        for p in self.__params:
            for a in answers:
                if p.range in a.range:
                    print(f'{p.name}: {p.parseData(a[p.range])}')
                    break


    def __repr__(self):
        if (len(self.__params) == 0):
            params = '*'
        else:
            params = '", "'.join([p.name for p in self.__params])
        return f'ConfigReadCommand({self.__dev}, "{params}")'


class AddressRead(Command):
    '''
        Read data by address in an Elitech device

        The addresses can be given as single address or address ranges.

        The implementation will send the minimum number of commands to read the addresses.
    '''

    cmdName = ('address', 'get')
    cmdArgs = 'range ...'

    def __init__(self, args, *params):
        self.__dev = Device(args.dev)
        self.__ranges = [Range.fromString(p) for p in params]

    def execute(self):
        ranges = Range.optimize(self.__ranges)
        print(ranges)

        answers = []
        for r in ranges:
            frame = Frame(Frame.Operation.GetParameter, r.start, r.len)
            with self.__dev:
                self.__dev.write(bytes(frame))
                try:
                    answers.append(frame.parse(self.__dev.read()))
                except ValueError as e:
                    warning(f"Got invalid response ({str(e)})")
        answers = Response.merge(answers)
        for r in self.__ranges:
            for a in answers:
                if r in a.range:
                    data = ' '.join([f'{b:02X}' for b in a[r]])
                    print(f'{r}: {data}')
                    break

    def __repr__(self):
        return f'AddressReadCommand({self.__dev}, {self.__ranges})'


class ConfigWrite(Command):
    '''
        Modify configuration parameters to an Elitech device

        Paramters and values can be given as parameter=value pairs (without spaces around equal sign)
        or parameter value (without equal sign).

        The implementation will send the minimum number of commands to set the parameters.
    '''

    cmdName = ('parameter', 'set')
    cmdArgs = 'parameter=value | parameter value ...'

    def __init__(self, args, *params):
        self.__dev = Device(args.dev)

        if (len(params) == 0):
            raise ValueError(f"No parameters were given")

        self.__params = []
        parameters = Parameters()
        i = 0
        while (i < len(params)):
            if '=' in params[i]:
                p, equals, v = params[i].partition('=')
                i = i + 1
            elif (i < len(params) - 1):
                p = params[i]
                v = params[i + 1]
                i = i + 2
            else:
                warning(f"Ignoring parameter without value: {params[i]}")
                break

            try:
                self.__params.append(parameters[p])
            except KeyError:
                warning(f"Ignoring unknown parameter: {p}")
                break

            if not self.__params[-1].writable:
                warning(f"Read-only parameter: {self.__params[-1].name}")
                del(self.__params[-1])
                break

            try:
                self.__params[-1].parseValue(v)
            except ValueError:
                warning(f"Invalid value for parameter: {self.__params[-1].name}")
                del(self.__params[-1])
                break

        if (len(self.__params) == 0):
            raise ValueError(f"All parameters have been ignored")

    def execute(self):
        ranges = Range.optimize([p.range for p in self.__params])
        print(ranges)

        answers = []
        for r in ranges:
            frame = Frame(Frame.Operation.GetParameter, r.start, r.len)
            with self.__dev:
                self.__dev.write(bytes(frame))
                try:
                    answers.append(frame.parse(self.__dev.read()))
                except ValueError as e:
                    warning(f"Got invalid response ({str(e)})")
        answers = Response.merge(answers)
        for p in self.__params:
            for a in answers:
                if p.range in a.range:
                    a[p.range] = bytes(p | a[p.range])
        print(answers)
        for r1 in ranges:
            parameters = Parameters()
            if parameters['configuration-time'].range not in r1:
                splitRanges = [r1]
            elif parameters['configuration-time'] in self.__params:
                splitRanges = [r1]
            else:
                splitRanges = r1 - parameters['configuration-time'].range

            for r2 in splitRanges:
                for a in answers:
                    if r2 in a.range:
                        frame = Frame(Frame.Operation.SetParameter, r2.start, a[r2])
                        with self.__dev:
                            self.__dev.write(bytes(frame))
                            try:
                                result = frame.parse(self.__dev.read())
                            except ValueError as e:
                                warning(f"Got invalid response ({str(e)})")
                            if not result:
                                params = ', '.join([p.name for p in self.__params if p.range in r2])
                                warning(f"Could not write parameter(s): {params}")

    def __repr__(self):
        params = '", "'.join([p.name + '=' + str(p) for p in self.__params])
        return f'ConfigWriteCommand({self.__dev}, "{params}")'


class AddressWrite(Command):
    '''
        Write data by address in an Elitech device

        The addresses can be given as single address or address ranges, the data is given as integers representing bytes.

        The implementation will send the minimum number of commands to write the data at the given addresses.
    '''

    cmdName = ('address', 'set')
    cmdArgs = 'range data ...'

    def __init__(self, args, *params):
        self.__dev = Device(args.dev)
        p = 0
        self.__ranges = []
        self.__data = []
        while (p < len(params)):
            r = Range.fromString(params[p])
            p = p + 1
            if (p + r.len > len(params)):
                raise ValueError(f"Not enough data for range: {r}")
            self.__ranges.append(r)
            self.__data.append(bytes([AddressWrite.parseByte(p) for p in params[p:(p + r.len)]]))
            p = p + r.len

    def execute(self):
        ranges = Range.optimize(self.__ranges)
        print(ranges)

        answers = []
        for r in ranges:
            frame = Frame(Frame.Operation.GetParameter, r.start, r.len)
            with self.__dev:
                self.__dev.write(bytes(frame))
                try:
                    answers.append(frame.parse(self.__dev.read()))
                except ValueError as e:
                    warning(f"Got invalid response ({str(e)})")
        answers = Response.merge(answers)
        for r, d in zip(self.__ranges, self.__data):
            for a in answers:
                if r in a.range:
                    a[r] = d
        print(answers)
        for r in ranges:
            for a in answers:
                if r in a.range:
                    frame = Frame(Frame.Operation.SetParameter, r.start, a[r])
                    with self.__dev:
                        self.__dev.write(bytes(frame))
                        try:
                            result = frame.parse(self.__dev.read())
                        except ValueError as e:
                            warning(f"Got invalid response ({str(e)})")
                        if not result:
                            params = ', '.join([p.name for p in self.__params if p.range in r])
                            warning(f"Could not write parameter(s): {params}")

    def __repr__(self):
        data = [[f'{b:02X}' for b in d] for d in self.__data]
        rangeData = ', '.join([f'{r}={d}' for r, d in zip(self.__ranges, self.__data)])
        return f'AddressWriteCommand({self.__dev}, [{rangeData}])'

    @staticmethod
    def parseByte(s):
        if (len(s) > 2) and s.startswith('0x'):
            b = int(s[2:], 16)
        elif (len(s) > 2) and s.startswith('0b'):
            b = int(s[2:], 2)
        elif (len(s) > 1) and s.startswith('0'):
            b = int(s[1:], 8)
        elif (len(s) > 0):
            b = int(s)
        if (b < 0) or (b > 0xFF):
            raise ValueError(f"Invalid byte value: {s}")
        return b



class RecordRead(Command):
    '''
        Read and interpret records from an Elitech device
    '''

    cmdName = ('record', 'get')
    cmdArgs = '[firstRecord:recordStep:lastRecord]'

    def __init__(self, args, *params):
        self.__dev = Device(args.dev)
        if (len(params) == 0):
            self.__range = slice(None, None, 1)
        elif (len(params) == 1):
            self.__range = RecordRead.sliceFromString(params[0])
        if (len(params) > 1):
            params = '", "'.join(params[1:])
            warning(f"Ignored parameters: \"{params}\"")

    def execute(self):
        answers = []
        r = self.__range.start or 0
        s = self.__range.step or 1
        while (self.__range.stop is None) or (r < self.__range.stop):
            n = 51 // Record.Length
            if (self.__range.stop is not None) and (r + n > self.__range.stop):
                n = self.__range.stop - r
            l = ((n + s - 1) // s) * s + 1 - s
            print((r, l, n))

            frame = Frame(Frame.Operation.GetRecord, r, l)
            with self.__dev:
                self.__dev.write(bytes(frame))
                try:
                    answers.append(frame.parse(self.__dev.read()))
                except ValueError as e:
                    warning(f"Got invalid response ({str(e)})")
            if (self.__range.stop is None) and (len(answers) != 0) and all([b == 0xFF for b in answers[-1][(8*r):(8*(r + n))]]):
                del(answers[-1])
                break
            r += ((n + s - 1) // s) * s

        r0 = self.__range.start or 0
        s = self.__range.step or 1
        for a in answers:
            r = r0
            while (8*(r - r0) < a.range.len):
                record = Record.parse(a[(8*r):(8*(r + 1))])
                if record is None:
                    if self.__range.stop is None:
                        break
                    print(f"{r + 1:-4d}\t---------- --------\tNo data")
                elif (record.flags & Record.Flags.Pause):
                    print(f"{r + 1:-4d}\t{record.time}\tPause")
                elif record.humidity is None:
                    print(f"{r + 1:-4d}\t{record.time}\t{record.temperature:.1f}°C")
                else:
                    print(f"{r + 1:-4d}\t{record.time}\t{record.temperature:.1f}°C\t{record.humidity:.1f}%")
                r += s
            r0 = r


    def __repr__(self):
        r = self.__range or '*'
        return f'RecordReadCommand({self.__dev}, {r})'

    @staticmethod
    def sliceFromString(s):
        parts = s.split(':')

        if (len(parts) == 1):
            if parts[0]:
                return slice(int(parts[0]) - 1, int(parts[0]))
            else:
                return slice(None, None)
        elif (len(parts) == 2):
            if (parts[0] and parts[1]):
                return slice(int(parts[0]) - 1, int(parts[1]))
            elif parts[0]:
                return slice(int(parts[0]) - 1, None)
            elif parts[1]:
                return slice(None, int(parts[1]))
            else:
                return slice(None, None)
        elif (len(parts) == 3):
            if not parts[1]:
                raise ValueError(f'Invalid record selection: {s}')
            if (parts[0] and parts[2]):
                return slice(int(parts[0]) - 1, int(parts[2]), int(parts[1]))
            elif parts[0]:
                return slice(int(parts[0]) - 1, None, int(parts[1]))
            elif parts[2]:
                return slice(None, int(parts[2]), int(parts[1]))
            else:
                return slice(None, None, int(parts[1]))
        else:
            raise ValueError(f'Invalid record selection: {s}')

