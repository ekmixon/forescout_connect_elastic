
# connect_elasticsearch

Forescout EyeExtend Connect app for Elastic

## Allow unsigned app install on Forescout

When you import an app, the signature of the app is validated to see if it has a valid Forescout signature. If the validation succeeds, the app is imported. If the validation fails, an error message is displayed and the app is not imported. To allow an app with an invalid signature to be imported use the following command on the Enterprise Manager:

`fstool allow_unsigned_connect_app_install true`

This is a global command. It disables the enforcement of signature validation for all apps that are imported after the command is run, including apps with invalid or missing signatures.

## Creating zip

You have to make sure to not include any "extra" files when zipping up the app for import into Forescout. If you use the default "Compress" item in Finder on macOS, an `__macosx` folder is included which will cause Forescout to balk. Avoid this by opening terminal and going into the `app` directory and running the zip command manually:

`rm -f connect_elasticsearch.zip; zip connect_elasticsearch.zip ./*`

Note the above command also deletes the `connect_ealsticsearch.zip` file if it's there so you have a fresh copy.

## About

This Elasticsearch app for Forescout EyeExtend Connect allows you to send data from Forescout into an Elasticsearch index.

- The app makes an API request directly to Elasticsearch.

- The app leverages the Forescout EyeExtend Connect Web Service API in order to obtain the data about a host and then send to elasticsearch, consequently, data is send to elasticsearch in nearly the same format as if you were consuming it via the Forescout OIM Web API `/host/<host_id>` API

- There is support for selecting custom host fields as well as renaming fields

## Setup

 1. Enable the Forescout Web API module
 2. Configure the Web API Module
	 - Create a credentail the app can use to cal lthe API
	 - Set the authentication token expiration time (or note the setting, needed during app configuration so EyeExtend Connect can refresh the Forescout API JWT)
	 - Ensure that the connecting appliance running the app can access the Web API (`Client IPs` tab)
 3. Install the EyeExtend Connect Elasticsearch app
 4. Configure
	 - Set an elasticsearch API endpoint address (include http/https and the port (:9200) in the URL specification
	 - Set a username/password that is allowed to perform BASIC Auth to the Elasticsearch API
	 - Set an Index name to send data to

## Actions

### Send Host Data

Found under the `Audit` menu, this action allows you to send host data to Elasticsearch. When you select the action, you can select to either send `All Data` or make a selection of fields via a free-form text box (`Forescout host field list`).

  

If the `All Data` checkmark is selected (value == `true`), all data will be sent to Forescout, regardless of what is typed into the `Forescout host field list` textbox.

  

The `Forescout host field list` field takes a comma seperated list of host properties to send to elasticsearch from the Forescout `/host/<host_id>` API response. It supprots feild renaming via a parenthesis after the field name. The field renaming specification is required (it can be the same name as the field attribute). The `configuration_utility` app can help you generate this comma seperated list. Additionally, a single wildcard character, `*`, can be included in a field specification to include fields matchinga certain pattern. The `*` character must be included in the field rename specificiation -- the wildcard matched characters are replaced in the field rename specification.

  

An example specification follow:

  

`in-group(device_groups),scap::*::oval_check_result(scap::*::oval_check_result),hostname(hostname),nbthost(nbthost),segment_path(segment_path),online(online),nbtdomain(nbtdomain),dhcp_hostname(dhcp_hostname),user(user),va_netfunc(va_netfunc)`

  

Above we've renamed the `in-group` property, included a wildcarded inclusion of SCAP scan results, and some additional host properties. In the example above, the string that is matched via the `*` in the host data is used to replaced the `*` in the rename field naming.

  

Supports Undo: Yes, via calling the DELETE method on the document that was POSTed to Elasticsearch. This will cause the host to be DELETEed from the index by the Forescout ID of the Host