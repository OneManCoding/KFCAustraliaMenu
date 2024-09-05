import os
import sys
import asyncio
import aiohttp
from store_info import get_store_info
from download_menu import download_data_and_save
from download_menu_items import download_menu_items
from json_handler import extract_mdmid_and_id

# Limit the number of concurrent downloads
CONCURRENT_DOWNLOADS = 7
base_directory = "/home/runner/work/kfc/kfc"

async def download_menu_data(store_number, store_info, menu_base_url, session):
    semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)

    async def download_with_semaphore(menu_option):
        async with semaphore:
            # Define store-specific metadata file
            metadata_file = f"metadata/metadata_menu_{store_number}.json"
            return await download_data_and_save(menu_base_url, store_number, menu_option, session, metadata_file)

    menu_options = store_info.get(store_number, [])
    if not menu_options:
        print(f"No menu options found for store number {store_number}")
        return True  # Consider this as a success since there's nothing to download

    tasks = [download_with_semaphore(menu_option) for menu_option in menu_options]
    results = await asyncio.gather(*tasks)

    # Check if all tasks returned False (indicating HTTP 302)
    return any(results)

async def extract_and_download_items(store_number, store_info, menu_item_base_url, session):
    semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)

    async def extract_and_download(menu_option):
        async with semaphore:
            directory = f"KFCAustraliaMenu/{store_number}/{menu_option}/"
            filename = f"KFCAustraliaMenu-{store_number}-{menu_option}.json"
            temp_filepath = os.path.join(directory, filename)

            # Check if the file exists
            if os.path.exists(temp_filepath):
                extracted_values = set()

                # Extract item IDs from the JSON file
                extract_mdmid_and_id(temp_filepath, extracted_values)
                item_ids = [value for value in extracted_values if value.startswith(('C', 'I'))]

                # Download each item immediately after extraction
                if item_ids:
                    # Define store-specific metadata file
                    metadata_file = f"metadata/metadata_menu_items_{store_number}.json"
                    await download_menu_items(menu_item_base_url, store_number, menu_option, item_ids, session, metadata_file)
                else:
                    print(f"No valid item IDs found in {filename} for store {store_number}, menu option {menu_option}.")

    menu_options = store_info.get(store_number, [])
    if not menu_options:
        print(f"No menu options found for store number {store_number}")
        return

    tasks = [extract_and_download(menu_option) for menu_option in menu_options]
    await asyncio.gather(*tasks)

async def main(store_numbers):
    store_info = get_store_info()
    menu_base_url = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/catalogs/afd3813afa364270bfd33f0a8d77252d/KFCAustraliaMenu-{}-{}"
    menu_item_base_url = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/catalogs/afd3813afa364270bfd33f0a8d77252d/KFCAustraliaMenu-{store_number}-{menu_option}/items/{item_id}"

    async with aiohttp.ClientSession() as session:
        all_skipped = True  # Assume all will be skipped unless proven otherwise
        for store_number in store_numbers:
            # Download the menu for the store number
            success = await download_menu_data(store_number, store_info, menu_base_url, session)

            if success:
                all_skipped = False  # At least one store was processed successfully

                # Extract and download items immediately after extraction
                await extract_and_download_items(store_number, store_info, menu_item_base_url, session)

        if all_skipped:
            print("All store numbers returned HTTP 302. Stopping the script.")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide at least one store number as an argument.")
        sys.exit(1)

    store_numbers = sys.argv[1:]
    asyncio.run(main(store_numbers))