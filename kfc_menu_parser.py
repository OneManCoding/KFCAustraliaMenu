import json

def extract_mdmid_and_id(json_filename):
    with open(json_filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        extract_fields(data)

def extract_fields(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "mdmId" or key == "id":
                if value and value not in extracted_values:
                    extracted_values.add(value)
            elif key == "products":
                extract_products(value)
            extract_fields(value)
    elif isinstance(data, list):
        for item in data:
            extract_fields(item)

def extract_products(products):
    if isinstance(products, list):
        for product in products:
            extract_fields(product)

if __name__ == "__main__":
    json_filename = "KFCAustraliaMenu-756-web-catering.json"
    extracted_values = set()
    
    extract_mdmid_and_id(json_filename)
    
    # Exclude lines containing "kfc", empty lines, and duplicates
    extracted_values = [value for value in extracted_values if "kfc" not in value.lower()]
    
    for value in extracted_values:
        print(value)