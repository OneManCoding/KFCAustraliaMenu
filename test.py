import requests

# URL of the resource
url = 'https://example.com'

# Initial request without ETag
response = requests.get(url)

# Get the ETag from the response
etag = response.headers.get("ETag")

# Store this ETag value for future requests

# Subsequent request with ETag
headers = {"If-None-Match": etag}
response = requests.get(url, headers=headers)

# Check the response status code, and proceed accordingly
if response.status_code == 304:
    print("Resource not modified, no need to download.")
else:
    # Resource has changed, process the response
    data = response()
    # Your processing logic here