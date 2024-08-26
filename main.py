import os
import asyncio
import aiohttp
from store_info import get_store_info
from download_menu import download_data_and_save
from download_menu_items import download_menu_items
from delete_empty_folders import remove_empty_folders
from hash_utils import calculate_sha1_compressed
from etag_helper_menu_items import update_metadata
from json_handler import extract_mdmid_and_id

# Limit the number of concurrent downloads
CONCURRENT_DOWNLOADS = 5
base_directory = "/home/runner/work/kfc/kfc"

async def download_menu_data(store_info, menu_base_url, session):
    semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)

    async def download_with_semaphore(number, menu_option):
        async with semaphore:
            await download_data_and_save(menu_base_url, number, menu_option, session)

    tasks = [
        download_with_semaphore(number, menu_option)
        for number, menu_options in store_info.items()
        for menu_option in menu_options
    ]

    await asyncio.gather(*tasks)

async def extract_and_download_items(store_info, menu_item_base_url, session):
    semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)

    async def extract_and_download(number, menu_option):
        async with semaphore:
            directory = f"KFCAustraliaMenu/{number}/{menu_option}/"
            filename = f"KFCAustraliaMenu-{number}-{menu_option}.json"
            temp_filepath = os.path.join(directory, filename)

            # Check if the file exists
            if os.path.exists(temp_filepath):
                extracted_values = set()
                
                # Extract item IDs from the JSON file
                extract_mdmid_and_id(temp_filepath, extracted_values)
                item_ids = [value for value in extracted_values if "kfc" not in value.lower()]
                
                # Download each item immediately after extraction
                if item_ids:
                    await download_menu_items(menu_item_base_url, number, menu_option, item_ids, session)
                else:
                    print(f"No valid item IDs found in {filename} for store {number}, menu option {menu_option}.")

    tasks = [
        extract_and_download(number, menu_option)
        for number, menu_options in store_info.items()
        for menu_option in menu_options
    ]

    await asyncio.gather(*tasks)

async def main():
    store_info = get_store_info()
    menu_base_url = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/catalogs/afd3813afa364270bfd33f0a8d77252d/KFCAustraliaMenu-{}-{}"
    menu_item_base_url = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/catalogs/afd3813afa364270bfd33f0a8d77252d/KFCAustraliaMenu-{store_number}-{menu_option}/items/{item_id}"

    async with aiohttp.ClientSession() as session:
        # Extract and download items immediately after extraction
        await extract_and_download_items(store_info, menu_item_base_url, session)

if __name__ == "__main__":
    asyncio.run(main())