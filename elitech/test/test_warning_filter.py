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

