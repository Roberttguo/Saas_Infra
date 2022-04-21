import json
import os
import unittest
from HCXSaasRestExt import HCXSaasRestExt
from Util import PrecheckSites

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'testdata.json')

class PreflightTestCase(unittest.TestCase):

    def setUp(self):
        self.testfile = open(TESTDATA_FILENAME)
        self.testdata=json.load(self.testfile)

    def test_precheck_sites(self):
        pass

    def test_Dev_Stack_Cleanup(self):
        self.testdata["csp_url"]
        obj=HCXSaasRestExt(self.testdata["csp_url"],self.testdata["api_token"])
        obj.cleanup_sites(self.testdata["dev_stack"],self.testdata["org_id"], "DISCONNECTED")
        result=obj.size_of_sites(self.testdata["dev_stack"],self.testdata["org_id"])==0
        self.assertEqual(True, result)


if __name__ == '__main__':
    unittest.main()
