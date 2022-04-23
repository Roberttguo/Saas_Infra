import requests
import os
import sys
import logging
import ssl

"""Set up local logger"""
log=logging.getLogger(os.path.basename(__file__))
log.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
log.addHandler(ch)
"""Set up local logger End"""


class PrecheckSites(object):
    def __init__(self,urls):
        self.url_list = urls

    def _getClassName(self):
        return self.__class__.__name__

    def checkUrls(self):
        if len(self.url_list)==0:
            log.info("No url specified.")
            return True
        requests.adapters.DEFAULT_RETRIES = 2
        for url in self.url_list:
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
                response = requests.get(url, verify=False)
                if response.status_code == 200:
                    log.info("url: %s is active"%url)
                else:
                    log.error("url: %s is not active" % url)
                    return False
            except Exception as ex:
                log.error("url: %s is not active or not accessible. Exception: %s" % (url, ex.message))
                return False
        return True


if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    urls=["https://console-stg.cloud.vmware.com","https://hcx-hcxaas-guot2-ds-nsbu01-stg-nsbu02-us-west-2.vdp-int-stg.vmware.com/"]

    u = PrecheckSites(urls)
    u.checkUrls()
