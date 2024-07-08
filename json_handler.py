# json_handler.py
import json
import os
import gzip

def extract_mdmid_and_id(temp_filename, extracted_values):
    with open(temp_filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        extract_fields(data, extracted_values)

def extract_fields(data, extracted_values):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "mdmId" or key == "id":
                if value and value not in extracted_values:
                    extracted_values.add(value)
            elif key == "products":
                extract_products(value, extracted_values)
            extract_fields(value, extracted_values)
    elif isinstance(data, list):
        for item in data:
            extract_fields(item, extracted_values)

def extract_products(products, extracted_values):
    if isinstance(products, list):
        for product in products:
            extract_fields(product, extracted_values)