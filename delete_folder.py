import subprocess

# Menu option
menu_option = 'kiosk-pickup'

# Function to run 7z delete command
def delete_from_archive(store_number, menu_option):
    # Construct the folder path to delete
    archive_path = f'KFCAustraliaMenu/{store_number}/{menu_option}/KFCAustraliaMenu-{store_number}-{menu_option}.json.7z'
    
    # Construct the command
    command = ['7z', 'd', archive_path, 'KFCAustraliaMenu']
    
    # Run the command
    subprocess.run(command, check=True)

# Iterate through store numbers from 0 to 816
for store_number in range(817):
    try:
        delete_from_archive(store_number, menu_option)
        print(f'Successfully deleted files for store number: {store_number}')
    except subprocess.CalledProcessError as e:
        print(f'Failed to delete files for store number: {store_number}. Error: {e}')

print('Finished processing all store numbers.')