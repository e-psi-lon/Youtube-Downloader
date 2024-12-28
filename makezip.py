import os
import zipfile


def create_zip(zip_file, root_folder):
    if not os.access(".", os.W_OK):
        print('You don\'t have permission to write in this folder.')
        return
    if not os.path.exists(root_folder):
        print(f"The folder '{root_folder}' doesn't exist.")
        return
    if os.path.exists(zip_file):
        os.remove(zip_file)
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as new_zip:
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_to_not_add = ["makezip.py", zip_file, '.gitignore', 'README.md']
                folder_to_not_add = ["__pycache__", ".git", 'venv', '.idea', 'cache', 'venv']
                if file not in file_to_not_add and not any(folder in root for folder in folder_to_not_add):
                    new_zip.write(file_path, str(os.path.relpath(str(file_path), root_folder)))
                    print(f'The file \'{file_path[3:]}\' has been added to the archive \'{zip_file}\'.')

    print(f'The archive \'{zip_file}\' has been created.')


create_zip("Youtube Downloader.zip", "../Youtube-Downloader")
