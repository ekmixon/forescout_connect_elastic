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
        "ip": sys.argv[2],
        "connect_authorization_token": sys.argv[3],
        "connect_elasticsearch_send_host_data_allfields": "",
        "connect_elasticsearch_send_host_data_hostfields": "",
        "connect_elasticsearch_url": "",
        "connect_elasticsearch_username": "",
        "connect_elasticsearch_password": "",
    }
# END CLI TESTING


# Hold response to Forescout EyeExtend Connect
# Like the action response, the response object must have a "succeeded" field to denote success. It can also optionally have
# a "result_msg" field to display a custom test result message.
response = {}

# Get Forescout OIM Web API Details (We connect to OIM to get data)
forescout_url = params["connect_elasticsearch_forescout_url"]
forescout_jwt_token = params["connect_authorization_token"]

# Get Elasticsearch API Details (To send data to)
elastic_url = params["connect_elasticsearch_url"]
elastic_username = params["connect_elasticsearch_username"]
elastic_password = params["connect_elasticsearch_password"]

# Get parameter details from action dialog
host_ip = params["ip"] # Host IP address
send_all_data = params["connect_elasticsearch_send_host_data_allfields"] # If all data should be included from host
specified_data = params["connect_elasticsearch_send_host_data_hostfields"] # or specific parsed version
host_data = {} # don't have host data yet

# Get host details from Forescout Web API
headers = {"Authorization": forescout_jwt_token}
request = urllib.request.Request(forescout_url + "/api/hosts/ip/" + host_ip, headers=headers)
try:
    # Make API request to Forescout Web API For host
    resp = urllib.request.urlopen(request, context=ssl_context) # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
    # If we are authorized return to EyeExtend Connect
    if resp.getcode() == 200:
        host_data = json.loads(resp.read().decode('utf-8'))
    else:
        response["succeeded"] = False
    response["result_msg"] = "Could not connect to Forescout Web API server."
except:
    response["succeeded"] = False
    response["result_msg"] = "Could not connect to Forescout Web API server."

# Process host data with respect to action configuration 
elastic_payload = {}

print(host_data)