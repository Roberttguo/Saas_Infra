import ssl
import logging
import time

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


class HCXRestExt(RestBase):
    def __init__(self, host, user, password):
        super(HCXRestExt, self).__init__(host, user, password)
        self.auth = {
            "username": user,
            "password": password
        }
        #self.headers = super.headers


    def get_session_token(self):
        '''
        Get session token based on given user and password
        :return: session token in str
        '''

        for i in xrange(Constant.RETRY):
          response = super(HCXRestExt, self)._request(Constant.HCX_SESSION, method='POST', data=self.auth, headers=self.headers)
          if response != None:
            print ("Error code:", response.code, response.code>=200 and response.code<300)
            logger.info("Response = %s"%response)
            return response.info().getheader('x-hm-authorization')
          else:
             logger.info("Response is None")
             time.sleep(20)
             logger.info("Retrying %sth..."%i)
        raise Exception("Failed to obtain session token")

if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    u = HCXRestExt('10.197.128.27', 'administrator@vsphere.local', "Admin!23")
    print u.get_session_token()
