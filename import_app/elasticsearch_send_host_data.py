import json
import urllib.request
import re

# CLI Testing
import sys
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
params = {
    "connect_elasticsearch_forescout_url": "https://fsctlab.corp.davsol.net",
    "ip": "10.1.40.53",
    "connect_authorization_token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZW1v4p-H67eD4YSQ57-e6a6R5ZqT6K-R4YWX4aqE5b2C57q56JC95KaC6IWP5pKV4bWj55uB5r-i5oeo5ba96pa06q6I6aOe5pGy5KKP6piS7Kel5rCG4LWu6JKV65uh74Kr8J2WhOW8guK2ruCltO-Dsuyku-yAhu6lru-jq-uNmeWwgOiDgOS_uuGutuqQj8Sm5K69466Q5Lq45Y2H7Kas4qCC7qai4ZS-6K-x7r6W6p-E5bK76pGp6qm87KKvIiwiZXhwIjoxNTkxMjI1NjkyfQ.LSo-DfromyiEVeQ1FfH_hnL5tYXMbFLD-86E42jCpfo",
    "connect_elasticsearch_send_host_data_allfields": 0,
    "connect_elasticsearch_send_host_data_hostfields": "service_installed(service_installed),va_os_cpe(va_os_cpe)",
    "connect_elasticsearch_url": "https://2be6b5cfb7f27e3019aabe1c1d5556fd.m.pipedream.net",
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

# Create request to get host data from Forescout
forescout_headers = {"Authorization": forescout_jwt_token}
forescout_request = urllib.request.Request(forescout_url + "/api/hosts/ip/" + host_ip, headers=forescout_headers)

try:
    # Make API request to Forescout Web API For host
    forescout_resp = urllib.request.urlopen(forescout_request, context=ssl_context) # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
    if forescout_resp.getcode() == 200:
        # Load response data
        host_data = json.loads(forescout_resp.read().decode('utf-8'))

        # Process host data with respect to EyeExtend Connect Send Data action specification
        elastic_payload = {}
        if(send_all_data):
            # If send all is checked, we send all, not need for extra formatting
            elastic_payload = host_data["host"]
        else: 
            # Add IP and mac field to data and setup for fields data
            elastic_payload["ip"] = host_data["host"]["ip"]
            elastic_payload["mac"] = host_data["host"]["mac"]
            elastic_payload["fields"] = {}

            # Take user input and extract requested fields and alias name
            specified_fields = specified_data.split(",") # split the stirng format at commas

            # Take each field specification and get the data form the host_data
            for field_token in specified_fields:
                re_match = re.match("(?P<field_name>.*)\((?P<alias_name>.*)\)", field_token) # Regex to break up the format
                elastic_payload["fields"][re_match.group('alias_name')] = host_data["host"]["fields"][re_match.group('field_name')]
                
        # Prepare API request to elastic
        elastic_headers = {"Content-Type": "application/json"}
        elastic_request = urllib.request.Request(elastic_url + "/index/_doc/" + str(host_data["host"]["id"]), headers=elastic_headers, data=bytes(json.dumps(elastic_payload), encoding="utf-8"))

        # Make API request to elasticsearch API to put document
        elastic_resp = urllib.request.urlopen(elastic_request, context=ssl_context) # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
        
        # Check response from elasticsearch
        if elastic_resp.getcode() == 200:
            response["succeeded"] = True
            response["result_msg"] = "Successfully sent data!"
        else:
            response["succeeded"] = False
            response["result_msg"] = "Failed API request to elasticsearch!"
    else:
        response["succeeded"] = False
        response["result_msg"] = "Failed API request to Forescout Web API server!"
except Exception as e:
    print(e)
    response["succeeded"] = False
    response["result_msg"] = "Exception! Something went wrong! Couldn't talk to Forescout, action parsing failed, or message to Elastic failed. See the debug logs for more info."

print(response)