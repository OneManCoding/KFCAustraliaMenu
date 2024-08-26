# main.py
import os
import time
import gzip
import chardet
from etag_helper import read_etags, save_etag_info
from json_handler import extract_mdmid_and_id, extract_fields
from hash_utils import calculate_sha1_hashes
from store_info import get_store_info
from download_menu import download_data_and_save
from download_menu_items import download_menu_items
from delete_empty_folders import remove_empty_folders
import subprocess
import asyncio

async def download_menu_data(store_info, menu_base_url):
    for number, menu_options in store_info.items():
        for menu_option in menu_options:
            # Your code to download menu data for each store and menu option
            await download_data_and_save(menu_base_url, number, menu_option)
            time.sleep(0.5)

async def download_and_save_menu_items(store_info, menu_item_base_url):
    for number, menu_options in store_info.items():
        for menu_option in menu_options:
            extracted_values = set()

            # Temporary decompress the JSON file to obtain item IDs
            compressed_filename = f"KFCAustraliaMenu/{number}/{menu_option}/KFCAustraliaMenu-{number}-{menu_option}.json.7z"
            temp_filename = f"KFCAustraliaMenu/{number}/{menu_option}/KFCAustraliaMenu-{number}-{menu_option}.json"

            try:
                # Extract the file from the 7-Zip archive
                extraction_command = [
                    "7z", "e", compressed_filename, f"-oKFCAustraliaMenu/{number}/{menu_option}"
                ]
                subprocess.run(extraction_command, check=True)
            except subprocess.CalledProcessError as extraction_error:
                print(f"Extraction error: {extraction_error}. Skipping {compressed_filename}.")
                continue  # Skip this file and move on to the next

            # Detect the character encoding of the extracted file
            with open(temp_filename, 'rb') as file:
                result = chardet.detect(file.read())
            file_encoding = result['encoding']

            # Read the extracted file with the detected encoding
            with open(temp_filename, 'r', encoding=file_encoding) as extracted_file:
                extracted_data = extracted_file.read()

            # Extract item IDs
            extract_mdmid_and_id(temp_filename, extracted_values)
            extracted_values = [value for value in extracted_values if "kfc" not in value.lower()]

            # Delete temporary JSON file
            os.remove(temp_filename)

            # Download menu items and store their metadata
            item_ids = list(extracted_values)
            await download_menu_items(menu_item_base_url, number, menu_option, item_ids)

async def main():
    store_info = get_store_info()
    menu_base_url = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/catalogs/afd3813afa364270bfd33f0a8d77252d/KFCAustraliaMenu-{}-{}"
    menu_item_base_url = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/catalogs/afd3813afa364270bfd33f0a8d77252d/KFCAustraliaMenu-{store_number}-{menu_option}/items/{item_id}"

    for store_number, menu_options in store_info.items():
        for menu_option in menu_options:
            await download_data_and_save(menu_base_url, store_number, menu_option)

if __name__ == "__main__":
    asyncio.run(main())