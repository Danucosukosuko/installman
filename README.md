# Installman

![installman-static-128x128](https://github.com/user-attachments/assets/8a9ecdde-7500-4898-acb1-9af5c12d5a3a)



Un administrador de paquetes para Windows (Posteriormente será para Linux y posiblemente macOS) para instalar paquetes.

#### Ejecutar como administrador.


## Prerequisitos

Usar `pip install -r requirements.txt`

Si quiere iniciar el programa sin descargarlo:

`curl https://raw.githubusercontent.com/Danucosukosuko/installman/main/installman.py | python`

Argumentos:

`install Nombrepaquete` Para instalar un paquete

`--installed` Para mostrar los paquetes

`update` Para actualizar todos los paquetes instalados vía Installman


Se creará una carpeta: `C:\installman`

En esa carpeta se creará un `data.dat` encriptado con fernet, ese archivo contiene los nombres de paquete encriptados 10 veces. Data.dat sólo puede ser desencriptado con key.iky


# PARA LOS QUE QUIERAN CREAR SU PROPIO REPOSITORIO CON PAQUETES E INSTALLMAN CUSTOM

Usar createkey.py (dentro del repositorio de paquetes) para crear una clave con Fernet para tu repositorio, posteriormente crear un archivo key.iky con la clave fernet en texto plano

Hay que modificar las siguientes líneas

Modificar la línea `KEY_URL = "https://github.com/danucosukosuko/installmanpkgs/raw/main/key.iky"` y poner vuestro repositorio (Poner key.iky)

Modificar la línea `response = requests.get("https://api.github.com/repos/danucosukosuko/installmanpkgs/contents")` y poner vuestro repositorio (Cuidado con no borrar `contents` y poner `api.github.com/repos`)

Modificar la línea: `download_url = f"https://github.com/danucosukosuko/installmanpkgs/raw/main/{package_name}.zip"` y poner vuestro repositorio (Cuidado con no borrar `raw/main/{package_name}.zip`)
