import os
import re
import sys
import shutil
from colorama import Fore, Style, init
import datetime
import time
import colorama
import hashlib
import json
import getpass
from collections import defaultdict
import requests
import traceback
import pyfiglet
import webbrowser as wb
import keyboard  # Import keyboard module for keypress handling
import vrchatapi
from vrchatapi.api import authentication_api
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode
from vrchatapi.api import avatars_api, worlds_api
from vrchatapi.rest import ApiException
from vrchatapi.api_client import ApiClient
from vrchatapi.configuration import Configuration
init(autoreset=True)
colorama.init()
user_directory = os.path.expanduser("~")

PATH = os.path.join(user_directory, "AppData", "LocalLow", "VRChat", "VRChat", "Cache-WindowsPlayer")

program_paused = False


# Fancy Welcome
def fancy_welcome(version="1.0.6", developers=None):
    if developers is None:
        developers = [
            {'name': 'Kaichi-Sama', 'role': 'Lead Developer'},
            {'name': '>_Unknown User', 'role': 'Backend Developer'},
        ]
    
    # ANSI escape codes for colors
    pink_color = '\033[95m'
    green_color = '\033[92m'
    red_color = '\033[91m'
    light_cyan_color = '\033[96m'
    reset_color = '\033[0m'
    box_width = 78  # The total width of the box

    # ASCII Art text for "Welcome to Kawaii Squad"
    welcome_text = r"""
 __    __                                    __  __         ______                                       __ 
/  |  /  |                                  /  |/  |       /      \                                     /  |
$$ | /$$/   ______   __   __   __   ______  $$/ $$/       /$$$$$$  |  ______   __    __   ______    ____$$ |
$$ |/$$/   /      \ /  | /  | /  | /      \ /  |/  |      $$ \__$$/  /      \ /  |  /  | /      \  /    $$ |
$$  $$<    $$$$$$  |$$ | $$ | $$ | $$$$$$  |$$ |$$ |      $$      \ /$$$$$$  |$$ |  $$ | $$$$$$  |/$$$$$$$ |
$$$$$  \   /    $$ |$$ | $$ | $$ | /    $$ |$$ |$$ |       $$$$$$  |$$ |  $$ |$$ |  $$ | /    $$ |$$ |  $$ |
$$ |$$  \ /$$$$$$$ |$$ \_$$ \_$$ |/$$$$$$$ |$$ |$$ |      /  \__$$ |$$ \__$$ |$$ \__$$ |/$$$$$$$ |$$ \__$$ |
$$ | $$  |$$    $$ |$$   $$   $$/ $$    $$ |$$ |$$ |      $$    $$/ $$    $$ |$$    $$/ $$    $$ |$$    $$ |
$$/   $$/  $$$$$$$/  $$$$$/$$$$/   $$$$$$$/ $$/ $$/        $$$$$$/   $$$$$$$ | $$$$$$/   $$$$$$$/  $$$$$$$/ 
                                                                          $$ |                              
                                                                          $$ |                              
                                                                          $$/                               
    """

    # Thank you message
    thank_you_text = "Thank you for using the Kawaii VRC Scanner Tool"

    # Version Box
    version_box = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                    Version: {version:<6}                               ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

    # Print the welcome message in pink
    print(pink_color + welcome_text + reset_color)
    # Print the thank you message in light cyan
    print(light_cyan_color + thank_you_text + reset_color)
    # Print the version box
    print(light_cyan_color + version_box + reset_color)

    # Heading for the developers section
    developers_heading = "Developers and Contributors"
    # Start of the box
    print(pink_color + "╔" + "═" * (box_width - 2) + "╗" + reset_color)
    # Heading
    print(pink_color + "║" + developers_heading.center(box_width - 2) + "║" + reset_color)
    # Separator
    print(pink_color + "║" + "─" * (box_width - 2) + "║" + reset_color)
    # List each developer and their role
    for dev in developers:
        name = dev.get('name', 'Unknown')
        role = dev.get('role', 'Contributor')
        # Prepare name and role with color
        name_colored = green_color + name + reset_color
        role_colored = red_color + role + reset_color
        # Creating the entry
        dev_entry = f"{name_colored} - {role_colored}"
        # Calculate the necessary padding
        padding = box_width - 2 - len(name) - len(role) - 3  # 3 for ' - ' between name and role
        left_padding = padding // 2
        right_padding = padding - left_padding
        # Print the entry
        print(pink_color + "║" + " " * left_padding + dev_entry + " " * right_padding + "║" + reset_color)
    # End of the box
    print(pink_color + "╚" + "═" * (box_width - 2) + "╝" + reset_color)
fancy_welcome("1.0.6")

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

#start le logger
def hash_file(filepath):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def load_log_data(log_path):
    """Load existing log data from a JSON file."""
    if not os.path.exists(log_path):
        return defaultdict(list)
    with open(log_path, 'r') as log_file:
        try:
            data = json.load(log_file)
            return defaultdict(list, data)  # Ensure it's a defaultdict
        except json.JSONDecodeError:
            return defaultdict(list)

def update_log_data(log_path, file_hash, file_id_without_extension, target_path):
    """Update log data with a new associated ID under the same HASH_ID and protect the first logged file from being removed."""
    log_data = load_log_data(log_path)

    # Check if the hash already exists in the log data
    if file_hash not in log_data:
        # It's the original file, so log it and return False (not a duplicate)
        log_data[file_hash] = [file_id_without_extension]
        with open(log_path, 'w') as log_file:
            json.dump(dict(log_data), log_file, indent=2)
        print(f"{Fore.BLUE}Original file logged: {file_id_without_extension}{Style.RESET_ALL}")
        return False

    # If the hash exists, but the file ID is not the first (original), it's a duplicate
    if file_id_without_extension != log_data[file_hash][0]:
        if file_id_without_extension not in log_data[file_hash]:
            # It's a new duplicate, so append it to the list
            log_data[file_hash].append(file_id_without_extension)
            with open(log_path, 'w') as log_file:
                json.dump(dict(log_data), log_file, indent=2)
            # Remove the duplicate file
            if os.path.exists(target_path):
                os.remove(target_path)
                print(f"{Fore.YELLOW}Duplicate file removed: {file_id_without_extension}{Style.RESET_ALL}")
            return True  # This is a duplicate
        else:
            # The file ID is already logged as a duplicate
            if os.path.exists(target_path):
                os.remove(target_path)
                print(f"{Fore.YELLOW}Duplicate file removed: {file_id_without_extension}{Style.RESET_ALL}")
            return True  # This is a confirmed duplicate
    else:
        # It's the original file
        print(f"{Fore.BLUE}Original file confirmed: {file_id_without_extension}{Style.RESET_ALL}")
        return False  # This is the original file, not a duplicate

def start_the_logger():
    print(f"{Fore.LIGHTMAGENTA_EX}Logger Started Network & Locally{Style.RESET_ALL}")
    create_directory("Logs")
    create_directory("VRCA")
    create_directory("VRCW")

    log_vrca_path = os.path.join("Logs", "ID_REF_VRCA.json")
    log_vrcw_path = os.path.join("Logs", "ID_REF_VRCW.json")

    processed_dirs = set()
    last_processed_time = None

    while True:
        new_processed_dirs = set()
        has_processed_files = False

        for root, dirs, files in os.walk(PATH):
            # Check if the directory has been modified since last check
            if root not in processed_dirs or last_processed_time is None or os.path.getmtime(root) > last_processed_time:
                new_processed_dirs.add(root)
                files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(root, x)))
                for file in files:
                    if file.endswith('__data'):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding="utf-8", errors='ignore') as f:
                                data = f.read()
                                avtr_ids_found = re.findall(r"avtr_[a-f0-9\-]{36}", data)
                                wrld_ids_found = re.findall(r"wrld_[a-f0-9\-]{36}", data)
                                if avtr_ids_found or wrld_ids_found:
                                    print(f"\n{Fore.YELLOW}File Analysis: {Fore.LIGHTCYAN_EX}{filepath}{Style.RESET_ALL}")
                                for ids_found, directory, log_path in [(avtr_ids_found, 'VRCA', log_vrca_path), (wrld_ids_found, 'VRCW', log_vrcw_path)]:
                                    for id_ in set(ids_found):
                                        file_id_without_extension = id_
                                        target_path = os.path.join(directory, f"{id_}.{directory.lower()}")
                                        file_hash = hash_file(filepath)
                                        
                                        is_duplicate = update_log_data(log_path, file_hash, file_id_without_extension, target_path)       
                                        if not os.path.exists(target_path) and not is_duplicate:
                                            shutil.copy(filepath, target_path)
                                            print(f"{datetime.datetime.now()} - {Fore.GREEN}{directory} Added Successfully: {id_}{Style.RESET_ALL}")
                                        elif os.path.exists(target_path):
                                            print(f"{datetime.datetime.now()} - {Fore.RED}{directory} Already Exists: {id_}{Style.RESET_ALL}")
                            has_processed_files = True
                        except Exception as e:
                            print(f"Error reading file {filepath}. Error message: {e}")
                            import traceback
                            traceback.print_exc()

        if not has_processed_files:
            # If no new files have been processed, wait for new files
            print(f"{datetime.datetime.now()} - Waiting for new files...")
            time.sleep(60)  # Wait for a minute before checking again

        processed_dirs.update(new_processed_dirs)
        last_processed_time = time.time()

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

#research id in local database   
def research_id_in_local_database(search_id):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    logs_path = os.path.join(current_directory, "Logs")
    file_names = ["ID_REF_VRCA.json", "ID_REF_VRCW.json"]
    file_found = False
    
    for file_name in file_names:
        file_path = os.path.join(logs_path, file_name)        
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)           
            for key, id_list in data.items():
                if search_id in id_list:
                    associated_id = id_list[0]  # Take the first ID in the list
                    # Determine whether the associated ID is VRCA or VRCW
                    file_type = "VRCA" if file_name.endswith("VRCA.json") else "VRCW"
                    associated_file_path = os.path.join(current_directory, file_type, f"{associated_id}.{file_type.lower()}")
                    print(Fore.GREEN + f"The searched ID is associated with: {associated_id}")
                    print(Fore.BLUE + "Here is the direct link to the file:")
                    print(Fore.YELLOW + associated_file_path)  # This may become a clickable link in some terminals
                    file_found = True
                    break  # Break the loop if the ID is found
        except FileNotFoundError:
            print(Fore.RED + f"File not found: {file_path}")
        except json.JSONDecodeError:
            print(Fore.RED + f"Could not parse JSON from file: {file_path}")

        if file_found:
            break  # Break the outer loop if the ID is found

    if not file_found:
        print(Fore.RED + "ID not found in any of the provided JSON files.")

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
        print("4. Research an ID in LocalDatabase")  # Nouvelle option ajoutée ici
        print("5. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            # Remplacez 'display_all_ids_in_cache' par le nom réel de votre fonction
            display_all_ids_in_cache()
        elif choice == "2":
            search_id = input("\nEnter the ID you want to research in cache: ")
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
        elif choice == "4":  # Nouveau cas pour la nouvelle option
            search_id = input("\nEnter the ID you want to research in the LocalDatabase: ")
            research_id_in_local_database(search_id)  # Fonction à définir
        elif choice == "5":
            break
        else:
            print("Invalid option, please try again.")
#pas finit
def Network_database_menu():   
    while True:
        print("\nNetwork Database Menu:")
        print("1. ")
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

#VRChat API & our API
if __name__ == "__main__":
    main_menu()
