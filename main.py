import os
import subprocess
from datetime import datetime
import re
import sys

# Extraer información de la URL de conexión
# DB_NAME=NexusPlataformaDb
# DB_USERNAME=postgres

# DB_HOST=localhost
# DB_PASSWORD=123
# DB_PORT=5432
# URL de conexión a la base de datos
connection_url = "postgresql://postgres:123@localhost:5432/NexusPlataformaDb"

# Usar expresiones regulares para extraer los componentes
pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
match = re.match(pattern, connection_url)

if match:
    username = match.group(1)
    password = match.group(2)
    host = match.group(3)
    port = match.group(4)
    database = match.group(5)

    # Verificar si estamos en Windows
    is_windows = sys.platform.startswith('win')

    # Usar docker para ejecutar pg_dump si estamos en Windows
    if is_windows:
        # Crear nombre de archivo con fecha y hora actual
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{database}_backup_{timestamp}.sql"
        final_backup = "backup.sql"

        # Comando para ejecutar pg_dump dentro de un contenedor Docker
        # Usamos postgres:16 para coincidir con la versión del servidor
        docker_command = [
            "docker", "run", "--rm",
            "-e", f"PGPASSWORD={password}",
            "postgres:16",
            "pg_dump",
            "-h", host,
            "-p", port,
            "-U", username,
            "-d", database,
            "-c",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            "--encoding=UTF8"  # Especificar codificación UTF-8
        ]

        try:
            # Ejecutar el comando y guardar la salida en un archivo con codificación UTF-8
            with open(backup_file, 'w', encoding='utf-8') as f:
                process = subprocess.run(
                    docker_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'  # Especificar la codificación UTF-8 para el proceso
                )

                # Escribir la salida en el archivo con codificación UTF-8
                f.write(process.stdout)

            if process.returncode == 0:
                print(f"Backup creado exitosamente: {backup_file}")

                # Renombrar el archivo a backup.sql
                os.rename(backup_file, final_backup)
                print(f"Archivo renombrado a: {final_backup}")

                # Instrucciones para restaurar
                print("\nPara restaurar el backup en tu contenedor Docker:")
                print(
                    f"Get-Content -Raw {final_backup} -Encoding UTF8 | docker exec -i nexus_db psql -U postgres -d NexusPlataformaDb")
            else:
                print(f"Error al crear el backup:")
                print(process.stderr)

        except Exception as e:
            print(f"Error al ejecutar el comando: {e}")

    else:
        # En sistemas Unix, podemos usar pg_dump directamente si está instalado
        print("Este script está optimizado para Windows. En sistemas Unix, considera instalar PostgreSQL cliente.")

else:
    print("No se pudo analizar la URL de conexión.")
