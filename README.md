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

You need to rename `constants.py.example` to `constants.py` and add your own variables such as:
* `RAINIER_USERNAME` is your username
* `RAINIER_PASSWORD` is your password
* `RAINIER_BASEURL` is the base URL (ie: "https://eu.ciscoiot.com" or "https://us.ciscoiot.com") without trailing slash
* `RAINIER_TENANTID` is the tenant ID (if you don't know one, leave this blank and run the program once and it will list the tenant IDs you have access to)

If you are using an API key instead of username/password:
* `RAINIER_ORG_NAME` is the full name of the organisation (ie: "Technical Marketing Engineers")
* `RAINIER_API_KEY_NAME` is the name of your API key as defined in IoT OD
* `RAINIER_API_KEY_SECRET` if the secret generate when the API key was created. If you misplaced it, you need to generate a new key.

You can also customize the `constants.py` to include credentials for
multiple tenants on multiple clusters. This will allow to call the scripts
using just the tenenat name.

# Pagination

All IoT OD APIs are using pagination to deal with thousands of entries, it
is better to run 10 queries for 100 devices each rather than one query for
1000 devices. 

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
