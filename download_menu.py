import os
import json
import requests
import time
import subprocess
import aiofiles
import asyncio
from etag_helper_menu_items import read_etags, update_metadata
from hash_utils import calculate_sha1_uncompressed

base_directory = "/home/runner/work/kfc/kfc"
metadata_file_path = os.path.join(base_directory, "metadata_menu.json")

async def download_data_and_save(menu_base_url, store_number, menu_option, session):
    url = menu_base_url.format(store_number, menu_option)
    filename = f"KFCAustraliaMenu-{store_number}-{menu_option}.json"
    directory = f"KFCAustraliaMenu/{store_number}/{menu_option}/"

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
        async with session.get(url, headers=headers, timeout=60) as response:  # Added timeout
            print(f"Fetching {url}")  # Debugging statement
            print (f"Printing Headers {headers}")

            if response.status == 200:
                if "ETag" in response.headers:
                    new_etag = response.headers["ETag"]
                    if etag_value is None or new_etag != etag_value:
                        etag_info = {"filename": filename, "etag": new_etag}
                        last_modified = response.headers.get("Last-Modified")
                        if last_modified:
                            etag_info["last-modified"] = last_modified

                        data_dict = json.loads(await response.text())

                        data = json.dumps(data_dict, ensure_ascii=False, indent=1)
                        async with aiofiles.open(os.path.join(directory, filename), mode='w', encoding='utf-8') as f:
                            await f.write(data)

                        sha1_uncompressed = calculate_sha1_uncompressed(data.encode('utf-8'))
                        etag_info["sha1_uncompressed"] = sha1_uncompressed

                        update_metadata(metadata_file_path, etag_info)
                        print(f"Downloaded and saved {filename} from {url}")
                    else:
                        print(f"{filename} has not been modified on the server.")
                else:
                    print(f"Failed to download {filename} from {url}. Status code: {response.status}")
            elif response.status == 304:
                print(f"{filename} has not been modified on the server.")
            else:
                print(f"Failed to download {filename} from {url}. Status code: {response.status}")

        await asyncio.sleep(0.5)

    except asyncio.TimeoutError:
        print(f"Request for {url} timed out.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
