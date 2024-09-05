import os
import json

def read_etags(metadata_file_path):
    etags = []

    try:
        with open(metadata_file_path, 'r', encoding='utf-8') as metadata_file:
            content = metadata_file.read()
            etags = json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        # Handle the case when the file is not found or doesn't contain valid JSON
        pass

    return etags

def update_metadata(metadata_file_path, etag_info):
    try:
        # Read existing metadata
        with open(metadata_file_path, 'r', encoding='utf-8') as metadata_file:
            metadata = json.load(metadata_file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file is not found or doesn't contain valid JSON, start with an empty list
        metadata = []

    # Update metadata or add new entry if it doesn't exist
    found = False
    for existing_etag_info in metadata:
        if existing_etag_info.get("filename") == etag_info.get("filename"):
            # Update existing entry
            existing_etag_info.update(etag_info)
            found = True
            break

    if not found:
        # Add a new entry to metadata
        metadata.append(etag_info)

    # Write the updated metadata back to the file
    with open(metadata_file_path, 'w', encoding='utf-8') as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    return metadata

def save_etag_info(etags, metadata_file_path):
    # Save the etags into the specific store's metadata file
    with open(metadata_file_path, 'w', encoding='utf-8') as metadata_file:
        json.dump(etags, metadata_file, indent=4)