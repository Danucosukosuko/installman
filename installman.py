import os
import requests
import zipfile
import subprocess
import base64
from cryptography.fernet import Fernet, InvalidToken
import hashlib
import sys
import urllib3
from tqdm import tqdm
from termcolor import colored
import shutil

# URL del archivo de clave
KEY_URL = "https://github.com/danucosukosuko/installmanpkgs/raw/main/key.iky"

# Ruta de la carpeta installman
INSTALLMAN_DIR = "C:\\installman"

# Ruta del archivo data.dat
DATA_FILE_PATH = os.path.join(INSTALLMAN_DIR, "data.dat")

# Ruta del archivo retry.dat
RETRY_FILE_PATH = os.path.join(INSTALLMAN_DIR, "retry.dat")

# Función para obtener la clave desde la URL
def get_secret_key():
    try:
        response = requests.get(KEY_URL)
        response.raise_for_status()  # Verifica si la solicitud fue exitosa
        return response.content.strip()
    except requests.exceptions.RequestException as e:
        print(colored("No se pueden encontrar los paquetes. Revise su conexión a internet e inténtelo de nuevo más tarde.", 'red'))
        sys.exit(1)

# Obtener la clave desde la URL
secret_key = get_secret_key()

if secret_key:
    # Configurar la clave Fernet
    cipher_suite = Fernet(secret_key)
else:
    print(colored("No se pudo obtener la clave. Verifica la conexión o la disponibilidad de la URL.", 'red'))
    sys.exit(1)

# Función para encriptar y desencriptar nombres de paquetes
def encrypt_package_name(package_name):
    encrypted_name = package_name.encode('utf-8')
    for _ in range(10):  # Encriptar 10 veces
        encrypted_name = cipher_suite.encrypt(encrypted_name)
    return encrypted_name

def decrypt_package_name(encrypted_name):
    decrypted_name = encrypted_name
    for _ in range(10):  # Desencriptar 10 veces
        decrypted_name = cipher_suite.decrypt(decrypted_name)
    return decrypted_name.decode('utf-8')

# Función para obtener la lista de paquetes disponibles
def get_available_packages():
    try:
        response = requests.get("https://api.github.com/repos/danucosukosuko/installmanpkgs/contents")
        response.raise_for_status()
        packages = [item['name'] for item in response.json() if item['name'].endswith('.zip')]
        return packages
    except requests.exceptions.RequestException as e:
        print(colored("No se pueden encontrar los paquetes. Revise su conexión a internet e inténtelo de nuevo más tarde.", 'red'))
        sys.exit(1)

# Función para descargar e instalar un paquete
def download_and_install_package(package_name, retry=False):
    download_url = f"https://github.com/danucosukosuko/installmanpkgs/raw/main/{package_name}.zip"
    download_path = os.path.join(INSTALLMAN_DIR, f"{package_name}.zip")
    extract_path = os.path.join(INSTALLMAN_DIR, package_name)

    if not os.path.exists(INSTALLMAN_DIR):
        os.makedirs(INSTALLMAN_DIR)

    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, colour='blue')

        with open(download_path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        os.remove(download_path)

        setup_exe_path = os.path.join(extract_path, "setup.exe")
        setup_msi_path = os.path.join(extract_path, "setup.msi")

        if os.path.exists(setup_exe_path):
            result = subprocess.run([setup_exe_path], check=True)
        elif os.path.exists(setup_msi_path):
            result = subprocess.run(["msiexec", "/i", setup_msi_path, "/quiet", "/norestart"], check=True)
        else:
            raise FileNotFoundError("El archivo setup.exe o setup.msi no se encontró")

        if result.returncode == 0:
            print(colored(f'El paquete "{package_name}" se ha instalado correctamente', 'green'))
            shutil.rmtree(extract_path)
        else:
            raise subprocess.CalledProcessError(result.returncode, setup_exe_path)

    except (requests.exceptions.RequestException, zipfile.BadZipFile) as e:
        print(colored(f"Error: No se puede descargar o extraer el paquete {package_name}.", 'red'))
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(colored(f"Ocurrió algún problema durante la instalación. Si quiere intentar instalar el programa pruebe con --retry-install", 'red'))
        if not retry:
            with open(RETRY_FILE_PATH, "wb") as retry_file:
                retry_file.write(package_name.encode('utf-8'))
        sys.exit(1)

# Función para actualizar los paquetes
def update_packages():
    if os.path.exists(DATA_FILE_PATH):
        with open(DATA_FILE_PATH, "rb") as file:
            encrypted_names = file.readlines()
        package_names = []
        for name in encrypted_names:
            try:
                decrypted_name = decrypt_package_name(name.strip())
                package_names.append(decrypted_name)
            except InvalidToken:
                print(colored("Error al desencriptar un nombre de paquete. El archivo data.dat puede estar corrupto.", 'red'))
        for package_name in package_names:
            download_and_install_package(package_name)
    else:
        print(colored("No se encontró el archivo data.dat. Asegúrese de que existe y vuelva a intentarlo.", 'red'))

# Función para guardar los nombres de los paquetes en data.dat
def save_package_names(package_names):
    if os.path.exists(DATA_FILE_PATH):
        with open(DATA_FILE_PATH, "rb") as file:
            existing_names = file.readlines()
        decrypted_names = []
        for name in existing_names:
            try:
                decrypted_name = decrypt_package_name(name.strip())
                decrypted_names.append(decrypted_name)
            except InvalidToken:
                print(colored("Error al desencriptar un nombre de paquete existente. Ignorando el paquete corrupto.", 'red'))
    else:
        decrypted_names = []

    with open(DATA_FILE_PATH, "ab") as file:
        for package_name in package_names:
            if package_name not in decrypted_names:
                encrypted_name = encrypt_package_name(package_name)
                file.write(encrypted_name + b'\n')

# Función para mostrar los paquetes instalados
def show_installed_packages():
    if os.path.exists(DATA_FILE_PATH):
        with open(DATA_FILE_PATH, "rb") as file:
            encrypted_names = file.readlines()
        package_names = []
        for name in encrypted_names:
            try:
                decrypted_name = decrypt_package_name(name.strip())
                package_names.append(decrypted_name)
            except InvalidToken:
                print(colored("Error al desencriptar un nombre de paquete. El archivo data.dat puede estar corrupto.", 'red'))
        print(colored("Paquetes instalados:", 'green'))
        for package_name in package_names:
            print(package_name)
    else:
        print(colored("No se encontró el archivo data.dat.", 'red'))

# Comprobación de parámetros y ejecución de comandos
if len(sys.argv) < 2:
    print("Uso: python installman.py [comando] [paquete]")
    sys.exit(1)

command = sys.argv[1]

if command == "install":
    if len(sys.argv) != 3:
        print("Uso: python installman.py install [paquete]")
        sys.exit(1)
    package_name = sys.argv[2]
    if package_name == "--retry-install":
        if os.path.exists(RETRY_FILE_PATH):
            with open(RETRY_FILE_PATH, "rb") as retry_file:
                package_name = retry_file.read().decode('utf-8')
            os.remove(RETRY_FILE_PATH)
            download_and_install_package(package_name, retry=True)
        else:
            print(colored("No se encontró ningún paquete para reintentar la instalación.", 'red'))
    else:
        download_and_install_package(package_name)
        # Guardar el paquete instalado en data.dat
        save_package_names([package_name])

elif command == "update":
    update_packages()

elif command == "--installed":
    show_installed_packages()

else:
    print("Comando no reconocido. Los comandos disponibles son: install, update, --installed")
    sys.exit(1)
