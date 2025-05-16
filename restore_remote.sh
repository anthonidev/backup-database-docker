#!/bin/bash

# Script para restaurar base de datos PostgreSQL en un servidor remoto
# Compatible con macOS y Linux

# Valores por defecto
BACKUP_FILE="backup.sql"
CONNECTION_URL="postgresql://postgres:123@localhost:5432/postgres"

# Función para mostrar uso
usage() {
    echo "Uso: $0 [opciones]"
    echo "Opciones:"
    echo "  -f, --file          Archivo de backup (default: backup.sql)"
    echo "  -c, --connection    URL de conexión PostgreSQL (default: postgresql://postgres:123@localhost:5432/postgres)"
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
        -c|--connection)
            CONNECTION_URL="$2"
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

# Función para verificar si psql está instalado
check_psql() {
    if ! command -v psql &> /dev/null; then
        echo "Error: psql no está instalado."
        echo "Instalar psql en macOS: brew install postgresql"
        echo "Instalar psql en Linux: sudo apt-get install postgresql-client"
        exit 1
    fi
}

# Función para analizar URL de conexión
parse_connection_url() {
    local url=$1
    
    # Extraer partes de la URL
    if [[ $url =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
        USERNAME="${BASH_REMATCH[1]}"
        PASSWORD="${BASH_REMATCH[2]}"
        HOST="${BASH_REMATCH[3]}"
        PORT="${BASH_REMATCH[4]}"
        DATABASE="${BASH_REMATCH[5]}"
        
        echo "Usuario: $USERNAME"
        echo "Host: $HOST"
        echo "Puerto: $PORT"
        echo "Base de datos: $DATABASE"
        
        return 0
    else
        echo "Error: Formato de URL incorrecto."
        echo "Formato esperado: postgresql://usuario:contraseña@host:puerto/basededatos"
        return 1
    fi
}

# Función para restaurar usando psql
restore_with_psql() {
    local backup_file=$1
    local connection_url=$2
    
    # Analizar URL de conexión
    if ! parse_connection_url "$connection_url"; then
        return 1
    fi
    
    echo "Restaurando la base de datos desde $backup_file..."
    echo "Destino: $HOST:$PORT/$DATABASE"
    
    # Usar PGPASSWORD para enviar la contraseña
    export PGPASSWORD="$PASSWORD"
    
    # Establecer codificación UTF-8
    export PGCLIENTENCODING=UTF8
    
    # Ejecutar restauración
    if psql -h "$HOST" -p "$PORT" -U "$USERNAME" -d "$DATABASE" < "$backup_file"; then
        echo "¡Base de datos restaurada exitosamente!"
        return 0
    else
        echo "Error al restaurar la base de datos."
        return 1
    fi
}

# Verificar herramientas disponibles
check_psql

# Ejecutar restauración
restore_with_psql "$BACKUP_FILE" "$CONNECTION_URL"

# Limpiar variable de contraseña
unset PGPASSWORD

echo "Nota: Si hay problemas con caracteres especiales, verifica la configuración de codificación de PostgreSQL."