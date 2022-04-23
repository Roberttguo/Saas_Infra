import base64
import logging
import json
import ssl
import sys
import os
import time
import urllib
import urllib2

import Constant

"""Set up local logger"""
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)
"""Set up local logger End"""

'''
BASE_HCX_API = "/hybridity/api"
HCX_SESSION = BASE_HCX_API+"/sessions"
HCX_SAAS_SITE = BASE_HCX_API+"/saas/site"
CSP_TOKEN_URI="/csp/gateway/am/api/auth/api-tokens/authorize?refresh_token=%s"
CSP_URL="console-stg.cloud.vmware.com"
'''


class RestBase(object):
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.api_url = None
        if isinstance(self.host, dict):
            if 'fqdn' in self.host:
                self.api_url = "https://%s" % (self.host['fqdn'])
            else:
                self.api_url = "https://%s" % (self.host['ip'])
        if isinstance(self.host, str):
            self.api_url = "https://%s" % (self.host)

        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_session_token(self):
        '''
        Get session token based on given user and password
        :return: session token in str
        '''

        for i in xrange(Constant.RETRY):
            response = self._request(HCX_SESSION, method='POST', data=self.auth, headers=self.headers)
            if response != None:
                logger.info("Response = %s" % response)
                return response.info().getheader('x-hm-authorization')
            else:
                logger.info("Response is None")
                time.sleep(20)
                logger.info("Retrying %sth..." % i)
        raise Exception("Failed to obtain session token")

    def _request(self, uri, method='GET', data=None, params=None, headers=None):

        url = uri
        if params:
            url = uri + "?" + urllib.urlencode(params)
        if not headers:
            headers = self.headers
        if url.find('://') == -1:
            url = self.api_url + url
        req = urllib2.Request(url, json.dumps(data), headers)
        req.get_method = lambda: method
        try:
            response = urllib2.urlopen(req)
            return response
        except urllib2.HTTPError as ex:
            logger.error('error %s' % ex)
            if ex.getcode() == 409:  # old site exists, conflict error
                logger.warning("Error code=409, possibly caused by a conflict with current state. heards=%s" % headers)
                return
            if ex.getcode() == 401:
                logger.warning("Connection timed out, try reconnecting")
                self.x_hm_authorization = self.get_session_token()
                if headers and "x-hm-authorization" in headers:
                    headers["x-hm-authorization"] = self.x_hm_authorization
                    logger.info("Reconnected")
            else:
                if ex.getcode() >= 500:
                    logger.warning("Error code %s, retrying..." % (ex.getcode()))
                else:
                    logger.error("Error: %s" % ex)
                    raise ex
        except Exception as ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            msg = 'non-http exception "%s" (%s/30)'
            logger.warning(msg, uri, ex)


if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    u = RestBase('10.197.129.79', 'administrator@vsphere.local', "Admin!23")

    print u.get_CSP_token("https://console-stg.cloud.vmware.com",
                          "96kZqY03yCH9wPxqaS7gfEk1gitWi3iCMg7iFoWAEoi-yYqXgPURAd56qaUjyWmI")
