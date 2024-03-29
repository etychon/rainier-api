#!/usr/bin/python3

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

print(r)

c = rl.cancelFirmwareJob("094319f8-a3c0-4fbf-95fe-3b95847e1919")

print(c)

#print("Getting all details of this gateway's name...")
#print(rl.getDeviceDetails(device_name="egon-ir1101-1"))

#print("Getting all details of non-existent gateway SN...")
#print(rl.getDeviceDetails(sn="FCWXXXXXX2X"))

#print("Getting all details for devices in group...")
#r = rl.getAllDevicesInGroup('etychon-ir1101-ecvd-adv-egon-nocell')
#if r:
#    print("found {} devices".format(len(r)))
#    for z in r:
#        print("{} - {}".format(z['name'], z['SN']))
#
#print("Done.")

#  add a new device
#r = rl.addNewDevice("IR1101-K9+AB123456788", "deleteme",
#                    "etychon-ir1101-ecvd-adv-egon-nocell")

# Did that request work?
#if r.status_code == 201:
#    print("Adding device done: {}".format(rl.showRainierErrorMessage(r)))
#else:
#    print("Failed :(")
#    print(rl.showRainierErrorMessage(r))

#  delete a device
#r = rl.deleteDevicesByEid("IR1101-K9+AB123456788")

# Did that request work?
#if r.status_code <= 201:
#    print("Delete device done: {}".format(rl.showRainierErrorMessage(r)))
#else:
#    print("Failed :(")
#    print(r.content)
#    print(rl.showRainierErrorMessage(r))
