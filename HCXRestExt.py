import ssl
import json
import logging
import sys
import os
import time
import urllib2

from RestBase import RestBase
import Constant

"""Set up local logger"""
logger = logging.getLogger(os.path.basename(__file__))
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
        self.session_token = self.get_session_token()

    def get_session_token(self):
        '''
        Get session token based on given user and password
        :return: session token in str
        '''

        for i in xrange(Constant.RETRY):
            response = super(HCXRestExt, self)._request(Constant.HCX_SESSION, method='POST', data=self.auth,
                                                        headers=self.headers)
            if response != None:
                print ("Error code:", response.code, response.code >= 200 and response.code < 300)
                logger.info("Response = %s" % response)
                return response.info().getheader('x-hm-authorization')
            else:
                logger.info("Response is None")
                time.sleep(20)
                logger.info("Retrying %sth..." % i)
        raise Exception("Failed to obtain session token")


    def is_HCX_service_enabled(self):
        saas_info, status, hcx_service_flag=self.get_HCX_service()
        return hcx_service_flag == "ENABLED"


    def is_HCX_service_onboarded(self):
        saas_info, status, hcx_service_flag =self.get_HCX_service()
        return saas_info!=None and status == "SITE_FULLY_ONBOARDED"


    def get_HCX_service(self):
        # compile url
        url = self.api_url
        url += Constant.HCX_SAAS_ADAPTER_SITE
        logger.info("url to register site: %s" % url)
        self.headers["x-hm-authorization"] = self.session_token
        for i in xrange(Constant.RETRY):
            try:
                response = super(HCXRestExt, self)._request(url, method='GET', data=None, headers=self.headers)
                if response != None:
                    logger.info("response contend: %s code: %s" % (dir(response), response.code))
                    if response.code == 200:
                        res = response.readlines()
                        res_data=None
                        if isinstance(res, list):
                            res_data = json.loads("".join(res))
                        logger.info("json obj=%s " % res_data)
                        logger.info("Response : %s" % res)
                        status = res_data["registration_status"]
                        saas_info = None
                        if saas_info in res_data:
                            saas_info = res_data["saas_info"]
                        return (saas_info, status, "ENABLED")
                    else:
                        continue
                else:
                    logger.info("Response is None")
                    time.sleep(20)
                    logger.info("Retrying %sth..." % i)
            except urllib2.HTTPError as ex:
                if ex.getcode() == 404:
                    return (None,None, "NO_ENABLED")

        raise Exception("Failed to obtain site info")

    def register_HCX_service(self, manifest, site_name):
        # compile url
        url = self.api_url
        url += Constant.HCX_SAAS_ADAPTER_SITE
        logger.info("url to register site: %s" % url)
        # insert required headers
        target_saas = "https://" + self.host
        self.headers["Origin"] = target_saas
        self.headers["x-hm-authorization"] = self.session_token
        logger.info("headers to register site: %s" % self.headers)
        data = {
            "passphrase": site_name,
            "type": "INLINE",
            "onboarding_manifest": manifest
        }
        logger.info("payload to register site: %s" % data)
        for i in xrange(Constant.RETRY):
            response = super(HCXRestExt, self)._request(url, method='POST', data=data, headers=self.headers)
            if response != None:
                if response.code == 200:
                    res = response.readlines()
                    logger.info("all responses for site registration... ")
                    for x in res:
                        logger.info("returned response >> " + x)
                    res_data = json.loads(res[0])
                    logger.info("Response for site onboard request: %s", res[0])
                    manifest = res_data["onboarding_manifest"]
                    return (site_name, manifest)
                else:
                    continue
            else:
                logger.info("Response is None")
                time.sleep(20)
                logger.info("Retrying %sth..." % i)
        raise Exception("Failed to register the site %s as an HCX service." % self.host)


if __name__ == '__main__':
    from HCXSaasRestExt import HCXSaasRestExt

    ssl._create_default_https_context = ssl._create_unverified_context
    u = HCXRestExt('10.197.134.6', 'administrator@vsphere.local', "Admin!23")
    #u = HCXRestExt('10.197.129.93', 'administrator@vsphere.local', "Admin!23")
    res = u.get_HCX_service()
    if res[2]=="ENABLED":
        print ("tuple[0]= %s, tuple[1]=%s"%(res[0],res[1]))
    else:
        print ("HCX service has not benn enabled.")
    exit(0)
    # print u.get_session_token()
    o = HCXSaasRestExt("hcx-hcxaas-guot2-ds-nsbu01-stg-nsbu02-us-west-2.vdp-int-stg.vmware.com", \
                       "https://console-stg.cloud.vmware.com",
                       "96kZqY03yCH9wPxqaS7gfEk1gitWi3iCMg7iFoWAEoi-yYqXgPURAd56qaUjyWmI")

    site_name, manifest = o.get_site_onboard_manifestId("onprem" + "_" + u.host)
    logger.info("manifest: %s,site_name: %s" % (manifest, site_name))
    time.sleep(5)
    u.register_HCX_service(manifest, site_name)
