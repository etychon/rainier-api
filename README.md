# rainier-api
Sample programs to demonstrate how to use Cisco IoT Operations Dashboard (IoT OD) APIs. This is a work in progress and an individual contribution. 

At this time there is no official API documentation - this is a work in progress.

# How to use? 

You need to rename `constants.py.example` to `constants.py` and add your own variables such as:
* `RAINIER_USERNAME` is your username
* `RAINIER_PASSWORD` is your password
* `RAINIER_BASEURL` is the base URL (ie: "https://eu.ciscoiot.com" or "https://us.ciscoiot.com") without trailing slash
* `RAINIER_TENANTID` is the tenant ID (if you don't know one, leave this blank and run the program once and it will list the tenant IDs you have access to)

If you are using an API key instead of username/password:
* `RAINIER_ORG_NAME` is the full name of the organisation (ie: "Technical Marketing Engineers")
* `RAINIER_API_KEY_NAME` is the name of your API key as defined in IoT OD
* `RAINIER_API_KEY_SECRET` if the secret generate when the API key was created. If you misplaced it, you need to generate a new key.

Simply run the sample program with:

`python3 api-test.py`

