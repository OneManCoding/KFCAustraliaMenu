import os
import json
import asyncio
import aiohttp
import aiofiles
from etag_helper_menu_items import read_etags, update_metadata
from hash_utils import calculate_sha1_uncompressed

base_directory = "/home/runner/work/kfc/kfc"

async def download_data_and_save(menu_base_url, store_number, menu_option, session, metadata_file, max_retries=5):
    url = menu_base_url.format(store_number, menu_option)
    filename = f"KFCAustraliaMenu-{store_number}-{menu_option}.json"
    directory = f"KFCAustraliaMenu/{store_number}/{menu_option}/"
    full_filename = os.path.join(directory, filename)

    os.makedirs(directory, exist_ok=True)

    etags = read_etags(metadata_file)
    etag_value = None
    for etag_info in etags:
        if etag_info.get("filename") == full_filename:
            etag_value = etag_info.get("etag")
            headers = {"If-None-Match": etag_value}
            break
    else:
        headers = {}

    for retry in range(max_retries):
        try:
            async with session.get(url, headers=headers) as response:

                if response.status == 200:
                    if "ETag" in response.headers:
                        new_etag = response.headers["ETag"]
                        if etag_value is None or new_etag != etag_value:
                            etag_info = {"filename": full_filename, "etag": new_etag}
                            last_modified = response.headers.get("Last-Modified")
                            if last_modified:
                                etag_info["last-modified"] = last_modified

                            data_dict = json.loads(await response.text())

                            data = json.dumps(data_dict, ensure_ascii=False, indent=1)
                            async with aiofiles.open(os.path.join(directory, filename), mode='w', encoding='utf-8') as f:
                                await f.write(data)

                            sha1_uncompressed = calculate_sha1_uncompressed(data.encode('utf-8'))
                            etag_info["sha1_uncompressed"] = sha1_uncompressed

                            update_metadata(metadata_file, etag_info)
                            print(f"Downloaded and saved {filename} from {url}")
                        else:
                            print(f"{filename} has not been modified on the server.")
                    else:
                        print(f"No ETag found in response for {filename}.")
                elif response.status == 304:
                    print(f"{filename} has not been modified on the server.")
                elif response.status == 302:
                    print(f"{filename} returned HTTP 302. Skipping store {store_number}.")
                    return False  # Indicate that this store should be skipped
                else:
                    print(f"Failed to download {filename} from {url}. Status code: {response.status}")

            await asyncio.sleep(0.5)
            break  # Break out of retry loop on success

        except aiohttp.ClientError as e:
            print(f"Request error: {e}")
            if retry < max_retries - 1:
                print(f"Retrying download of {filename} ({retry + 1}/{max_retries})...")
                await asyncio.sleep(1)
            else:
                print(f"Max retries reached for {filename}. Skipping.")
                break
        except asyncio.TimeoutError:
            print(f"Request for {url} timed out. Retrying...")
            if retry == max_retries - 1:
                print(f"Max retries reached for {filename}. Skipping.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            break

    return True  # Indicate that the store was processed successfully