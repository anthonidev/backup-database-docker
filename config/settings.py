#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuración de la aplicación
APP_TITLE = "PostgreSQL Backup Tool"
DEFAULT_WIDTH = 700
DEFAULT_HEIGHT = 600

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