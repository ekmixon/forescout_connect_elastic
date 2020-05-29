# Hold response to Forescout
response = {}

url = params["connect_elasticsearch_url"]

request = urllib.request.Request(url, data=bytes(json.dumps(params), encoding="utf-8"))
# To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
resp = urllib.request.urlopen(request, context=ssl_context)
response = {}

# Like the action response, the response object must have a "succeeded" field to denote success. It can also optionally have
# a "result_msg" field to display a custom test result message.
if resp.getcode() == 200:
    response["succeeded"] = True
    response["result_msg"] = "Successfully connected."
else:
    response["succeeded"] = False
    response["result_msg"] = "Could not connect to Elasticsearch server."