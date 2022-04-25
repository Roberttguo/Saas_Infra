import os
import unittest

import lib.HTMLTestRunner

from test.suites.PreflightTest import PreflightTest
from test.suites.SitePairsTest import SitePairsTest
from test.suites.NetworkExtensionsTest import NetworkExtensionsTest
from test.suites.HCXSaasAdapterTest import HCXSaasAdapaterTest


def get_attrs():
    build=os.getenv('BUILD_NUMBER')
    g2attrs = [
        ('Project Name', 'HCX Saas Automation'),
        ('Responsible Team', 'HCX Saas Team'),
        ('Build Number', build),

    ]
    g3attrs = [
        ('Produc Under Test', 'HCX Saas adapter test Suite'),
        ('Product Team', 'HCX Saas Team')
    ]

    attrs = {"group2": g2attrs, "group3": g3attrs}
    return attrs


def get_description():
    des = "HCX Saas Automation"
    return des

if __name__ == '__main__':
    # Create the report file
    html_report = open('report/test_reports.html', 'wb')
    # Create the runner and set the file as output and higher verbosity
    runner = lib.HTMLTestRunner.HTMLTestRunner(stream=html_report, verbosity=2, attrs=get_attrs(),
                                               description=get_description())
    # Create a test list
    tests = [
        PreflightTest, HCXSaasAdapaterTest,
        SitePairsTest,NetworkExtensionsTest
    ]
    # Load test cases
    loader = unittest.TestLoader()
    # Create a SuiteCase
    test_list = []
    for test in tests:
        cases = loader.loadTestsFromTestCase(test)
        test_list.append(cases)
    suite = unittest.TestSuite(test_list)
    # Run the suite
    runner.run(suite)
