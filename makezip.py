import os
import zipfile

def create_zip(zip_file, root_folder):
    if not os.access(".", os.W_OK):
        print("Vous n'avez pas les droits d'écriture dans le répertoire actuel.")
        return
    if not os.path.exists(root_folder):
        print(f"Le dossier {root_folder} n'existe pas.")
        return
    if os.path.exists(zip_file):
        os.remove(zip_file)
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if file not in ["makezip.py", zip_file]:
                    zip.write(file_path, os.path.relpath(file_path, root_folder))
                    print(f"Le fichier {file_path[3:]} a été ajouté au dossier compressé '{zip_file}'.")

    print(f"L'archive zip '{zip_file}' a été créée avec succès.")

create_zip("Youtube Downloader.zip", "../Youtube Downloader")