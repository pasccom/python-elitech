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

import argparse
from .commands import Command

def main():
    # Determine version from package information
    version = '0.0.1'
    try:
        import importlib.metadata
        importlib.metadata.version('elitech')
    except ImportError:
        pass
    except importlib.metadata.PackageNotFoundError:
        pass

    # Parse command line
    parser = argparse.ArgumentParser(description="Console tool to interact with Elitech temperature and humidity loggers")
    parser.add_argument('-d', '--dev', '--device', action='store', default='',
                        help='The device to interact with')
    parser.add_argument('-c', '--compat', action='store_const', const=True, default=False,
                        help='Forces to write all parameters (as Elitech official software does). Should not be needed')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)
    parser.add_argument('cmds', action='extend', nargs='+',
                        help="The commands to execute. To see help on a specific command, use the 'help' command.")
    args = parser.parse_args()

    cmd = Command(args)
    print(cmd)
    cmd.execute()
