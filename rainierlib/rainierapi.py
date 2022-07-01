"""
rainier-library.py: a library class to do usefull things with Cisco IoT OD APIs

TODO: add proper error handling,
especially in the ``__add__`` and ``__mul__`` methods.

"""

import requests, json
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

	def __init__(self):
		api_url = "https://jsonplaceholder.typicode.com/todos"

	def libVersion(self):
		return(self.LIBV)

	def setAPIbaseURL(self, url):
		self.RAINIER_BASEURL = url

	def getAPIbaseURL(self):
		return(self.RAINIER_BASEURL)

	def setUsernamePassword(self, username, password):
		self.RAINIER_USERNAME = username
		self.RAINIER_PASSWORD = password
		self.USE_API_KEY = False

	def authenticate(self):
		if self.USE_API_KEY == False:
			# Let's authenticate with username / password
			print("Authenticating with username/password...")
			task = {"username":self.RAINIER_USERNAME,"password":self.RAINIER_PASSWORD}
			resp = requests.post(self.RAINIER_BASEURL+'/iam/auth/token', 
			json=task, verify=False)
			if resp.status_code != 200:
    			# This means something went wrong.
				if self.DEBUG: print('**ERROR** ' , resp.status_code, ' ', resp.reason)

			else:
				print('Request returned ' , resp.status_code, ' ', resp.reason)
				resp_json = resp.json()
				if self.DEBUG: print(resp_json)
    
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
				if self.DEBUG: print('**ERROR** ' , resp.status_code, ' ', resp.reason)

			else:

				print('Request returned ' , resp.status_code, ' ', resp.reason)
				resp_json = resp.json()
    
				self.access_token = resp.json()['access_token']

		if self.access_token == "" :
			print("Can't get access token, authentication failed, stopping here.")
			exit(1)
		else:
			print("Autentication OK.")
			return(0)

	def setAPIkey(self, key_name, key_secret, org_name):
		self.RAINIER_API_KEY_NAME = key_name
		self.RAINIER_API_KEY_SECRET = key_secret
		self.RAINIER_ORG_NAME = org_name
		self.USE_API_KEY = True

	def setTenantID(self, t):
		self.RAINIER_TENANTID = t

	def loadTParameters(self,c):
		# Set the base URL
		if c.RAINIER_BASEURL:
			self.setAPIbaseURL(c.RAINIER_BASEURL)
		else:
			print("Tenant definition is missing the base URL (ie: 'https://eu.ciscoiot.com'")
			exit(1)

		if c.RAINIER_TENANTID:
			self.setTenantID(c.RAINIER_TENANTID)
		else:
			print("Tenant definition is missing the x-tenant-id (ie: 'e0874499-c6d1-4b9e-bb7b-795b001fcefa'")
			exit(1)

		if c.RAINIER_USERNAME and c.RAINIER_PASSWORD:
			self.setUsernamePassword(c.RAINIER_USERNAME, c.RAINIER_PASSWORD)
			self.authenticate()
		else: 
			if c.RAINIER_API_KEY_NAME and c.RAINIER_API_KEY_SECRET and c.RAINIER_ORG_NAME:
				self.setAPIkey(c.RAINIER_API_KEY_NAME, c.RAINIER_API_KEY_SECRET, c.RAINIER_ORG_NAME)
				self.authenticate()
			else:
				print("Tenant definition is missing authentication information")
				exit(1)

	def getAllDevices(self):
		## Get all devices, returns a list

		devices = []

		page = 1
		size = self.PAGE_SIZE

		print("Requesting device list for tenant ID %s..." % self.RAINIER_TENANTID)
		headers = {
			"Content-Type" : "application/json",
			"Authorization" : "Bearer " + self.access_token,
			"x-access-token" : self.access_token,
			"x-tenant-id": self.RAINIER_TENANTID}

		while size > 0:
	
			# It is important to use "sortBy=eid" otherwise the content of a "page" is unpredictable
			# You miss some gateway, and have some duplicates
			resp = requests.get(self.RAINIER_BASEURL+'/resource/rest/api/v1/devices?sortBy=eid&sortDir=asc&page='+str(page)+
				'&size='+str(size),headers=headers,verify=False)
			if resp.status_code != 200:
  				# This means something went wrong.
  				print('**ERROR** ' , resp.status_code, ' ', resp.reason)
  				exit(1)
			else:

				r = resp.json()
				devices = devices + r['results']
				total = int(r['total'])
				received = len(r['results'])

				if self.DEBUG:
					print("Progress page {}, size {}, ({}-{}/{}): got {} entries".format(page,size,(page-1)*size,(page*size)-1,total,received)) 
					#print(" {} % ... ".format(min(100,round((page*size*100)/total))), end = '', flush=True)
					#print(r)

				if received < size:
					# that was the last page
					break

				page = page + 1

		return(devices)

