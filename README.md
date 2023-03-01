REPOSITORY DESCRIPTION
----------------------
This repository contains a pure python client library for [Elitech](https://www.elitechlog.com/)
data loggers (see [Supported devices](#supported-devices) for a detailed list).

The information on the communication protocol used by [Elitech](https://www.elitechlog.com/)
data loggers (using the USB HID interface) has been obtained by reverse engineering
the official Windows software using [Ghidra](https://ghidra-sre.org/)
(with an unpublished custom plugin to disassemble CIL).

FEATURES
--------
*python-elitech* can be used in two ways:
  - Using the embedded CLI (Command Line Interface) from a Linux shell,
see [Usage](#cli)
  - As a library of a larger application, see the documentation
(yet to be done)

It supports the following operations:
  - Locating [supported Elitech devices](#supported-devices)
  - Getting parameters
  - Setting parameters
  - Downloading recorded data

REQUIREMENTS
------------
## Supported devices
The following Elitech devices are supported. The software relies on the USB
vendor and product identifiers, as listed in the second and third colums
of the following table, to identify supported devices. Currently, 
*python-elitech* has only been tested on an RC-5+, as indicated in the last
column of the below table.

| Name                         | Vendor Id  | Product Id | udev | Tested |
|:-----------------------------|:----------:|:----------:|:----:|:------:|
| Elitech RC-51                |   0x04d8   | 0x0033     | Yes  | No     |
| Elitech RC-51H               |   0x04d8   |   0x0133   | Yes  | No     |
| Elitech RC-5+                |   0x04d8   |   0x3005   | Yes  | Yes    |
| Elitech RC-55                |   0x04d8   |   0x0037   | Yes  | No     |
| Elitech TemLog 20            |   0x04d8   |   0x1014   | Yes  | No     |
| Elitech TemLog 20H           |   0x04d8   |   0x1114   | Yes  | No     |
| Elitech RC-18                |   0x04d8   |   0x0012   | Yes  | No     |
| Elitech RC-19                |   0x04d8   |   0x0013   | Yes  | No     |
| Elitech ST5                  |   0x04d8   |   0x1005   | Yes  | No     |
| Elitech LogEt 6              |   0x0416   |   0x3006   | Yes  | No     |
| Elitech LogEt 8              |   0x0416   |   0x4008   | Yes  | No     |
| Elitech LogEt 8 Life Science |   0x0416   |   0x4308   | Yes  | No     |
| Elitech LogEt 8 Food         |   0x0416   |   0x3008   | Yes  | No     |
| Elitech MSL-51               |   0x04d8   |   0x2033   | Yes  | No     |
| Elitech MSL-51H              |   0x04d8   |   0x2133   | Yes  | No     |
| Elitech LogEt 1              |   0x0416   |   0x0001   | Yes  | No     |
| Elitech LogEt 1TH            |   0x0416   |   0x0101   | Yes  | No     |
| Elitech LogEt 1Bio           |   0x0416   |   0x0201   | Yes  | No     |
|                              |   0x04d8   |   0xF564   | Yes  | No     |
|                              |   0x0416   |   0x3A01   | Yes  | No     |
|                              |   0x464d   |   0x0402   | No   | No     |

If your device is not in this list:
  - Either it is an Elitech device of the previous generation, which used
an USB to serial chip: This is supported under linux by the project
[elitech-datareader](https://github.com/civic/elitech-datareader),
  - Or it is a newer device for which partial support is possible. You can test
at your own risks (As stated in [Licensing information](#LICENSING-INFORMATION),
I do not guarantee anything, your device may even be damaged).

## Supported Platforms
Due to the use of the `\dev` and `\sys` trees, this software will run only under Linux.


USAGE
-----
## Installation
After you downloaded *python-elitech*, no further installation steps are required
as the (lightweight) dependences are provided as submodules for simplicity.

Nevertheless, it is ***highly*** recommended that you add the [rules](60-elitech.rules)
to `udev`. This can be done by simply copying (as root) this file
to `/etc/udev/rules.d` (or any other place that is recommended for local admin
configuration by your distribution). The priority of the rules can be adjusted
by changing the numeric part of the file name. I used priority 60, as it seemed
to be fine on my system.

These rules will change the group of the Elitech HID devices, detected using
the vendor identifiers (for details see the fourth column of the table of
[Supported devices](#supported-devices)), in the `/dev` tree
to `dialout` group (instead of `root`). The `dialout` group seemed fine
on my system, but any other existing group can be chosen by editing the file.
This will enable a stadard user, provided he is a member of the `dialout` group,
to access the device.

## CLI
The CLI interface can be invoked using `python elitech [command]`
in the project root directory (which contains this README).

### Help
Available commands can be listed using
```sh
$ python elitech help
```
Embedded help on a command can be obtained using
```sh
$ python elitech help [command]
```

### Devices
The list of supported devices can be obtained with
```sh
$ python elitech devices list
```

### Parameters
The list of supported parameters (with their meaning) can be obtained with
```sh
$ python elitech parameters list
```

To get the current values for given parameters from a device, use
```sh
$ python elitech --device [/dev/path] parameters get [parameter-name]
```
where `/dev/path` stands for the path to the HID device. Similarly, a parameter
can be set into a device using
```
$ python elitech --device [/dev/path] parameters set [parameter-name] [value]
```
Multiple parameters or multiple parameter/value pairs can be get or set
in a single command.

Notice that the `device-time` is read-only and the device time is effectively
set by setting the `configuration-time` parameter. This can simply be done with
```sh
$ python elitech --device [/dev/path] parameters get configuration-time "$(date '+%Y-%m-%d %H:%M:%S')"
```

### Records
The records can be read through the HID interface using
```sh
$ python elitech --device [/dev/path] record get [recordSlice]
```
For instance, to get all the records currently in the device memory, use
```sh
$ python elitech --device [/dev/path] record get 1:
```

### Address
For debugging purposes (for example, to configure an unsupported parameter,
or give a parameter an unsupported value), the configuration can directly be
accessed by address. To get the current values in a given address range, use
```sh
$ python elitech --device [/dev/path] parameters get [addressRange]
```

To set new values in a given address range, use
```sh
$ python elitech --device [/dev/path] parameters get [addressRange] [value ...]
```

PLANNED DEVELOPMENTS
--------------------
Of course, I plan to implement support for the parameters which are not yet
accessible easily. I also plan to implement the parameter address change
depending on device type and protocol version number.

The following new functionalities may be implemented in the future:
  - Better message format
  - New output formats for the returned data

Suggestions are, of course, welcome, but I remind you that this is only a hobby
project, consequently, do not expect any "professional grade" support from me.

LICENSING INFORMATION
---------------------
*python-elitech* is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

*python-elitech* is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with *python-elitech*. If not, see http://www.gnu.org/licenses/
