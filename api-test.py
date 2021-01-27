#!/usr/bin/python3

import requests, json
import constants
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# constants
debug = True 

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

### REQUESTING TOKEN FOR AUTHENTICATION 

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

print("Authenticating with API Key...")
headers = {'content-type': 'application/json'}
# Organization name and API key name both in lowercase format
task = {'grant_type': 'client_credentials',
		'client_id': "%s->%s" % (constants.RAINIER_ORG_NAME.lower(), constants.RAINIER_API_KEY_NAME.lower()),
		'client_secret': constants.RAINIER_API_KEY_SECRET}
if debug: print(task)
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
	if debug: print(resp_json)
    
	access_token = resp.json()['access_token']

try:
  access_token
except NameError:
	print("Can't get access token, stopping here.")
	exit(1)

### GETTING ALL TENANTS AND ROLES FOR THIS USER

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

### GETTING ALL DEVICES FOR A SPECIFIC TENANT

print("Requesting device list for tenant ID %s..." % constants.RAINIER_TENANTID)
headers = {
	"Content-Type" : "application/json",
	"Authorization" : "Bearer " + access_token, 
	"x-access-token" : access_token,
	"x-tenant-id": constants.RAINIER_TENANTID}
	
resp = requests.get(constants.RAINIER_BASEURL+'/resource/rest/api/v1/devices',
	headers=headers,
	verify=False)
if resp.status_code != 200:
    # This means something went wrong.
	print('**ERROR** ' , resp.status_code, ' ', resp.reason)
	exit(1)

else:

	if debug: print('Request returned ' , resp.status_code, ' ', resp.reason)
	
	if debug: print(resp.json())

	for z in resp.json()['results']:
		print(z['name'],' ',z['status'])


### GETTING ALL DEVICES FOR CURRENT TENANT

print("Requesting device list for current tenant...")
headers = {
	"Content-Type" : "application/json",
	"Authorization" : "Bearer " + access_token, 
	"x-access-token" : access_token}
	
resp = requests.get(constants.RAINIER_BASEURL+'/resource/rest/api/v1/devices',
	headers=headers,
	verify=False)
if resp.status_code != 200:
    # This means something went wrong.
	print('**ERROR** ' , resp.status_code, ' ', resp.reason)
	exit(1)

else:

	if debug: print('Request returned ' , resp.status_code, ' ', resp.reason)
	
	if debug: print(resp.json())

	for z in resp.json()['results']:
		print(z['name'],' ',z['status'])

