#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess

def get_system_info():
    """Detecta el sistema operativo y devuelve información básica"""
    
    # Detectar sistema operativo
    is_windows = sys.platform.startswith('win')
    is_macos = sys.platform == 'darwin'
    is_linux = sys.platform.startswith('linux')
    
    os_name = "Windows" if is_windows else "macOS" if is_macos else "Linux" if is_linux else sys.platform
    
    return {
        "os_name": os_name,
        "platform": sys.platform,
        "is_windows": is_windows,
        "is_macos": is_macos,
        "is_linux": is_linux
    }

def check_docker():
    """Verifica si Docker está disponible"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_pg_dump():
    """Verifica si pg_dump está instalado localmente"""
    try:
        subprocess.run(["pg_dump", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_available_tools():
    """Devuelve información sobre las herramientas disponibles"""
    return {
        "has_docker": check_docker(),
        "has_pg_dump": check_pg_dump()
    }

def get_install_instructions():
    """Devuelve instrucciones de instalación según SO"""
    system_info = get_system_info()
    
    instructions = "Por favor, instala una de las siguientes opciones:\n"
    
    if system_info["is_macos"]:
        instructions += "1. Instalar PostgreSQL client: brew install postgresql\n"
        instructions += "2. Instalar Docker: https://www.docker.com/products/docker-desktop/"
    elif system_info["is_windows"]:
        instructions += "1. Instalar Docker: https://www.docker.com/products/docker-desktop/"
    else:  # Linux
        instructions += "1. Instalar PostgreSQL client: sudo apt-get install postgresql-client\n"
        instructions += "2. Instalar Docker: https://www.docker.com/products/docker-desktop/"
    
    return instructions