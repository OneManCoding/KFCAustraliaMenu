import os
import json
import requests
import subprocess
import time
import aiofiles
from etag_helper_menu_items import read_etags, update_metadata, save_etag_info
from hash_utils import calculate_sha1_hashes
import chardet

# Define your proxy settings
proxy = {
    "http": "http://127.0.0.1:8890",
    "https": "http://127.0.0.1:8890"
}

base_directory = "C:/Users/conno/Documents/kfc"

async def download_menu_items(menu_item_base_url, store_number, menu_option, item_ids, max_retries=5):
    for item_id in item_ids:
        url = menu_item_base_url.format(store_number=store_number, menu_option=menu_option, item_id=item_id)
        filename = f"KFCAustraliaMenu/{store_number}/{menu_option}/items/{item_id}.json"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        os.chdir(base_directory)

        etags = read_etags("metadata_menu_items.json")
        etag_value = None
        for etag_info in etags:
            if etag_info.get("filename") == filename:
                etag_value = etag_info.get("etag")
                headers = {"If-None-Match": etag_value}
                break
        else:
            headers = {}

        for retry in range(max_retries):
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

                            data = json.dumps(response.json(), ensure_ascii=False, indent=4)

                            async with aiofiles.open(filename, mode='w', encoding='utf-8') as f:
                                await f.write(data)

                            if data:
                                os.chdir(os.path.dirname(filename))

                                compression_command = [
                                    "7z", "a", "-t7z", "-m0=lzma2:d1024m", "-mx=9", "-aoa", "-mfb=64", "-md=32m", "-ms=on", "-sdel", f"{item_id}.json.7z", f"{item_id}.json"
                                ]
                                subprocess.run(compression_command, check=True)
                                
                                os.chdir(base_directory)

                                sha1_uncompressed, sha1_compressed = calculate_sha1_hashes(data.encode(), response.content)

                                etag_info["sha1_uncompressed"] = sha1_uncompressed
                                etag_info["sha1_compressed"] = sha1_compressed

                                update_metadata("metadata_menu_items.json", etag_info)

                                print(f"Downloaded and saved {filename} from {url}")
                                break
                            else:
                                print(f"{filename} is empty, skipping compression.")
                                break
                        else:
                            print(f"{filename} has not been modified on the server.")
                            break
                    elif response.status_code == 304:
                        print(f"{filename} has not been modified on the server.")
                        break
                    else:
                        print(f"Failed to download {filename} from {url}. Status code: {response.status_code}")
                elif response.status_code == 403:
                    print(f"{filename} is forbidden (HTTP 403). Skipping.")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                if retry < max_retries - 1:
                    print(f"Retrying download of {filename} ({retry + 1}/{max_retries})...")
                    time.sleep(1)
                else:
                    print(f"Max retries reached for {filename}. Skipping.")
                    break

        time.sleep(0.5)

    return {}

async def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)