#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuración de la aplicación
APP_TITLE = "PostgreSQL Backup & Restore Tool"
DEFAULT_WIDTH = 700
DEFAULT_HEIGHT = 650

# Configuración por defecto de la conexión
DEFAULT_CONNECTION_URL = "postgresql://usuario:contraseña@localhost:5432/mi_base_de_datos"

# Nombres de archivos
DEFAULT_BACKUP_FILENAME = "backup.sql"

# Comandos y parámetros de backup
PGDUMP_PARAMS = [
    "-c",
    "--if-exists",
    "--no-owner",
    "--no-privileges",
    "--encoding=UTF8"
]

# Imagen Docker para PostgreSQL
POSTGRES_DOCKER_IMAGE = "postgres:16"

# Configuración por defecto para restauración
DEFAULT_CONTAINER_NAME = "nexus_db"
DEFAULT_DATABASE_NAME = "NexusDB"
DEFAULT_USERNAME = "postgres"
DEFAULT_REMOTE_CONNECTION_URL = "postgresql://postgres:123@remotehost:5432/postgres"