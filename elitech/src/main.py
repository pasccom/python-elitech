import argparse
from .commands import Command

def main(argv):
    parser = argparse.ArgumentParser(description="Console tool to interact with Elitech temperature and humidity loggers")
    parser.add_argument('-d', '--dev', '--device', action='store', default='',
                        help='The device to interact with')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.0')
    parser.add_argument('cmds', action='extend', nargs='+',
                        help="The commands to execute. To see help on a specific command, use the 'help' command.")
    args = parser.parse_args(argv)

    cmd = Command(args)
    print(cmd)
    cmd.execute()
