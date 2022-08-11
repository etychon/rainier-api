# rainier-api
Sample scripts to demonstrate how to use Cisco IoT Operations Dashboard (IoT OD) APIs.

At this time there is no official API documentation.
This is a work in progress and an individual contribution as Cisco IoT Operations Dashboard APIs are currently not supported by Cisco.

# Download the code

Clone this repository on your computer:

```
git clone git@github.com:etychon/rainier-api.git
cd rainier-api/
```

# How to use?

Those scripts will require credentials and cluster details to work. I have provided an example of such a file in `constants.py.example`.
This one file can be used to hold credentials for mutliple organisations, users, or clusters.

You need to rename `constants.py.example` to `constants.py` and add your own variables.

For example to add new tenant 'ACME_1_EU' with username and password authentication, add a block to `constants.py` like this:

```python
if t_name == "ACME_1_EU":
  ### ACME company 1 on EU cluster with username and password
  RAINIER_BASEURL = "https://eu.ciscoiot.com"
  RAINIER_USERNAME = "user@mail.com"
  RAINIER_PASSWORD = "secret"
  RAINIER_TENANTID = "8b591a0b-15f5-45f2-8586-bf2524a9e5b6"
```

To add a new new tenant using API Key authentication, add a block to `constants.py` like this:

```python
if t_name == 'ACME_3_API':
  # ACME company 3 using API Keys
  RAINIER_BASEURL = "https://us.ciscoiot.com"
  RAINIER_ORG_NAME = "ACME_3"
  RAINIER_API_KEY_NAME = "keyname"
  RAINIER_API_KEY_SECRET = "apisecret"
  RAINIER_TENANTID = "44a84a86-dca4-4a37-8a84-1a47eb0f5ee6"
```

You need to rename `constants.py.example` to `constants.py` and add your own variables.

Always needed:

* `RAINIER_BASEURL` is the base URL (ie: "https://eu.ciscoiot.com" or "https://us.ciscoiot.com") with the HTTPS on front and without trailing slash
* `RAINIER_TENANTID` is the tenant ID (see below on how to get it)

Needed for username password authentication:

* `RAINIER_USERNAME` is your username
* `RAINIER_PASSWORD` is your password

Needed for API authentication:

* `RAINIER_ORG_NAME` is the full name of the organisation (ie: "Technical Marketing Engineers")
* `RAINIER_API_KEY_NAME` is the name of your API key as defined in IoT OD
* `RAINIER_API_KEY_SECRET` if the secret generate when the API key was created. If you misplaced it, you need to generate a new key.

You can also customize the `constants.py` to include credentials for
multiple tenants on multiple clusters. This will allow to call the scripts
using just the tenenat name.

# How to get the RAINIER_TENANTID ?

RAINIER_TENANTID is an identifier used by APIs, and not directly visible to the end-user in the web interface. It identifies your Cisco IoT OD organisation in an immutable way, so it always remains the same even if the organisation name changes.

To get the RAINIER_TENANTID for a specific organisation:

1. login to your tenant and go in EDM -> Inventory
2. In Chrome open the developer tools in View -> Developper -> Developper Tools
3. Select the "Network" tab at the top
4. In IoT OD click on the "refresh button once"
5. In the Developer Tool you will see an API call like this https://eu.ciscoiot.com/resource/rest/api/v1/devices?sortBy=lastHeard&sortDir=desc&page=1&size=100
6. Click on this call
7. Open the "Headers" section
8. Scroll down and look for the value called "x-tenant-id", right click, copy value (it looks like "e0874499-c6d1-4b9e-bb7b-795b001fcefa")
9. Paste that value in the constants.py file as explained above

# Pagination

All IoT OD APIs are using pagination to deal with thousands of entries, it
is better to run 10 queries for 100 devices each rather than 1 query for
1000 devices, or 1000 queries for 1 device each.

Pagination method used in EDM if different than the pagination method used
for application management. Please see the examples below on how use them.

# Using the Device Management API

This API can be used to manage gateways in IoT OD, such as checking gateway
status, IOS release and other details. This script show how to use
API pagination in EDM API.

Simply run the sample program with:

`python3 ./api-test.py`

# Using the Application Management API

The application management API allows to collect information on IOx
applications running on gateways. This gateway supports pagination on
Application management API.

For example one can list all applications installed on all gateways with
their operational status with:

`python3 ./appmgmnt.py`

# Using the Rainier library (new)

I have started developping a Python library to improve code re-usability. It is very basic but its a foundation to add more capabilies in the future.

Check this example to see how to use the library:

`rainier-library-test.py`

# Loading credentials

Once the `constants.py` is complete with your credentials you can load them very simply with just a couple of lines, for example to load the credentials for organisation "ACME_4_API" simply do this:

```python
import constants
constants.load_tenant_creds("ACME_4_API")
```

# Authentication to IoT OD

Once the constants have been loaded at the previous step, add `rainierlib` module, load and validate the credentials with just a couple line:

```python
import rainierlib.rainierapi
rl = rainierlib.rainierapi.rainierlib()
rl.loadTParameters(constants)
```

That's it. When you instanciate the class in "rl", it will store the credentials, access_token, and will take care of token refresh for you while you focus on what matters.

You should see a message "Autentication OK." if you run this and all is fine.

# Getting the device list

The library will do all the heavy lifting for you, for example you list all the devices and associated parameters with just one line:

```python
print(rl.getAllDevices())
```

# Getting the device list with all the details

From the previous example we can get all devices from the selected organisation. But this list is missing some information, for example the AP firmware release is not in that inventory. The only way to get the AP firmware release is to query the specific device data by querying the "href".

The code below gets all devices, and for each device queries the specific device attributed. It extends the current dictionary from getAllDevices() by adding all the additional parameters from the device specific query.

Word of caution as this will create one API call per device, this request is slow and expensive to run.

PS: you can convert this output (in JSON) to CSV very simply by doing: `dasel -f <input_filename>.json -p json -w csv > <output_filename>.csv`

```python
r = rl.getAllDevices()

# Here is the basic list
print(r)

# Let's add more information to that list - slow and expensive

for item in r:
    print(item['name'])
    # Let's query the specific device details
    resp = rl.runRainierQuery('GET', item['href']+'/data')
    if resp.status_code != 200:
        print("HTTPS return code: {}".format(resp.status_code))
    else:
        # Add all fields to this device's dict entry
        for f in resp.json():
            item.update({f['field']: f['value']})

# Here is the enriched list with all additional properties
print(r)

```

You can find a specific example on how to do that here: https://github.com/etychon/rainier-api/blob/main/get-full-devices-details.py

# Why is this called "Rainier"?

Let's talk about the internal laundry. When we start developing a product we do not know yet what is going to be the customer facing product name, so we always use internal project names early on.

"Rainier" - taking inspiration of the famous Mount Rainier, is the Cisco internal product name for "Cisco IoT Operations Dashboard". Prior to that name it was briefly called "Cisco IoT Operations Center" and you may still see references to "IOTOC" in Cisco Commerce Workplace (the ordering platform).
