# forescout_connect_elastic
EyeExtend Connect app for Elastic

## Allow unsigned app install on Forescout
When you import an app, the signature of the app is validated to see if it has a valid Forescout signature. If the validation succeeds, the app is imported. If the validation fails, an error message is displayed and the app is not imported. To allow an app with an invalid signature to be imported use the following command on the Enterprise Manager: 
 
`fstool allow_unsigned_connect_app_install true`  

This is a global command. It disables the enforcement of signature validation for all apps that are imported after the command is run, including apps with invalid or missing signatures.

## Creating zip
You have to make sure to not include any "extra" files when zipping up the app for import into Forescout. If you use the default "Compress" item in Finder on macOS, an `__macosx` folder is included which will cause Forescout to balk. Avoid this by opening terminal and going into the `app` directory and running the zip command manually: 
`rm -f connect_elasticsearch.zip; zip connect_elasticsearch.zip ./*` 
Note the above command also deletes the `connect_ealsticsearch.zip` file if it's there so you have a fresh copy.