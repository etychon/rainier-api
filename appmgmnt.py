#!/usr/bin/python3

import requests, json
import constants
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# constants
debug = True 
use_API_Key = False

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def refresh_iox_device(devId):
	print("Refreshing " + devId)

	headers = {
        	"Content-Type" : "application/json",
        	"Authorization" : "Bearer " + access_token,
        	"X-Tenant-ID": constants.RAINIER_TENANTID}

	myobj = '{"actionType": "RefreshInventory"}'
	print(myobj)

	resp = requests.post(constants.RAINIER_BASEURL+'/appmgmt/devices/'+devId+'/action',
        	headers=headers,verify=False, data = myobj)

	#print(resp.request.url)
	#print(resp.request.headers)
	#print(resp.request.body)

	if resp.status_code != 200:
        # This means something went wrong.
        	if debug: print('**ERROR** ' , resp.status_code, ' ', resp.reason)
	else:
		print('Request returned ' , resp.status_code, ' ', resp.reason)

if (not use_API_Key):

	### REQUESTING TOKEN FOR AUTHENTICATION (with username/password)

	print("Authenticating with username/password...")
	task = {"username":constants.RAINIER_USERNAME,"password":constants.RAINIER_PASSWORD}
	resp = requests.post(constants.RAINIER_BASEURL+'/iam/auth/token', 
		json=task, 
		verify=False)
	if resp.status_code != 200:
    	# This means something went wrong.
		if debug: print('**ERROR** ' , resp.status_code, ' ', resp.reason)

	else:

		print('Request returned ' , resp.status_code, ' ', resp.reason)
		resp_json = resp.json()
		#if debug: print(resp_json)
    
		access_token = resp.json()['access_token']

else:

	### REQUESTING TOKEN FOR AUTHENTICATION (with API KEY)

	print("Authenticating with API Key...")
	headers = {'content-type': 'application/json'}

	# Organization name and API key name both in lowercase format
	task = {'grant_type': 'client_credentials',
			'client_id': "%s->%s" % (constants.RAINIER_ORG_NAME.lower(), constants.RAINIER_API_KEY_NAME.lower()),
			'client_secret': constants.RAINIER_API_KEY_SECRET}
	resp = requests.post(constants.RAINIER_BASEURL+'/iam/auth/token', 
		json=task, 
		headers=headers,
		verify=False)
	if resp.status_code != 200:
    	# This means something went wrong.
		if debug: print('**ERROR** ' , resp.status_code, ' ', resp.reason)

	else:

		print('Request returned ' , resp.status_code, ' ', resp.reason)
		resp_json = resp.json()
    
		access_token = resp.json()['access_token']

### STOP HERE IF NO ACCESS TOKEN (BOTH AUTH FAILED)

try:
  access_token
except NameError:
	print("Can't get access token, stopping here.")
	exit(1)

print("Requesting app management device list for tenant ID %s..." % constants.RAINIER_TENANTID)
headers = {
	"Content-Type" : "application/json",
	"Authorization" : "Bearer " + access_token, 
	"x-access-token" : access_token,
	"x-tenant-id": constants.RAINIER_TENANTID}

output = []
next = str('offset=0&limit=10')
	
while True:
	resp = requests.get(constants.RAINIER_BASEURL+'/appmgmt/devices?'+next,
	headers=headers,verify=False)
	if resp.status_code != 200:
    		# This means something went wrong.
    		print('**ERROR** ' , resp.status_code, ' ', resp.reason)
    		exit(1)

	else:
		#if debug: print(resp.json())
		output.extend(resp.json()['data'])
		print(".", end='')
		#if debug: print('Request returned ' , resp.status_code, ' ', resp.reason)
		if 'next' in resp.json():
			next = resp.json()['next'].split('?',1)[1]
		else:
			break

devices_ok = ""
devices_unreach = ""
devices_with_errors = ""

for z in output:
	if z['status'] == "DISCOVERED":
	    apps = []
	    #print(json.dumps(z['tags'], indent=2))
	    for zz in z['tags']:
	    	if not zz['name'].startswith("Group=") and not zz['name'].startswith("Type="):
	    		apps.append(zz['name'])
	    devices_ok = devices_ok + str("{:<20} | {:<15} | {:<15}".format(z['userProvidedSerialNumber'], z['status'], str(apps)))+'\n'
	    continue
	if (('errorMessage' in z) and (z['errorMessage'] == "Device unreachable : null")):
	    devices_unreach = devices_unreach + str("{:<20} | {:<15} | {:<15}".format(z['userProvidedSerialNumber'], z['status'], z['errorMessage'])) + '\n'
	    continue
    
	devices_with_errors = devices_with_errors + str("{:<20} | {:<15} | {:<15}".format(z['userProvidedSerialNumber'], z['status'], z['errorMessage'])) + '\n'

	# Let's refresh devices with errors
	refresh_iox_device(z['deviceId'])

print("")
print("-[ OK ]------------------------------")
print(devices_ok)

print("-[ UNREACHABLE ----------------------")
print(devices_unreach)
   	
print("-[ ERRORS ]--------------------------")
print(devices_with_errors)
