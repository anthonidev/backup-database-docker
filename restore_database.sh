#!/bin/bash

# Script para restaurar base de datos PostgreSQL con manejo apropiado de codificación UTF-8
# Compatible con macOS y Linux

# Valores por defecto
BACKUP_FILE="backup.sql"
CONTAINER_NAME="nexus_db"
DATABASE_NAME="NexusDB"
USERNAME="postgres"
HOST="localhost"
PORT="5432"
PASSWORD="123"

# Función para mostrar uso
usage() {
    echo "Uso: $0 [opciones]"
    echo "Opciones:"
    echo "  -f, --file          Archivo de backup (default: backup.sql)"
    echo "  -c, --container     Nombre del contenedor Docker (default: nexus_db)"
    echo "  -d, --database      Nombre de la base de datos (default: NexusPlataformaDb)"
    echo "  -u, --username      Usuario de PostgreSQL (default: postgres)"
    echo "  -h, --host          Host (default: localhost)"
    echo "  -p, --port          Puerto (default: 5432)"
    echo "  -P, --password      Contraseña (default: 123)"
    echo "  --help              Mostrar este mensaje"
    exit 1
}

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            BACKUP_FILE="$2"
            shift 2
            ;;
        -c|--container)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -d|--database)
            DATABASE_NAME="$2"
            shift 2
            ;;
        -u|--username)
            USERNAME="$2"
            shift 2
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -P|--password)
            PASSWORD="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            echo "Opción desconocida: $1"
            usage
            ;;
    esac
done

# Verificar que el archivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: El archivo de backup $BACKUP_FILE no existe."
    exit 1
fi

# Función para verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker no está instalado."
        echo "Instalar Docker en macOS: brew install --cask docker"
        exit 1
    fi
}

# Función para verificar si psql está instalado
check_psql() {
    if ! command -v psql &> /dev/null; then
        return 1
    fi
    return 0
}

# Función para restaurar usando Docker
restore_with_docker() {
    # Verificar que el contenedor está en ejecución
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        echo "Error: El contenedor $CONTAINER_NAME no está en ejecución."
        exit 1
    fi

    echo "Configurando entorno del contenedor para UTF-8..."
    docker exec -i "$CONTAINER_NAME" bash -c "echo 'client_encoding = UTF8;' > /tmp/psqlrc"
    docker exec -i "$CONTAINER_NAME" bash -c "export PGCLIENTENCODING=UTF8"

    echo "Restaurando la base de datos desde $BACKUP_FILE..."
    # Método 1: Copiar el archivo al contenedor y restaurar desde allí
    docker cp "$BACKUP_FILE" "${CONTAINER_NAME}:/tmp/backup.sql"
    
    if docker exec -i "$CONTAINER_NAME" bash -c "PGCLIENTENCODING=UTF8 psql -U $USERNAME -d $DATABASE_NAME -f /tmp/backup.sql"; then
        echo "¡Base de datos restaurada exitosamente!"
        docker exec -i "$CONTAINER_NAME" rm /tmp/backup.sql
    else
        echo "Error al restaurar la base de datos."
        docker exec -i "$CONTAINER_NAME" rm /tmp/backup.sql
        exit 1
    fi
}

# Función para restaurar usando psql local
restore_with_local_psql() {
    echo "Restaurando la base de datos usando psql local..."
    
    # Usar PGPASSWORD para enviar la contraseña
    export PGPASSWORD="$PASSWORD"
    
    if psql -h "$HOST" -p "$PORT" -U "$USERNAME" -d "$DATABASE_NAME" < "$BACKUP_FILE"; then
        echo "¡Base de datos restaurada exitosamente!"
    else
        echo "Error al restaurar la base de datos."
        exit 1
    fi
    
    # Limpiar la variable de contraseña
    unset PGPASSWORD
}

# Detectar sistema operativo
OS=$(uname -s)
echo "Detectado: $OS"

# Verificar herramientas disponibles
has_docker=false
has_psql=false

if check_docker 2>/dev/null; then
    has_docker=true
fi

if check_psql; then
    has_psql=true
fi

echo "Docker disponible: $has_docker"
echo "psql disponible: $has_psql"

# Ejecutar restauración según las herramientas disponibles
if [ "$has_docker" = true ]; then
    restore_with_docker
elif [ "$has_psql" = true ]; then
    restore_with_local_psql
else
    echo "Error: No hay herramientas disponibles para restaurar la base de datos."
    echo "Por favor, instala una de las siguientes opciones:"
    if [ "$OS" = "Darwin" ]; then
        echo "1. Docker: brew install --cask docker"
        echo "2. PostgreSQL client: brew install postgresql"
    else
        echo "1. Docker: https://www.docker.com/"
        echo "2. PostgreSQL client: sudo apt-get install postgresql-client"
    fi
    exit 1
fi

echo "Nota: Si aún hay problemas con caracteres especiales, verifica la configuración de tu contenedor PostgreSQL."