#!/usr/bin/python3

### TODO
### Add ability to download IOx tech-support logs for gateways in error
### Add ability to cross-check GOS / IOS / HV version and identify mismatch (IR8x9 only)

import argparse
import requests, json
import constants
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning

parser = argparse.ArgumentParser(prog='PROG', description='Process IoT OD gateways with application management.')
parser.add_argument('--refresh', '-r', choices=['error', 'null', 'all'], help='refresh application management on gateways with errors, null or all')
parser.add_argument('--verbose', '-v', help='verbose output', action='store_true')
parser.add_argument('--tenant', '-t', help='tenant nickname as defined in constants.py')
args = parser.parse_args()

# constants
debug = args.verbose
use_API_Key = False

if debug: print("[INFO] verbose output is enabled")

# don't warn if HTTPS connections are not valid
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Read tenant nick name from CLI args if provided
if args.tenant:
    constants.tenant_name = args.tenant

# Load current tenant credentials
constants.load_tenant_creds(constants.tenant_name)

print("tenant = {}, url = {}".format(constants.tenant_name, constants.RAINIER_BASEURL))

def refresh_iox_device(devId):

	if debug: print("Refreshing device "+devId)

	headers = {
        	"Content-Type" : "application/json",
        	"Authorization" : "Bearer " + access_token,
        	"X-Tenant-ID": constants.RAINIER_TENANTID}

	myobj = '{"actionType": "RefreshInventory"}'

	resp = requests.post(constants.RAINIER_BASEURL+'/appmgmt/devices/'+devId+'/action',
        	headers=headers,verify=False, data = myobj)

	#print(resp.request.url)
	#print(resp.request.headers)
	#print(resp.request.body)

	if resp.status_code != 200:
        # This means something went wrong.
        	if debug: print('**ERROR** ' , resp.status_code, ' ', resp.reason)
	else:
		if debug: print('Request returned ' , resp.status_code, ' ', resp.reason)

def do_dev_refresh_print(devId):
    print(" refreshing...", end='', flush = True)
    refresh_iox_device(devId)
    print(" done.", end='', flush = True)


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

print("Requesting app management device list for tenant ID %s..." % constants.RAINIER_TENANTID)
headers = {
	"Content-Type" : "application/json",
	"Authorization" : "Bearer " + access_token, 
	"x-access-token" : access_token,
	"x-tenant-id": constants.RAINIER_TENANTID}

output = []
next = str('offset=0&limit=10')

print("Getting device list", end='', flush = True)
	
while True:
	resp = requests.get(constants.RAINIER_BASEURL+'/appmgmt/devices?detail=app&'+next,
	headers=headers,verify=False)
	if resp.status_code != 200:
    		# This means something went wrong.
    		print('**ERROR** ' , resp.status_code, ' ', resp.reason)
    		exit(1)

	else:
		if debug: print(json.dumps(resp.json(), indent=2))
		output.extend(resp.json()['data'])
		print(".", end='', flush = True)
		if debug: print('Request returned ' , resp.status_code, ' ', resp.reason)
		if 'next' in resp.json():
			next = resp.json()['next'].split('?',1)[1]
		else:
			break

# Initialize lists of devices (strings)
devices_ok = []
devices_unreach = []
devices_with_errors = []

# Let's go through all devices in 'output' and classify them in 3 lists
for z in output:
	if z['status'] == "DISCOVERED":
		devices_ok.append(z)
		continue
	if (('errorMessage' in z) and (z['errorMessage'] == "Device unreachable : null")):
		devices_unreach.append(z)
		continue
	devices_with_errors.append(z)	

# Process OK devices
print("\n-[ OK: {} ]------------------------------".format(len(devices_ok)))
for z in devices_ok:
	apps = []
    # print(json.dumps(z, indent=2))
	for zz in z['apps']:
		#if not zz['name'].startswith("Group=") and not zz['name'].startswith("Type="):
		apps.append(zz['name'] + "("+zz['status']+")")
	print("{:<25.25} | {:<13.13} | {:<15}".format(z['userProvidedSerialNumber'], z['status'], str(apps)), end='', flush = True)
	if args.refresh == "all" :
		do_dev_refresh_print(z['deviceId'])
	print('')

# Process unreachable devices
print("\n-[ UNREACHABLE: {} ]------------------------------".format(len(devices_unreach)))
for z in devices_unreach:
	print(("{:<25.25} | {:<21.21} | {:<15}".format(z['userProvidedSerialNumber'], z['status'], z['errorMessage'])), end='', flush = True)
	if args.refresh == "all" or args.refresh == "null":
		do_dev_refresh_print(z['deviceId'])
	print('')

# Process devices with error
print("\n-[ ERROR: {} ]--------------------------".format(len(devices_with_errors)))
for z in devices_with_errors:
	print(("{:<25.25} | {:<21.21} | {:<15}".format(z['userProvidedSerialNumber'], z['status'], z['errorMessage'])), end='', flush = True)
	if args.refresh == "all" or args.refresh == "error":
		do_dev_refresh_print(z['deviceId'])
	print('')

sys.exit("\ndone")

