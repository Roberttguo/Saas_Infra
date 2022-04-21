import sys
import os
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

    def __init__(self, csp_url, api_token):
        super(HCXSaasRestExt, self).__init__(csp_url, None, None)
        self.csp_url=csp_url
        self.api_token=api_token
        self.csp_token = self._get_CSP_token()
        self.site_cache=None

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
             #print "response.msg()=   ", response.msg
             if response.code>=200 and response.code<220:
                res=response.readlines()
                res_data=json.loads(res[0])
                if 'access_token' in res_data:
                    return res_data['access_token']
                else:
                    continue
          else:
             logging.info("Response is None")
             time.sleep(20)
             logging.info("Retrying %sth..."%i)
        raise Exception("Failed to obtain csp token")

    def get_registered_sites(self, dev_stack, org_id):
        #compile url
        url=""
        if "https://" in dev_stack:
            url=dev_stack
        else:
            url="https://"+dev_stack
        url+=Constant.BASE_HCX_SAAS_API
        url+="/org/%s"%org_id+"/sites:summarize"
        #insert required headers
        self.headers["authority"]=dev_stack if "https://" not in dev_stack else dev_stack[dev_stack.find("//")+2:]
        self.headers["Authorization"]="Bearer %s"%self.csp_token
        logger.info("csp url to obtain access token:"+url)
        for i in xrange(Constant.RETRY):
          response = super(HCXSaasRestExt, self)._request(url, method='GET', data=None, headers=self.headers)
          if response != None:
            if response.code ==200:
                res=response.readlines()
                res_data=json.loads(res[0])
                #print ("json obj: ", type(res_data))
                self.site_cache = res_data["sites"]
                return res_data["sites"]
            else:
                continue
          else:
              logging.info("Response is None")
              time.sleep(20)
              logging.info("Retrying %sth..." % i)
        raise Exception("Failed to obtain site info")

    def query_site_Ids(self, dev_stack, org_id, status):
        if not self.site_cache:
            self.get_registered_sites(dev_stack, org_id)
        site_ids=[]
        for it in self.site_cache:
            print (it)
            if "status" in it and it["status"]==status:
                site_ids.append((it["name"], it["site_id"]))
        return site_ids


    def size_of_sites(self, dev_stack, org_id):
        '''

        :param dev_stack:
        :param org_id:
        :return: total nums of registered sites regardless of status
        '''
        return len(self.get_registered_sites(dev_stack, org_id))

    def cleanup_sites(self, dev_stack, org_id, status=None):
        #compile url
        url=""
        if "https://" in dev_stack:
            url=dev_stack
        else:
            url="https://"+dev_stack
        url+=Constant.BASE_HCX_SAAS_API
        url+="/site-onboarding/deregister"
        #insert required headers
        self.headers["authority"]=dev_stack if "https://" not in dev_stack else dev_stack[dev_stack.find("//")+2:]
        self.headers["authorization"]="Bearer %s"%self.csp_token
        refer= "https://"+ dev_stack if "https://" not in dev_stack else dev_stack
        refer+="/customer/infrastructure/sites"
        self.headers["referer"] = refer

        logger.info("url to obtain access token:"+url)
        site_ids = self.query_site_Ids(dev_stack, org_id, status)
        print ("all sites %s with status: %s"%(site_ids, status))
        for name, id in site_ids:
          print ("name: %s and id:%s to cleanup."%(name, id))
          raw_data = {"site_id":id}
          if status=="DISCONNECTED":
            raw_data["force"] = True
          else:
            raw_data["force"] = False
          try:
            response = super(HCXSaasRestExt, self)._request(url, method='POST', data=raw_data, headers=self.headers)
            if response != None:
                if response.code ==200:
                    res=response.readlines()
                    res_data=json.loads(res[0])
                    print ("deregistering..."+res[0])
                else:
                    continue
            else:
              logging.info("Response is None")
              time.sleep(20)
              logging.info("Retrying %sth..." % i)
            #raise Exception("Failed to obtain session token")
          except urllib2.HTTPError as ex:
              if ex.getcode() == 400:
                  pass
              else:
                  print (ex.readlines()[0])
                  raise ex



if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    u = HCXSaasRestExt("https://console-stg.cloud.vmware.com","96kZqY03yCH9wPxqaS7gfEk1gitWi3iCMg7iFoWAEoi-yYqXgPURAd56qaUjyWmI") #RestBase('10.197.129.79', 'administrator@vsphere.local', "Admin!23")


    #print ("access token:", u.csp_token)
    jdata = u.get_registered_sites("hcx-hcxaas-guot2-ds-nsbu01-stg-nsbu02-us-west-2.vdp-int-stg.vmware.com", "6d2918d8-b939-49ed-931f-796e1c5057e2")
    print ("returned data type: ", type(jdata))
    print u.query_site_Ids("hcx-hcxaas-guot2-ds-nsbu01-stg-nsbu02-us-west-2.vdp-int-stg.vmware.com", "6d2918d8-b939-49ed-931f-796e1c5057e2", "DISCONNECTED")

    print "total sites: ", u.size_of_sites("hcx-hcxaas-guot2-ds-nsbu01-stg-nsbu02-us-west-2.vdp-int-stg.vmware.com",
                                           "6d2918d8-b939-49ed-931f-796e1c5057e2")
    u.cleanup_sites("hcx-hcxaas-guot2-ds-nsbu01-stg-nsbu02-us-west-2.vdp-int-stg.vmware.com", "6d2918d8-b939-49ed-931f-796e1c5057e2", "DISCONNECTED")