import json

def load_json_with_conflicts(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split the content by conflict markers
    if '<<<<<<<' in content:
        base_part, incoming_part = content.split('=======')[0], content.split('=======')[1].split('>>>>>>>')[0]
        
        base_json = json.loads(base_part.replace('<<<<<<< HEAD\n', '').strip())
        incoming_json = json.loads(incoming_part.strip())
        
        return base_json, incoming_json
    
    return json.loads(content), []

def merge_json_objects(base_json, incoming_json):
    merged_json = base_json.copy()
    
    for item in incoming_json:
        if item not in base_json:
            merged_json.append(item)
    
    return merged_json

def save_json(file_path, json_content):
    with open(file_path, 'w') as file:
        json.dump(json_content, file, indent=4)

def resolve_conflict(file_path):
    try:
        base_json, incoming_json = load_json_with_conflicts(file_path)
        
        if incoming_json:
            merged_json = merge_json_objects(base_json, incoming_json)
            save_json(file_path, merged_json)
            print(f"Successfully merged {file_path}")
        else:
            print(f"No conflict markers found in {file_path}")
    
    except Exception as e:
        print(f"Error while merging {file_path}: {e}")