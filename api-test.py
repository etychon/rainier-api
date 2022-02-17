#!/usr/bin/python3

import requests, json
import constants
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning


parser = argparse.ArgumentParser(prog='PROG', description='Process IoT OD gateways with Edge Device Manager API')
parser.add_argument('--verbose', '-v', help='verbose output', action='store_true')
parser.add_argument('--tenant', '-t', help='tenant nickname as defined in constants.py')
parser.add_argument('--push', '-p', help='push config on this device')
args = parser.parse_args()

# constants
debug = True 
use_API_Key = False

# limit all queries to a fixed # of devices (handy when developing)
limit = 1000

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Read tenant nick name from CLI args if provided
if args.tenant:
	constants.tenant_name = args.tenant

# Load current tenant credentials
constants.load_tenant_creds(constants.tenant_name)

print("tenant = {}, url = {}".format(constants.tenant_name, constants.RAINIER_BASEURL))

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
		if debug: print(resp_json)
    
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

### GETTING ALL TENANTS AND ROLES FOR THIS USER
### This won't work when using API key

print("Requesting tenants list and roles...")
headers = {
	"Content-Type" : "application/json",
	"Authorization" : "Bearer " + access_token, 
	"x-access-token" : access_token}
if debug: print(headers)
resp = requests.get(constants.RAINIER_BASEURL+'/iam/users/me',
	headers=headers,
	verify=False)

if resp.status_code != 200:
    # This means something went wrong.
	print('**ERROR** ' , resp.status_code, ' ', resp.reason)

else:
	if debug: print('Request returned ' , resp.status_code, ' ', resp.reason)
	
	if debug: print(resp.json())

	for z in resp.json()['roles']:
		print(z['tenant_name'], ' ', z['tenant_id'], ' ', z['role_name'])

## Get all devices, returns a list
def get_all_devices():

	devices = []

	page = 1
	size = 100

	print("Requesting device list for tenant ID %s..." % constants.RAINIER_TENANTID)
	headers = {
		"Content-Type" : "application/json",
		"Authorization" : "Bearer " + access_token,
		"x-access-token" : access_token,
		"x-tenant-id": constants.RAINIER_TENANTID}

	while size > 0:
	
		resp = requests.get(constants.RAINIER_BASEURL+'/resource/rest/api/v1/devices?page='+str(page)+
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

			if debug:
				# print("Progress ({}-{}/{}): got {} entries".format((page-1)*size,(page*size)-1,total,received)) 
				print(" {} % ... ".format(min(100,round((page*size*100)/total))), end = '', flush=True)
				#print(r)

			if received < size:
				# that was the last page
				break

			page = page + 1

	return(devices)


## Push config on one device - take one eid and deviceType
## deviceType is case sensitive (ir800 and not IR800)
def push_config(eid, deviceType):

	headers = {
		"Content-Type" : "application/json",
        "Authorization" : "Bearer " + access_token,
        # "x-access-token" : access_token,
        "x-tenant-id": constants.RAINIER_TENANTID}          

	myobj = '[{"eid": "' + eid + '","fields":{"deviceType":"' +deviceType+ '"}}]'
	print(myobj)

	resp = requests.post(constants.RAINIER_BASEURL+'/resource/rest/api/v1/devices/config?operationType=PUSH',
	headers=headers,verify=False, data=myobj)

	if resp.status_code != 200:
		# This means something went wrong.
		print('**ERROR** ' , resp.status_code, ' ', resp.reason)
		print('It could be that a config push is already in progress')
		exit(1)
	else:
		print(resp)
	
	return(0)


out = get_all_devices()

print("*** total "+str(len(out))+" devices ***")

for z in out:
	print("-> {} | {} [coords:{},{}]".format(str(z['name']), str(z['status']), z['lat'], z['lng']))

if args.push:
	print("Pushing config on device name: {}".format(args.push))
	# Push API needs both "eid" and "deviceType", got get them
	for z in out:
		if (args.push == z['name']):
			print("found device to push config: eid = {}, deviceType= {}".format(z['eid'], z['deviceType']))
			if z['status'] == "configuring":
				print("A config push is already in progress, not pushing config.")
			else:
				print("Pushing config on {}".format(z['name']))
				push_config(z['eid'], z['deviceType'].lower())
  