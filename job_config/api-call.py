import requests

url = "https://adb-2701504584282370.10.azuredatabricks.net/api/2.0/dbfs/put"

#Open and read the local file
with open("./dlt-config.json", "rb") as file:
    file_contents = file.read()

payload = "{\n  \"path\": \"/dbfs/FileStore/users/dlt-config3.json\",\n  \"contents\": file_contents,\n  \"overwrite\": \"true\"\n}"
headers = {
  'Content-Type': 'text/plain',
  'Authorization': 'Bearer dapi6fb63c3d7659275e831613df52ac11ac'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)