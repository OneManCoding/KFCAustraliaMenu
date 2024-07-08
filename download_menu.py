import os
import json
import requests
import time
import subprocess
import asyncio
from store_info import get_store_info
import aiofiles

# Define your proxy settings
proxy = {
    "http": "http://127.0.0.1:8890",
    "https": "http://127.0.0.1:8890"
}

base_directory = "C:/Users/conno/Documents/kfc"

async def download_data_and_save(menu_base_url, store_number, menu_option):
    url = menu_base_url.format(store_number=store_number, menu_option=menu_option)
    filename = f"KFCAustraliaMenu/{store_number}/{menu_option}/KFCAustraliaMenu-{store_number}-{menu_option}.json"

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:
        response = requests.get(url, proxies=proxy, verify=False)
        if response.status_code == 200:
            data = response.json()
            pretty_json = json.dumps(data, ensure_ascii=False, indent=4)
            async with aiofiles.open(filename, mode='w', encoding='utf-8') as f:
                await f.write(pretty_json)
            
            print(f"Downloaded and saved {filename} from {url}")

            # Compress the data using 7z with LZMA2 and level 9 compression
            compressed_filename = f"KFCAustraliaMenu\{store_number}\{menu_option}\KFCAustraliaMenu-{store_number}-{menu_option}.json.7z"
            uncompressed_filename = f"KFCAustraliaMenu\{store_number}\{menu_option}\KFCAustraliaMenu-{store_number}-{menu_option}.json"
            compression_command = [
                "7z", "a", "-t7z", f"-m0=lzma2:d1024m", "-mx=9", "-aoa", f"-mfb=64", f"-md=32m", f"-ms=on", "-sdel", compressed_filename, uncompressed_filename
            ]
            subprocess.run(compression_command, check=True)
            
            print(f"Compressed {filename} to {compressed_filename}")

        else:
            print(f"Failed to download {filename} from {url}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

    # Add a delay of 0.5 seconds between requests
    await asyncio.sleep(0.5)

async def main():
    store_info = get_store_info()

    base_url = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/catalogs/afd3813afa364270bfd33f0a8d77252d/KFCAustraliaMenu-{store_number}-{menu_option}"

    for store_number, menu_options in store_info.items():
        for menu_option in menu_options:
            await download_data_and_save(base_url, store_number, menu_option)

if __name__ == "__main__":
    asyncio.run(main())