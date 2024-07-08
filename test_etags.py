import os
import json

def save_etag_info(etags, file_path):
    try:
        with open(file_path, "w") as metadata_file:
            for item in etags:
                metadata_file.write(json.dumps(item) + "\n")
            metadata_file.flush()
    except Exception as e:
        print(f"Error while saving ETag info: {str(e)}")

# Define a sample ETag list
sample_etags = [{'filename': 'KFCAustraliaMenu/2/web-catering/items/C-31072-prod.json', 'etag': '"cde9b3e22a0d8111578e7cae2e0cc536"', 'last-modified': 'Mon, 23 Oct 2023 04:57:44 GMT', 'sha1_uncompressed': 'f6fda433a5bbca130861e441b551da078805d2c7', 'sha1_compressed': 'f9ed98c69a7b8ebb57b3280aa8c26b9a0af726d0'}]

# Define the absolute file path
absolute_file_path = "metadata_menu_items.json"

# Call the save_etag_info function
save_etag_info(sample_etags, absolute_file_path)