import json
import os
import unittest

from HCXSaasRestExt import HCXSaasRestExt

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/testdata.json')
TESTBED_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/testbed_info.json')

class HCXSaasAdapaterTest(unittest.TestCase):

    def setUp(self):
        self.testfile = open(TESTDATA_FILENAME)
        self.testbedfile = open(TESTBED_FILENAME)
        self.testdata=json.load(self.testfile)
        self.testbed_info=json.load(self.testbedfile)
        sites=["onpremhcm1", "hmva"]
        hosts=self.testbed_info["hosts"]
        for x in sites:
            if x in hosts:
                self.urls.append("https://"+hosts[x]["fqdn"])

    def test_registe_site(self):