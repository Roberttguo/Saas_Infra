import sys
import os
import random
import ssl
import logging
import json
import time
import urllib2

from RestBase import RestBase
import Constant

"""Set up local logger"""
logger=logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)
"""Set up local logger End"""

class HCXSaasRestExt(RestBase):
    """
    Mainly designed to access HCXSaas portal/server site
    """
    def __init__(self, saas_srv_url, csp_url, api_token):
        super(HCXSaasRestExt, self).__init__(csp_url, None, None)
        self.saas_srv_url = saas_srv_url
        self.csp_url = csp_url
        self.api_token = api_token
        self.csp_token = self._get_CSP_token()
        self.site_cache = None

    def _get_CSP_token(self):
        if self.csp_url==None or len(self.csp_url) == 0:
            self.csp_url=Constant.CSP_URL
        csp=self.csp_url+Constant.CSP_TOKEN_URI%self.api_token
        logger.info("csp url to obtain access token:"+csp)
        for i in xrange(Constant.RETRY):
          response = super(HCXSaasRestExt, self)._request(csp, method='POST', data=None, headers=self.headers)
          if response != None:
             logger.info("Response = %s"%response)
             logger.info("response.info()=  %s" %response.info())
             if response.code>=200 and response.code<220:
                res=response.readlines()
                res_data=json.loads(res[0])
                if 'access_token' in res_data:
                    return res_data['access_token']
                else:
                    continue
          else:
             logger.info("Response is None")
             time.sleep(20)
             logger.info("Retrying %sth..."%i)
        raise Exception("Failed to obtain csp token")

    def get_registered_sites(self, org_id):
        #compile url
        url=""
        if "https://" in self.saas_srv_url:
            url=self.saas_srv_url
        else:
            url="https://"+self.saas_srv_url
        url+=Constant.BASE_HCX_SAAS_API
        url+="/org/%s"%org_id+"/sites:summarize"
        #insert required headers
        self.headers["authority"]=self.saas_srv_url if "https://" not in self.saas_srv_url else self.saas_srv_url[self.saas_srv_url.find("//")+2:]
        self.headers["Authorization"]="Bearer %s"%self.csp_token
        logger.info("csp url to obtain access token:"+url)
        for i in xrange(Constant.RETRY):
          response = super(HCXSaasRestExt, self)._request(url, method='GET', data=None, headers=self.headers)
          if response != None:
            if response.code ==200:
                res=response.readlines()
                res_data=json.loads(res[0])
                self.site_cache = res_data["sites"]
                return res_data["sites"]
            else:
                continue
          else:
              logger.info("Response is None")
              time.sleep(20)
              logger.info("Retrying %sth..." % i)
        raise Exception("Failed to obtain site info")

    def get_site_onboard_manifestId(self, site_name):
        #compile url
        url=""
        if "https://" in self.saas_srv_url:
            url=self.saas_srv_url
        else:
            url="https://" + self.saas_srv_url
        url+=Constant.HCXSAAS_SRV_ONBOARD_REQ
        #insert required headers
        target_saas = self.saas_srv_url if "https://" not in self.saas_srv_url else self.saas_srv_url[self.saas_srv_url.find("//") + 2:]
        self.headers["Origin"] = target_saas
        self.headers["Authorization"]="Bearer %s"%self.csp_token
        self.headers["Referer"] = target_saas + "/customer/infrastructure/sites"
        site_name+="_"+hex(random.randint(0,2**31-1))[2:]
        data = {
            "name": site_name,
            "passphrase": site_name
        }
        for i in xrange(Constant.RETRY):
          response = super(HCXSaasRestExt, self)._request(url, method='POST', data=data, headers=self.headers)
          if response != None:
            if response.code ==200:
                res=response.readlines()
                logger.info("all responses... ")
                for x in res:
                    logger.info("returned response>> "+x)
                res_data=json.loads(res[0])
                logger.info ("Response for site onboard request: %s", res[0])
                manifest = res_data["onboarding_manifest"]
                return (site_name, manifest)
            else:
                continue
          else:
              logger.info("Response is None")
              time.sleep(20)
              logger.info("Retrying %sth..." % i)
        raise Exception("Failed to obtain site info")

    def query_site_Ids(self, org_id, status=None):
        if not self.site_cache:
            self.get_registered_sites(org_id)
        site_ids=[]
        for it in self.site_cache:
            if "status" in it and (not status or it["status"] in status):
                site_ids.append((it["name"], it["site_id"], it["status"]))
        return site_ids


    def size_of_sites(self, org_id):
        '''

        :param dev_stack:
        :param org_id:
        :return: total nums of registered sites regardless of status
        '''
        return len(self.get_registered_sites(org_id))

    def cleanup_sites(self, org_id, status=None):
        #compile url
        url=""
        if "https://" in self.saas_srv_url:
            url=self.saas_srv_url
        else:
            url="https://"+self.saas_srv_url
        url+=Constant.BASE_HCX_SAAS_API
        url+="/site-onboarding/deregister"
        #insert required headers
        self.headers["authority"] = self.saas_srv_url if "https://" not in self.saas_srv_url else self.saas_srv_url[self.saas_srv_url.find("//")+2:]
        self.headers["authorization"] = "Bearer %s"%self.csp_token
        refer= "https://"+ self.saas_srv_url if "https://" not in self.saas_srv_url else self.saas_srv_url
        refer+="/customer/infrastructure/sites"
        self.headers["referer"] = refer

        logger.info("url to obtain access token:"+url)
        site_ids = self.query_site_Ids(org_id, status)
        for name, id, _status in site_ids:
          logger.info("name: %s and id:%s to cleanup."%(name, id))
          raw_data = {"site_id":id}
          if _status=="DISCONNECTED" or _status=="DEREGISTRATION_REQUESTED":
            raw_data["force"] = True
          else:
            raw_data["force"] = False
          try:
            response = super(HCXSaasRestExt, self)._request(url, method='POST', data=raw_data, headers=self.headers)
            if response != None:
                if response.code ==200:
                    res=response.readlines()
                    #res_data=json.loads(res[0])
                    logger.info("Response for Deregister: %s" %res[0])
                else:
                    continue
            else:
              logger.info("Response is None")
              time.sleep(20)
              logger.info("Retrying %sth..." % i)
          except urllib2.HTTPError as ex:
              if ex.getcode() == 400:
                  pass
              else:
                  logger.error(ex.readlines()[0])
                  raise ex



if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    u = HCXSaasRestExt("mysaas_url.com",\
                       "https://mysaas.com",\
                       "xxxxxxxx")

    jdata = u.get_registered_sites( "test_id2")
    print ("returned data type: ", type(jdata))
    print u.query_site_Ids("6d2918d8-b939-49ed-931f-796e1c5057e2", "DISCONNECTED")

    print "total sites: ", u.size_of_sites("6d2918d8-b939-49ed-931f-796e1c5057e2")
    exit(0)
    #u.cleanup_sites("mytest_site.com", "6d2918d8-b939-49ed-931f-796e1c5057e2", "CONNECTED")
    dev_stack="mytest_site.com"
    site_name="Tian_test2"
    res=u.get_site_onboard_manifestId(dev_stack, site_name)
    print "res=", res
