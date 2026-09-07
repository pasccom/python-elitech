RC-5 (HID) — protocol notes and reverse-engineering log
=======================================================

This document records what is known about the recent **Elitech RC-5**
(USB id `246c:9001`, reported as *FMSH MSC+HID*), the temperature logger that
replaced the USB-to-serial RC-5 with a USB HID interface. It reports **protocol
version 0x35** and firmware `0x21` on the unit used here.

The **RC-5+ with a recent firmware** (USB id `04d8:3005`, protocol version 0x38,
firmware V5.2) belongs to the same generation: as reported in
[issue #1](https://github.com/pasccom/python-elitech/issues/1) it hit the same
configuration-write failure, and the maintainer's analysis of the new official
software matches the findings below. Everything here that is gated on
"protocol version >= 0x30" therefore applies to it as well, whereas the older
RC-5+ (protocol version around 0x24, which accepts partial writes and uses the
old record layout) is left untouched.

Unless stated otherwise, everything below was obtained either by probing the
device directly, or by reading `ElitechLogWin` 8.0.5.0 (`DL.exe`, which ships a
full `DL.pdb`) with `monodis`. The relevant classes are
`ElitechLog.Devices.Usb.{DataFactory,UsbCommand,hid}` and
`ElitechLog.Monitor.CUSB`.

The device also exposes a USB mass-storage interface (a 128 KB FAT12 volume
labelled "Data Logger"). On the plain RC-5 it stays empty: the automatic PDF
report is an RC-5+/TE feature. It is not used by this library.


Transport and frames
---------------------
The RC-5 speaks the same frame format as the RC-5+. A request is a 64-byte HID
report:

    33 CC 00 LL OP EX 00 OH OL OX NN <data...> CK

  - `33 CC 00`   fixed header
  - `LL`         frame length (header + data + checksum), i.e. index of `CK` + 1
  - `OP`         operation (low byte), `EX` its high byte / "extended command"
  - `OH OL OX`   offset, big-endian in the first two bytes, third byte is bits 16-23
  - `NN`         data length
  - `CK`         checksum = sum of all preceding bytes, low byte

Operations seen in the official software (`RcCommandType` and the command
builders in `DataFactory`):

  | Operation             | `OP` | `EX` | Notes                                       |
  |:----------------------|:----:|:----:|:--------------------------------------------|
  | GetRecord             | 0x01 |  --  | `EX` is an "extended command" (0 in practice)|
  | GetParameter (main)   | 0x03 | 0x00 | reads the main config space                 |
  | SetParameter          | 0x04 | 0x00 | writes the main config space                |
  | GetParameter (shadow) | 0x05 | 0x00 | reads a second "shadow" space (see below)   |
  | FormatCommand         | 0xC0 | 0x02 | i.e. operation 0x02C0                        |
  | StopCommand           | 0xC0 | 0x03 | i.e. operation 0x03C0                        |
  | FirmwareUpdate        | 0x11 | ...  | not implemented here                        |

The device is not required to answer. When a record beyond the ones it holds is
requested, it stays silent, so reads must time out (`Device.ReadTimeout`).


Two address spaces
------------------
Operation 0x03 and operation 0x05 read **different** memory:

  - **Main space** (op 0x03 / written with op 0x04): the configuration and the
    parameters exposed by this library.
  - **Shadow space** (op 0x05, read only as far as is known): a second image
    holding, among other things, the record count at offset **0x85** and the
    time of the last record around 0x88. `format` clears it (see below).

The device serves both spaces as a **frozen snapshot** most of the time: after a
configuration is written, or while recording, the values read back (clock,
record count, device state) keep the values they had at that moment and stop
tracking reality. The LCD is the ground truth for the device state, not the
values read over USB. Writing the last configuration block at 0x13C (see below)
is what keeps the snapshot live for a while.


Configuration write
-------------------
The RC-5 **discards a partial configuration write**: a single-block write is
acknowledged, can be read back, and is then reverted a few seconds later. Only a
write of the whole configuration is committed. `DataFactory.GetListForSet` of the
official software writes it in these blocks (operation 0x04), in this order:

    [0x00, 0x30)  [0x30, 0x30)  [0x60, 0x30)  [0x98, 0x34)
    [0xCC, 0x30)  [0xFD, 0x2F)  [0x13C, 0x19)

Each block is 64 bytes with the checksum at index 59 (sum of bytes 0..58). This
library writes them via `--compat`, which is implied for the RC-5.

Notes obtained the hard way:

  - The 25 bytes at **0x13C** are the device name. Writing this block is what
    keeps the served configuration snapshot live; without it the record count,
    the device state and `device-time` freeze at the moment of the write.
  - The **device state** bytes (`0x25`, `0x26`) are **not writable**: the device
    overwrites them with its own state within ~15 s. They cannot be used to start
    or arm the device. Observed values of 0x25: `0x04` ready, `0xC4`/`0x09`
    stopped-ish, `0xC7` recording (the high nibble varies with the snapshot).
  - The RC-5 does **not** derive its clock from `configuration-time`; the clock
    (`device-time`, 0x88) has to be written together with the configuration.
  - Writing any configuration **deletes the records**, as the official software
    warns.
  - A date and time is 7 bytes: `YY MM DOW DD hh mm ss`, the third byte being the
    day of the week counted from Sunday (`DateTime.DayOfWeek`).
  - Non-written bytes are left **erased (0xFF)**, not blank (0x00). This is why
    `device-capacity` reads e.g. `0xFFFF7D00` (= 32000) and why unset dates and
    strings must tolerate 0xFF.


Device state
------------
The byte at 0x25 (masked to 7 bits) is the device state. The values were
contributed by SarangKulkarni in
[issue #1](https://github.com/pasccom/python-elitech/issues/1) and match the
RC-5 seen here. The RC-5 sets bit 6, the RC-51H and the RC-5+ do not; the low
bits are shared:

  | State           | RC-51H / RC-5+ | RC-5   |
  |:----------------|:--------------:|:------:|
  | Configured      | 0b0000100      | 0b1000100 |
  | Start delay     | 0b0000101      | 0b1000101 |
  | Logging         | 0b0000111      | 0b1000111 |
  | Stopped         | 0b0001001      | 0b1001001 |

The state byte is served by the device and cannot be written (see above).


Records
-------
Records are read with GetRecord (op 0x01), `offset` = first record index,
`length` = number of records. **Records are only served once the device is
stopped** and holds finalised data; a recording or freshly configured device
answers "no record". The count is at 0x85 in the shadow space (and, on older
devices, around 0x4A/0x5A in the main space).

The record layout for protocol >= 0x30 (the RC-5, 0x35) is
`DataFactory.ParseRecord`, which is **not** the layout of the older devices.
For an 8-byte record `b0..b7`:

  - `b0` bit0 mark, bit1 pause, bit2 stop, bit4 light, bit5 vibration,
    **bit3 = temperature sign**, **bit6 = humidity sign**, bit7 set on every
    record of this device (it is not an error flag).
  - time: `second=(b1>>2)&0x3F`, `year=2000+(b2&0x7F)`,
    `month=((b3&7)<<1)|((b2>>7)&1)`, `day=(b3>>3)&0x1F`, `hour=b4&0x1F`,
    `minute=b6&0x3F`.
  - temperature (tenths of a degree): `(((b1>>1)&1)<<11) | (b5<<3) | (b4>>5)`,
    negated if `b0` bit3 is set.
  - humidity (tenths of a percent): `(b7<<2) | (b6>>6)`, negated if `b0` bit6.
  - the values -100.0, -101.0, -111.0, -1001.0, -1002.0, -1003.0 mean "no
    reading": for the temperature-only RC-5 the humidity is -100.0 and is
    reported as no humidity.

Verified against an RC-5: two records read back as 31.7 degC at
2026-09-06 17:25:52 and 32.1 degC at 2026-09-06 17:40:52.


Stopping, formatting and resetting
----------------------------------
A stopped RC-5 **cannot be restarted by its button** (the *Repeat start*
function is RC-5+/RC-5+TE only). It must be reconfigured, which the official
software calls "Quick Reset" (internal string `QUICKFORMAT`).

`QUICKFORMAT` is the ordinary configuration write **followed by a format**. The
official state machine (`UsbCommand.SetParameter` response handling in
`CUSB.Device_DataReceived`, `CmdType == 2`) sends the configuration blocks one
by one, and **after the last block it sends `FormatCommand`**. The order is
essential: a `format` on its own, or before the configuration, does nothing
useful; only a `format` sent after a full configuration write clears the shadow
record count at 0x85.

The sequence that re-arms a stopped RC-5 from Linux, verified on the device:

  1. Write the whole configuration (all blocks above), with a valid state,
     `device-time` set to now, and the record counters zeroed.
  2. Send `FormatCommand`. This clears the records and the shadow count, and
     erases the main configuration space (it reads back 0xFF).
  3. Write the whole configuration again (the format erased it).

After step 3 the STOPPED indicator disappears and the device is armable again;
pressing the left button for 5 s then starts a recording. A replug is not
required, though it does no harm.


Tooling used
------------
  - `monodis` (mono-utils) to read the IL and metadata tables of `DL.exe`.
    `DL.pdb` provides the original source file names.
  - `innoextract` to unpack the Inno Setup installer.
  - A small pure-python ECMA-335 reader was used to extract method IL bodies
    that `monodis` could not fully disassemble (it stops on a class whose
    signature needs `System.Data`, which is not installed).


Open questions
--------------
  - Why the served configuration snapshot freezes, and exactly which event makes
    it live again.
  - The full meaning of the device-state byte at 0x25.
  - The layout of the shadow space beyond the record count at 0x85.
