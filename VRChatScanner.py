import os
import re
import sys
import shutil
from colorama import Fore, Style  # Import colorama for colored output
import datetime
import time
import colorama
import webbrowser as wb
import keyboard  # Import keyboard module for keypress handling
import requests
import base64
colorama.init()


def get_base64_credentials(username, password):
    credentials = f"{username}:{password}"
    credentials_bytes = credentials.encode('ascii')
    base64_bytes = base64.b64encode(credentials_bytes)
    base64_credentials = base64_bytes.decode('ascii')
    return base64_credentials

def vrchat_login():
    username = input("Entrez votre nom d'utilisateur VRChat: ")
    password = input("Entrez votre mot de passe VRChat: ")
    
    base64_credentials = get_base64_credentials(username, password)
    headers = {
        "Authorization": f"Basic {base64_credentials}"
    }
    
    url = "https://api.vrchat.cloud/api/1/auth/user"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("Connexion réussie!")
        print(response.json())
    elif "2FA" in response.text or response.status_code == 401:
        # Vous devriez vérifier la réponse exacte de VRChat pour savoir comment ils indiquent que la 2FA est requise.
        two_factor_code = input("Entrez votre code de double authentification: ")
        headers["X-VRChat-OTP"] = two_factor_code
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Connexion réussie!")
            print(response.json())
        else:
            print("Échec de la connexion. Vérifiez vos identifiants, votre code de double authentification et réessayez.")
            print("Status code:", response.status_code)
            print("Response:", response.text)
    else:
        print("Échec de la connexion. Vérifiez vos identifiants et réessayez.")
        print("Status code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    continue_execution = input("Voulez-vous exécuter la connexion VRChat ? (Oui/Non): ")
    if continue_execution.lower() == "oui":
        vrchat_login()
    else:
        print("Programme terminé.")

# Obtenez le répertoire de l'utilisateur actuel
user_directory = os.path.expanduser("~")

# Utilisez le répertoire de l'utilisateur pour créer des chemins de fichiers relatifs
PATH = os.path.join(user_directory, "AppData", "LocalLow", "VRChat", "VRChat", "Cache-WindowsPlayer")

# Variable pour mettre en pause le programme
program_paused = False

def animated_progress_bar(total, length=40):
    for i in range(total):
        progress = (i + 1) / total
        bar_length = int(length * progress)
        bar = "=" * bar_length + " " * (length - bar_length)
        sys.stdout.write(f"\r[{bar}] {int(progress * 100)}%")
        sys.stdout.flush()
        time.sleep(0.1)

# Utilisation de l'animation
animated_progress_bar(50)  # Par exemple, pour afficher une barre de progression de 50 étapes
print(f"{Fore.RED}\nNasa get Hacked by Kaichi-Sama.{Style.RESET_ALL}")

def save_vrcw_vrca_continuous():
    # Create "VRCW" and "VRCA" directories if they don't exist
    create_directory("VRCW")
    create_directory("VRCA")

    processed_files = set()  # Pour garder une trace des fichiers déjà traités

    while True:  # Boucle infinie pour surveiller le dossier en continu
        if program_paused:  # Vérifiez si le programme est en pause
            print("Program paused. Press F1 to resume.")
            while program_paused:
                if keyboard.is_pressed('F1'):  # Attendez la touche F1 pour reprendre
                    print("Program resumed.")
                    break
                time.sleep(1)
            continue  # Reprendre la boucle

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

def display_all_ids():
    print(f"\n{Fore.GREEN}♥ Kaichi-Sama Menu UwU ♥{Style.RESET_ALL}:")
    print("1. Display All IDs in Cache")
    print("2. Search an ID in Cache")
    print("3. Search ID in Your Database")
    print("4. Filtered Search")
    print("5. Save VRCW and VRCA")
    print("6. Exit")

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
        print(f"{Fore.GREEN}Une correspondance a été trouvée.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Aucune correspondance n'a été trouvée.{Style.RESET_ALL}")

def search_id_in_database(search_id):
    global program_paused  # Utilisez la variable globale pour la pause

    try:
        while not program_paused:
            # Votre code pour la recherche d'ID ici
            pass
    except KeyboardInterrupt:
        print("Function interrupted by user (F1). Returning to main menu.")
        return

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

    print(f"\nDisplaying {entity} Info in Your Database:")
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(f".{folder.lower()}"):
                entity_id = os.path.splitext(file)[0]
                print(f"{entity} ID: {entity_id}")

def display_world_info():
    print("\nDisplaying World Info in Your Database:")
    for root, dirs, files in os.walk("VRCW"):
        for file in files:
            if file.endswith(".vrcw"):
                world_id = os.path.splitext(file)[0]
                print(f"World ID: {world_id}")

<<<<<<< HEAD
=======
    if not found_in_vrca and not found_in_vrcw:
        print(f"{Fore.RED}Aucune correspondance trouvée.{Style.RESET_ALL}")

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

    print(f"\nDisplaying {entity} Info in Your Database:")
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(f".{folder.lower()}"):
                entity_id = os.path.splitext(file)[0]
                print(f"{entity} ID: {entity_id}")

def display_world_info():
    print("\nDisplaying World Info in Your Database:")
    for root, dirs, files in os.walk("VRCW"):
        for file in files:
            if file.endswith(".vrcw"):
                world_id = os.path.splitext(file)[0]
                print(f"World ID: {world_id}")

>>>>>>> a4b8ef1080d1b15495605ad53314ae150b09e630
def display_avatar_info():
    print("\nDisplaying Avatar Info in Your Database:")
    for root, dirs, files in os.walk("VRCA"):
        for file in files:
            if file.endswith(".vrca"):
                avatar_id = os.path.splitext(file)[0]
                print(f"Avatar ID: {avatar_id}")

def main():
    global program_paused

    while True:
        if not program_paused:
            print(f"{Fore.LIGHTMAGENTA_EX}Powered by Kawaii Squad{Style.RESET_ALL}")
            print(f"\n{Fore.GREEN}♥ Kaichi-Sama Menu UwU ♥{Style.RESET_ALL}:")
            print("1. Display All IDs in Cache")
            print("2. Search an ID in Cache")
            print("3. Search ID in Your Database")
            print("4. Filtered Search")
            print("5. Save VRCW and VRCA")
<<<<<<< HEAD
            print(f"{Fore.RED}6. DON'T CLICK HERE{Style.RESET_ALL}")  # Option 6 en rouge
            print("7. Exit")  # Mettez à jour le numéro des options ici
=======
            print("6. Exit")
>>>>>>> a4b8ef1080d1b15495605ad53314ae150b09e630
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
                save_vrcw_vrca_continuous()
<<<<<<< HEAD
            elif choice == "6":  # Ajout de l'option "DON'T CLICK HERE" en rouge
                open_youtube()  # Exécute la fonction pour ouvrir YouTube
            elif choice == "7":  # Mettez à jour le numéro de sortie ici
=======
            elif choice == "6":
>>>>>>> a4b8ef1080d1b15495605ad53314ae150b09e630
                print("\nGoodbye!")
                break
            else:
                print("Invalid option, please try again.")
        else:
            if keyboard.is_pressed('F1'):
                program_paused = False
                print("Program resumed.")
                continue  # Revenir au menu principal
            time.sleep(1)  # Attendez pendant 1 seconde lorsque le programme est en pause

def open_youtube():
    url = 'https://youtu.be/a3Z7zEc7AXQ'
    wb.open(url)

if __name__ == "__main__":
    main()
    
