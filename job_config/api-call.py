import requests
import json
import base64


url = "https://adb-2701504584282370.10.azuredatabricks.net/api/2.0/dbfs/put"

#Open and read the local file
with open("./dlt-config.json", "rb") as file:
    file_contents = file.read()
#with open("./dlt-config.json") as f:
 #   file_contents = json.load(f)      

# Data to encode
data_to_encode = "Hello, World!"  
# Encode the data to Base64
#encoded_data = base64.b64encode(file_contents.encode("utf-8")).decode("utf-8")  
encoded_data = file_contents.decode("utf-8")  

#payload = "{\n  \"path\": \"/dbfs/FileStore/users/dlt_config1.json\",\n  \"contents\": encoded_data,\n  \"overwrite\": \"true\"\n}"
payload = {
    "path": "/dbfs/FileStore/users/dlt-config3.json",
    "contents": encoded_data,
    "overwrite": "true"
}

json_payload = json.dumps(payload)

headers = {
  'Content-Type': 'text/plain',
  'Authorization': 'Bearer dapi6fb63c3d7659275e831613df52ac11ac'
}

#response = requests.request("POST", url, headers=headers, data=payload)
response = requests.post(url, data=json_payload, headers=headers)

print(response.text)