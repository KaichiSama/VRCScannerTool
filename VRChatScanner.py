import os
import re
import sys
import shutil
from colorama import Fore, Style  # Import colorama for colored output
import datetime
import time

# Obtenez le répertoire de l'utilisateur actuel
user_directory = os.path.expanduser("~")

# Utilisez le répertoire de l'utilisateur pour créer des chemins de fichiers relatifs
PATH = os.path.join(user_directory, "AppData", "LocalLow", "VRChat", "VRChat", "Cache-WindowsPlayer")

# Variable pour mettre en pause le programme
program_paused = False

def get_ids_from_file(filepath, pattern):
    ids_found = []
    try:
        with open(filepath, 'r', encoding="utf-8", errors='ignore') as f:
            data = f.read()
            ids_found = re.findall(pattern, data)
    except Exception as e:
        print(f"Error reading file {filepath}. Error message: {e}")
    return ids_found

def create_directory(directory):
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        print(f"Error creating directory {directory}. Error message: {e}")

def display_world_info():
    print("\nDisplaying World Info in Your Database:")
    for root, dirs, files in os.walk("VRCW"):
        for file in files:
            if file.endswith(".vrcw"):
                world_id = os.path.splitext(file)[0]
                print(f"World ID: {world_id}")

def display_avatar_info():
    print("\nDisplaying Avatar Info in Your Database:")
    for root, dirs, files in os.walk("VRCA"):
        for file in files:
            if file.endswith(".vrca"):
                avatar_id = os.path.splitext(file)[0]
                print(f"Avatar ID: {avatar_id}")

def display_all_ids():
    for root, dirs, files in os.walk(PATH):
        for file in files:
            if file == '__data':
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding="utf-8", errors='ignore') as f:
                        data = f.read()
                        avtr_ids_found = re.findall(r"avtr_[a-f0-9\-]{36}", data)
                        wrld_ids_found = re.findall(r"wrld_[a-f0-9\-]{36}", data)

                        if avtr_ids_found or wrld_ids_found:
                            print(f"\nFile Analysis: {filepath}")
                            for avtr_id in set(avtr_ids_found):
                                print(f"{datetime.datetime.now()} - {Fore.GREEN}Avatar ID : {avtr_id}{Style.RESET_ALL}")
                            for wrld_id in set(wrld_ids_found):
                                print(f"{datetime.datetime.now()} - {Fore.GREEN}World ID : {wrld_id}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"Error reading file {filepath}. Error message: {e}")

def search_for_id(search_id):
    for root, dirs, files in os.walk(PATH):
        for file in files:
            if file == '__data':
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding="utf-8", errors='ignore') as f:
                        data = f.read()
                        if search_id in data:
                            print(f"{datetime.datetime.now()} - ID {search_id} found in: {filepath}")
                except Exception as e:
                    print(f"Error reading file {filepath}. Error message: {e}")

def display_ids_filtered(option):
    pattern = r"avtr_[a-f0-9\-]{36}" if option == "Avatar" else r"wrld_[a-f0-9\-]{36}"

    if option == "Avatar":
        print("\nDisplaying Avatar IDs:")
    else:
        print("\nDisplaying World IDs:")

    found_ids = set()

    for root, dirs, files in os.walk(PATH):
        for file in files:
            if file == '__data':
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding="utf-8", errors='ignore') as f:
                        data = f.read()
                        ids_found = re.findall(pattern, data)

                        if ids_found:
                            print(f"File Analysis: {filepath}")
                            for id_ in set(ids_found):
                                found_ids.add(id_)
                                print(f"{datetime.datetime.now()} - {Fore.YELLOW}{option} ID : {id_}{Style.RESET_ALL}")

                except Exception as e:
                    print(f"Error reading file {filepath}. Error message: {e}")

    if not found_ids:
        print(f"No {option} ID found in the analyzed files.")

def save_vrcw_vrca_continuous():
    # Create "VRCW" and "VRCA" directories if they don't exist
    create_directory("VRCW")
    create_directory("VRCA")

    processed_files = set()  # Pour garder une trace des fichiers déjà traités

    while True:  # Boucle infinie pour surveiller le dossier en continu
        for root, dirs, files in os.walk(PATH):
            for file in files:
                if file == '__data':
                    filepath = os.path.join(root, file)
                    if filepath not in processed_files:  # Vérifiez si le fichier n'a pas été traité
                        try:
                            with open(filepath, 'r', encoding="utf-8", errors='ignore') as f:
                                data = f.read()
                                avtr_ids_found = re.findall(r"avtr_[a-f0-9\-]{36}", data)
                                wrld_ids_found = re.findall(r"wrld_[a-f0-9\-]{36}", data)

                                if avtr_ids_found:
                                    for id_ in set(avtr_ids_found):
                                        target_path = os.path.join("VRCA", f"{id_}.vrca")
                                        if not os.path.exists(target_path):
                                            shutil.copy(filepath, target_path)
                                            print(f"{datetime.datetime.now()} - {Fore.GREEN}VRCA Added Successfully: {id_}.vrca{Style.RESET_ALL}")
                                        else:
                                            print(f"{datetime.datetime.now()} - {Fore.RED}VRCA Already Exists: {id_}.vrca{Style.RESET_ALL}")
                                if wrld_ids_found:
                                    for id_ in set(wrld_ids_found):
                                        target_path = os.path.join("VRCW", f"{id_}.vrcw")
                                        if not os.path.exists(target_path):
                                            shutil.copy(filepath, target_path)
                                            print(f"{datetime.datetime.now()} - {Fore.GREEN}VRCW Added Successfully: {id_}.vrcw{Style.RESET_ALL}")
                                        else:
                                            print(f"{datetime.datetime.now()} - {Fore.RED}VRCW Already Exists: {id_}.vrcw{Style.RESET_ALL}")

                            processed_files.add(filepath)  # Ajoutez le fichier traité à l'ensemble

                        except Exception as e:
                            print(f"Error reading file {filepath}. Error message: {e}")

        time.sleep(60)  # Attendez 60 secondes avant de vérifier à nouveau (vous pouvez ajuster cela)
        print(f"{datetime.datetime.now()} - Waiting for new files...")

    # Reset the console color to default
    print(Style.RESET_ALL)

def search_id_in_database(search_id):
    found_in_vrca = False
    found_in_vrcw = False

    for root, dirs, files in os.walk("VRCA"):
        if f"{search_id}.vrca" in files:
            found_in_vrca = True
            vrca_file_path = os.path.join(root, f"{search_id}.vrca")
            print(f"{Fore.GREEN}Correspondance trouvée dans VRCA !{Style.RESET_ALL}")
            print(f"Accédez au fichier VRCA ici : file://{vrca_file_path}")
            break

    for root, dirs, files in os.walk("VRCW"):
        if f"{search_id}.vrcw" in files:
            found_in_vrcw = True
            vrcw_file_path = os.path.join(root, f"{search_id}.vrcw")
            print(f"{Fore.GREEN}Correspondance trouvée dans VRCW !{Style.RESET_ALL}")
            print(f"Accédez au fichier VRCW ici : file://{vrcw_file_path}")
            break

    if not found_in_vrca and not found_in_vrcw:
        print(f"{Fore.RED}Aucune correspondance trouvée.{Style.RESET_ALL}")

# Ajouter "Powered by Kawaii Squad" en rose
print(f"{Fore.LIGHTMAGENTA_EX}Powered by Kawaii Squad{Style.RESET_ALL}")

def main():
    while True:
        if not program_paused:
            print(f"\n{Fore.GREEN}Kaichi Menu UwU:{Style.RESET_ALL}")
            print("1. Display World Info in Your Database")
            print("2. Display Avatar Info in Your Database")
            print("3. Filtered Search")
            print("4. Save VRCW and VRCA")
            print("5. Search ID in Your Database")
            print("6. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                display_world_info()
            elif choice == "2":
                display_avatar_info()
            elif choice == "3":
                print("\nSub-Menu:")
                print("1. Display World Info in Your Database")
                print("2. Display Avatar Info in Your Database")
                sub_choice = input("Choose an option: ")

                if sub_choice == "1":
                    display_world_info()
                elif sub_choice == "2":
                    display_avatar_info()
                else:
                    print("Invalid option, please try again.")
            elif choice == "4":
                save_vrcw_vrca_continuous()
            elif choice == "5":
                search_id = input("\nEnter the ID you want to search for: ")
                search_id_in_database(search_id)
            elif choice == "6":
                print("\nGoodbye!")
                break
            else:
                print("Invalid option, please try again.")
        else:
            time.sleep(1)  # Attendez pendant 1 seconde lorsque le programme est en pause

if __name__ == "__main__":
    main()
