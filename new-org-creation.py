#!/usr/bin/python3

"""
Example of execution to create a new org, name "etychon-test-003", on EU cluster, with SEA, App Management and CyberVision:

  python3 ./new-org-creation.py --operation create --cluster EU etychon-test-003 --services sra app-mgmt ccv
"""

import requests, json
import constants
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

"""
  	Add a block like this in constants.py to make this work, do it for US and EU clusters:
  	if t_name == 'root_org_credentials_US':
      # root org on US cluster
      RAINIER_BASEURL = "https://us.ciscoiot.com"
      RAINIER_API_KEY_NAME = "**replace with API key name**"
      RAINIER_API_KEY_SECRET = "**replace with API secret**"
      PARENT_TENANT_ID = '**replace with root org uuid**'
      AUTO_ADMINS = "**replace with your email**"
"""

parser = argparse.ArgumentParser(prog='PROG', description='Create, delete and modify IoT OD organizations')
parser.add_argument('--verbose', '-v', help='verbose output', action='store_true')
parser.add_argument('--operation', help='Operation to execute (create, update)', choices=['create', 'update'], required=True)
parser.add_argument('name', help='organization name')
parser.add_argument('--cluster', choices=['EU', 'US'], help='Cluster for new org (EU or US)', required=True)
parser.add_argument('--services', choices=['app-mgmt', 'asset-visibility', 'network-mgmt', 'ccv', 'urwb', 'sra', 'edge-intelligence'], nargs="+", required=True)

args = parser.parse_args()

# constants
debug = True 
use_API_Key = True

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Read cluster from CLI args and create a tenant name to use with constants.py
if args.cluster:
	root_org_credentials = "root_org_credentials_"+args.cluster
	print("Using credentials for "+root_org_credentials)
	constants.tenant_name = root_org_credentials

# Load current tenant credentials
constants.load_tenant_creds(constants.tenant_name)

print("tenant = {}, url = {}".format(constants.tenant_name, constants.RAINIER_BASEURL))

if (not use_API_Key):
	print("This script only supports API token authentication, exiting...")
	quit()

### REQUESTING TOKEN FOR AUTHENTICATION (with API KEY)

print("Authenticating with API Key...")
headers = {'content-type': 'application/json'}
# Organization name and API key name both in lowercase format
task = {'grant_type': 'client_credentials',
		'client_id': constants.RAINIER_API_KEY_NAME.lower(),
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

def create_new_org():
	print("Creating new top-level organization '%s'..." % args.name)
	headers = {
		"Content-Type" : "application/json",
		"Authorization" : "Bearer " + access_token,
		"x-access-token" : access_token,
		"x-tenant-id": constants.PARENT_TENANT_ID}
	params = dict(
		name=args.name,
		description=args.name,
		parent_tenant_id=constants.PARENT_TENANT_ID,
		metadata="POC",
		admins=[constants.AUTO_ADMINS],
		new_cci_admins=[],
		services=[
			dict(
				uuid="79e64b1f-e6cc-4e0f-88c7-4c2b82e27114",
				name="app-mgmt",
				display_name="Application Manager", 
				description="Synchronize and manage applications for your network devices.",
				enabled=("app-mgmt" in args.services), 
				status="active"
			),
			dict(
				uuid="efd36200-ab1e-42c7-b9e8-eda2ee6915bb",
				name="asset-visibility",
				display_name="Asset Vision", 
				description="Track and monitor telemetry of your assets and sensors.", 
				enabled=("asset-visibility" in args.services), 
				status="active"
			),
			dict(
				uuid="989cf627-c94a-4383-a83a-e2504f7c8137", 
				name="network-mgmt", 
				display_name="Edge Device Manager", 
				description="Manage your network of devices.", 
				enabled=("network-mgmt" in args.services), 
				status="active"
			),
        	dict(
				uuid="10e52dda-479f-4520-b18f-c32da317de66", 
				name="ccv", 
				display_name="Cyber Vision", 
				description="Secure your Industrial Control Systems.", 
				enabled=("ccv" in args.services), 
				status="active"
			), 
        	dict(
				uuid="dd614e0f-4b1f-a83a-f922-ab1ef62791c4", 
				name="urwb", 
				display_name="Industrial Wireless", 
				description="Configure and manage your Industrial Wireless devices", 
				enabled=("urwb" in args.services), 
				status="active"
			), 
        	dict(
				uuid="57533aaa-65e2-4b01-a61d-b25adcbfc199", 
				name="sra", 
				display_name="Secure Equipment Access", 
				description="Securely access your equipment.", 
				enabled=("sra" in args.services), 
				status="active"
			), 
        	dict(
				uuid="67fdbe66-dd61-4ffe-91cc-d05cd5caac60", 
				name="edge-intelligence", 
				display_name="Edge Intelligence", 
				description="Extract, Transform, Govern and Deliver your data from Edge to Multi Cloud destinations.", 
				enabled=("edge-intelligence" in args.services),
				status="active"
			) 
		]
	)

	print(json.dumps(params))

	resp = requests.post(constants.RAINIER_BASEURL+'/iam/tenants/',
		headers=headers,verify=False, data=json.dumps(params))

	print(resp.status_code, ' ', resp.reason, ' ')
	if resp.status_code != 200:
		# This means something went wrong.
		print('**ERROR** ' , resp.json().get('message'))
		print('This operation did not execute.')
		exit(1)
	else:
		print('Operation completed with success.')
		print('Services enabled: %s' % args.services)
		print(resp)

	return(0)

def update_org():
	print("Updating top-level organization '%s'..." % args.name)
	headers = {
		"Content-Type" : "application/json",
		"Authorization" : "Bearer " + access_token,
		"x-access-token" : access_token,
		"x-tenant-id": constants.PARENT_TENANT_ID}
	params = dict(
		name=args.name,
		description=args.name,
		parent_tenant_id=constants.PARENT_TENANT_ID,
		metadata="POC",
		admins=[constants.AUTO_ADMINS],
		new_cci_admins=[],
		services=[
			dict(
				uuid="79e64b1f-e6cc-4e0f-88c7-4c2b82e27114",
				name="app-mgmt",
				display_name="Application Manager", 
				description="Synchronize and manage applications for your network devices.",
				enabled=True, 
				status="active"
			)
		]
	)

	print(json.dumps(params))

	resp = requests.put(constants.RAINIER_BASEURL+'/iam/tenants/{tenant_uuid}',
		headers=headers,verify=False, data=json.dumps(params))

	if resp.status_code != 200:
		# This means something went wrong.
		print('**ERROR** ' , resp.status_code, ' ', resp.reason, ' ', resp.content, ' ', resp.headers)
		print(resp.content)
		print('This operation did not execute.')
		exit(1)
	else:
		print(resp)
	return(0)



if args.operation == "create":
	print("Creating new top-level organization '%s'..." % args.name)
	create_new_org()
elif args.operation == "update":
	print("Updating top-level organization '%s'..." % args.name)
	update_org()
else:
	print("Nothing to do, exiting...")

exit()

