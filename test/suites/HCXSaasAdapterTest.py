import json
import os
import ssl
import sys
import logging
import time
import unittest
import lib.HTMLTestRunner as HTMLTestRunner

import Constant
from HCXSaasRestExt import HCXSaasRestExt
from HCXRestExt import HCXRestExt

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/testdata.json')
TESTBED_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/testbed_info.json')

"""Set up local logger"""
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)
"""Set up local logger End"""


class HCXSaasAdapaterTest(unittest.TestCase):

    def setUp(self):
        self.testfile = open(TESTDATA_FILENAME)
        self.testbedfile = open(TESTBED_FILENAME)
        self.testdata = json.load(self.testfile)
        self.testbed_info = json.load(self.testbedfile)
        self.hcxsaas_instance = HCXSaasRestExt(self.testdata["dev_stack"], self.testdata["csp_url"],
                                               self.testdata["api_token"])
        hosts = self.testbed_info["hosts"]
        self.onprem_hsm = HCXRestExt(hosts[Constant.sites[0][0]]["fqdn"], hosts[Constant.sites[0][1]]["username"],
                                     hosts[Constant.sites[0][1]]["password"])
        self.cloud_hsm = HCXRestExt(hosts[Constant.sites[1][0]]["fqdn"], hosts[Constant.sites[1][1]]["username"],
                                    hosts[Constant.sites[1][1]]["password"])

    #@unittest.skipIf(not hcx_service_enabled_onprem or not_onboarded_onprem, "Onprem HCX service disabled or already onboarded")
    def test_registe_site_onprem(self):
        hcx_service_enabled_onprem = self.onprem_hsm.is_HCX_service_enabled()
        if  not hcx_service_enabled_onprem:
            logger.info("Onprem HCX service disabled or already onboarded")
            return
        onboarded_onprem = self.onprem_hsm.is_HCX_service_onboarded()
        if onboarded_onprem:
            logger.info("Onprem HCX service already onboarded")
            return

        site_name, manifest = self.hcxsaas_instance.get_site_onboard_manifestId("onprem" + "_" + self.onprem_hsm.host)
        logger.info("manifest: %s,site_name: %s" % (manifest, site_name))
        time.sleep(5)
        test_res = False
        res = self.onprem_hsm.register_HCX_service(manifest, site_name)
        logger.info("is registered? returned tuple: (%s, %s" % (res[0], res[1]))
        if res[0] == res[1] and res[0] == None:
            count = Constant.RETRY
            while count > 0:
                test_res = self.onprem_hsm.is_HCX_service_onboarded()
                logger.info("is registered? %s" % test_res)
                time.sleep(15)
                if test_res:
                    break
                count -= 1
        else:
            test_res = res[0]!=None
        self.assertEqual(True, test_res)

    #@unittest.skipIf(not hcx_service_enabled_cloud or not_onboarded_cloud, "Cloud HCX service disabled or already onboarded")
    def test_registe_site_cloud(self):
        hcx_service_enabled_cloud = self.cloud_hsm.is_HCX_service_enabled()
        if not hcx_service_enabled_cloud:
            logger.info("Cloud HCX service has not enabled.")
            return
        onboarded_cloud = self.cloud_hsm.is_HCX_service_onboarded()
        if onboarded_cloud:
            logger.info("Cloud already onboarded.")
            return

        site_name, manifest = self.hcxsaas_instance.get_site_onboard_manifestId("cloud" + "_" + self.cloud_hsm.host)
        logger.info("manifest: %s,site_name: %s" % (manifest, site_name))
        time.sleep(5)
        test_res = False
        res = self.cloud_hsm.register_HCX_service(manifest, site_name)
        logger.info("is registered? returned tuple: (%s, %s)" % (res[0], res[1]))
        if res[0] == res[1] and res[0] == None:
            count = Constant.RETRY
            while count > 0:
                test_res = self.cloud_hsm.is_HCX_service_onboarded()
                logger.info("is registered? %s" % test_res)
                time.sleep(15)
                if test_res:
                    break
                count -= 1
        else:
            test_res = res[0] != None
        self.assertEqual(True, test_res)


def get_attrs():
    g2attrs = [
        ('Project Name', 'HCX Saas Automation'),
        ('Responsible Team', 'HCX Saas Team'),
        ('Build Number', '42'),

    ]
    g3attrs = [
        ('Produc Under Test', 'HCX Saas adapter test Suite'),
        ('Product Team', 'HCX Saas Team')
    ]

    attrs={"group2":g2attrs,"group3":g3attrs}
    return attrs


def get_description():
    des="HCX Saas Automation"
    return des


if __name__ == '__main__':
    html_report = open('../../report/test_results.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=html_report, verbosity=2, attrs=get_attrs(),
                                           description=get_description())

    suite = unittest.TestLoader().loadTestsFromTestCase(HCXSaasAdapaterTest)
    # Run the suite
    runner.run(suite)