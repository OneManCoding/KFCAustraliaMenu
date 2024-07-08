import json

def validate_json(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError as e:
        print(f"JSON validation error: {e}")
        return False

# Read the file and validate its content
with open('metadata.json', 'r', encoding='utf8') as metadata_file:
    file_contents = metadata_file.read()
    if validate_json(file_contents):
        print("JSON is valid")