# rainier-api
Sample programs to demonstrate how to use Cisco IoT Operations Dashboard (IoT OD) APIs. This is a work in progress and an individual contribution. 

You need to rename `constants.py.example` to `constants.py` and add your own variables such as:
* username
* password
* base URL (ie: "https://eu.ciscoiot.com" or "https://us.ciscoiot.com" - not trailing slash)
* tenant ID (if you don't know one, leave this blank and run the program once and it will list the tenant IDs you have access to)

Simply run the sample program with:

python3 api-test.py
