import os

def remove_empty_folders(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if not os.listdir(folder_path):
                os.rmdir(folder_path)
                print(f"Removed empty folder: {folder_path}")

if __name__ == "__main__":
    directory_to_clean = "KFCAustraliaMenu"  # Specify the directory you want to clean
    remove_empty_folders(directory_to_clean)