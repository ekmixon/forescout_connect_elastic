Remove-Item "C:\Users\clayt\OneDrive\Documents\GitHub\forescout_connect_elastic\import_app.zip"

$compress = @{
  Path = "C:\Users\clayt\OneDrive\Documents\GitHub\forescout_connect_elastic\app\*"
  CompressionLevel = "Fastest"
  DestinationPath = "C:\Users\clayt\OneDrive\Documents\GitHub\forescout_connect_elastic\import_app.zip"
}
Compress-Archive @compress