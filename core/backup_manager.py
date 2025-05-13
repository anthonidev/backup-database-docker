#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import subprocess
from datetime import datetime

from core.system_utils import get_system_info
from config.settings import PGDUMP_PARAMS, POSTGRES_DOCKER_IMAGE, DEFAULT_BACKUP_FILENAME

class BackupManager:
    def __init__(self, logger_callback=None):
        """
        Inicializa el gestor de backups
        
        Args:
            logger_callback (callable): Función para registrar mensajes
        """
        self.logger = logger_callback if logger_callback else print
        self.system_info = get_system_info()
    
    def log(self, message):
        """Registra un mensaje usando el callback configurado"""
        if self.logger:
            self.logger(message)
    
    def parse_connection_url(self, connection_url):
        """Analiza una URL de conexión PostgreSQL y devuelve sus componentes"""
        pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, connection_url)
        
        if not match:
            self.log("✗ No se pudo analizar la URL de conexión.")
            return None
        
        return {
            "username": match.group(1),
            "password": match.group(2),
            "host": match.group(3),
            "port": match.group(4),
            "database": match.group(5)
        }
    
    def create_backup_filename(self, database_name):
        """Crea un nombre de archivo de backup con timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{database_name}_backup_{timestamp}.sql"
    
    def backup_with_docker(self, conn_info, backup_file, final_backup):
        """Ejecuta el backup usando Docker"""
        docker_command = [
            "docker", "run", "--rm",
            "-e", f"PGPASSWORD={conn_info['password']}",
            POSTGRES_DOCKER_IMAGE,
            "pg_dump",
            "-h", conn_info['host'],
            "-p", conn_info['port'],
            "-U", conn_info['username'],
            "-d", conn_info['database']
        ] + PGDUMP_PARAMS
        
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
                self.log(f"✓ Backup creado exitosamente: {backup_file}")
                os.rename(backup_file, final_backup)
                self.log(f"✓ Archivo renombrado a: {final_backup}")
                return True
            else:
                self.log(f"✗ Error al crear el backup:")
                self.log(process.stderr)
                return False
                
        except Exception as e:
            self.log(f"✗ Error al ejecutar el comando: {e}")
            return False
    
    def backup_with_local_pg_dump(self, conn_info, backup_file, final_backup):
        """Ejecuta el backup usando pg_dump local"""
        # Configurar variable de entorno para la contraseña
        env = os.environ.copy()
        env['PGPASSWORD'] = conn_info['password']
        
        pg_dump_command = [
            "pg_dump",
            "-h", conn_info['host'],
            "-p", conn_info['port'],
            "-U", conn_info['username'],
            "-d", conn_info['database'],
            "-f", backup_file
        ] + PGDUMP_PARAMS
        
        try:
            process = subprocess.run(
                pg_dump_command,
                env=env,
                capture_output=True,
                text=True
            )
            
            if process.returncode == 0:
                self.log(f"✓ Backup creado exitosamente: {backup_file}")
                os.rename(backup_file, final_backup)
                self.log(f"✓ Archivo renombrado a: {final_backup}")
                return True
            else:
                self.log(f"✗ Error al crear el backup:")
                self.log(process.stderr)
                return False
                
        except Exception as e:
            self.log(f"✗ Error al ejecutar el comando: {e}")
            return False
    
    def get_restore_instructions(self, conn_info, final_backup):
        """Genera instrucciones de restauración según el SO"""
        is_windows = self.system_info["is_windows"]
        is_macos = self.system_info["is_macos"]
        
        instructions = []
        instructions.append("=" * 50)
        instructions.append("INSTRUCCIONES DE RESTAURACIÓN")
        instructions.append("=" * 50)
        
        if is_windows:
            instructions.append("\nPara PowerShell:")
            instructions.append(f"Get-Content -Raw {final_backup} -Encoding UTF8 | docker exec -i nexus_db psql -U postgres -d NexusPlataformaDb")
            instructions.append("\nO alternativamente, usando el script PowerShell:")
            instructions.append(f".\\restore_database.ps1 -BackupFile {final_backup}")
        elif is_macos:
            instructions.append("\nOpción 1 - Si tienes PostgreSQL instalado localmente:")
            instructions.append(f"PGPASSWORD={conn_info['password']} psql -h {conn_info['host']} -p {conn_info['port']} -U {conn_info['username']} -d {conn_info['database']} < {final_backup}")
            instructions.append("\nOpción 2 - Usando Docker:")
            instructions.append(f"cat {final_backup} | docker exec -i nexus_db psql -U postgres -d NexusPlataformaDb")
            instructions.append("\nSi necesitas corregir problemas de codificación:")
            instructions.append(f"iconv -f UTF-8 -t UTF-8 {final_backup} | docker exec -i nexus_db psql -U postgres -d NexusPlataformaDb")
        else:
            instructions.append("\nPara restaurar en Linux/Unix:")
            instructions.append(f"cat {final_backup} | docker exec -i nexus_db psql -U postgres -d NexusPlataformaDb")
        
        return instructions