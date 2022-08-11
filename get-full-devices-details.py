#!/usr/bin/python3

## Copyright 2021 Emmanuel Tychon
## Use of this source code is governed by an MIT-style
## license that can be found in the LICENSE file or at
## https://opensource.org/licenses/MIT.

## This code is an individual contribution not endorsed, nor supported by Cisco

## This will output a JSON file with _all_ the device details in the selected IoT OD org.
## It is expensive to run as a single API call will need to be done for each device.
## 
## Run this script like: get-full-devices-details.py -t <ORG_NAME> -o <filename>.json

## Output file is in JSON format but can be converted to CSV with the "dasdel" (data slelector) utility
## ie: dasel -f <filename>.json -p json -w csv > <filename>.csv

from enum import Enum
import rainierlib.rainierapi
import constants
import json
import argparse

def is_not_blank(s):
    return bool(s and not s.isspace())

parser = argparse.ArgumentParser(
    prog='PROG', description='Process IoT OD gateways with Edge Device Manager API')
parser.add_argument('--verbose', '-v',
                    help='verbose output', action='store_true')
parser.add_argument(
    '--tenant', '-t', help='tenant nickname as defined in constants.py')
parser.add_argument(
    '--output', '-o', help='Write JSON output as a file')
args = parser.parse_args()

# Read tenant nick name from CLI args if provided
if args.tenant:
	constants.tenant_name = args.tenant

# Load current tenant credentials from constants (see README.md file for how to do this)
constants.load_tenant_creds(constants.tenant_name)

print("Using tenant = {}, url = {}".format(
    constants.tenant_name, constants.RAINIER_BASEURL))

# Instanciate the rainierlib class
rl = rainierlib.rainierapi.rainierlib()

# Set the debug flag if verbose is set
if args.verbose:
    rl.enableDebugs(True)

if rl.DEBUG:
    print("**INFO** : Debugs enabled")

# Load all parameters for cluster, authentication, username, keys, etc... for this tenant
rl.loadTParameters(constants)

#print("Getting list #1")
## Get all devices in this tenant
r = rl.getAllDevices()

# Let's add more information to that list - slow and expensive
# the JSON  file can be converted to CSV laster using ie:
# dasel -f TSAEU.json -p json -w csv > TSAEU.csv

for item in r:
    print(item)
    print(item['name'])
    print(item['href'])
    resp = rl.runRainierQuery('GET', item['href']+'/data')
    if resp.status_code != 200:
        print("HTTPS return code: {}".format(resp.status_code))
    else:
        print(resp.json())
        for f in resp.json():
            item.update({f['field']: f['value']})

if args.output:
    with open(args.output, 'w') as json_file:
        json.dump(r, json_file, indent=4, separators=(',', ': '))

    print('Successfully written to the JSON file: {}'.format(args.output))
