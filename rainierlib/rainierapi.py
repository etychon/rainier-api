"""
rainier-library.py: a library class to do usefull things with Cisco IoT OD APIs

(c) Emmanuel Tychon

"""

import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class rainierlib:

    LIBV = "0.1"
    RAINIER_URL = ""
    RAINIER_BASEURL = ""
    RAINIER_USERNAME = ""
    RAINIER_PASSWORD = ""
    RAINIER_ORG_NAME = ""
    RAINIER_API_KEY_NAME = ""
    RAINIER_API_KEY_SECRET = ""
    RAINIER_TENANTID = ""
    DEBUG = True
    access_token = ""
    USE_API_KEY = ""
    PAGE_SIZE = 200
    edm_devices = []

    def libVersion(self):
        return(self.LIBV)

    def setAPIbaseURL(self, url):
        self.RAINIER_BASEURL = url

    def getAPIbaseURL(self):
        return(self.RAINIER_BASEURL)

    def enableDebugs(self, b):
        self.DEBUG = b

    def setUsernamePassword(self, username, password):
        self.RAINIER_USERNAME = username
        self.RAINIER_PASSWORD = password
        self.USE_API_KEY = False

    def authenticate(self):
        if self.USE_API_KEY == False:
            # Let's authenticate with username / password
            print("Authenticating with username/password...")
            task = {"username": self.RAINIER_USERNAME,
                    "password": self.RAINIER_PASSWORD}
            resp = requests.post(self.RAINIER_BASEURL+'/iam/auth/token',
                                 json=task, verify=False)
            if resp.status_code != 200 and resp.status_code != 201:
                # This means something went wrong.
                if self.DEBUG:
                    print('**ERROR** ', resp.status_code, ' ', resp.reason)

            else:
                print('Request returned ', resp.status_code, ' ', resp.reason)
                resp_json = resp.json()
                if self.DEBUG:
                    print(resp_json)

                self.access_token = resp.json()['access_token']

        if self.USE_API_KEY == True:
            ### REQUESTING TOKEN FOR AUTHENTICATION (with API KEY)
            print("Authenticating with API Key...")
            headers = {'content-type': 'application/json'}
            # Organization name and API key name both in lowercase format
            task = {'grant_type': 'client_credentials',
                    'client_id': "%s->%s" % (self.RAINIER_ORG_NAME.lower(),
                                             self.RAINIER_API_KEY_NAME.lower()),
                    'client_secret': self.RAINIER_API_KEY_SECRET}
            resp = requests.post(self.RAINIER_BASEURL+'/iam/auth/token',
                                 json=task, headers=headers, verify=False)
            if resp.status_code != 200:
                # This means something went wrong.
                if self.DEBUG:
                    print('**ERROR** ', resp.status_code, ' ', resp.reason)

            else:

                print('Request returned ', resp.status_code, ' ', resp.reason)
                resp_json = resp.json()
                self.access_token = resp.json()['access_token']

        if self.access_token == "":
            print("Can't get access token, authentication failed, stopping here.")
            exit(1)
        else:
            print("Autentication OK.")
            return(0)

    # Verb can be 'GET', 'POST', etc...
    def runRainierQuery(self, verb, querystr, data=None):

        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer " + self.access_token,
                   "x-access-token": self.access_token,
                   "x-tenant-id": self.RAINIER_TENANTID}

        try:
            resp = requests.request(verb, self.RAINIER_BASEURL+querystr,
                                    headers=headers, verify=False, data=data)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            raise SystemExit(err)
        if resp.status_code != 200:
            # This means something went wrong.
            if self.DEBUG:
                print('**ERROR** ', resp.status_code, ' ', resp.reason)
        return(resp)

    def setAPIkey(self, key_name, key_secret, org_name):
        self.RAINIER_API_KEY_NAME = key_name
        self.RAINIER_API_KEY_SECRET = key_secret
        self.RAINIER_ORG_NAME = org_name
        self.USE_API_KEY = True

    def setTenantID(self, t):
        self.RAINIER_TENANTID = t

    def loadTParameters(self, c):
        # Set the base URL
        if c.RAINIER_BASEURL:
            self.setAPIbaseURL(c.RAINIER_BASEURL)
        else:
            print(
                "Tenant definition is missing the base URL (ie: 'https://eu.ciscoiot.com'")
            exit(1)

        if c.RAINIER_TENANTID:
            self.setTenantID(c.RAINIER_TENANTID)
        else:
            print(
                "Tenant definition is missing the x-tenant-id (ie: 'e0874499-c6d1-4b9e-bb7b-795b001fcefa'")
            exit(1)

        if c.RAINIER_USERNAME and c.RAINIER_PASSWORD:
            self.setUsernamePassword(c.RAINIER_USERNAME, c.RAINIER_PASSWORD)
            self.authenticate()
        else:
            if c.RAINIER_API_KEY_NAME and c.RAINIER_API_KEY_SECRET and c.RAINIER_ORG_NAME:
                self.setAPIkey(c.RAINIER_API_KEY_NAME,
                               c.RAINIER_API_KEY_SECRET, c.RAINIER_ORG_NAME)
                self.authenticate()
            else:
                print("Tenant definition is missing authentication information")
                exit(1)

    def getAllDevices(self, force_refresh=False, filter=None):
        ## Get all devices, returns a list

        # Do we already have cached values and not forcing refresh?
        if len(self.edm_devices) and not force_refresh and not filter:
            return(self.edm_devices)

        devices = []

        page = 1
        size = self.PAGE_SIZE

        print("Requesting device list for tenant ID %s..." %
              self.RAINIER_TENANTID)

        if filter:
            filter_str = '&filter=  '+filter+'"'
        else:
            filter_str = ''

        while size > 0:
            resp = self.runRainierQuery(
                'GET', '/resource/rest/api/v1/devices?sortBy=eid&sortDir=asc&page=' + str(page) + '&size='+str(size) + filter_str)
            if resp.status_code != 200:
                if self.DEBUG:
                    print("HTTPS return code: {}".format(resp.status_code))
                return(devices)
            else:
                resp = resp.json()
                devices = devices + resp['results']
                total = int(resp['total'])
                received = len(resp['results'])

                if self.DEBUG:
                    print("Progress page {}, size {}, ({}-{}/{}): got {} entries".format(page,
                                                                                         size, (page-1)*size, (page*size)-1, total, received))
                #print(" {} % ... ".format(min(100,round((page*size*100)/total))), end = '', flush=True)
                #print(r)

                if received < size:
                    # that was the last page
                    break

                page = page + 1

                if not filter:
                    self.edm_devices = devices

        return(devices)

    # filter based on search string (ie: "name=ir1101-etychon")
    # this can return multiple results depending on the search filter
    # TODO: Need to add pagination support
    def filterDevices(self, searchString):

        resp = self.getAllDevices(filter=searchString)

        return(resp)

    # Finds the _first_ gateway that matches  name or SN, and return that device JSON details
    def getDeviceDetails(self, device_name=None, sn=None):

        # if cached information available, let's use that
        if len(self.edm_devices):
            for zItem in self.edm_devices:
                if sn and zItem['SN'] == sn:
                    return(zItem)
                if device_name and zItem['name'] == device_name:
                    return(zItem)

        # If not found in cache or cache is not built
        # Let's filter specifically for this name using API
        if device_name:
            z = self.filterDevices('name:'+device_name)
            try:
                return(z['results'][0])
            except:
                pass

        # filter specifically for this SN
        if sn:
            z = self.filterDevices('SN:'+sn)
            try:
                return(z['results'][0])
            except:
                pass

        return(None)

    def getAllDevicesInGroup(self, group_name):

        s = self.filterDevices("configGroup:"+group_name)

        try:
            return(s)
        except:
            return(None)

    # eid is this format SKU+SN, ei: IE-3400-8P2S+AB123456789
    def deleteDevicesByEid(self, eid):

        myobj = '{"eids": ["' + eid + '"],"rollbackConfig":false}'

        resp = self.runRainierQuery(
            'DELETE', '/resource/rest/api/v1/devices/delete', data=myobj)

        return(resp)

    def getDeviceTypeFromSKU(self, sku):
        sku = sku.upper()
        if (sku.startswith("IE-34")):
            return("ie3400")
        if (sku.startswith("IR11")):
            return("ir1100")
        if (sku.startswith("IR-8")):
            return("ir800")

        return(None)

        # https://rainierdemo3.ciscoiotdev.io/resource/rest/api/v1/devices POST
        # [{"eid":"IE-3400-8P2S+AB123456789","fields":{"deviceType":"ie3400","configGroup":"IE3400 Default","field:name":"deletemetwo"}}]
    def addNewDevice(self, eid, name, configGroup):

        deviceType = self.getDeviceTypeFromSKU(eid)

        if not deviceType:
            return(None)

        myobj = '[{"eid":"' + eid + \
            '","fields":{"deviceType":"'+deviceType + \
                '","configGroup":"'+configGroup+'","field:name":"'+name+'"}}]'

        print(myobj)

        resp = self.runRainierQuery(
            'POST', '/resource/rest/api/v1/devices', data=myobj)

        if resp.status_code != 200:
            print("Something went wrong when adding device")

        return(resp)

    def showRainierErrorMessage(self, r):

        try:
            return(json.loads(r.content)['message'])
        except:
            return(None)


    def validateCC(self, username, url, api_key, account_id, carrier_id, account_name):

        myobj = '{"username":"'+username+'","url":"'+url+'","api_key":"'+api_key+'","account_id":"'+\
            account_id+'","carrier_id":"'+carrier_id+'","account_name":"'+account_name+'","enabled":true}'

        print(myobj)

        resp = self.runRainierQuery(
            'POST', '/iam/tenants/'+self.RAINIER_TENANTID+'/control-centers/validate/', data=myobj)

        if resp.status_code != 200:
            print("Something went wrong when validating CC")

        return(resp)

    def addCC(self, username, url, api_key, account_id, carrier_id, account_name):

        myobj = '{"control_center_list":[{"username":"'+username+'","url":"'+url+'","api_key":"'+api_key+'","account_id":"'+\
            account_id+'","carrier_id":"'+carrier_id+'","account_name":"'+account_name+'","enabled":true}]}'
            
        print(myobj)

        resp = self.runRainierQuery(
            'PUT', '/iam/tenants/'+self.RAINIER_TENANTID+'/control-centers/', data=myobj)

        if resp.status_code != 200:
            print("Something went wrong when adding CC")

        return(resp)