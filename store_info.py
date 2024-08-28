import requests
import json

def get_store_info():
    url = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/stores"
    headers = {"X-Tenant-Id": "afd3813afa364270bfd33f0a8d77252d"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            pretty_json = json.dumps(data, ensure_ascii=False, indent=4)
            response_data = json.loads(pretty_json)

            store_info = {}
            for store in response_data:
                number = store["id"]
                menu_options = []

                for channel_service in store["channelWiseServices"]:
                    channel = channel_service["channel"]
                    services = channel_service.get("services", [])
                    
                    # Combine channel and each service separately
                    combined_options = [f"{channel}-{service}" for service in services]
                    menu_options.extend(combined_options)

                store_info[number] = menu_options

            # Save the store_info to a file
            with open('/home/runner/work/KFC/KFC/store_info.json', 'w', encoding='utf-8') as f:
                json.dump(store_info, f, ensure_ascii=False, indent=4)

            return store_info
        else:
            print("Failed to get store information. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

    return None

def main():
    store_info = get_store_info()
    if store_info is not None:
        for number, menu_options in store_info.items():
            print(f"Store Number: {number}")
            print(f"Menu Options: {', '.join(menu_options)}")
    else:
        print("No store information retrieved.")

if __name__ == "__main__":
    main()