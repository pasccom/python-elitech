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

import unittest

from PythonUtils import testdata

import warnings

from elitech.src.device import WarningFilter

class TestWarning1(Warning):
    pass

class TestWarning2(Warning):
    pass

class TestWarningFilter(unittest.TestCase):
    @testdata.TestData([
        {'cls': TestWarning1},
        {'cls': TestWarning2},
    ])
    def testAll(self, cls):
        with warnings.catch_warnings(record=True) as w:
            with WarningFilter():
                warnings.warn(cls('test'))
        self.assertEqual(len(w), 0)

    @testdata.TestData([
        {'cls': TestWarning1},
        {'cls': TestWarning2},
    ])
    def testFilter(self, cls):
        with warnings.catch_warnings(record=True) as w:
            with WarningFilter(cls):
                warnings.warn(cls('test'))
        self.assertEqual(len(w), 0)

    @testdata.TestData([
        {'cls1': TestWarning1, 'cls2': TestWarning2},
        {'cls1': TestWarning2, 'cls2': TestWarning1},
    ])
    def testNoFilter(self, cls1, cls2):
        with warnings.catch_warnings(record=True) as w:
            with WarningFilter(cls1):
                warnings.warn(cls2('test'))
        self.assertEqual(len(w), 1)
        self.assertEqual(w[0].category, cls2)

