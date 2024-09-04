import json
import re

def load_json_with_conflicts(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Remove conflict markers
    content = re.sub(r'<<<<<<<.*?\n', '', content)
    content = re.sub(r'=======\n', '', content)
    content = re.sub(r'>>>>>>>.*?\n', '', content)

    # Fix any malformed JSON due to missing braces
    content = content.strip()
    if not content.startswith('['):
        content = '[' + content
    if not content.endswith(']'):
        content = content + ']'

    try:
        json_data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON after removing conflict markers in {file_path}: {e}")

    return json_data

def merge_json_objects(base_json, incoming_json):
    merged_json = base_json.copy()

    for incoming_item in incoming_json:
        if incoming_item not in base_json:
            merged_json.append(incoming_item)

    return merged_json

def save_json(file_path, json_content):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_content, file, indent=4)

def resolve_conflict(file_path):
    try:
        base_json = load_json_with_conflicts(file_path)

        # Assuming that the loaded JSON is a list of objects.
        if isinstance(base_json, list):
            # Deduplicate the JSON objects by 'filename' key
            seen_filenames = set()
            deduped_json = []
            for item in base_json:
                filename = item.get('filename')
                if filename not in seen_filenames:
                    deduped_json.append(item)
                    seen_filenames.add(filename)
            save_json(file_path, deduped_json)
            print(f"Successfully merged and deduplicated {file_path}")
        else:
            print(f"The content in {file_path} is not a JSON array. Manual check needed.")

    except Exception as e:
        print(f"Error while merging {file_path}: {e}")

# Example usage in a GitHub Action or script
# resolve_conflict('metadata_menu_items.json')