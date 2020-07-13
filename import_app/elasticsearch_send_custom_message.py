import json
import urllib.request
import base64
from datetime import datetime

######################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################
# CLI Testing
######################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################

# import logging
# import sys
# import ssl
# logging.getLogger().setLevel(logging.DEBUG)
# ssl_context = ssl.create_default_context()
# ssl_context.check_hostname = False
# ssl_context.verify_mode = ssl.CERT_NONE
# params = {
#     "ip": "10.1.40.53",

#     "connect_elasticsearch_forescout_url": "https://forescout.lab.davsol.net",
#     "connect_elasticsearch_forescout_username": "demo",
#     "connect_elasticsearch_forescout_password": "demo",

#     "connect_elasticsearch_send_custom_message_index_override": "",
#     "connect_elasticsearch_send_custom_message_type": "policy_status",
#     "connect_elasticsearch_send_custom_message_custom_field1": "C365 - CND - 30 Day Vuln Scan Compliance",
#     "connect_elasticsearch_send_custom_message_custom_field2": "Non-Compliant",
#     "connect_elasticsearch_send_custom_message_custom_field3": "",
#     "connect_elasticsearch_send_custom_message_body": "",

#     "connect_elasticsearch_url": "https://elastic.davsol.net",
#     "connect_elasticsearch_index": "forescout",
#     "connect_elasticsearch_username": "elastic",
#     "connect_elasticsearch_password": "elastic",
# }

# # Making an API call to get the Forescout JWT token
# headers = {"Content-Type": "application/x-www-form-urlencoded"}
# data = {"username": params["connect_elasticsearch_forescout_username"], "password": params["connect_elasticsearch_forescout_password"]}
# request = urllib.request.Request(params["connect_elasticsearch_forescout_url"] + "/api/login", headers=headers, data=bytes(urllib.parse.urlencode(data), encoding="utf-8"))

# # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
# response = {} # respones to forecout EyeExtend Connect
# try:
#     # Make API request
#     resp = urllib.request.urlopen(request, context=ssl_context)
#     # If we are authorized return to EyeExtend Connect
#     if resp.getcode() == 200:
#         logging.info("Received new Forescout OIM Web API JWT")
#         params["connect_authorization_token"] = resp.read().decode('utf-8')
#     else:
#         logging.error("Failed to get new Forescout OIM Web API JWT")
#         params["connect_authorization_token"] = ""
# except:
#     params["connect_authorization_token"] = ""

######################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################
# END CLI TESTING
######################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################

# Hold response to Forescout EyeExtend Connect
# Like the action response, the response object must have a "succeeded" field to denote success. It can also optionally have
# a "result_msg" field to display a custom test result message.
response = {}

# Get Forescout OIM Web API Details (We connect to OIM to get data)
forescout_url = params["connect_elasticsearch_forescout_url"]
forescout_jwt_token = params["connect_authorization_token"]

# Get Elasticsearch API Details (To send data to)
elastic_url = params["connect_elasticsearch_url"]
elastic_index = params["connect_elasticsearch_send_custom_message_index_override"] or params["connect_elasticsearch_index"]
elastic_username = params["connect_elasticsearch_username"]
elastic_password = params["connect_elasticsearch_password"]

# Get parameter details from action dialog
host_ip = params["ip"] # Host IP address
msg_type = params["connect_elasticsearch_send_custom_message_type"]
field1 = params["connect_elasticsearch_send_custom_message_custom_field1"]
field2 = params["connect_elasticsearch_send_custom_message_custom_field2"]
field3 = params["connect_elasticsearch_send_custom_message_custom_field3"]
body = params["connect_elasticsearch_send_custom_message_body"]
host_data = {} # don't have host data yet

# Create request to get host data from Forescout
forescout_headers = {"Authorization": forescout_jwt_token}
forescout_request = urllib.request.Request(forescout_url + "/api/hosts/ip/" + host_ip, headers=forescout_headers)

logging.debug("connect_elasticsearch_send_custom_message: Preparing to get host data from Forescout Web API")

try:
    # Make API request to Forescout Web API For host
    forescout_resp = urllib.request.urlopen(forescout_request, context=ssl_context) # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
    if forescout_resp.getcode() == 200:
        logging.debug("connect_elasticsearch_send_custom_message: Got data from Forescout Web API")
        # Load response data
        host_data = json.loads(forescout_resp.read().decode('utf-8'))

        # Process host data with respect to EyeExtend Connect Send Data action specification
        logging.debug("connect_elasticsearch_send_custom_message: Preparing elasticsearch payload")
        elastic_payload = {
            "time": datetime.now().isoformat(),
            "ip": host_data["host"]["ip"],
            "mac": host_data["host"]["mac"],
            "id": host_data["host"]["id"],
            "msg_type": msg_type,
            "custom_field1": field1,
            "custom_field2": field2,
            "custom_field3": field3,
            "body": body
        }

        # Prepare API request to elastic
        logging.debug(json.dumps(elastic_payload))
        credentials = ('%s:%s' % (elastic_username, elastic_password))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))
        elastic_headers = {
            "Content-Type": "application/json",
            'Authorization': 'Basic %s' % encoded_credentials.decode("ascii")
        }
        elastic_request = urllib.request.Request(elastic_url + "/" + elastic_index + "/_doc/", headers=elastic_headers, data=bytes(json.dumps(elastic_payload), encoding="utf-8"))

        # Make API request to elasticsearch API to put document
        elastic_resp = urllib.request.urlopen(elastic_request, context=ssl_context) # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
        elastic_resp_parse = json.loads(elastic_resp.read().decode('utf-8'))
        logging.debug(elastic_resp_parse)
        
        # Check response from elasticsearch
        if "result" in elastic_resp_parse and (elastic_resp_parse["result"] == "created" or elastic_resp_parse["result"] == "updated"):
            logging.info("connect_elasticsearch_send_custom_message: Sent host data to Elasticsearch succesfully!")
            response["succeeded"] = True
            response["result_msg"] = "Successfully sent data!"
            response["cookie"] = elastic_resp_parse["_id"]
        else:
            logging.error("connect_elasticsearch_send_custom_message: Failed to send host data to Elasticsearch!")
            logging.debug(elastic_resp.read().decode('utf-8'))
            response["succeeded"] = False
            response["result_msg"] = "Failed API request to elasticsearch!"
    else:
        logging.error("connect_elasticsearch_send_custom_message: Failed API Request to Forescout to get host data!")
        response["succeeded"] = False
        response["result_msg"] = "Failed API request to Forescout Web API server!"
except Exception as e:
    logging.error("connect_elasticsearch_send_custom_message exception: {}".format(e))
    response["succeeded"] = False
    response["result_msg"] = "Exception! Something went wrong! Couldn't talk to Forescout, action parsing failed, or message to Elastic failed. See the debug logs for more info."