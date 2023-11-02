import os
import re
import sys
import shutil
from colorama import Fore, Style  # Import colorama for colored output
import datetime
import time
import colorama
import hashlib
import requests
import webbrowser as wb
import keyboard  # Import keyboard module for keypress handling

colorama.init()
user_directory = os.path.expanduser("~")
PATH = os.path.join(user_directory, "AppData", "LocalLow", "VRChat", "VRChat", "Cache-WindowsPlayer")
program_paused = False

#prend tout les id 
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
#remove duplicate files
def calculate_file_hash_except_ids(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            data_without_ids = data.replace(b"avtr_", b"").replace(b"wrld_", b"")
            sha256_hash.update(data_without_ids)
    return sha256_hash.hexdigest()

def remove_duplicate_files(directory_path, file_extension, log_file_name):
    if not os.path.isdir(directory_path):
        print("The specified directory does not exist")
        return

    files_hash = {}
    duplicate_files = {}

    for filename in os.listdir(directory_path):
        if filename.endswith(file_extension):
            filepath = os.path.join(directory_path, filename)
            file_hash = calculate_file_hash_except_ids(filepath)

            if file_hash:
                if file_hash not in files_hash:
                    files_hash[file_hash] = filename
                else:
                    if file_hash not in duplicate_files:
                        duplicate_files[file_hash] = [files_hash[file_hash]]
                    duplicate_files[file_hash].append(filename)
                    os.remove(filepath)
                    print(f"File deleted: {filepath}")

    log_file_path = os.path.join(directory_path, log_file_name)
    with open(log_file_path, 'w') as log_file:
        for original_hash, file_list in duplicate_files.items():
            log_file.write(f"Original ID: {original_hash}\n")
            log_file.write("Sub IDs:\n")
            for file_id in file_list:
                log_file.write(f"{file_id}\n")
            log_file.write("\n")
    print(f"Log of deleted files saved in {log_file_path}")

    log_file_path = os.path.join(os.path.dirname(directory_path), log_file_name)
    with open(log_file_path, 'w') as log_file:
        for original_hash, file_list in duplicate_files.items():
            log_file.write(f"Original ID: {original_hash}\n")
            log_file.write("Sub IDs:\n")
            for file_id in file_list:
                log_file.write(f"{file_id}\n")
            log_file.write("\n")
    print(f"Log of deleted files saved in {log_file_name}")

def remove_duplicate_files_button():
    script_directory = os.path.dirname(os.path.realpath(__file__))

    vrca_directory = os.path.join(script_directory, "VRCA")
    vrcw_directory = os.path.join(script_directory, "VRCW")

    print("Analyzing the VRCA folder...")
    remove_duplicate_files(vrca_directory, ".vrca", "ID_REF_VRCA.txt")

    print("Analyzing the VRCW folder...")
    remove_duplicate_files(vrcw_directory, ".vrcw", "ID_REF_VRCW.txt")
#start le logger
def start_the_logger():
    print(f"{Fore.LIGHTMAGENTA_EX}Logger Started Network & Locally{Style.RESET_ALL}")
    create_directory("VRCW")
    create_directory("VRCA")

    while True:
        for root, dirs, files in os.walk(PATH):
            for file in files:
                if file == '__data':
                    filepath = os.path.join(root, file)
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

                    except Exception as e:
                        print(f"Error reading file {filepath}. Error message: {e}")
        time.sleep(60)
        print(f"{datetime.datetime.now()} - Waiting for new files...")

    # Reset the console color to default
    print(Style.RESET_ALL)
#affiche tout les ids dans le cache
def display_all_ids_in_cache():
    print("\nDisplaying All IDs in Your Cache:")
    for root, dirs, files in os.walk(PATH):
        for file in files:
            if file == '__data':
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding="utf-8", errors='ignore') as f:
                        data = f.read()
                        avtr_ids_found = re.findall(r"(avtr_[a-f0-9\-]{36})", data)
                        wrld_ids_found = re.findall(r"(wrld_[a-f0-9\-]{36})", data)

                        if avtr_ids_found or wrld_ids_found:
                            print(f"\n{Fore.YELLOW}File Analysis: {Fore.LIGHTCYAN_EX}{filepath}{Style.RESET_ALL}")
                            for avtr_id in set(avtr_ids_found):
                                print(f"{datetime.datetime.now()} - {Fore.LIGHTYELLOW_EX}Avatar ID : {Fore.GREEN}{avtr_id}{Style.RESET_ALL}")
                            for wrld_id in set(wrld_ids_found):
                                print(f"{datetime.datetime.now()} - {Fore.LIGHTMAGENTA_EX}World ID : {Fore.GREEN}{wrld_id}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"Error reading file {filepath}. Error message: {e}")
#search ID in Cache
def search_in_cache(search_id):
    found_in_cache = False

    for root, dirs, files in os.walk(PATH):
        for file in files:
            if file == '__data':
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding="utf-8", errors='ignore') as f:
                        data = f.read()
                        if search_id in data:
                            print(f"{datetime.datetime.now()} - ID {search_id} found in: {Fore.LIGHTCYAN_EX}{filepath}{Style.RESET_ALL}")
                            found_in_cache = True
                except Exception as e:
                    print(f"Error reading file {filepath}. Error message: {e}")

    if found_in_cache:
        print(f"{Fore.GREEN}Avatar {search_id} found in cache.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Avatar {search_id} not found in cache.{Style.RESET_ALL}")
#Display Filtering
def display_ids_filtered(option):
    if option == "World":
        folder = "VRCW"
        entity = "World"
    elif option == "Avatar":
        folder = "VRCA"
        entity = "Avatar"
    else:
        print("Invalid option, please try again.")
        return

    print(f"\nDisplaying {entity} Info in Local Database:")
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(f".{folder.lower()}"):
                entity_id = os.path.splitext(file)[0]
                print(f"{entity} ID: {entity_id}")

def display_world_info():
    print("\nDisplaying World Info in Local Database:")
    for root, dirs, files in os.walk("VRCW"):
        for file in files:
            if file.endswith(".vrcw"):
                world_id = os.path.splitext(file)[0]
                print(f"World ID: {world_id}")

def display_avatar_info():
    print("\nDisplaying Avatar Info in Local Database:")
    for root, dirs, files in os.walk("VRCA"):
        for file in files:
            if file.endswith(".vrca"):
                avatar_id = os.path.splitext(file)[0]
                print(f"Avatar ID: {avatar_id}")
#Main Menu Principal
def main_menu():
    while True:
        print(f"{Fore.RED}\nNasa get Hacked by Kaichi-Sama {Fore.GREEN}for question dm Discord : kaichisama.{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}Join : https://discord.gg/7KprcpxhEH{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}Powered by Kawaii Squad Devs : Kaichi-Sama / >_Unknown User{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}♥ Kaichi-Sama Menu UwU ♥{Style.RESET_ALL}:")
        print("1. Local Database")
        print(f"2. Network Database {Fore.RED}Not Finished Need an other Dev for fix it Thanks <3{Style.RESET_ALL}")
        print("3. Start The Logger")
        print(f"{Fore.RED}4. DON'T CLICK HERE{Style.RESET_ALL}")  # Option 6 en rouge
        print("5. Exit")  # Mettez à jour le numéro des options ici
        choice = input("Choose an option: ")

        if choice == "1":
            local_database_menu()
        elif choice == "2":
            Network_database_menu()
        elif choice == "3":
            start_the_logger()
        elif choice == "4":
            print("you get Rickrolled by KawaiiTools Dev Team <3")
            rickroll()
        elif choice == "5":  # Mettez à jour le numéro de sortie ici
            print("\nHave Sex with Me!")
            break
        else:
            print("Invalid option, please try again.")
#Local Database Menu
def local_database_menu():
    while True:
        print("\nLocal Database Menu:")
        print("1. Display All IDs in Cache")
        print("2. Research an ID in Cache")
        print("3. Filtered Local Research")
        print(f"4. Remove Duplicate Files : {Fore.RED}recommend doing it 1 time per day or per week{Style.RESET_ALL}")
        print("5. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            # Remplacez 'display_all_ids_in_cache' par le nom réel de votre fonction
            display_all_ids_in_cache()
        elif choice == "2":
            search_id = input("\nEnter the ID you want to search for: ")
            search_in_cache(search_id)
        elif choice == "3":
            print("\nSub-Menu:")
            print("1. Display World Info")
            print("2. Display Avatar Info")
            sub_choice = input("Choose an option: ")

            if sub_choice == "1":
                display_world_info()
            elif sub_choice == "2":
                display_ids_filtered("Avatar")
            else:
                print("Invalid option, please try again.")
        elif choice == "4":
            remove_duplicate_files_button()
        elif choice == "5":
            break
        else:
            print("Invalid option, please try again.")
#pas finit
def Network_database_menu():
    while True:
        print("\nNetwork Database Menu:")
        print("1. Display All IDs in Cache")
        print("2. Research an ID in Network Database")
        print("3. ")
        print("4. Filtered Network Research")
        print("5. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            display_all_ids()
        elif choice == "2":
            search_id = input("\nEnter the ID you want to search for: ")
            search_in_cache(search_id)
        elif choice == "3":
            search_id = input("\nEnter the ID you want to search for: ")
            search_id_in_database(search_id)
        elif choice == "4":
            print("\nSub-Menu:")
            print("1. Display World Info")
            print("2. Display Avatar Info")
            sub_choice = input("Choose an option: ")

            if sub_choice == "1":
                display_world_info()
            elif sub_choice == "2":
                display_ids_filtered("Avatar")
            else:
                print("Invalid option, please try again.")
        elif choice == "5":
            break
        else:
            print("Invalid option, please try again.")
#fait un RickRoll
def rickroll():
    url = 'https://youtu.be/a3Z7zEc7AXQ'
    wb.open(url)

if __name__ == "__main__":
    main_menu()
