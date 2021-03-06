import unittest
from pitivi.settings import ExportSettings


class TestExportSettings(unittest.TestCase):
    """Test the settings.ExportSettings class."""

    def setUp(self):
        self.settings = ExportSettings()

    def testMasterAttributes(self):
        self._testMasterAttribute('muxer', dependant_attr='containersettings')
        self._testMasterAttribute('vencoder', dependant_attr='vcodecsettings')
        self._testMasterAttribute('aencoder', dependant_attr='acodecsettings')

    def _testMasterAttribute(self, attr, dependant_attr):
        """Test changing the specified attr has effect on its dependant attr."""
        attr_value1 = "%s_value1" % attr
        attr_value2 = "%s_value2" % attr

        setattr(self.settings, attr, attr_value1)
        setattr(self.settings, dependant_attr, {})
        getattr(self.settings, dependant_attr)["key1"] = "v1"

        setattr(self.settings, attr, attr_value2)
        setattr(self.settings, dependant_attr, {})
        getattr(self.settings, dependant_attr)["key2"] = "v2"

        setattr(self.settings, attr, attr_value1)
        self.assertTrue("key1" in getattr(self.settings, dependant_attr))
        self.assertFalse("key2" in getattr(self.settings, dependant_attr))
        self.assertEqual("v1", getattr(self.settings, dependant_attr)["key1"])
        setattr(self.settings, dependant_attr, {})

        setattr(self.settings, attr, attr_value2)
        self.assertFalse("key1" in getattr(self.settings, dependant_attr))
        self.assertTrue("key2" in getattr(self.settings, dependant_attr))
        self.assertEqual("v2", getattr(self.settings, dependant_attr)["key2"])
        setattr(self.settings, dependant_attr, {})

        setattr(self.settings, attr, attr_value1)
        self.assertFalse("key1" in getattr(self.settings, dependant_attr))
        self.assertFalse("key2" in getattr(self.settings, dependant_attr))

        setattr(self.settings, attr, attr_value2)
        self.assertFalse("key1" in getattr(self.settings, dependant_attr))
        self.assertFalse("key2" in getattr(self.settings, dependant_attr))
