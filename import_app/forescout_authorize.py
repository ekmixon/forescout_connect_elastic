import json
import urllib.request

# CLI Testing
try:
    params
    # running in eyeExtend connect
except: 
    import sys
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    params = {
        "connect_elasticsearch_forescout_url": sys.argv[1],
        "connect_elasticsearch_forescout_username": sys.argv[2],
        "connect_elasticsearch_forescout_password": sys.argv[3]
    }
# END CLI TESTING

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params["connect_elasticsearch_forescout_url"] # Server URL
username = params["connect_elasticsearch_forescout_username"] # OIM Username
password = params["connect_elasticsearch_forescout_password"] # OIM Password

# Making an API call to get the JWT token
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {"username": username, "password": password}
request = urllib.request.Request(url + "/api/login", headers=headers, data=bytes(urllib.parse.urlencode(data), encoding="utf-8"))

# To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
response = {} # respones to forecout EyeExtend Connect
try:
    # Make API request
    resp = urllib.request.urlopen(request, context=ssl_context)
    # If we are authorized return to EyeExtend Connect
    if resp.getcode() == 200:
        response["token"] = resp.read().decode('utf-8')
    else:
        response["token"] = ""
except:
    response["token"] = ""

print(response)