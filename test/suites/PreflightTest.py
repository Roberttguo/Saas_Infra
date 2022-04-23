import json
import os
import ssl
import time
import unittest

import Constant
import lib.HTMLTestRunner as HTMLTestRunner


from HCXSaasRestExt import HCXSaasRestExt
from util.PrecheckSites import PrecheckSites

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/testdata.json')
TESTBED_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/testbed_info.json')


class PreflightTestCase(unittest.TestCase):

    def setUp(self):
        self.precheck = False
        self.testfile = open(TESTDATA_FILENAME)
        self.testbedfile = open(TESTBED_FILENAME)
        self.testdata=json.load(self.testfile)
        self.testbed_info=json.load(self.testbedfile)
        self.urls=[]
        self.urls.append(self.testdata["csp_url"])
        if "https://" not in self.testdata["dev_stack"]:
            self.urls.append("https://"+self.testdata["dev_stack"])
        else:
            self.urls.append(self.testdata["dev_stack"])
        sites=["onpremhcm1", "hmva"]
        hosts=self.testbed_info["hosts"]
        for x in sites:
            if x in hosts:
                self.urls.append("https://"+hosts[x]["fqdn"])


    def test_precheck_sites(self):
        obj=PrecheckSites(self.urls)
        result=obj.checkUrls()
        self.precheck = result
        self.assertEqual(True, result)



    #@unittest.skipIf(not (this.precheck), "precheck failed.")
    def test_Dev_Stack_Cleanup(self):
        obj=HCXSaasRestExt(self.testdata["dev_stack"], self.testdata["csp_url"],self.testdata["api_token"])
        result = False
        for _ in range(Constant.RETRY_CLEANUP):
            obj.cleanup_sites(self.testdata["org_id"], ["DISCONNECTED", "CONNECTED", "DEREGISTRATION_REQUESTED"])
            result=obj.size_of_sites(self.testdata["org_id"]) == 0
            if result:
                break
            time.sleep(15)
        self.assertEqual(True, result)




def fake_attrs():
    g2attrs = [
        ('My Project Name', 'Fake Project Name'),
        ('Reponsible Team', 'Fake Team'),
        ('Build Number', '42'),
    ]
    g3attrs = [
        ('Produc Under Test', 'The Fake Product Site'),
        ('Product Team', 'Fake Product Team')
    ]
    attrs = {'group2': g2attrs, 'group3': g3attrs}
    return attrs


def fake_description():
    desc = """This is a fake description
    divided in two lines."""
    return desc


if __name__ == '__main__':
    #unittest.main()
    #html_report_dir="\\report"
    #outfile=file("report.html",'w')
    #unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output=html_report_dir))

    #suite = unittest.TestLoader().loadTestsFromTestCase(PreflightTestCase)
    #unittest.TextTestRunner(verbosity=2).run(suite)

    #outfile = file("test_results.html", "w")
    # Create the report file
    html_report = open('../../report/test_results.html', 'wb')
    #print ("open file:", html_report)
    # Create the runner and set the file as output and higher verbosity
    ssl._create_default_https_context = ssl._create_unverified_context
    runner = HTMLTestRunner.HTMLTestRunner(stream=html_report, verbosity=2, attrs=fake_attrs(),

                                           description=fake_description())

    '''
    # Create a test list
    tests = [
        PreflightTestCase
    ]
    # Load test cases
    loader = unittest.TestLoader()
    # Create a SuiteCase
    test_list = []
    for test in tests:
        cases = loader.loadTestsFromTestCase(test)
        test_list.append(cases)
    suite = unittest.TestSuite(test_list)
    '''
    suite = unittest.TestLoader().loadTestsFromTestCase(PreflightTestCase)
    # Run the suite
    runner.run(suite)
    all=html_report.readlines()
    #print ("html file content:", all)
    #html_report.close()


    #HtmlTestRunner.main()
