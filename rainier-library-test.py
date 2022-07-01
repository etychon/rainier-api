#!/usr/bin/python3

import rainierlib.rainierapi
import constants
import argparse

def is_not_blank(s):
    return bool(s and not s.isspace())

parser = argparse.ArgumentParser(prog='PROG', description='Process IoT OD gateways with Edge Device Manager API')
parser.add_argument('--verbose', '-v', help='verbose output', action='store_true')
parser.add_argument('--tenant', '-t', help='tenant nickname as defined in constants.py')
args = parser.parse_args()

# Read tenant nick name from CLI args if provided
if args.tenant:
	constants.tenant_name = args.tenant

# Load current tenant credentials from constants (see README.md file for how to do this)
constants.load_tenant_creds(constants.tenant_name)

print("Using tenant = {}, url = {}".format(constants.tenant_name, constants.RAINIER_BASEURL))

# Instanciate the rainierlib class
rl = rainierlib.rainierapi.rainierlib()

# Load all parameters for cluster, authentication, username, keys, etc... for this tenant
rl.loadTParameters(constants)

# Get all devices in this tenant
print(rl.getAllDevices())

print("Done.")
