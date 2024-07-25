# Installman

![installman-static-128x128](https://github.com/user-attachments/assets/8a9ecdde-7500-4898-acb1-9af5c12d5a3a)



Un administrador de paquetes para Windows (Posteriormente será para Linux y posiblemente macOS) para instalar paquetes.

#### Ejecutar como administrador.


## Prerequisitos

Usar `pip install -r requirements.txt`

Argumentos:

`install Nombrepaquete` Para instalar un paquete

`--installed` Para mostrar los paquetes

`update` Para actualizar todos los paquetes instalados vía Installman

# PARA LOS QUE QUIERAN CREAR SU PROPIO REPOSITORIO CON PAQUETES E INSTALLMAN CUSTOM

Usar createkey.py (dentro del repositorio de paquetes) para crear una clave con Fernet para tu repositorio, posteriormente crear un archivo key.iky con la clave fernet en texto plano

Hay que modificar las siguientes líneas

Modificar la línea `KEY_URL = "https://github.com/danucosukosuko/installmanpkgs/raw/main/key.iky"` y poner vuestro nombre y nombre de repositorio en vez de mi nombre
