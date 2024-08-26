import os
import json
import requests
import time
import subprocess
import asyncio
import aiofiles
from store_info import get_store_info
from etag_helper_menu_items import read_etags, update_metadata, save_etag_info
from hash_utils import calculate_sha1_hashes

# Define your proxy settings
proxy = {
    "http": "http://127.0.0.1:8890",
    "https": "http://127.0.0.1:8890"
}

base_directory = "E:/kfc"
metadata_file_path = os.path.join(base_directory, "metadata_menu.json")

async def download_data_and_save(menu_base_url, store_number, menu_option):
    url = menu_base_url.format(store_number=store_number, menu_option=menu_option)
    filename = f"KFCAustraliaMenu-{store_number}-{menu_option}.json"
    directory = os.path.join(base_directory, f"KFCAustraliaMenu/{store_number}/{menu_option}/")

    os.makedirs(directory, exist_ok=True)

    etags = read_etags(metadata_file_path)
    etag_value = None
    for etag_info in etags:
        if etag_info.get("filename") == filename:
            etag_value = etag_info.get("etag")
            headers = {"If-None-Match": etag_value}
            break
    else:
        headers = {}

    try:
        response = requests.get(url, headers=headers, proxies=proxy, verify=False)
        if response.status_code == 200:
            if "ETag" in response.headers:
                new_etag = response.headers["ETag"]
                if etag_value is None or new_etag != etag_value:
                    etag_info = {"filename": filename, "etag": new_etag}
                    last_modified = response.headers.get("Last-Modified")
                    if last_modified:
                        etag_info["last-modified"] = last_modified

                    data = json.dumps(response.json(), ensure_ascii=False, indent=1)
                    json_path = os.path.join(directory, filename)
                    async with aiofiles.open(json_path, mode='w', encoding='utf-8') as f:
                        await f.write(data)

                    os.chdir(directory)
                    compression_command = [
                        "7z", "a", "-t7z", "-m0=lzma2:d1024m", "-mx=9", "-aoa", "-mfb=64", "-md=32m", "-ms=on", f"{filename}.7z", filename
                    ]
                    subprocess.run(compression_command, check=True)

                    # Calculate SHA-1 hashes for both compressed and uncompressed data
                    with open(filename, 'rb') as uncompressed_file:
                        uncompressed_data = uncompressed_file.read()
                    with open(f"{filename}.7z", 'rb') as compressed_file:
                        compressed_data = compressed_file.read()

                    sha1_uncompressed, sha1_compressed = calculate_sha1_hashes(uncompressed_data, compressed_data)
                    etag_info["sha1_uncompressed"] = sha1_uncompressed
                    etag_info["sha1_compressed"] = sha1_compressed

                    update_metadata(metadata_file_path, etag_info)
                    print(f"Downloaded and saved {filename} from {url}")

                    # Delete the uncompressed file after updating metadata
                    os.remove(json_path)
                else:
                    print(f"{filename} has not been modified on the server.")
            else:
                print(f"Failed to download {filename} from {url}. Status code: {response.status_code}")
        elif response.status_code == 304:
            print(f"{filename} has not been modified on the server.")
        else:
            print(f"Failed to download {filename} from {url}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

    await asyncio.sleep(0.5)

async def main():
    store_info = get_store_info()
    base_url = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/catalogs/afd3813afa364270bfd33f0a8d77252d/KFCAustraliaMenu-{store_number}-{menu_option}"

    for store_number, menu_options in store_info.items():
        for menu_option in menu_options:
            await download_data_and_save(base_url, store_number, menu_option)

if __name__ == "__main__":
    asyncio.run(main())