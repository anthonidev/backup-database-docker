import os
import subprocess
from datetime import datetime
import re
import sys
import shutil

# Configuración de la base de datos
connection_url = input("Introduce la URL de conexión a la base de datos (ejemplo: postgresql://usuario:contraseña@localhost:5432/mi_base_de_datos): ")

# Usar expresiones regulares para extraer los componentes
pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
match = re.match(pattern, connection_url)

if match:
    username = match.group(1)
    password = match.group(2)
    host = match.group(3)
    port = match.group(4)
    database = match.group(5)

    # Detectar el sistema operativo
    is_windows = sys.platform.startswith('win')
    is_macos = sys.platform == 'darwin'
    is_linux = sys.platform.startswith('linux')

    # Crear nombre de archivo con fecha y hora actual
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{database}_backup_{timestamp}.sql"
    final_backup = "backup.sql"

    # Función para verificar si Docker está disponible
    def check_docker():
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    # Función para verificar si pg_dump está instalado localmente
    def check_pg_dump():
        try:
            subprocess.run(["pg_dump", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    # Función para ejecutar el backup usando Docker
    def backup_with_docker():
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
            "--encoding=UTF8"
        ]

        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                process = subprocess.run(
                    docker_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                f.write(process.stdout)

            if process.returncode == 0:
                print(f"✓ Backup creado exitosamente: {backup_file}")
                os.rename(backup_file, final_backup)
                print(f"✓ Archivo renombrado a: {final_backup}")
                return True
            else:
                print(f"✗ Error al crear el backup:")
                print(process.stderr)
                return False

        except Exception as e:
            print(f"✗ Error al ejecutar el comando: {e}")
            return False

    # Función para ejecutar el backup usando pg_dump local
    def backup_with_local_pg_dump():
        # Configurar variable de entorno para la contraseña
        env = os.environ.copy()
        env['PGPASSWORD'] = password

        pg_dump_command = [
            "pg_dump",
            "-h", host,
            "-p", port,
            "-U", username,
            "-d", database,
            "-c",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            "--encoding=UTF8",
            "-f", backup_file
        ]

        try:
            process = subprocess.run(
                pg_dump_command,
                env=env,
                capture_output=True,
                text=True
            )

            if process.returncode == 0:
                print(f"✓ Backup creado exitosamente: {backup_file}")
                os.rename(backup_file, final_backup)
                print(f"✓ Archivo renombrado a: {final_backup}")
                return True
            else:
                print(f"✗ Error al crear el backup:")
                print(process.stderr)
                return False

        except Exception as e:
            print(f"✗ Error al ejecutar el comando: {e}")
            return False

    # Función para imprimir instrucciones de restauración según el SO
    def print_restore_instructions():
        print("\n" + "="*50)
        print("INSTRUCCIONES DE RESTAURACIÓN")
        print("="*50)
        
        if is_windows:
            print("\nPara PowerShell:")
            print(f"Get-Content -Raw {final_backup} -Encoding UTF8 | docker exec -i nexus_db psql -U postgres -d NexusPlataformaDb")
            print("\nO alternativamente, usando el script PowerShell:")
            print(f".\\restore_database.ps1 -BackupFile {final_backup}")
        elif is_macos:
            print("\nOpción 1 - Si tienes PostgreSQL instalado localmente:")
            print(f"PGPASSWORD={password} psql -h {host} -p {port} -U {username} -d {database} < {final_backup}")
            print("\nOpción 2 - Usando Docker:")
            print(f"cat {final_backup} | docker exec -i nexus_db psql -U postgres -d NexusPlataformaDb")
            print("\nSi necesitas corregir problemas de codificación:")
            print(f"iconv -f UTF-8 -t UTF-8 {final_backup} | docker exec -i nexus_db psql -U postgres -d NexusPlataformaDb")
        else:
            print("\nPara restaurar en Linux/Unix:")
            print(f"cat {final_backup} | docker exec -i nexus_db psql -U postgres -d NexusPlataformaDb")

    # Lógica principal de respaldo
    print("="*50)
    print(f"INICIANDO BACKUP DE BASE DE DATOS")
    print(f"Sistema operativo: {sys.platform}")
    print("="*50)

    # Verificar qué herramientas están disponibles
    has_docker = check_docker()
    has_pg_dump = check_pg_dump()

    print(f"\nVerificación de herramientas:")
    print(f"Docker: {'✓ disponible' if has_docker else '✗ no disponible'}")
    print(f"pg_dump: {'✓ disponible' if has_pg_dump else '✗ no disponible'}")

    # Ejecutar backup según las herramientas disponibles
    backup_successful = False

    if has_pg_dump and not is_windows:
        print(f"\n→ Usando pg_dump local...")
        backup_successful = backup_with_local_pg_dump()
    elif has_docker:
        print(f"\n→ Usando Docker...")
        backup_successful = backup_with_docker()
    else:
        print("\n✗ No hay herramientas disponibles para crear el backup.")
        print("\nPor favor, instala una de las siguientes opciones:")
        if is_macos:
            print("1. Instalar PostgreSQL client: brew install postgresql")
            print("2. Instalar Docker: https://www.docker.com/products/docker-desktop/")
        elif is_windows:
            print("1. Instalar Docker: https://www.docker.com/products/docker-desktop/")
        else:
            print("1. Instalar PostgreSQL client: sudo apt-get install postgresql-client")
            print("2. Instalar Docker: https://www.docker.com/products/docker-desktop/")

    # Mostrar instrucciones de restauración si el backup fue exitoso
    if backup_successful:
        print_restore_instructions()

else:
    print("✗ No se pudo analizar la URL de conexión.") 